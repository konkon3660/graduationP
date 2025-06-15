# ws_router.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws")
async def control_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎮 제어 WebSocket 연결됨")

    try:
        while True:
            command = await websocket.receive_text()
            print(f"[제어 명령 수신] {command}")

            from services.command_service import handle_command
            response = await handle_command(command)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("🔌 제어 WebSocket 연결 종료")
