# services/feed_service.py

import RPi.GPIO as GPIO
import asyncio
import logging
from datetime import datetime, timedelta
from services.settings_service import settings_service

logger = logging.getLogger(__name__)

SERVO_PIN = 18  # 급식용 서보모터 (PIN 12, hardware PWM)
PWM_FREQUENCY = 50

# 전역 변수
pwm = None
_initialized = False
_gpio_initialized = False

def _init_gpio():
    """GPIO 초기화 (한 번만 실행)"""
    global _gpio_initialized
    if _gpio_initialized:
        return True
        
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # GPIO 경고 무시
        _gpio_initialized = True
        logger.debug("급식 서보 GPIO 모드 설정 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 급식 서보 GPIO 초기화 실패: {e}")
        return False

def init_feed_servo():
    """급식 서보모터 초기화"""
    global pwm, _initialized
    
    if _initialized:
        return True
        
    try:
        if not _init_gpio():
            return False
            
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
        pwm.start(0)
        
        _initialized = True
        logger.info("✅ 급식 서보모터 초기화 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 급식 서보모터 초기화 실패: {e}")
        cleanup()
        return False

def _set_angle_sync(angle):
    """서보모터 각도 설정 (순수 동기 함수 - run_in_executor용)"""
    try:
        if pwm is None:
            logger.error("PWM 객체가 초기화되지 않음")
            return False
            
        duty = angle / 18 + 2
        if duty < 2 or duty > 12:
            logger.warning(f"⚠️ 듀티사이클 {duty}%는 비정상입니다.")
            return False
            
        # 서보모터 제어: PWM 신호 보내기
        pwm.ChangeDutyCycle(duty)
        
        # 서보모터가 움직일 시간을 주기 위해 짧은 대기
        import time
        time.sleep(0.1)  # 100ms 대기 (최소한으로)
        
        # PWM 신호 끄기 (중요!)
        pwm.ChangeDutyCycle(0)
        
        logger.debug(f"급식 서보 각도 설정: {angle}도")
        return True
    except Exception as e:
        logger.error(f"❌ 급식 서보 각도 설정 실패: {e}")
        return False

def set_angle(angle):
    """서보모터 각도 설정 (동기 래퍼 - 하위 호환성)"""
    if not init_feed_servo():
        return False
    return _set_angle_sync(angle)

async def set_angle_async(angle):
    """서보모터 각도 설정 (비동기 버전)"""
    try:
        if not init_feed_servo():
            return False
            
        # 비동기 실행자에서 동기 함수 호출
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _set_angle_sync, angle)
        
        return result
    except Exception as e:
        logger.error(f"❌ 비동기 급식 서보 제어 실패: {e}")
        return False

async def feed_once():
    """한 번의 급식을 실행합니다. (비동기 버전)"""
    try:
        logger.info("🍽 급식 서보모터 동작 시작")
        
        # 비동기로 각도 설정
        await set_angle_async(60)
        await asyncio.sleep(0.3)  # 비동기 대기
        await set_angle_async(120)
        await asyncio.sleep(0.2)  # 비동기 대기
        
        logger.info("✅ 급식 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 급식 실행 실패: {e}")
        return False

async def feed_multiple(count: int):
    """여러 번의 급식을 실행합니다."""
    try:
        logger.info(f"🍽 {count}회 급식 시작")
        
        for i in range(count):
            if i > 0:
                await asyncio.sleep(1)  # 급식 간 대기
            await feed_once()
            
        logger.info(f"✅ {count}회 급식 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 다중 급식 실행 실패: {e}")
        return False

def cleanup():
    """급식 서보모터 리소스 정리"""
    global pwm, _initialized
    
    try:
        if pwm:
            pwm.stop()
            pwm = None
        _initialized = False
        logger.info("🧹 급식 서보모터 정리 완료")
    except Exception as e:
        logger.error(f"⚠️ 급식 서보모터 정리 중 오류: {e}")

# 기존 동기 함수들 (하위 호환성 유지) - 비동기로 래핑
def feed_once_sync():
    """한 번의 급식을 실행합니다. (동기 버전 - 하위 호환성)"""
    print("🍽 서보모터 동작")
    # 동기 함수를 비동기로 래핑하여 실행
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 이미 실행 중인 루프가 있으면 새 태스크 생성
            asyncio.create_task(feed_once())
        else:
            # 루프가 없으면 새로 실행
            loop.run_until_complete(feed_once())
    except Exception as e:
        logger.error(f"❌ 급식 실행 실패: {e}")
        # 폴백: 동기 실행 (최소한의 블로킹)
        set_angle(90)
        import time
        time.sleep(0.1)
        set_angle(120)
        time.sleep(0.1)
