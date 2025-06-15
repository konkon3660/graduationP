from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws")
async def control_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎮 제어 WebSocket 연결됨")

    try:
        while True:
            message = await websocket.receive_text()
            print(f"[제어 명령 수신] {message}")
            await websocket.send_text(f"명령 수신: {message}")
    except Exception as e:
        print(f"제어 연결 종료: {e}")
