from flask import Flask, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok")

def get_transcript(video_id: str) -> str:
    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = ytt_api.fetch(video_id)

    formatter = TextFormatter()
    full_text = formatter.format_transcript(fetched_transcript)

    return " ".join(full_text.split())

@app.get("/transcript/<video_id>")
def transcript(video_id):
    try:
        text = get_transcript(video_id)
        return jsonify(transcript=text)
    except Exception as e:
        return jsonify(error=str(e)), 400
    
CHECKPOINT = "t5-small" # small + fast, can switch to "facebook/bart-large-cnn" later

# Load once at startup (important: don’t reload on every request)
tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
model = AutoModelForSeq2SeqLM.from_pretrained(CHECKPOINT)

def summerize_transcript(transcript: str) -> str:
    """
    Accepts a transcript string and returns an abstractive summary string.
    Uses an encoder-decoder model (T5) and model.generate().
    """

    # T5 requires a task prefix for summarization
    text = "summerize: " + transcript.strip() # per HF guidance :contentReference[oaicite:1]{index=1}

    # Tokenize with truncation so we don't exceed model max input length
    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=1024,      # model input cap (tokens); transcript longer than this must be truncated/chunked
        truncation=True
    )

    # Generate summary (tune these later)
    summary_ids = model.generate(
        **inputs,
        max_new_tokens=220,
        min_new_tokens=60,
        num_beams=4,
        length_penalty=1.2,
        early_stopping=True,
        no_repeat_ngram_size=3
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary.strip()

from flask import request, jsonify

@app.post("/summarize")
def summarize_route():
    try:
        data = request.get_json(force=True) or {}
        transcript = data.get("transcript", "")

        if not transcript:
            return jsonify(error="Missing 'transcript' in JSON body"), 400

        summary = summerize_transcript(transcript)
        return jsonify(summry=summary)
    
    except Exception as e:
        return jsonify(error=str(e)), 400
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)