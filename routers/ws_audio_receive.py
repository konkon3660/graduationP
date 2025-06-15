# routers/ws_audio_receive.py
from services.audio_receive_status import audio_receive_status

@router.websocket("/ws/audio_receive")
async def websocket_audio_receive(websocket: WebSocket):
    await websocket.accept()
    audio_receive_status.ws_clients.add(websocket)
    print("🎤 [AUDIO_RECEIVE] 연결됨, 기본값: 송출 OFF")
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        while True:
            if audio_receive_status.on:
                data = stream.read(1024)
                await websocket.send_bytes(data)
            else:
                await asyncio.sleep(0.1)  # OFF 상태에서는 잠시 대기
    except WebSocketDisconnect:
        print("🔌 [AUDIO_RECEIVE] 클라이언트 연결 해제")
    finally:
        audio_receive_status.ws_clients.discard(websocket)
        stream.stop_stream()
        stream.close()
        audio.terminate()
