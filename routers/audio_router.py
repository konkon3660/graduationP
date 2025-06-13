from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.audio_service import set_audio_streaming, get_audio_streaming

router = APIRouter()

clients = set()

@router.websocket("/ws/audio")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    print("[Audio] 클라이언트 연결됨")

    try:
        while True:
            data = await websocket.receive_bytes()

            if get_audio_streaming():
                for client in clients:
                    if client != websocket:
                        try:
                            await client.send_bytes(data)
                        except:
                            pass  # 송신 실패시 무시
    except WebSocketDisconnect:
        print("[Audio] 클라이언트 연결 종료")
    finally:
        clients.discard(websocket)
