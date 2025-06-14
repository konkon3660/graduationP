import asyncio
from fastapi import FastAPI
from routers import ws_router, mjpeg_router, audio_router
from services.mic_sender_instance import mic_sender

app = FastAPI()
app.state.mic_sender = mic_sender
app.include_router(ws_router.router)
app.include_router(mjpeg_router.router)
app.include_router(audio_router.router)
