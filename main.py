import asyncio
from services.microphone_sender_service import MicrophoneSender
from fastapi import FastAPI
from routers import ws_router, mjpeg_router, audio_router

app = FastAPI()
app.include_router(ws_router.router)
app.include_router(mjpeg_router.router)
app.include_router(audio_router.router)

@app.on_event("startup")
async def start_background_tasks():
    ws_url = "ws://localhost:8000/ws/audio"  # 필요시 실제 주소로 수정
    asyncio.create_task(send_microphone_audio(ws_url))
    

mic_sender = MicrophoneSender("ws://localhost:8000/ws/audio")