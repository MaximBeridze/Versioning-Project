from flask import Flask, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

app = Flask(__name__)
app.json.ensure_ascii = False  # keep Unicode symbols like ♪

def get_transcript(video_id: str) -> str:
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id)

    formatter = TextFormatter()
    transcript_text = formatter.format_transcript(fetched)

    # Keep transcript as-is (symbols, cues, etc.)
    return transcript_text.strip()

@app.get("/transcript/<video_id>")
def transcript(video_id):
    try:
        text = get_transcript(video_id)
        return jsonify(transcript=text)
    except Exception as e:
        return jsonify(error=str(e)), 400
