from fastapi import FastAPI
from utils.alsa_suppress import suppress_alsa_errors
from routers.ws_router import router as ws_router
from routers.ws_audio_receive import router as audio_receive_router
from routers.mjpeg_router import router as mjpeg_router
from routers.ws_audio_send import router as audio_send_router
from services.microphone_sender_instance import mic_streamer
from services.mic_sender_instance import mic_sender
import asyncio
from routers.ws_audio_send import audio_output_loop

app = FastAPI()
app.state.mic_sender = mic_sender
app.state.mic_streamer = mic_streamer
app.include_router(ws_router)
app.include_router(audio_receive_router)
app.include_router(audio_send_router)
app.include_router(mjpeg_router)

@app.on_event("startup")
async def startup_event():
    with suppress_alsa_errors():  # ✅ 마이크 생성 전 suppress
        mic_streamer.start()
    asyncio.create_task(audio_output_loop())  # 🔄 병렬 실행

@app.on_event("shutdown")
async def shutdown_event():
    mic_streamer.stop()
