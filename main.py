from fastapi import FastAPI
from utils.alsa_suppress import suppress_alsa_errors
from routers import ws_router, mjpeg_router, ws_audio_send, ws_audio_receive
from services.microphone_sender_instance import mic_streamer

app = FastAPI()

app.include_router(ws_router)
app.include_router(mjpeg_router)
app.include_router(ws_audio_send)
app.include_router(ws_audio_receive)

@app.on_event("startup")
async def startup_event():
    with suppress_alsa_errors():
        mic_streamer.start()

@app.on_event("shutdown")
async def shutdown_event():
    mic_streamer.stop()
