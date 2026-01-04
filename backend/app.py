import re
from urllib.parse import urlparse, parse_qs

from flask import Flask, jsonify, request

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False  # keep Unicode like ♪


# ----------------------------
# 1) Transcript function
# ----------------------------
def get_transcript(video_id: str) -> str:
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id)  # new API versions
    raw = TextFormatter().format_transcript(fetched)
    return raw.strip()


# ----------------------------
# 2) Summarization setup + function
# ----------------------------
CHECKPOINT = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
model = AutoModelForSeq2SeqLM.from_pretrained(CHECKPOINT)

def summarize_transcript(transcript: str) -> str:
    text = transcript.strip()  # NO "summarize: " prefix for BART

    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=1024,   # BART max input tokens
        truncation=True
    )

    summary_ids = model.generate(
        **inputs,
        num_beams=6,
        max_new_tokens=180,
        min_new_tokens=60,
        length_penalty=1.0,
        no_repeat_ngram_size=3,
        early_stopping=True
    )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()

# ----------------------------
# 3) Extract video id from YouTube URL
# ----------------------------
def extract_youtube_video_id(youtube_url: str) -> str:
    """
    Supports:
      - https://www.youtube.com/watch?v=VIDEOID
      - https://youtu.be/VIDEOID
      - https://www.youtube.com/shorts/VIDEOID
      - https://www.youtube.com/embed/VIDEOID
    """
    if not youtube_url or not isinstance(youtube_url, str):
        raise ValueError("youtube_url is required")

    # If user passes just the id, accept it (11 chars typical)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", youtube_url.strip()):
        return youtube_url.strip()

    parsed = urlparse(youtube_url.strip())
    host = (parsed.netloc or "").lower()
    path = parsed.path or ""

    # youtu.be/<id>
    if "youtu.be" in host:
        vid = path.lstrip("/").split("/")[0]
        if vid:
            return vid

    # youtube.com/watch?v=<id>
    if "youtube.com" in host:
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]

        # youtube.com/shorts/<id> or /embed/<id>
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2 and parts[0] in ("shorts", "embed"):
            return parts[1]

    raise ValueError("Could not extract video id from the provided URL")


# ----------------------------
# 4) Required REST endpoint
# ----------------------------
@app.get("/api/summarize")
def api_summarize():
    try:
        youtube_url = request.args.get("youtube_url", "").strip()
        if not youtube_url:
            return jsonify(error="Missing required query param: youtube_url"), 400

        video_id = extract_youtube_video_id(youtube_url)

        transcript = get_transcript(video_id)
        summary = summarize_transcript(transcript)

        return jsonify(
            video_id=video_id,
            summary=summary
        ), 200

    except ValueError as e:
        # bad input like invalid URL
        return jsonify(error=str(e)), 400
    except Exception as e:
        # transcript not available, network issues, etc.
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
