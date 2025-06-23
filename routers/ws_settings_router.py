import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.settings_service import settings_service
from services.feed_scheduler import feed_scheduler
from services.auto_play_service import auto_play_service
from services.audio_playback_service import audio_playback_service
from services.ultrasonic_service import get_distance

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws/settings")
async def settings_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔗 설정 WebSocket 클라이언트 연결됨")
    
    # 자동 놀이 서비스에 클라이언트 등록
    auto_play_service.register_client(websocket)
    
    try:
        # 초기 설정 전송
        initial_settings = settings_service.get_settings()
        scheduler_status = feed_scheduler.get_status()
        auto_play_status = auto_play_service.get_status()
        audio_status = audio_playback_service.get_status()
        
        response = {
            "type": "init",
            "settings": initial_settings,
            "scheduler_status": scheduler_status,
            "auto_play_status": auto_play_status,
            "audio_status": audio_status
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
                    auto_play_status = auto_play_service.get_status()
                    audio_status = audio_playback_service.get_status()
                    
                    response = {
                        "type": "settings",
                        "settings": current_settings,
                        "scheduler_status": scheduler_status,
                        "auto_play_status": auto_play_status,
                        "audio_status": audio_status
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
                
                elif message_type == "set_auto_play_delay":
                    # 자동 놀이 대기 시간 설정
                    delay = data.get("delay", 70)
                    auto_play_service.set_auto_play_delay(delay)
                    
                    response = {
                        "type": "auto_play_delay_updated",
                        "delay": delay,
                        "success": True
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info(f"⏰ 자동 놀이 대기 시간 설정: {delay}초")
                
                elif message_type == "get_auto_play_status":
                    # 자동 놀이 상태 조회
                    auto_play_status = auto_play_service.get_status()
                    
                    response = {
                        "type": "auto_play_status",
                        "auto_play_status": auto_play_status,
                        "success": True
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                
                elif message_type == "set_obstacle_distance":
                    # 장애물 감지 거리 설정
                    distance = data.get("distance", 20)
                    auto_play_service.set_obstacle_distance(distance)
                    
                    response = {
                        "type": "obstacle_distance_updated",
                        "distance": distance,
                        "success": True
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info(f"📏 장애물 감지 거리 설정: {distance}cm")
                
                elif message_type == "set_motor_speed":
                    # 모터 속도 설정
                    speed = data.get("speed", 60)
                    auto_play_service.set_motor_speed(speed)
                    
                    response = {
                        "type": "motor_speed_updated",
                        "speed": speed,
                        "success": True
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info(f"🚗 모터 속도 설정: {speed}")
                
                elif message_type == "set_audio_volume":
                    # 오디오 볼륨 설정
                    volume = data.get("volume", 0.7)
                    audio_playback_service.set_volume(volume)
                    
                    response = {
                        "type": "audio_volume_updated",
                        "volume": volume,
                        "success": True
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info(f"🔊 오디오 볼륨 설정: {volume}")
                
                elif message_type == "play_sound":
                    # 음성 재생
                    sound = data.get("sound", "happy")
                    success = audio_playback_service.play_sound(sound)
                    
                    response = {
                        "type": "sound_played",
                        "sound": sound,
                        "success": success
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info(f"🎵 음성 재생: {sound}")
                
                elif message_type == "test_obstacle_detection":
                    # 장애물 감지 테스트
                    distance = get_distance()
                    
                    response = {
                        "type": "obstacle_detection_result",
                        "distance": distance,
                        "success": distance is not None
                    }
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info(f"📏 장애물 감지 테스트: {distance}cm")
                
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
    finally:
        # 자동 놀이 서비스에서 클라이언트 해제
        auto_play_service.unregister_client(websocket) 