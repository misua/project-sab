from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import whisper
import json
import logging

app = FastAPI()

# Set verbose logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn.error")

# Allow CORS for local web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "audio_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAPPINGS_FILE = "mappings.json"

def load_mappings():
    if not os.path.exists(MAPPINGS_FILE):
        return {}
    with open(MAPPINGS_FILE, "r") as f:
        return json.load(f)

def save_mappings(mappings):
    with open(MAPPINGS_FILE, "w") as f:
        json.dump(mappings, f, indent=2)

custom_dict = load_mappings()

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...), child_id: str = Form(None)):
    """
    Receives an audio file from the web client and saves it locally.
    Transcribes the audio using OpenAI Whisper.
    Applies custom mapping if available.
    """
    logger.info(f"Received audio upload: filename={file.filename}, child_id={child_id}")
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    logger.info(f"Saved audio file to {file_location}")
    model = whisper.load_model("base")
    result = model.transcribe(file_location)
    transcript = result.get("text", "").strip().lower()
    logger.info(f"Transcript: {transcript}")
    mapped = custom_dict.get(transcript, transcript)
    logger.info(f"Mapped meaning: {mapped}")
    return JSONResponse({"status": "ok", "result": {"transcript": transcript, "meaning": mapped}})

@app.post("/feedback/")
async def feedback(child_id: str = Form(...), transcript: str = Form(...), correction: str = Form(None)):
    """
    Receives feedback/correction from parent and updates mappings/model (placeholder).
    """
    # Placeholder: Save correction and update model/mapping
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "AI Speech App FastAPI backend running."}

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/index.html")
def index_html():
    return FileResponse("static/index.html")

@app.get("/mappings.html")
def mappings_html():
    return FileResponse("static/mappings.html")

@app.get("/record.html")
def get_record_page():
    return FileResponse("static/record.html")

@app.get("/mappings/")
def get_mappings():
    return custom_dict

@app.post("/mappings/")
async def add_mapping(request: Request):
    data = await request.json()
    child_word = data.get("child_word", "").strip().lower()
    meaning = data.get("meaning", "").strip().lower()
    if not child_word or not meaning:
        return JSONResponse({"error": "Invalid input"}, status_code=400)
    custom_dict[child_word] = meaning
    save_mappings(custom_dict)
    return {"status": "ok"}

@app.delete("/mappings/")
async def delete_mapping(request: Request):
    data = await request.json()
    child_word = data.get("child_word", "").strip().lower()
    if child_word in custom_dict:
        del custom_dict[child_word]
        save_mappings(custom_dict)
        return {"status": "ok"}
    return JSONResponse({"error": "Not found"}, status_code=404)

@app.post("/upload-recording/")
async def upload_recording(file: UploadFile = File(...), child: str = Form(...)):
    """
    Receives an audio file and a child selection (sab/chaz), saves under respective folder.
    """
    folder = os.path.join("audio_uploads", child)
    os.makedirs(folder, exist_ok=True)
    filename = file.filename
    # Avoid overwriting: add a timestamp
    import time
    ts = int(time.time() * 1000)
    filename = f"{ts}_{filename}"
    file_location = os.path.join(folder, filename)
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"status": "ok", "filename": filename}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
