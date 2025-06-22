# routers/ws_router.py
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.command_service import handle_command_async
from services.ultrasonic_service import get_distance_data

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔗 WebSocket 클라이언트 연결됨")
    try:
        while True:
            # 클라이언트에서 받은 메시지
            message = await websocket.receive_text()
            
            try:
                # JSON 형식인지 확인
                command_data = json.loads(message)
                logger.info(f"📨 JSON 명령 수신: {command_data}")
                
                # 초음파 센서 데이터 요청인지 확인
                if command_data.get("type") == "ultrasonic" and command_data.get("action") == "get_distance_data":
                    # 거리 데이터 측정 및 전송
                    distance_data = get_distance_data()
                    await websocket.send_text(json.dumps(distance_data, ensure_ascii=False))
                    logger.info(f"📏 초음파 센서 데이터 전송: {distance_data}")
                    continue
                
                # JSON 명령 처리
                success = await handle_command_async(command_data)
                
                # 응답 전송
                response = {
                    "success": success,
                    "command": command_data,
                    "message": "명령 처리 완료" if success else "명령 처리 실패"
                }
                await websocket.send_text(json.dumps(response, ensure_ascii=False))
                
            except json.JSONDecodeError:
                # JSON이 아닌 경우 문자열 명령으로 처리
                logger.info(f"📨 문자열 명령 수신: {message}")
                
                # 초음파 센서 거리 측정 명령인지 확인
                if message == "get_distance":
                    distance_data = get_distance_data()
                    await websocket.send_text(json.dumps(distance_data, ensure_ascii=False))
                    logger.info(f"📏 초음파 센서 데이터 전송: {distance_data}")
                    continue
                
                # 문자열 명령 처리
                success = await handle_command_async(message)
                
                # 기존 호환성을 위해 그대로 응답
                await websocket.send_text(message)
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket 클라이언트 연결 해제됨")
    except Exception as e:
        logger.error(f"❌ WebSocket 오류: {e}")
