# services/command_service.py - 올바른 버전
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)

# 동기 버전 handle_command 함수
def handle_command(command: str, websocket: WebSocket = None) -> str:
    """명령 처리 함수 (동기)"""
    try:
        logger.info(f"명령 처리 중: {command}")
        
        if command == "laser_on":
            logger.info("🔴 레이저 ON 명령 처리")
            return "레이저가 켜졌습니다"
        elif command == "laser_off":
            logger.info("⚫ 레이저 OFF 명령 처리")  
            return "레이저가 꺼졌습니다"
        elif command.startswith("joystick"):
            logger.info(f"🕹️ 조이스틱 명령: {command}")
            return f"조이스틱 명령 처리됨: {command}"
        else:
            logger.info(f"일반 명령 처리: {command}")
            return f"명령 처리됨: {command}"
            
    except Exception as e:
        logger.error(f"명령 처리 오류: {e}")
        return f"명령 처리 실패: {str(e)}"

# 비동기 버전 handle_command 함수
async def handle_command_async(command: str, websocket: WebSocket = None) -> str:
    """비동기 명령 처리 함수"""
    try:
        logger.info(f"비동기 명령 처리 중: {command}")
        
        # JSON 파싱 시도
        try:
            data = json.loads(command)
            msg_type = data.get("type", "command")
            content = data.get("content", command)
            
            if msg_type == "command":
                if content == "laser_on":
                    logger.info("🔴 레이저 ON (JSON)")
                    return "레이저가 켜졌습니다"
                elif content == "laser_off":
                    logger.info("⚫ 레이저 OFF (JSON)")
                    return "레이저가 꺼졌습니다"
                elif content.startswith("joystick"):
                    logger.info(f"🕹️ 조이스틱 (JSON): {content}")
                    return f"조이스틱 명령 처리됨: {content}"
                    
        except json.JSONDecodeError:
            # 일반 텍스트로 처리
            if command == "laser_on":
                logger.info("🔴 레이저 ON (텍스트)")
                return "레이저가 켜졌습니다"
            elif command == "laser_off":
                logger.info("⚫ 레이저 OFF (텍스트)")
                return "레이저가 꺼졌습니다"
            elif command.startswith("joystick"):
                logger.info(f"🕹️ 조이스틱 (텍스트): {command}")
                return f"조이스틱 명령 처리됨: {command}"
        
        return f"명령 처리됨: {command}"
        
    except Exception as e:
        logger.error(f"비동기 명령 처리 오류: {e}")
        return f"명령 처리 실패: {str(e)}"