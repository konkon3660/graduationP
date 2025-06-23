import asyncio
import pyaudio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/audio_receive")
async def websocket_audio_receive(websocket: WebSocket):
    await websocket.accept()
    print("🎤 [AUDIO_RECEIVE] 서버 마이크 → 클라이언트 송출 시작")

    # 마이크 열기
    audio = pyaudio.PyAudio()
    try:
        # ⚠️ 입력장치 번호는 실제 환경에 따라 조정(1, 2 등)
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            input=True,
                            frames_per_buffer=1024)
        while True:
            data = stream.read(1024)
            await websocket.send_bytes(data)
            await asyncio.sleep(0)  # 딜레이 최소화

    except WebSocketDisconnect:
        print("🔌 [AUDIO_RECEIVE] 클라이언트 연결 종료")
    except Exception as e:
        print(f"❌ [AUDIO_RECEIVE] 에러: {e}")
    finally:
        try:
            if 'stream' in locals() and stream is not None:
                stream.stop_stream()
                stream.close()
            if 'audio' in locals() and audio is not None:
                audio.terminate()
        except Exception:
            pass
