import sys
import os
import asyncio
import numpy as np
import sounddevice as sd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from tensorflow import keras

sys.path.append("src")
from audio_utils import extract_melspectrogram

load_dotenv()
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # רק ה-React שלנו יכול לדבר עם השרת
    allow_methods=["*"],
    allow_headers=["*"],
)

CATEGORIES = ["scream", "crying", "explosion", "background"]
SR = 22050
DURATION = 2
STEP = 1
THRESHOLD = 0.50
MEAN, STD = -30.0, 15.0

model = keras.models.load_model("src/sos_model.keras")
buffer = np.zeros(int(DURATION * SR), dtype="float32")
is_listening = False


def verify_key(key: str = Depends(api_key_header)):
    """בודק שה-API Key נכון — אחרת דוחה את הבקשה"""
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return key


def process_chunk(audio: np.ndarray) -> dict:
    mel = extract_melspectrogram(audio, sr=SR)
    mel = (mel - MEAN) / (STD + 1e-8)
    mel = mel[np.newaxis, ..., np.newaxis]
    probs = model.predict(mel, verbose=0)[0]
    label = CATEGORIES[np.argmax(probs)]
    confidence = float(probs.max())
    return {
        "label": label,
        "confidence": round(confidence * 100, 1),
        "alert": label != "background" and confidence >= THRESHOLD,
        "probs": {cat: round(float(p) * 100, 1) for cat, p in zip(CATEGORIES, probs)},
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket — שולח תוצאות זיהוי בזמן אמת ל-React"""
    global buffer, is_listening

    # בדיקת API Key דרך query parameter ב-WebSocket
    key = websocket.query_params.get("api_key")
    if key != API_KEY:
        await websocket.close(code=1008)  # 1008 = Policy Violation
        return

    await websocket.accept()
    chunk_size = int(STEP * SR)
    try:
        while True:
            if not is_listening:
                await asyncio.sleep(0.1)
                continue
            loop = asyncio.get_event_loop()
            new_audio = await loop.run_in_executor(
                None,
                lambda: sd.rec(chunk_size, samplerate=SR, channels=1, dtype="float32", blocking=True).flatten()
            )
            buffer = np.roll(buffer, -chunk_size)
            buffer[-chunk_size:] = new_audio
            result = process_chunk(buffer.copy())
            await websocket.send_json(result)
    except WebSocketDisconnect:
        is_listening = False


@app.post("/start")
async def start(key: str = Depends(verify_key)):
    """מתחיל האזנה — דורש API Key תקין"""
    global is_listening
    is_listening = True
    return {"status": "listening"}


@app.post("/stop")
async def stop(key: str = Depends(verify_key)):
    """עוצר האזנה — דורש API Key תקין"""
    global is_listening
    is_listening = False
    return {"status": "stopped"}


@app.get("/status")
async def status(key: str = Depends(verify_key)):
    """מחזיר את מצב ההאזנה הנוכחי"""
    return {"is_listening": is_listening}
