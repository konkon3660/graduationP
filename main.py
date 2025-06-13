import asyncio
from fastapi import FastAPI
from routers import ws_router, mjpeg_router, audio_router
from services.mike_service import MicSender  # 분리된 모듈에서 import


mic_sender = MicSender()
app.state.mic_sender = mic_sender  # app에 공유 객체로 저장
app = FastAPI()
app.include_router(ws_router.router)
app.include_router(mjpeg_router.router)
app.include_router(audio_router.router)