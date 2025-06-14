from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from datetime import datetime
import asyncio
from services.audio_service import get_audio_streaming, set_audio_streaming
from services.audio_output_service import play_audio_chunk, init_audio_stream
from services.mic_sender_instance import mic_sender  # ✅ 안전한 방식

router = APIRouter()
clients = set()

@router.websocket("/ws")
async def control_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎮 제어 WebSocket 연결됨")

    try:
        while True:
            message = await websocket.receive_text()
            print(f"[제어 명령 수신] {message}")

            if message == "audio_receive_on":
                set_audio_streaming(True)
                # mic_sender.start()  # 🟢 마이크 송출 시작
                await websocket.send_text("ack: 음성 수신 시작됨")

            elif message == "audio_receive_off":
                set_audio_streaming(False)
                # mic_sender.stop()   # 🔴 마이크 송출 중지
                await websocket.send_text("ack: 음성 수신 종료됨")

            else:
                await websocket.send_text(f"명령 수신: {message}")
    except Exception as e:
        print(f"제어 연결 종료: {e}")


@router.websocket("/ws/audio")
async def audio_ws(websocket: WebSocket):
    await websocket.accept()
    mic_sender.register(websocket)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_audio_{now}.pcm"
    async def receive_client_audio():
        try:
            with open(filename, "wb") as f:
                while True:
                    chunk = await websocket.receive_bytes()

                    if get_audio_streaming():
                        f.write(chunk)
                        init_audio_stream()
                        play_audio_chunk(chunk)
                        await mic_sender.broadcast(chunk)
        except WebSocketDisconnect:
            print("🎤 오디오 클라이언트 연결 종료")
        finally:
            mic_sender.unregister(websocket)

    async def send_server_mic_audio():
        while True:
            await asyncio.sleep(1)  # 나중에 확장용

    await asyncio.gather(
        receive_client_audio(),
        send_server_mic_audio()
    )
