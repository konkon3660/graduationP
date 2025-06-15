# main.py - 간소화된 버전
from fastapi import FastAPI
from routers.ws_router import router as ws_router
from routers.ws_audio_receive import router as audio_receive_router
from routers.mjpeg_router import router as mjpeg_router  
from routers.ws_audio_send import router as audio_send_router
from services.microphone_sender_instance import mic_streamer
from services.mic_sender_instance import mic_sender

app = FastAPI()

# 공유 인스턴스 등록
app.state.mic_sender = mic_sender
app.state.mic_streamer = mic_streamer

# 라우터 등록
app.include_router(ws_router)
app.include_router(audio_receive_router)
app.include_router(audio_send_router)
app.include_router(mjpeg_router)

@app.on_event("startup")
async def startup_event():
    print("🚀 서버 시작 완료 (1:1 음성통신 모드)")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        # 간단한 정리
        mic_streamer.stop()
        print("🛑 서버 종료 완료")
    except Exception as e:
        print(f"⚠️ 종료 중 예외: {e}")