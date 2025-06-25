# main.py - 업데이트된 메인 서버 (리팩토링된 명령 서비스 적용)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.ws_router import router as ws_router
from routers.ws_audio_receive import router as audio_receive_router
from routers.mjpeg_router import router as mjpeg_router  
from routers.ws_audio_send import router as audio_send_router
from routers.ws_settings_router import router as settings_router
from services.microphone_sender_instance import mic_streamer
from services.mic_sender_instance import mic_sender
from services.auto_play_service import auto_play_service
from services.audio_playback_service import audio_playback_service

app = FastAPI()

# CORS 설정 (WebSocket 포함)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영시에는 도메인 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 공유 인스턴스 등록
app.state.mic_sender = mic_sender
app.state.mic_streamer = mic_streamer
app.state.auto_play_service = auto_play_service
app.state.audio_playback_service = audio_playback_service

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
# 정적 디렉터리 mount
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    return HTMLResponse(content=open("index.html", "r", encoding="utf-8").read())

# 헬스체크 엔드포인트 추가
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "서버가 정상 동작 중입니다"}

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
    
    # 자동 놀이 서비스 상태 출력
    auto_play_status = auto_play_service.get_status()
    print(f"🎮 자동 놀이 서비스 초기화됨:")
    print(f"   - 대기시간: {auto_play_status['auto_play_delay']}초")
    print(f"   - 연결된 클라이언트: {auto_play_status['connected_clients']}명")
    print(f"   - 자동 놀이 상태: {'실행 중' if auto_play_status['is_auto_playing'] else '대기 중'}")
    print(f"   - 태스크 상태: {auto_play_status['task_status']}")
    print(f"   - 모터 속도: {auto_play_status['motor_speed']}")
    
    # 오디오 재생 서비스 상태 출력
    audio_status = audio_playback_service.get_status()
    print(f"🎵 오디오 재생 서비스 초기화됨 (볼륨: {audio_status['volume']})")

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
    
    # 자동 놀이 서비스 정리
    try:
        auto_play_service.stop_auto_play()
        print("⏹ 자동 놀이 서비스 중지됨")
    except Exception as e:
        print(f"⚠️ 자동 놀이 서비스 중지 실패: {e}")
    
    # 오디오 재생 서비스 정리
    try:
        audio_playback_service.cleanup()
        print("⏹ 오디오 재생 서비스 정리됨")
    except Exception as e:
        print(f"⚠️ 오디오 재생 서비스 정리 실패: {e}")
    
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