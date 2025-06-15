import asyncio
from fastapi import FastAPI
from routers import ws_router, mjpeg_router, ws_audio_receive, ws_audio_send
from services.mic_sender_instance import mic_sender
from services.microphone_sender_instance import mic_streamer

app = FastAPI()
app.state.mic_sender = mic_sender
app.state.mic_streamer = mic_streamer
app.include_router(ws_router.router)
app.include_router(mjpeg_router.router)
app.include_router(ws_audio_send.router)
app.include_router(ws_audio_receive.router)