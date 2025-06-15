from fastapi import FastAPI
from utils.alsa_suppress import suppress_alsa_errors
from routers.ws_router import router as ws_router
from routers.ws_audio_receive import router as audio_receive_router
from routers.mjpeg_router import router as mjpeg_router
from routers.ws_audio_send import router as audio_send_router
from services.microphone_sender_instance import mic_streamer  # ✅ 싱글톤 마이크 객체 import

app = FastAPI()

app.include_router(ws_router)
app.include_router(audio_receive_router)
app.include_router(audio_send_router)
app.include_router(mjpeg_router)

@app.on_event("startup")
async def startup_event():
    with suppress_alsa_errors():  # ✅ 마이크 생성 전 suppress
        mic_streamer.start()

@app.on_event("shutdown")
async def shutdown_event():
    mic_streamer.stop()
