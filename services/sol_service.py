# services/sol_service.py - 솔레노이드(발사 장치) 제어 서비스
import RPi.GPIO as GPIO
import time
import logging

logger = logging.getLogger(__name__)

# 릴레이 핀 번호 (BCM 기준)
RELAY_PIN = 5
FIRE_DURATION = 0.3  # 발사 지속 시간(초)

def init_solenoid():
    """솔레노이드 초기화"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # 초기 상태: OFF
        logger.info("✅ 솔레노이드 초기화 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 솔레노이드 초기화 실패: {e}")
        return False

def fire(duration: float = FIRE_DURATION):
    """
    솔레노이드 발사
    
    Args:
        duration: 발사 지속 시간(초)
    """
    if not init_solenoid():
        return False
        
    try:
        logger.info(f"🔥 솔레노이드 발사 시작 ({duration}초)")
        
        # LOW: 릴레이 ON (솔레노이드 동작)
        GPIO.output(RELAY_PIN, GPIO.LOW)
        time.sleep(duration)
        
        # HIGH: 릴레이 OFF (솔레노이드 정지)
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        
        logger.info("✅ 솔레노이드 발사 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ 솔레노이드 발사 실패: {e}")
        return False
    finally:
        # 안전을 위해 항상 OFF 상태로
        try:
            GPIO.output(RELAY_PIN, GPIO.HIGH)
        except:
            pass

def emergency_stop():
    """비상 정지"""
    try:
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        logger.info("🛑 솔레노이드 비상 정지")
        return True
    except Exception as e:
        logger.error(f"❌ 솔레노이드 비상 정지 실패: {e}")
        return False

def get_solenoid_status():
    """솔레노이드 상태 조회"""
    try:
        pin_state = GPIO.input(RELAY_PIN)
        return {
            "pin": RELAY_PIN,
            "state": "OFF" if pin_state == GPIO.HIGH else "ON",
            "fire_duration": FIRE_DURATION
        }
    except Exception as e:
        logger.error(f"솔레노이드 상태 조회 실패: {e}")
        return {"error": str(e)}

def cleanup():
    """솔레노이드 리소스 정리"""
    try:
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # 안전하게 OFF
        GPIO.cleanup()
        logger.info("🧹 솔레노이드 정리 완료")
    except Exception as e:
        logger.error(f"⚠️ 솔레노이드 정리 중 오류: {e}")

# 프로그램 종료 시 자동 정리
import atexit
atexit.register(cleanup)