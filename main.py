# main.py - 업데이트된 메인 서버 (리팩토링된 명령 서비스 적용)
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

# ✅ 라우터 등록
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
    print("🚀 서버 시작 완료 (하드웨어 제어 모드)")
    print("🔗 사용 가능한 엔드포인트:")
    print("   - /ws (제어 명령)")
    print("   - /ws/audio_receive (서버→클라이언트 음성)")
    print("   - /ws/audio_send (클라이언트→서버 음성)")
    print("   - /mjpeg (카메라)")
    print("   - /system/status (시스템 상태)")
    print("   - /system/commands (사용 가능한 명령)")
    print("   - /system/test/{command} (개별 명령 테스트)")
    
    # 하드웨어 초기화
    try:
        from services.command_service import command_handler
        command_handler.initialize()
        print("🔧 하드웨어 초기화 완료")
    except Exception as e:
        print(f"⚠️ 하드웨어 초기화 실패: {e}")
    
    # # 급식 자동화 시작
    # try:
    #     import asyncio
    #     from services