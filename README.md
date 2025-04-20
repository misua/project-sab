# AI Speech App (Edge-Processed)

## Overview
This project is a privacy-focused, AI-powered speech recognition and intent app for children (especially those with unique speech patterns). The phone/tablet/PC acts as a microphone interface, while all AI runs locally on your computer (no cloud dependency).

## How it Works
- The web client records audio and uploads it to your computer (server).
- The FastAPI backend receives audio, processes it with TensorFlow/PyTorch, and returns a transcript.
- Parents can correct or map words; the server adapts and learns.

## How to Run
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
3. Open `static/index.html` in your browser (on your phone or PC).
   - Make sure your phone/PC is on the same network as the server.
   - Change the fetch URL in `index.html` if the server is not `localhost`.

## Next Steps
- Integrate TensorFlow/PyTorch speech-to-text.
- Add custom word mapping, intent recognition, and feedback/correction loop.
- Optimize for privacy and speed.

---

For more, see the To-Do List in this repo.
