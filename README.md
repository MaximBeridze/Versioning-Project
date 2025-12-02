# YouTube Transcript Summarizer

This project provides a Chrome Extension that extracts the transcript of a YouTube video and sends it to a backend REST API built with Flask. The backend processes the text using NLP techniques and returns a summarized version of the transcript.

## Features

* Chrome Extension interface

* Flask-based REST API

* NLP-powered transcript summarization

* Works directly on YouTube video pages

## Collaborators

- Maxim Beridze
- Costi-Iulian Asanache 
- Jaimie Mathangi 
- Adithya Reddy Manda 
- Muhammad Saad Javed 
- Krishan Baragama Acharige 

## Languages
Frontend:

- HTML

- CSS

- JavaScript

Backend:

- Python

- Flask


## How It Works
    1. The user opens a YouTube video.
    2. The Chrome Extension extracts the video ID and retrieves the transcript.
    3. The transcript is sent to the Flask backend via a REST API request.
    4. The backend runs NLP summarization.
    5. The summarized output is returned and displayed in the extension popup.


## File Structure (Temporary)
```
youtube-transcript-summarizer/
│
├── chrome-extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── styles.css
│   └── icons/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── summarizer.py
│   └── utils/
│
└── README.md
```