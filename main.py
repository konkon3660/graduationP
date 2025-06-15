# main.py - 디버깅용 로그 추가
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

# ✅ 라우터 등록 순서 및 로그 추가
print("🔌 WebSocket 라우터 등록 중...")
app.include_router(ws_router)
print("✅ ws_router 등록 완료")

app.include_router(audio_receive_router)
print("✅ audio_receive_router 등록 완료")

app.include_router(audio_send_router)
print("✅ audio_send_router 등록 완료")

app.include_router(mjpeg_router)
print("✅ mjpeg_router 등록 완료")

@app.on_event("startup")
async def startup_event():
    print("🚀 서버 시작 완료 (1:1 음성통신 모드)")
    print("🔗 사용 가능한 엔드포인트:")
    print("   - /ws (제어 명령)")
    print("   - /ws/audio_receive (서버→클라이언트 음성)")
    print("   - /ws/audio_send (클라이언트→서버 음성)")
    print("   - /mjpeg (카메라)")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        mic_streamer.stop()
        print("🛑 서버 종료 완료")
    except Exception as e:
        print(f"⚠️ 종료 중 예외: {e}")

# ✅ 디버깅용 루트 엔드포인트 추가
@app.get("/")
async def root():
    return {
        "message": "라즈베리파이 제어 서버 실행 중",
        "endpoints": {
            "control": "/ws",
            "audio_receive": "/ws/audio_receive", 
            "audio_send": "/ws/audio_send",
            "camera": "/mjpeg"
        }
    }

# ✅ WebSocket 연결 상태 확인용
@app.get("/status")
async def status():
    return {
        "server": "running",
        "websockets": ["ws", "ws/audio_receive", "ws/audio_send"],
        "camera": "mjpeg"
    }

