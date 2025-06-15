# routers/ws_router.py
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.command_service import handle_command_async
from services.audio_receive_status import audio_receive_status

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔗 WebSocket 클라이언트 연결됨")
    try:
        while True:
            # 클라이언트에서 받은 명령 (plain text)
            command = await websocket.receive_text()
            # 명령 처리 (실제 동작)
            if command == "audio_receive_on":
                audio_receive_status.on = True
            elif command == "audio_receive_off":
                audio_receive_status.on = False
            await handle_command_async(command)
            # 그대로 응답 (클라에서 그대로 화면에 뿌림)
            await websocket.send_text(command)
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket 클라이언트 연결 해제됨")
    except Exception as e:
        logger.error(f"❌ WebSocket 오류: {e}")
