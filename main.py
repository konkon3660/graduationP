# main.py - 업데이트된 메인 서버 (리팩토링된 명령 서비스 적용)
from fastapi import FastAPI
from routers.ws_router import router as ws_router
from routers.ws_audio_receive import router as audio_receive_router
from routers.mjpeg_router import router as mjpeg_router  
from routers.ws_audio_send import router as audio_send_router
from routers.ws_settings_router import router as settings_router
from services.microphone_sender_instance import mic_streamer
from services.mic_sender_instance import mic_sender

app = FastAPI()

# 공유 인스턴스 등록
app.state.mic_sender = mic_sender
app.state.mic_streamer = mic_streamer

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
# 정적 디렉터리 mount
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    return HTMLResponse(content=open("test_json_commands.html", "r", encoding="utf-8").read())


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

app.include_router(settings_router)
print("✅ settings_router 등록 완료")

@app.on_event("startup")
async def startup_event():
    print("🚀 서버 시작 완료 (하드웨어 제어 모드)")
    print("🔗 사용 가능한 엔드포인트:")
    print("   - /ws (제어 명령)")
    print("   - /ws/audio_receive (서버→클라이언트 음성)")
    print("   - /ws/audio_send (클라이언트→서버 음성)")
    print("   - /ws/settings (급식 설정)")
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
    
    # 급식 스케줄러 시작
    try:
        from services.feed_scheduler import feed_scheduler
        await feed_scheduler.start()
        print("🍽 급식 스케줄러 시작됨")
    except Exception as e:
        print(f"⚠️ 급식 스케줄러 시작 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 서버 종료 중...")
    
    # 급식 스케줄러 중지
    try:
        from services.feed_scheduler import feed_scheduler
        await feed_scheduler.stop()
        print("⏹ 급식 스케줄러 중지됨")
    except Exception as e:
        print(f"⚠️ 급식 스케줄러 중지 실패: {e}")
    
    # GPIO 정리
    try:
        from services.feed_service import cleanup
        cleanup()
        print("🧹 GPIO 정리 완료")
    except Exception as e:
        print(f"⚠️ GPIO 정리 실패: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)