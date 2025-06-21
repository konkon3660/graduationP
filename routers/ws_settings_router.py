import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.settings_service import settings_service
from services.feed_scheduler import feed_scheduler

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws/settings")
async def settings_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔗 설정 WebSocket 클라이언트 연결됨")
    
    try:
        # 초기 설정 전송
        initial_settings = settings_service.get_settings()
        scheduler_status = feed_scheduler.get_status()
        
        response = {
            "type": "init",
            "settings": initial_settings,
            "scheduler_status": scheduler_status
        }
        await websocket.send_text(json.dumps(response, ensure_ascii=False))
        
        while True:
            # 클라이언트에서 받은 JSON 메시지
            message = await websocket.receive_text()
            
            try:
                data = json.loads(message)
                message_type = data.get("type", "")
                
                if message_type == "update_settings":
                    # 설정 업데이트
                    new_settings = data.get("settings", {})
                    try:
                        updated_settings = settings_service.update_settings(new_settings)
                        
                        # 스케줄러 리셋 (설정 변경 시)
                        feed_scheduler.reset_schedule()
                        
                        response = {
                            "type": "settings_updated",
                            "settings": updated_settings,
                            "success": True
                        }
                        await websocket.send_text(json.dumps(response, ensure_ascii=False))
                        
                        logger.info(f"🔧 설정 업데이트됨: {updated_settings}")
                        
                    except ValueError as e:
                        # 유효성 검사 실패
                        response = {
                            "type": "error",
                            "message": str(e),
                            "success": False
                        }
                        await websocket.send_text(json.dumps(response, ensure_ascii=False))
                        logger.warning(f"⚠️ 설정 업데이트 실패: {e}")
                
                elif message_type == "get_settings":
                    # 현재 설정 요청
                    current_settings = settings_service.get_settings()
                    scheduler_status = feed_scheduler.get_status()
                    
                    response = {
                        "type": "settings",
                        "settings": current_settings,
                        "scheduler_status": scheduler_status
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                
                elif message_type == "start_scheduler":
                    # 스케줄러 시작
                    await feed_scheduler.start()
                    scheduler_status = feed_scheduler.get_status()
                    
                    response = {
                        "type": "scheduler_started",
                        "scheduler_status": scheduler_status,
                        "success": True
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info("🚀 스케줄러 시작됨")
                
                elif message_type == "stop_scheduler":
                    # 스케줄러 중지
                    await feed_scheduler.stop()
                    scheduler_status = feed_scheduler.get_status()
                    
                    response = {
                        "type": "scheduler_stopped",
                        "scheduler_status": scheduler_status,
                        "success": True
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info("⏹ 스케줄러 중지됨")
                
                elif message_type == "manual_feed":
                    # 수동 급식 실행
                    amount = data.get("amount", 1)
                    from services.feed_service import feed_once
                    
                    for i in range(amount):
                        feed_once()
                        if i < amount - 1:
                            import asyncio
                            await asyncio.sleep(1)
                    
                    response = {
                        "type": "manual_feed_completed",
                        "amount": amount,
                        "success": True
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info(f"🍽 수동 급식 완료: {amount}회")
                
                else:
                    # 알 수 없는 메시지 타입
                    response = {
                        "type": "error",
                        "message": f"알 수 없는 메시지 타입: {message_type}",
                        "success": False
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.warning(f"⚠️ 알 수 없는 메시지 타입: {message_type}")
                
            except json.JSONDecodeError:
                # JSON 파싱 실패
                response = {
                    "type": "error",
                    "message": "잘못된 JSON 형식입니다",
                    "success": False
                }
                await websocket.send_text(json.dumps(response, ensure_ascii=False))
                logger.warning("⚠️ 잘못된 JSON 형식")
            
            except Exception as e:
                # 기타 오류
                response = {
                    "type": "error",
                    "message": f"서버 오류: {str(e)}",
                    "success": False
                }
                await websocket.send_text(json.dumps(response, ensure_ascii=False))
                logger.error(f"❌ WebSocket 처리 오류: {e}")
    
    except WebSocketDisconnect:
        logger.info("🔌 설정 WebSocket 클라이언트 연결 해제됨")
    except Exception as e:
        logger.error(f"❌ 설정 WebSocket 오류: {e}") 