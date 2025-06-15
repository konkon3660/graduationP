# routers/ws_audio_receive.py
import asyncio
import pyaudio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.audio_receive_status import audio_receive_status

router = APIRouter()

@router.websocket("/ws/audio_receive")
async def websocket_audio_receive(websocket: WebSocket):
    await websocket.accept()
    audio_receive_status.ws_clients.add(websocket)
    print("🎤 [AUDIO_RECEIVE] 연결됨, 기본값: 송출 OFF")
    try:
        audio = pyaudio.PyAudio()   
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        while True:
            if audio_receive_status.on:
                data = stream.read(512)  # 필요하다면 512로 줄여서 테스트
                await websocket.send_bytes(data)
            else:
                await asyncio.sleep(0.05)  # 10~50ms, OFF상태만
    except WebSocketDisconnect:
        print("🔌 [AUDIO_RECEIVE] 클라이언트 연결 해제")
    finally:
        audio_receive_status.ws_clients.discard(websocket)
        stream.stop_stream()
        stream.close()
        audio.terminate()
