# services/command_service.py - 리팩토링된 명령 처리 서비스
import logging
import asyncio
from typing import Dict, List, Optional

# 각 하드웨어 서비스 import
from services.laser_service import laser_on, laser_off
from services.motor_service import (
    set_right_motor, set_left_motor, stop_motors, 
    cleanup as motor_cleanup, init_motor
)
from services.xy_servo import set_servo_angle, set_xy_servo_angles, handle_laser_xy, cleanup as servo_cleanup
from services.sol_service import fire as solenoid_fire
from services.feed_service import feed_once

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
                set_right_motor(speed, 0)  # 좌회전
                set_left_motor(speed, 1)
            elif direction == "right":
                set_right_motor(speed, 1)  # 우회전
                set_left_motor(speed, 0)
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
                
            set_servo_angle(angle)
            self.current_servo_angle = angle
            logger.info(f"🎯 서보 각도 변경: {angle}도")
            return True
        except Exception as e:
            logger.error(f"❌ 서보 제어 실패: {e}")
            return False

    def handle_laser_xy(self, x: int, y: int):
        """레이저 XY 좌표 제어 (서보 각도로 변환)"""
        try:
            # 새로운 handle_laser_xy 함수 사용
            return handle_laser_xy(x, y)
        except Exception as e:
            logger.error(f"❌ 레이저 XY 제어 실패: {e}")
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
    def handle_feed_now(self):
        """즉시 급식"""
        try:
            feed_once()
            logger.info("🍚 즉시 급식 실행")
            return True
        except Exception as e:
            logger.error(f"❌ 급식 실패: {e}")
            return False

# 전역 인스턴스
command_handler = CommandHandler()

async def handle_command_async(command: str) -> bool:
    """
    명령 문자열을 파싱하여 적절한 하드웨어 함수 호출
    
    Args:
        command: 명령 문자열
        
    Returns:
        bool: 명령 처리 성공 여부
    """
    try:
        cmd = command.strip().lower()
        
        # === 레이저 명령 ===
        if cmd == "laser_on":
            return command_handler.handle_laser_on()
        elif cmd == "laser_off":
            return command_handler.handle_laser_off()
        
        # === 모터 명령 ===
        elif cmd == "stop":
            return command_handler.handle_motor_command("stop")
        elif cmd in ["forward", "backward", "left", "right"]:
            return command_handler.handle_motor_command(cmd)
        elif ":" in cmd and cmd.split(":")[0] in ["forward", "backward", "left", "right"]:
            # 속도 지정 명령: forward:50
            parts = cmd.split(":")
            direction = parts[0]
            try:
                speed = int(parts[1])
                return command_handler.handle_motor_command(direction, speed)
            except ValueError:
                logger.error(f"잘못된 속도 값: {parts[1]}")
                return False
        
        # === 서보 명령 ===
        elif cmd.startswith("servo:"):
            # 서보 각도 명령: servo:90
            try:
                angle_str = cmd.split(":")[1]
                angle = int(angle_str)
                return command_handler.handle_servo_angle(angle)
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
                return command_handler.handle_laser_xy(x, y)
            except (IndexError, ValueError) as e:
                logger.error(f"레이저 XY 파싱 오류: {e}")
                return False
        
        # === 솔레노이드 명령 ===
        elif cmd == "fire":
            return command_handler.handle_fire()
        
        # === 급식 명령 ===
        elif cmd == "feed_now":
            return command_handler.handle_feed_now()
        
        # === 시스템 명령 ===
        elif cmd == "reset":
            command_handler.reset()
            return True
        
        # === 오디오 명령 (로그만) ===
        elif cmd == "audio_receive_on":
            logger.info("🎧 오디오 수신 시작")
            return True
        elif cmd == "audio_receive_off":
            logger.info("🎧 오디오 수신 종료")
            return True
        
        # === 알 수 없는 명령 ===
        else:
            logger.warning(f"알 수 없는 명령: {command}")
            return False
            
    except Exception as e:
        logger.error(f"명령 처리 중 예외 발생: {e}")
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
        "laser_xy:X,Y",  # 예: laser_xy:90,120
        
        # 모터
        "forward", "backward", "left", "right", "stop",
        "forward:SPEED", "backward:SPEED", "left:SPEED", "right:SPEED",  # 속도 지정
        
        # 서보
        "servo:ANGLE",  # 예: servo:90
        
        # 솔레노이드
        "fire",
        
        # 급식
        "feed_now",
        
        # 시스템
        "reset",
        
        # 오디오
        "audio_receive_on", "audio_receive_off"
    ]