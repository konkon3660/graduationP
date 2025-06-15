# ✅ audio_receive: 서버 → 클라이언트로 음성 전송 (서버 마이크)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import asyncio

router = APIRouter()

@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket, request: Request):
    await websocket.accept()
    print("🔈 클라이언트 스피커 연결됨 (/ws/audio_receive)")

    mic_streamer = request.app.state.mic_streamer
    mic_streamer.register(websocket)  # 🎯 PCM 데이터 수신 대상 등록

    try:
        while True:
            await asyncio.sleep(1)  # 전송은 백그라운드에서 자동 발생
    except WebSocketDisconnect:
        print("🔌 클라이언트 스피커 연결 종료")
    finally:
        mic_streamer.unregister(websocket)  # 🎯 연결 해제
