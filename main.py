from fastapi import FastAPI
from utils.alsa_suppress import suppress_alsa_errors
from routers.ws_router import router as ws_router
from routers.ws_audio_receive import router as audio_receive_router
from routers.mjpeg_router import router as mjpeg_router
from routers.ws_audio_send import router as audio_send_router
from services.microphone_sender_instance import mic_streamer
from services.mic_sender_instance import mic_sender
import threading

# audio_output_loop만 늦게 import → 루프 안에서 큐 사용 시 loop 충돌 방지
def run_audio_output_loop_in_background():
    import asyncio
    try:
        from routers.ws_audio_send import audio_output_loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(audio_output_loop())
    except Exception as e:
        print(f"❌ [run_audio_output_loop_in_background] 예외 발생: {e}")

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
    try:
        print("🚀 서버 시작 중...")
        
        # ✅ 마이크 스트리밍은 필요할 때만 시작
        # mic_streamer.start() 제거
        
        # 오디오 출력 루프만 백그라운드에서 시작
        threading.Thread(
            target=run_audio_output_loop_in_background,
            daemon=True
        ).start()
        
        print("✅ 서버 시작 완료")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        mic_streamer.stop()
        print("🛑 마이크 송출 종료")
    except Exception as e:
        print(f"⚠️ [shutdown] 예외 발생: {e}")
