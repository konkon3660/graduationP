# main.py - 시스템 상태 엔드포인트 추가
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
    print("   - /system/status (시스템 상태)")
    print("   - /system/commands (사용 가능한 명령)")
    
    # 급식 자동화 시작
    try:
        import asyncio
        from services.feed_service import auto_feed_loop
        asyncio.create_task(auto_feed_loop())
        print("🍚 급식 자동화 시작됨")
    except Exception as e:
        print(f"⚠️ 급식 자동화 시작 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        mic_streamer.stop()
        # 하드웨어 정리
        from services.command_service import command_handler
        command_handler.reset()
        print("🛑 서버 종료 완료")
    except Exception as e:
        print(f"⚠️ 종료 중 예외: {e}")

# ✅ 기본 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "라즈베리파이 제어 서버 실행 중",
        "version": "2.0.0",
        "endpoints": {
            "control": "/ws",
            "audio_receive": "/ws/audio_receive", 
            "audio_send": "/ws/audio_send",
            "camera": "/mjpeg",
            "system_status": "/system/status",
            "available_commands": "/system/commands"
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

# 🆕 시스템 상태 엔드포인트
@app.get("/system/status")
async def system_status():
    """하드웨어 시스템 상태 조회"""
    try:
        from services.command_service import get_system_status
        return get_system_status()
    except Exception as e:
        return {"error": f"시스템 상태 조회 실패: {e}"}

# 🆕 사용 가능한 명령 목록
@app.get("/system/commands")
async def available_commands():
    """사용 가능한 명령 목록 조회"""
    try:
        from services.command_service import get_available_commands
        return {
            "commands": get_available_commands(),
            "usage": {
                "basic": "WebSocket으로 명령 전송: 'laser_on', 'forward' 등",
                "positioning": "레이저 포지셔닝: 'laser_xy:90,120'",
                "motor_speed": "향후 지원 예정: 'forward:50' (속도 지정)"
            }
        }
    except Exception as e:
        return {"error": f"명령 목록 조회 실패: {e}"}

# 🆕 하드웨어 테스트 엔드포인트 (디버깅용)
@app.post("/system/test/{command}")
async def test_command(command: str):
    """개별 명령 테스트 (HTTP POST)"""
    try:
        from services.command_service import handle_command_async
        success = await handle_command_async(command)
        return {
            "command": command,
            "success": success,
            "message": f"명령 '{command}' {'성공' if success else '실패'}"
        }
    except Exception as e:
        return {
            "command": command,
            "success": False,
            "error": str(e)
        }