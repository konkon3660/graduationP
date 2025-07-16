# services/command_service.py - 리팩토링된 명령 처리 서비스
import logging
import asyncio
import json
from typing import Dict, List, Optional, Union
import concurrent.futures

# 각 하드웨어 서비스 import
from services.laser_service import laser_on, laser_off
from services.motor_service import (
    set_right_motor, set_left_motor, stop_motors, 
    cleanup as motor_cleanup, init_motor
)
from services.xy_servo import (
    set_servo_angle, set_xy_servo_angles, handle_laser_xy, 
    set_servo_angle_async, set_xy_servo_angles_async,
    cleanup as servo_cleanup
)
from services.sol_service import fire as solenoid_fire
from services.feed_service import (
    feed_once, feed_multiple, set_angle,
    cleanup as feed_cleanup, feed_once_sync
)
from services.ultrasonic_service import get_distance, get_distance_data, cleanup_ultrasonic

logger = logging.getLogger(__name__)

class CommandHandler:
    """하드웨어 명령 처리 클래스"""
    
    def __init__(self):
        self.is_initialized = False
        self.current_servo_angle = 90  # 현재 서보 각도 추적  
    def initialize(self):
        """하드웨어 초기화"""
        if not self.is_initialized:
            try:
                init_motor()  # 모터 초기화
                logger.info("🔧 하드웨어 초기화 완료")
                self.is_initialized = True
            except Exception as e:
                logger.error(f"❌ 하드웨어 초기화 실패: {e}")
    def reset(self):
        """모든 하드웨어 리셋"""
        try:
            # 모터 정지
            stop_motors()
            # 레이저 끄기
            laser_off()
            # 서보 중앙 위치로
            set_servo_angle(90)
            self.current_servo_angle = 90
            logger.info("🔄 하드웨어 리셋 완료")
        except Exception as e:
            logger.error(f"❌ 하드웨어 리셋 실패: {e}")
    def cleanup(self):
        """리소스 정리"""
        try:
            motor_cleanup()
            servo_cleanup()
            feed_cleanup()
            self.is_initialized = False
            logger.info("🧹 하드웨어 정리 완료")
        except Exception as e:
            logger.error(f"⚠️ 하드웨어 정리 중 오류: {e}")
    # === 레이저 제어 ===
    def handle_laser_on(self):
        """레이저 켜기"""
        try:
            laser_on()
            logger.info("🔴 레이저 ON")
            return True
        except Exception as e:
            logger.error(f"❌ 레이저 ON 실패: {e}")
            return False
    def handle_laser_off(self):
        """레이저 끄기"""
        try:
            laser_off()
            logger.info("⚫ 레이저 OFF")
            return True
        except Exception as e:
            logger.error(f"❌ 레이저 OFF 실패: {e}")
            return False
    def handle_laser_x(self, x: int):
        """X축만 제어"""
        try:
            return set_servo_angle(x, "x")
        except Exception as e:
            logger.error(f"❌ 레이저 X축 제어 실패: {e}")
            return False
    def handle_laser_y(self, y: int):
        """Y축만 제어"""
        try:
            return set_servo_angle(y, "y")
        except Exception as e:
            logger.error(f"❌ 레이저 Y축 제어 실패: {e}")
            return False
    def handle_laser_xy(self, x: int, y: int):
        """레이저 XY 좌표 제어 (서보 각도로 변환)"""
        try:
            return set_xy_servo_angles(x, y)
        except Exception as e:
            logger.error(f"❌ 레이저 XY 제어 실패: {e}")
            return False
    # === 모터 제어 ===
    def handle_motor_command(self, direction: str, speed: int = 70):
        """모터 제어 (방향별)"""
        self.initialize()
        
        try:
            if direction == "forward":
                set_right_motor(speed, 0)  # 전진
                set_left_motor(speed, 0)
            elif direction == "backward":
                set_right_motor(speed, 1)  # 후진
                set_left_motor(speed, 1)
            elif direction == "left":
                set_right_motor(speed, 1)  # 좌회전
                set_left_motor(speed, 0)
            elif direction == "right":
                set_right_motor(speed, 0)  # 우회전
                set_left_motor(speed, 1)
            elif direction == "stop":
                stop_motors()
            else:
                logger.warning(f"알 수 없는 방향: {direction}")
                return False
                
            logger.info(f"🕹️ 모터 {direction} (속도: {speed})")
            return True
        except Exception as e:
            logger.error(f"❌ 모터 제어 실패 ({direction}): {e}")
            return False
    # === 서보 제어 ===
    def handle_servo_angle(self, angle: int):
        """서보 각도 제어"""
        try:
            if not (0 <= angle <= 180):
                logger.warning(f"서보 각도 범위 초과: {angle}")
                return False
                
            result = set_servo_angle(angle)
            if result:
                self.current_servo_angle = angle
                logger.info(f"🎯 서보 각도 변경: {angle}도")
            return result
        except Exception as e:
            logger.error(f"❌ 서보 제어 실패: {e}")
            return False
    def handle_feed_servo_angle(self, angle: int):
        """급식용 서보모터 각도 제어 (GPIO 18)"""
        try:
            if not (0 <= angle <= 180):
                logger.warning(f"급식 서보 각도 범위 초과: {angle}")
                return False
            
            # feed_service의 서보모터 제어 함수 사용
            result = set_angle(angle)
            if result:
                logger.info(f"🍚 급식 서보 각도 변경: {angle}도")
            return result
        except Exception as e:
            logger.error(f"❌ 급식 서보 제어 실패: {e}")
            return False
    def handle_laser_servo_angle(self, angle: int):
        """레이저용 서보모터 각도 제어 (GPIO 19, 13)"""
        try:
            if not (0 <= angle <= 180):
                logger.warning(f"레이저 서보 각도 범위 초과: {angle}")
                return False
            
            # xy_servo의 X축 서보모터 제어 함수 사용
            result = set_servo_angle(angle, "x")
            if result:
                logger.info(f"🎯 레이저 서보 각도 변경: {angle}도")
            return result
        except Exception as e:
            logger.error(f"❌ 레이저 서보 제어 실패: {e}")
            return False
    # === 솔레노이드 제어 ===
    def handle_fire(self):
        """발사 장치 동작"""
        try:
            solenoid_fire()
            logger.info("🔥 솔레노이드 발사")
            return True
        except Exception as e:
            logger.error(f"❌ 솔레노이드 발사 실패: {e}")
            return False
    # === 급식 제어 ===
    def handle_feed_once(self):
        """급식 한 번 실행"""
        try:
            feed_once_sync()  # 동기 버전 사용
            logger.info("🍽 급식 실행 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 급식 실행 실패: {e}")
            return False
    def handle_feed_multiple(self, count: int):
        """급식 여러 번 실행"""
        try:
            for _ in range(count):
                feed_once_sync()  # 동기 버전 반복 실행
            logger.info(f"🍽 {count}회 급식 실행 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 다중 급식 실행 실패: {e}")
            return False
    # === 초음파 센서 제어 ===
    def handle_get_distance(self):
        """거리 측정"""
        try:
            distance = get_distance()
            if distance is not None:
                logger.info(f"📏 거리 측정: {distance}cm")
                return True
            else:
                logger.warning("⚠️ 거리 측정 실패")
                return False
        except Exception as e:
            logger.error(f"❌ 거리 측정 실패: {e}")
            return False
    def handle_get_distance_data(self):
        """거리 데이터 반환 (클라이언트 전송용)"""
        try:
            distance_data = get_distance_data()
            logger.info(f"📊 거리 데이터 생성: {distance_data}")
            return distance_data
        except Exception as e:
            logger.error(f"❌ 거리 데이터 생성 실패: {e}")
            return None

# 전역 인스턴스
command_handler = CommandHandler()
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

async def handle_command_async(command: Union[str, dict]) -> bool:
    """
    비동기 명령 처리 (개선된 버전)
    """
    try:
        if isinstance(command, dict):
            return await handle_json_command(command)
        
        cmd = command.strip().lower()
        logger.info(f"📨 명령 수신: {cmd}")
        
        # === 급식 명령 ===
        if cmd == "feed":
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_feed_once)
        elif cmd.startswith("feed:"):
            try:
                count = int(cmd.split(":")[1])
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_feed_multiple, count)
            except (IndexError, ValueError):
                logger.error(f"급식 횟수 파싱 오류: {cmd}")
                return False
        
        # === 레이저 명령 ===
        elif cmd == "laser_on":
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_on)
        elif cmd == "laser_off":
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_off)
        elif cmd.startswith("laser_x:"):
            try:
                x = int(cmd.split(":")[1])
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_x, x)
            except (IndexError, ValueError):
                logger.error(f"레이저 X 좌표 파싱 오류: {cmd}")
                return False
        elif cmd.startswith("laser_y:"):
            try:
                y = int(cmd.split(":")[1])
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_y, y)
            except (IndexError, ValueError):
                logger.error(f"레이저 Y 좌표 파싱 오류: {cmd}")
                return False
        
        # === 모터 명령 ===
        elif cmd in ["forward", "backward", "left", "right"]:
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_motor_command, cmd)
        elif ":" in cmd and cmd.split(":")[0] in ["forward", "backward", "left", "right"]:
            # 속도 지정 명령: forward:50
            parts = cmd.split(":")
            direction = parts[0]
            try:
                speed = int(parts[1])
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_motor_command, direction, speed)
            except ValueError:
                logger.error(f"잘못된 속도 값: {parts[1]}")
                return False
        
        # === 서보 명령 ===
        elif cmd.startswith("servo:"):
            # 서보 각도 명령: servo:90
            try:
                angle_str = cmd.split(":")[1]
                angle = int(angle_str)
                # 비동기 서보 제어 사용
                return await set_servo_angle_async(angle)
            except (IndexError, ValueError) as e:
                logger.error(f"서보 각도 파싱 오류: {e}")
                return False
        
        # === 레이저 XY 명령 ===
        elif cmd.startswith("laser_xy:"):
            # 레이저 XY 명령: laser_xy:90,120
            try:
                value = cmd.split(":")[1]
                x_str, y_str = value.split(",")
                x = int(x_str)
                y = int(y_str)
                # 비동기 XY 서보 제어 사용
                return await set_xy_servo_angles_async(x, y)
            except (IndexError, ValueError) as e:
                logger.error(f"레이저 XY 파싱 오류: {e}")
                return False
        
        # === 솔레노이드 명령 ===
        elif cmd == "fire":
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_fire)
        
        # === 급식 서보 명령 ===
        elif cmd.startswith("feed_servo:"):
            try:
                angle_str = cmd.split(":")[1]
                angle = int(angle_str)
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_feed_servo_angle, angle)
            except (IndexError, ValueError) as e:
                logger.error(f"급식 서보 각도 파싱 오류: {e}")
                return False
        
        # === 레이저 서보 명령 ===
        elif cmd.startswith("laser_servo:"):
            try:
                angle_str = cmd.split(":")[1]
                angle = int(angle_str)
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_servo_angle, angle)
            except (IndexError, ValueError) as e:
                logger.error(f"레이저 서보 각도 파싱 오류: {e}")
                return False
        
        # === 기타 명령 ===
        elif cmd == "stop":
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_motor_command, "stop")
        elif cmd == "reset":
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.reset)
        elif cmd == "status":
            logger.info("📊 하드웨어 상태 조회")
            return True
        else:
            logger.warning(f"알 수 없는 명령: {cmd}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 명령 처리 중 예외 발생: {e}")
        return False

async def handle_json_command(command_data: dict) -> bool:
    """
    JSON 명령 처리 (개선된 버전)
    """
    try:
        command_type = command_data.get("type", "").lower()
        logger.info(f"📨 JSON 명령 수신: {command_type}")
        
        # === 급식 관련 JSON 명령 ===
        if command_type == "feed":
            action = command_data.get("action", "").lower()
            if action == "once":
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_feed_once)
            elif action == "multiple":
                count = command_data.get("count", 1)
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_feed_multiple, count)
            else:
                # 기본 동작: 한 번 급식
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_feed_once)
        
        elif command_type == "feed_servo":
            # 급식용 서보모터 제어 (GPIO 18)
            angle = command_data.get("angle", 90)
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_feed_servo_angle, angle)
        
        elif command_type == "laser_servo":
            # 레이저용 서보모터 제어 (GPIO 19, 13)
            angle = command_data.get("angle", 90)
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_servo_angle, angle)
        
        # === 레이저 관련 JSON 명령 ===
        elif command_type == "laser":
            action = command_data.get("action", "").lower()
            if action == "on":
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_on)
            elif action == "off":
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_off)
            elif action == "xy":
                x = command_data.get("x", 90)
                y = command_data.get("y", 90)
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_xy, x, y)
            elif action == "x":
                x = command_data.get("x", 90)
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_x, x)
            elif action == "y":
                y = command_data.get("y", 90)
                return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_laser_y, y)
        
        # === 모터 관련 JSON 명령 ===
        elif command_type == "motor":
            direction = command_data.get("direction", "").lower()
            speed = command_data.get("speed", 70)
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_motor_command, direction, speed)
        
        # === 솔레노이드 관련 JSON 명령 ===
        elif command_type == "fire":
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.handle_fire)
        
        # === 서보 관련 JSON 명령 ===
        elif command_type == "servo":
            angle = command_data.get("angle", 90)
            # 비동기 서보 제어 사용
            return await set_servo_angle_async(angle)
        
        # === 기타 JSON 명령 ===
        elif command_type == "reset":
            return await asyncio.get_event_loop().run_in_executor(_executor, command_handler.reset)
        elif command_type == "status":
            logger.info("📊 하드웨어 상태 조회")
            return True
        else:
            logger.warning(f"알 수 없는 JSON 명령 타입: {command_type}")
            return False
            
    except Exception as e:
        logger.error(f"❌ JSON 명령 처리 중 예외 발생: {e}")
        return False

def get_system_status() -> Dict:
    """시스템 상태 조회"""
    return {
        "hardware_initialized": command_handler.is_initialized,
        "current_servo_angle": command_handler.current_servo_angle,
        "status": "operational"
    }

def get_available_commands() -> List[str]:
    """사용 가능한 명령 목록"""
    return [
        # 레이저
        "laser_on", "laser_off", 
        "laser_x:X", "laser_y:Y",  # 예: laser_x:90
        
        # 모터
        "forward", "backward", "left", "right", "stop",
        "forward:SPEED", "backward:SPEED", "left:SPEED", "right:SPEED",  # 속도 지정
        
        # 서보
        "servo:ANGLE",  # 예: servo:90
        
        # 솔레노이드
        "fire",
        
        # 급식
        "feed_now",
        
        # 초음파 센서
        "get_distance",
        
        # 시스템
        "reset",
        
        # 오디오
        "audio_receive_on", "audio_receive_off"
    ]

def get_available_json_commands() -> List[Dict]:
    """사용 가능한 JSON 명령 목록"""
    return [
        # 설정 (클라이언트 호환성)
        {"mode": "auto", "amount": 5, "interval": 480},
        {"mode": "manual", "amount": 1, "interval": 60},
        
        # 급식 (기본)
        {"type": "feed", "amount": 1},
        {"type": "feed_now"},
        {"type": "feed_multiple", "amount": 3},
        
        # 급식 (클라이언트 호환성)
        {"type": "feeding", "amount": 1},
        {"type": "give_food", "amount": 1},
        {"type": "food", "amount": 1},
        {"type": "dispense", "amount": 1},
        {"type": "servo", "action": "feed", "amount": 1},
        
        # 레이저
        {"type": "laser", "action": "on"},
        {"type": "laser", "action": "off"},
        {"type": "laser", "action": "xy", "x": 90, "y": 90},
        {"type": "laser", "action": "x", "x": 90},
        {"type": "laser", "action": "y", "y": 90},
        
        # 모터
        {"type": "motor", "direction": "forward", "speed": 70},
        {"type": "motor", "direction": "backward", "speed": 70},
        {"type": "motor", "direction": "left", "speed": 70},
        {"type": "motor", "direction": "right", "speed": 70},
        {"type": "motor", "direction": "stop"},
        
        # 서보
        {"type": "servo", "angle": 90},
        
        # 솔레노이드
        {"type": "fire"},
        
        # 초음파 센서
        {"type": "ultrasonic", "action": "get_distance"},
        {"type": "ultrasonic", "action": "get_distance_data"},
        
        # 시스템
        {"type": "reset"}
    ]