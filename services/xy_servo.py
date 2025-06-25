# services/xy_servo.py - X축, Y축 서보모터 제어 서비스
import RPi.GPIO as GPIO
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 서보모터 제어 핀 번호 (BCM 기준)
X_SERVO_PIN = 19  # X축 서보모터 (좌우)
Y_SERVO_PIN = 13  # Y축 서보모터 (상하)
PWM_FREQUENCY = 50

# 전역 변수
x_pwm: Optional[GPIO.PWM] = None
y_pwm: Optional[GPIO.PWM] = None
_initialized = False
_gpio_initialized = False

# 현재 각도 추적
current_x_angle = 90
current_y_angle = 90

def _init_gpio():
    """GPIO 초기화 (한 번만 실행)"""
    global _gpio_initialized
    if _gpio_initialized:
        return True
        
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # GPIO 경고 무시
        _gpio_initialized = True
        logger.debug("GPIO 모드 설정 완료")
        return True
    except Exception as e:
        logger.error(f"❌ GPIO 초기화 실패: {e}")
        return False

def init_xy_servo():
    """X축, Y축 서보 모터 초기화"""
    global x_pwm, y_pwm, _initialized
    
    if _initialized:
        return True
        
    try:
        if not _init_gpio():
            return False
            
        # 핀 설정
        GPIO.setup(X_SERVO_PIN, GPIO.OUT)
        GPIO.setup(Y_SERVO_PIN, GPIO.OUT)
        
        # PWM 객체 생성
        x_pwm = GPIO.PWM(X_SERVO_PIN, PWM_FREQUENCY)
        y_pwm = GPIO.PWM(Y_SERVO_PIN, PWM_FREQUENCY)
        
        # PWM 시작
        x_pwm.start(0)
        y_pwm.start(0)
        
        _initialized = True
        logger.info("✅ X축, Y축 서보모터 초기화 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 서보모터 초기화 실패: {e}")
        # 실패 시 정리
        cleanup()
        return False

def set_servo_angle(angle: int, axis: str = "x"):
    """
    서보 모터 각도 설정 (비동기 안전 버전)
    
    Args:
        angle: 0~180도 범위의 각도
        axis: "x" 또는 "y" (기본값: "x")
    """
    global current_x_angle, current_y_angle
    
    if not init_xy_servo():
        logger.error("서보모터 초기화 실패")
        return False
        
    if not (0 <= angle <= 180):
        logger.error(f"각도 범위 초과: {angle} (0~180도만 허용)")
        return False
    
    try:
        # 각도를 PWM 듀티사이클로 변환
        duty = 2 + (angle / 18)  # 0도=2.5%, 180도=12.5%
        
        if axis.lower() == "x":
            if x_pwm is None:
                logger.error("X축 PWM 객체가 초기화되지 않음")
                return False
                
            # 서보모터 제어: PWM 신호 보내기
            x_pwm.ChangeDutyCycle(duty)
            
            # time.sleep 제거 - 블로킹 방지
            # 서보모터는 PWM 신호만으로도 충분히 동작함
            
            current_x_angle = angle
            logger.info(f"🎯 X축 서보 각도 설정: {angle}도")
            
        elif axis.lower() == "y":
            if y_pwm is None:
                logger.error("Y축 PWM 객체가 초기화되지 않음")
                return False
                
            # 서보모터 제어: PWM 신호 보내기
            y_pwm.ChangeDutyCycle(duty)
            
            # time.sleep 제거 - 블로킹 방지
            # 서보모터는 PWM 신호만으로도 충분히 동작함
            
            current_y_angle = angle
            logger.info(f"🎯 Y축 서보 각도 설정: {angle}도")
            
        else:
            logger.error(f"잘못된 축 지정: {axis}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 서보 각도 설정 실패: {e}")
        return False

async def set_servo_angle_async(angle: int, axis: str = "x"):
    """
    서보 모터 각도 설정 (비동기 버전)
    """
    try:
        # 비동기 실행자에서 동기 함수 호출
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, set_servo_angle, angle, axis)
        
        if result:
            # 서보모터 안정화를 위한 비동기 대기
            await asyncio.sleep(0.2)  # 200ms 비동기 대기
            
            # PWM 신호 끄기 (서보모터 안정화 후)
            if axis.lower() == "x" and x_pwm:
                x_pwm.ChangeDutyCycle(0)
            elif axis.lower() == "y" and y_pwm:
                y_pwm.ChangeDutyCycle(0)
        
        return result
    except Exception as e:
        logger.error(f"❌ 비동기 서보 제어 실패: {e}")
        return False

def set_xy_servo_angles(x_angle: int, y_angle: int):
    """
    X축, Y축 서보모터 동시 제어 (동기 버전)
    
    Args:
        x_angle: X축 각도 (0~180)
        y_angle: Y축 각도 (0~180)
    """
    if not init_xy_servo():
        return False
    
    try:
        # 각도 범위 검증
        if not (0 <= x_angle <= 180) or not (0 <= y_angle <= 180):
            logger.error(f"각도 범위 초과: X={x_angle}, Y={y_angle} (0~180도만 허용)")
            return False
        
        # X축과 Y축 동시 제어
        success_x = set_servo_angle(x_angle, "x")
        success_y = set_servo_angle(y_angle, "y")
        
        if success_x and success_y:
            logger.info(f"🎯 XY 서보 각도 설정 완료: X={x_angle}도, Y={y_angle}도")
            return True
        else:
            logger.error(f"❌ XY 서보 제어 실패: X={success_x}, Y={success_y}")
            return False
            
    except Exception as e:
        logger.error(f"❌ XY 서보 제어 중 예외 발생: {e}")
        return False

async def set_xy_servo_angles_async(x_angle: int, y_angle: int):
    """
    X축, Y축 서보모터 동시 제어 (비동기 버전)
    """
    try:
        # 비동기 실행자에서 동기 함수 호출
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, set_xy_servo_angles, x_angle, y_angle)
        
        if result:
            # 서보모터 안정화를 위한 비동기 대기
            await asyncio.sleep(0.2)  # 200ms 비동기 대기
            
            # PWM 신호 끄기 (서보모터 안정화 후)
            if x_pwm:
                x_pwm.ChangeDutyCycle(0)
            if y_pwm:
                y_pwm.ChangeDutyCycle(0)
        
        return result
    except Exception as e:
        logger.error(f"❌ 비동기 XY 서보 제어 실패: {e}")
        return False

def handle_laser_xy(x: int, y: int):
    """
    레이저 XY 좌표를 서보 각도로 변환하여 제어
    
    Args:
        x: X 좌표 (0~180 범위)
        y: Y 좌표 (0~180 범위)
    """
    try:
        # 좌표를 각도로 변환 (필요시 매핑 로직 추가 가능)
        x_angle = max(0, min(180, x))
        y_angle = max(0, min(180, y))
        
        logger.info(f"🎯 레이저 XY 좌표 변환: ({x}, {y}) → X각도={x_angle}, Y각도={y_angle}")
        return set_xy_servo_angles(x_angle, y_angle)
        
    except Exception as e:
        logger.error(f"❌ 레이저 XY 제어 실패: {e}")
        return False

def get_servo_status():
    """서보모터 상태 조회"""
    return {
        "initialized": _initialized,
        "current_x_angle": current_x_angle,
        "current_y_angle": current_y_angle,
        "pins": {
            "x_servo": X_SERVO_PIN,
            "y_servo": Y_SERVO_PIN
        },
        "pwm_frequency": PWM_FREQUENCY
    }

def get_servo_limits():
    """서보 각도 제한값 반환"""
    return {"min": 0, "max": 180}

def reset_to_center():
    """서보모터를 중앙 위치로 리셋"""
    logger.info("🔄 서보모터 중앙 위치로 리셋")
    return set_xy_servo_angles(90, 90)

def cleanup():
    """서보 리소스 정리"""
    global x_pwm, y_pwm, _initialized
    
    try:
        if x_pwm:
            x_pwm.stop()
            x_pwm = None
        if y_pwm:
            y_pwm.stop()
            y_pwm = None
        _initialized = False
        logger.info("🧹 X축, Y축 서보모터 정리 완료")
    except Exception as e:
        logger.error(f"⚠️ 서보모터 정리 중 오류: {e}")

# 프로그램 종료 시 자동 정리
import atexit
atexit.register(cleanup)