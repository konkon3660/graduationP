# routers/ws_router.py
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from services.command_service import handle_command_async

logger = logging.getLogger(__name__)

router = APIRouter()

# 중복 로그 방지를 위한 마지막 명령 추적
last_command = {"type": None, "timestamp": 0}
COMMAND_LOG_INTERVAL = 1.0  # 1초 간격으로만 같은 명령 로그 출력

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔗 WebSocket 클라이언트 연결됨")
    
    try:
        while True:
            # 메시지 수신
            data = await websocket.receive_text()
            
            # JSON 파싱 시도
            try:
                message = json.loads(data)
                command_type = message.get('type', '').lower()
                
                # 조이스틱 명령 처리
                if command_type == 'joystick':
                    direction = message.get('direction', '').lower()
                    await _handle_joystick_command(websocket, direction)
                
                # 레이저 명령 처리  
                elif command_type in ['laser_on', 'laser_off']:
                    await _handle_laser_command(websocket, command_type)
                
                # 기타 명령 처리
                elif command_type:
                    await _handle_general_command(websocket, command_type, message)
                
                else:
                    logger.warning(f"❓ 알 수 없는 명령 타입: {command_type}")
                    
            except json.JSONDecodeError:
                # 일반 텍스트 명령 처리
                await _handle_text_command(websocket, data.strip())
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket 클라이언트 연결 해제됨")
    except Exception as e:
        logger.error(f"❌ WebSocket 오류: {e}")

async def _handle_joystick_command(websocket: WebSocket, direction: str):
    """조이스틱 명령 처리 (중복 로그 방지)"""
    import time
    current_time = time.time()
    
    # 중복 로그 방지
    if (last_command["type"] == f"joystick_{direction}" and 
        current_time - last_command["timestamp"] < COMMAND_LOG_INTERVAL):
        return
    
    last_command["type"] = f"joystick_{direction}"
    last_command["timestamp"] = current_time
    
    try:
        # 명령 처리
        result = await handle_command_async(f"joystick_{direction}")
        
        # 통일된 응답 형식
        response_message = f"🕹️ 조이스틱 {_get_direction_korean(direction)} 이동 완료"
        logger.info(response_message)
        
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "command": f"joystick_{direction}",
            "status": "success",
            "message": response_message
        }))
        
    except Exception as e:
        error_message = f"❌ 조이스틱 {direction} 명령 처리 실패: {e}"
        logger.error(error_message)
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "command": f"joystick_{direction}",
            "status": "error", 
            "message": error_message
        }))

async def _handle_laser_command(websocket: WebSocket, command_type: str):
    """레이저 명령 처리"""
    try:
        result = await handle_command_async(command_type)
        
        # 통일된 응답 형식
        if command_type == "laser_on":
            response_message = "🔴 레이저가 켜졌습니다"
        else:
            response_message = "⚫ 레이저가 꺼졌습니다"
            
        logger.info(response_message)
        
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "command": command_type,
            "status": "success",
            "message": response_message
        }))
        
    except Exception as e:
        error_message = f"❌ {command_type} 명령 처리 실패: {e}"
        logger.error(error_message)
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "command": command_type,
            "status": "error",
            "message": error_message
        }))

async def _handle_general_command(websocket: WebSocket, command_type: str, message: dict):
    """일반 명령 처리"""
    try:
        result = await handle_command_async(command_type)
        
        # 명령별 응답 메시지 생성
        response_message = _get_command_response_message(command_type)
        logger.info(response_message)
        
        await websocket.send_text(json.dumps({
            "type": "command_response", 
            "command": command_type,
            "status": "success",
            "message": response_message
        }))
        
    except Exception as e:
        error_message = f"❌ {command_type} 명령 처리 실패: {e}"
        logger.error(error_message)
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "command": command_type,
            "status": "error",
            "message": error_message
        }))

async def _handle_text_command(websocket: WebSocket, command: str):
    """텍스트 명령 처리"""
    try:
        result = await handle_command_async(command)
        
        response_message = _get_command_response_message(command)
        logger.info(response_message)
        
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "command": command,
            "status": "success", 
            "message": response_message
        }))
        
    except Exception as e:
        error_message = f"❌ {command} 명령 처리 실패: {e}"
        logger.error(error_message)
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "command": command,
            "status": "error",
            "message": error_message
        }))

def _get_direction_korean(direction: str) -> str:
    """방향을 한국어로 변환"""
    direction_map = {
        "forward": "전진",
        "backward": "후진", 
        "left": "좌회전",
        "right": "우회전",
        "up": "상승",
        "down": "하강"
    }
    return direction_map.get(direction, direction)

def _get_command_response_message(command: str) -> str:
    """명령별 통일된 응답 메시지 생성"""
    command_messages = {
        "fire": "🔥 발화 명령이 실행되었습니다",
        "sol": "🔥 발화 명령이 실행되었습니다", 
        "laser_on": "🔴 레이저가 켜졌습니다",
        "laser_off": "⚫ 레이저가 꺼졌습니다",
        "stop": "🛑 정지 명령이 실행되었습니다",
        "reset": "🔄 리셋 명령이 실행되었습니다"
    }
    
    return command_messages.get(command.lower(), f"✅ {command} 명령이 처리되었습니다")