# routers/ws_audio_receive.py - 1:1 전용 간소화 버전
import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import pyaudio

router = APIRouter()

# 전역 오디오 스트림 상태
audio_stream = None
pyaudio_instance = None

@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket):
    global audio_stream, pyaudio_instance
    
    await websocket.accept()
    print("🎙️ 서버 마이크 → 클라이언트 스피커 연결됨")

    try:
        # 🔧 오디오 설정
        RATE = 16000
        CHUNK = 2048
        DEVICE_INDEX = 1

        # 🎤 PyAudio로 마이크 열기
        pyaudio_instance = pyaudio.PyAudio()
        audio_stream = pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            input_device_index=DEVICE_INDEX,
            frames_per_buffer=CHUNK
        )

        print("✅ 서버 마이크 스트림 열기 성공")

        # 🔁 클라이언트에게 실시간 전송 루프
        while True:
            # 비동기로 오디오 읽기
            data = await asyncio.get_event_loop().run_in_executor(
                None, lambda: audio_stream.read(CHUNK, exception_on_overflow=False)
            )
            await websocket.send_bytes(data)

    except WebSocketDisconnect:
        print("🔌 클라이언트 연결 종료됨")

    except Exception as e:
        print(f"❌ 오디오 수신 예외: {e}")

    finally:
        # 🛑 리소스 정리
        if audio_stream:
            try:
                audio_stream.stop_stream()
                audio_stream.close()
            except:
                pass
        if pyaudio_instance:
            try:
                pyaudio_instance.terminate()
            except:
                pass
        audio_stream = None
        pyaudio_instance = None
        print("🛑 마이크 스트림 종료됨")