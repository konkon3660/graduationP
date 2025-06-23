# routers/ws_router.py
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.command_service import handle_command_async
from services.ultrasonic_service import get_distance_data
from services.auto_play_service import auto_play_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔗 WebSocket 클라이언트 연결됨")
    
    # 자동 놀이 서비스에 클라이언트 등록
    auto_play_service.register_client(websocket)
    
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
                    if distance_data.get("distance") is not None:
                        # 성공 시: distance: 실제거리 형식
                        response_text = f"distance: {distance_data['distance']}"
                    else:
                        # 실패 시: error: 오류메시지 형식
                        error_msg = distance_data.get("error", "측정 실패")
                        response_text = f"error: {error_msg}"
                    
                    await websocket.send_text(response_text)
                    logger.info(f"📏 초음파 센서 데이터 전송: {response_text}")
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
                    if distance_data.get("distance") is not None:
                        # 성공 시: distance: 실제거리 형식
                        response_text = f"distance: {distance_data['distance']}"
                    else:
                        # 실패 시: error: 오류메시지 형식
                        error_msg = distance_data.get("error", "측정 실패")
                        response_text = f"error: {error_msg}"
                    
                    await websocket.send_text(response_text)
                    logger.info(f"📏 초음파 센서 데이터 전송: {response_text}")
                    continue
                
                # 문자열 명령 처리
                success = await handle_command_async(message)
                
                # 기존 호환성을 위해 그대로 응답
                await websocket.send_text(message)
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket 클라이언트 연결 해제됨")
    except Exception as e:
        logger.error(f"❌ WebSocket 오류: {e}")
    finally:
        # 자동 놀이 서비스에서 클라이언트 해제
        auto_play_service.unregister_client(websocket)
