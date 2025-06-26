import json
import logging
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from services.auto_play_service import auto_play_service
from services.audio_playback_service import audio_playback_service
from services.feed_service import feed_multiple
from services.settings_service import settings_service
from services.feed_scheduler import feed_scheduler
import asyncio

logger = logging.getLogger(__name__)

class SettingsWebSocketRouter:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔧 설정 웹소켓 연결됨 (총 {len(self.active_connections)}개)")
        
        # 현재 상태 전송
        await self.send_status(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"🔧 설정 웹소켓 연결 해제됨 (총 {len(self.active_connections)}개)")
    
    async def send_status(self, websocket: WebSocket):
        """현재 상태 전송"""
        try:
            status = {
                "type": "status",
                "auto_play": auto_play_service.get_status(),
                "audio": {
                    "volume": audio_playback_service.get_volume(),
                    "available_sounds": audio_playback_service.get_available_sounds()
                },
                "feed": settings_service.get_settings(),
                "scheduler": feed_scheduler.get_status()
            }
            await websocket.send_text(json.dumps(status))
        except Exception as e:
            logger.error(f"❌ 상태 전송 실패: {e}")
    
    async def broadcast_status(self):
        """모든 연결에 상태 브로드캐스트"""
        for connection in self.active_connections:
            try:
                await self.send_status(connection)
            except Exception as e:
                logger.error(f"❌ 브로드캐스트 실패: {e}")
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """메시지 처리"""
        try:
            data = json.loads(message)
            logger.info(f"🔧 설정 명령 수신: {data}")
            
            # 급식 명령 처리
            if "mode" in data:
                try:
                    # 설정 업데이트
                    new_settings = {
                        "mode": data["mode"],
                        "amount": int(data.get("amount", 1)),
                    }
                    
                    if data["mode"] == "auto" and "interval" in data:
                        new_settings["interval"] = int(data["interval"])
                    
                    # 설정 저장
                    settings_service.update_settings(new_settings)
                    
                    if data["mode"] == "auto":
                        # 자동 모드 시작
                        await feed_scheduler.start()
                        feed_scheduler.reset_schedule()  # 스케줄 초기화
                    else:
                        # 수동 모드: amount만큼 급식
                        await feed_multiple(new_settings["amount"])
                        # 자동 스케줄러 중지
                        await feed_scheduler.stop()
                    
                    # 상태 브로드캐스트
                    await self.broadcast_status()
                    
                    # 성공 응답
                    await websocket.send_text(json.dumps({
                        "type": "settings_updated",
                        "settings": settings_service.get_settings(),
                        "success": True
                    }))
                    
                    # observer들에게 표정 변경 알림
                    from routers.ws_router import observer_websockets
                    face_msg = {"type": "face", "state": "food-on"}
                    for obs_ws in list(observer_websockets):
                        try:
                            await obs_ws.send_text(json.dumps(face_msg))
                            logger.info(f"🟢 observer에게 표정(food-on) 전송")
                        except Exception as e:
                            logger.warning(f"❌ observer 전송 실패: {e}")
                    
                except Exception as e:
                    logger.error(f"❌ 급식 설정 처리 실패: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"급식 설정 처리 실패: {str(e)}",
                        "success": False
                    }))
                return
            
            # 기존 명령 처리
            command = data.get("command")
            if command == "get_status":
                await self.send_status(websocket)
            elif command == "set_auto_play_delay":
                delay = data.get("delay", 70)
                auto_play_service.set_auto_play_delay(delay)
                await self.broadcast_status()
            elif command == "set_motor_speed":
                speed = data.get("speed", 60)
                auto_play_service.set_motor_speed(speed)
                await self.broadcast_status()
            elif command == "set_audio_volume":
                volume = data.get("volume", 0.5)
                audio_playback_service.set_volume(volume)
                await self.broadcast_status()
            elif command == "play_sound":
                sound_type = data.get("sound_type", "excited")
                audio_playback_service.play_sound(sound_type)
            elif command == "test_motor_forward":
                from services.motor_service import move_forward, stop_motors
                speed = data.get("speed", 60)
                duration = data.get("duration", 2.0)
                
                logger.info(f"🚗 모터 전진 테스트 (속도: {speed}, 시간: {duration}초)")
                move_forward(speed)
                await asyncio.sleep(duration)
                stop_motors()
                
            elif command == "test_motor_turn":
                from services.motor_service import turn_left, turn_right, stop_motors
                direction = data.get("direction", "left")
                speed = data.get("speed", 60)
                duration = data.get("duration", 1.0)
                
                logger.info(f"🔄 모터 회전 테스트 (방향: {direction}, 속도: {speed}, 시간: {duration}초)")
                if direction == "left":
                    turn_left(speed)
                else:
                    turn_right(speed)
                await asyncio.sleep(duration)
                stop_motors()
                
            elif command == "test_solenoid":
                from services.sol_service import fire
                count = data.get("count", 1)
                
                logger.info(f"🔥 솔레노이드 테스트 ({count}회)")
                for i in range(count):
                    fire()
                    await asyncio.sleep(0.5)
                
            elif command == "test_laser":
                from services.laser_service import laser_on, laser_off
                duration = data.get("duration", 3.0)
                
                logger.info(f"🔴 레이저 테스트 ({duration}초)")
                laser_on()
                await asyncio.sleep(duration)
                laser_off()
                
            elif command == "test_servo":
                from services.xy_servo import set_xy_servo_angles, reset_to_center
                x = data.get("x", 90)
                y = data.get("y", 90)
                duration = data.get("duration", 2.0)
                
                logger.info(f"🎯 서보 테스트 (x: {x}, y: {y}, 시간: {duration}초)")
                set_xy_servo_angles(x, y)
                await asyncio.sleep(duration)
                reset_to_center()
                
            else:
                logger.warning(f"⚠️ 알 수 없는 명령: {command}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"알 수 없는 명령: {command}"
                }))
                
        except json.JSONDecodeError:
            logger.error("❌ JSON 파싱 오류")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "잘못된 JSON 형식"
            }))
        except Exception as e:
            logger.error(f"❌ 메시지 처리 오류: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"처리 오류: {str(e)}"
            }))

# 전역 인스턴스
settings_router = SettingsWebSocketRouter() 

router = APIRouter()

@router.websocket("/ws/settings")
async def websocket_settings(websocket: WebSocket):
    await settings_router.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await settings_router.handle_message(websocket, message)
    except WebSocketDisconnect:
        settings_router.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ 설정 웹소켓 오류: {e}")
        settings_router.disconnect(websocket) 