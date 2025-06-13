from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
from services.audio_service import get_audio_streaming, set_audio_streaming
from services.audio_output_service import play_audio_chunk

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
                await websocket.send_text("ack: 음성 수신 시작됨")

            elif message == "audio_receive_off":
                set_audio_streaming(False)
                await websocket.send_text("ack: 음성 수신 종료됨")

            else:
                await websocket.send_text(f"명령 수신: {message}")

    except Exception as e:
        print(f"제어 연결 종료: {e}")


@router.websocket("/ws/audio")
async def audio_ws(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    print("🎤 오디오 WebSocket 연결됨")

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_audio_{now}.pcm"

    try:
        with open(filename, "wb") as f:
            while True:
                chunk = await websocket.receive_bytes()

                if get_audio_streaming():
                    f.write(chunk)
                    play_audio_chunk(chunk)  # 🔊 이 부분 추가됨

                    # 다른 클라이언트에게 중계 (옵션)
                    for client in clients:
                        if client != websocket:
                            try:
                                await client.send_bytes(chunk)
                            except:
                                pass
    except WebSocketDisconnect:
        print("🎤 오디오 클라이언트 연결 종료")
    except Exception as e:
        print(f"오디오 연결 종료: {e}")
    finally:
        clients.discard(websocket)
