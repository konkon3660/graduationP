from fastapi import FastAPI
from utils.alsa_suppress import suppress_alsa_errors
from routers.ws_router import router as ws_router
from routers.ws_audio_receive import router as audio_receive_router
from routers.mjpeg_router import router as mjpeg_router
from routers.ws_audio_send import router as audio_send_router
from services.microphone_sender_instance import mic_streamer
from services.mic_sender_instance import mic_sender
import asyncio
from routers.ws_audio_send import audio_output_loop
import threading

app = FastAPI()
app.state.mic_sender = mic_sender
app.state.mic_streamer = mic_streamer
app.include_router(ws_router)
app.include_router(audio_receive_router)
app.include_router(audio_send_router)
app.include_router(mjpeg_router)


def run_audio_output_loop_in_background():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(audio_output_loop())

@app.on_event("startup")
async def startup_event():
    try:
        with suppress_alsa_errors():
            mic_streamer.start()
        threading.Thread(target=run_audio_output_loop_in_background, daemon=True).start()
        print("✅ startup 이벤트 완료됨")
    except Exception as e:
        print(f"❌ startup_event 중 예외 발생: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    mic_streamer.stop()
