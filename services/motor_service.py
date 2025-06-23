# services/motor_service.py - DC 모터 제어 서비스 (개선된 버전)
import RPi.GPIO as GPIO
import logging
import time

logger = logging.getLogger(__name__)

# 핀 번호 정의 (하드웨어 구성표에 맞게 수정)
ENA, INT1, INT2 = 26, 23, 24  # 우측 모터 (ENA=PIN37, IN1=PIN16, IN2=PIN18)
ENB, INT3, INT4 = 21, 27, 22  # 좌측 모터 (ENB=PIN40, IN3=PIN13, IN4=PIN15)

# PWM 객체 및 초기화 상태
pwmA = None  # 우측 모터 PWM
pwmB = None  # 좌측 모터 PWM
_initialized = False

# 기본 설정
DEFAULT_SPEED = 70
PWM_FREQUENCY = 1000

def init_motor():
    """모터 핀 및 PWM 설정 (최초 1회만 호출)"""
    global pwmA, pwmB, _initialized
    
    if _initialized:
        return True

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # 핀 설정
        motor_pins = [ENA, INT1, INT2, ENB, INT3, INT4]
        GPIO.setup(motor_pins, GPIO.OUT)

        # PWM 객체 생성
        pwmA = GPIO.PWM(ENA, PWM_FREQUENCY)
        pwmB = GPIO.PWM(ENB, PWM_FREQUENCY)
        pwmA.start(0)
        pwmB.start(0)

        _initialized = True
        logger.info("✅ DC 모터 초기화 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ DC 모터 초기화 실패: {e}")
        return False

def set_right_motor(speed: int, direction: int):
    """
    우측 모터 제어
    
    Args:
        speed: 모터 속도 (0~100)
        direction: 회전 방향 (0=전진, 1=후진)
    """
    if not init_motor():
        return False
        
    if not (0 <= speed <= 100):
        logger.warning(f"속도 범위 초과: {speed} (0~100 허용)")
        speed = max(0, min(100, speed))
    
    try:
        GPIO.output(INT1, GPIO.HIGH if direction == 0 else GPIO.LOW)
        GPIO.output(INT2, GPIO.LOW if direction == 0 else GPIO.HIGH)
        pwmA.ChangeDutyCycle(speed)
        
        logger.debug(f"우측 모터: 속도={speed}, 방향={'전진' if direction == 0 else '후진'}")
        return True
    except Exception as e:
        logger.error(f"❌ 우측 모터 제어 실패: {e}")
        return False

def set_left_motor(speed: int, direction: int):
    """
    좌측 모터 제어
    
    Args:
        speed: 모터 속도 (0~100)
        direction: 회전 방향 (0=전진, 1=후진)
    """
    if not init_motor():
        return False
        
    if not (0 <= speed <= 100):
        logger.warning(f"속도 범위 초과: {speed} (0~100 허용)")
        speed = max(0, min(100, speed))
    
    try:
        GPIO.output(INT3, GPIO.HIGH if direction == 0 else GPIO.LOW)
        GPIO.output(INT4, GPIO.LOW if direction == 0 else GPIO.HIGH)
        pwmB.ChangeDutyCycle(speed)
        
        logger.debug(f"좌측 모터: 속도={speed}, 방향={'전진' if direction == 0 else '후진'}")
        return True
    except Exception as e:
        logger.error(f"❌ 좌측 모터 제어 실패: {e}")
        return False

def move_forward(speed: int = DEFAULT_SPEED):
    """전진"""
    logger.info(f"🚗 전진 (속도: {speed})")
    return set_right_motor(speed, 0) and set_left_motor(speed, 0)

def move_backward(speed: int = DEFAULT_SPEED):
    """후진"""
    logger.info(f"🔄 후진 (속도: {speed})")
    return set_right_motor(speed, 1) and set_left_motor(speed, 1)

def turn_left(speed: int = DEFAULT_SPEED):
    """좌회전"""
    logger.info(f"⬅️ 좌회전 (속도: {speed})")
    return set_right_motor(speed, 0) and set_left_motor(speed, 1)

def turn_right(speed: int = DEFAULT_SPEED):
    """우회전"""
    logger.info(f"➡️ 우회전 (속도: {speed})")
    return set_right_motor(speed, 1) and set_left_motor(speed, 0)

def stop_motors():
    """모터 정지"""
    if not init_motor():
        return False
        
    try:
        # 모든 제어 핀을 LOW로
        GPIO.output(INT1, GPIO.LOW)
        GPIO.output(INT2, GPIO.LOW)
        GPIO.output(INT3, GPIO.LOW)
        GPIO.output(INT4, GPIO.LOW)
        
        # PWM 듀티사이클 0으로
        pwmA.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)
        
        logger.info("🛑 모터 정지")
        return True
    except Exception as e:
        logger.error(f"❌ 모터 정지 실패: {e}")
        return False

def get_motor_status():
    """모터 상태 조회"""
    return {
        "initialized": _initialized,
        "pins": {
            "right_motor": {"enable": ENA, "control": [INT1, INT2]},
            "left_motor": {"enable": ENB, "control": [INT3, INT4]}
        },
        "pwm_frequency": PWM_FREQUENCY,
        "default_speed": DEFAULT_SPEED
    }

def cleanup():
    """모터 리소스 정리"""
    global _initialized, pwmA, pwmB
    
    try:
        if _initialized:
            stop_motors()
            
        if pwmA:
            pwmA.stop()
        if pwmB:
            pwmB.stop()
            
        GPIO.cleanup()
        _initialized = False
        pwmA = None
        pwmB = None
        
        logger.info("🧹 DC 모터 정리 완료")
    except Exception as e:
        logger.error(f"⚠️ DC 모터 정리 중 오류: {e}")

# 프로그램 종료 시 자동 정리
import atexit
atexit.register(cleanup)