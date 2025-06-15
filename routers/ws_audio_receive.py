from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import asyncio

router = APIRouter()

@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket, request: Request):  # ✅ request 명시
    await websocket.accept()
    print("🔈 클라이언트 스피커 연결됨 (/ws/audio_receive)")

    mic_streamer = request.app.state.mic_streamer  # 🎯 앱 상태에서 접근

    mic_streamer.register(websocket)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("🔌 클라이언트 스피커 연결 종료")
    finally:
        mic_streamer.unregister(websocket)
