# services/servo.py - 서보모터 제어 서비스
import RPi.GPIO as GPIO
import time
import logging

logger = logging.getLogger(__name__)

# 서보모터 제어 핀 번호 (BCM 기준)
SERVO_PIN = 21
PWM_FREQUENCY = 50

# 전역 변수
pwm = None
_initialized = False

def init_servo():
    """서보 모터 초기화"""
    global pwm, _initialized
    
    if _initialized:
        return True
        
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        
        pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
        pwm.start(0)
        
        _initialized = True
        logger.info("✅ 서보모터 초기화 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 서보모터 초기화 실패: {e}")
        return False

def set_servo_angle(angle: int):
    """
    서보 모터 각도 설정
    
    Args:
        angle: 0~180도 범위의 각도
    """
    if not init_servo():
        logger.error("서보모터 초기화 실패")
        return False
        
    if not (0 <= angle <= 180):
        logger.error(f"각도 범위 초과: {angle} (0~180도만 허용)")
        return False
    
    try:
        # 각도를 PWM 듀티사이클로 변환
        duty = 2 + (angle / 18)  # 0도=2.5%, 180도=12.5%
        
        GPIO.output(SERVO_PIN, True)
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)  # 움직일 시간 대기
        GPIO.output(SERVO_PIN, False)
        pwm.ChangeDutyCycle(0)  # 떨림 방지
        
        logger.info(f"🎯 서보 각도 설정: {angle}도")
        return True
        
    except Exception as e:
        logger.error(f"❌ 서보 각도 설정 실패: {e}")
        return False

def get_servo_limits():
    """서보 각도 제한값 반환"""
    return {"min": 0, "max": 180}

def cleanup():
    """서보 리소스 정리"""
    global pwm, _initialized
    
    try:
        if pwm:
            pwm.stop()
        GPIO.cleanup()
        _initialized = False
        logger.info("🧹 서보모터 정리 완료")
    except Exception as e:
        logger.error(f"⚠️ 서보모터 정리 중 오류: {e}")

# 프로그램 종료 시 자동 정리
import atexit
atexit.register(cleanup)