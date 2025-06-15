import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import pyaudio

router = APIRouter()

@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎙️ 서버 마이크 → 클라이언트 스피커 연결됨 (/ws/audio_receive)")

    try:
        # 🔧 오디오 설정
        RATE = 16000
        CHUNK = 2048
        DEVICE_INDEX = 1  # ✅ "pulse" 장치 사용

        # 🎤 PyAudio로 마이크 열기
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=RATE,
                        input=True,
                        input_device_index=DEVICE_INDEX,
                        frames_per_buffer=CHUNK)

        print("✅ 서버 마이크 스트림 열기 성공")

        # 🔁 클라이언트에게 실시간 전송 루프
        while True:
            data = stream.read(CHUNK)
            await websocket.send_bytes(data)

    except WebSocketDisconnect:
        print("🔌 클라이언트 스피커 연결 종료됨")

    except Exception as e:
        print(f"❌ 예외 발생: {e}")

    finally:
        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except:
            pass
        print("🛑 마이크 스트림 종료됨")
