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

        with suppress_alsa_errors():
            try:
                mic_streamer.start()
                print("🎤 서버 마이크 송출 시작")
            except Exception as e:
                print(f"❌ [mic_streamer.start()] 예외 발생: {e}")

        try:
            threading.Thread(
                target=run_audio_output_loop_in_background,
                daemon=True
            ).start()
            print("🔊 오디오 출력 루프 시작됨 (스레드)")
        except Exception as e:
            print(f"❌ [스레드 시작] 예외 발생: {e}")

        print("✅ startup 이벤트 완료됨")
    except Exception as e:
        print(f"❌ [startup_event 전체] 예외 발생: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        mic_streamer.stop()
        print("🛑 마이크 송출 종료")
    except Exception as e:
        print(f"⚠️ [shutdown] 예외 발생: {e}")
