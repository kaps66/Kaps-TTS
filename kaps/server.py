"""FastAPI server with REST + WebSocket streaming endpoints."""
import asyncio
import json
import uvicorn
from fastapi import FastAPI, WebSocket, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from kaps.model import KapsTTS
from kaps.phonemizer import phonemize

app = FastAPI(title="Kaps-TTS API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

MODEL: KapsTTS = None


@app.on_event("startup")
async def load_model():
    global MODEL
    MODEL = KapsTTS.from_pretrained("./weights", fp8=True)


@app.post("/v1/tts/design")
async def voice_design(payload: dict):
    """Non-streaming voice design endpoint for simple requests."""
    phonemes = phonemize(payload["text"], payload.get("language", "en"))
    # In production: encode description → style vector → generate full audio
    return {"status": "ok", "phonemes": phonemes}


@app.websocket("/v1/tts/stream")
async def tts_stream(ws: WebSocket):
    await ws.accept()
    kv_cache = None
    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)

            if data["action"] == "synthesize":
                phonemes = phonemize(data["text"], data.get("language", "en"))
                # Stream chunks back as binary Opus/PCM
                audio_chunk, kv_cache = MODEL.synthesize_chunk(
                    phonemes, style_vector=None, kv_cache=kv_cache
                )
                await ws.send_bytes(audio_chunk.numpy().tobytes())

            elif data["action"] == "flush":
                await ws.send_bytes(b"")  # EOS marker
                break
    except Exception as e:
        await ws.close(code=1011, reason=str(e))


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
