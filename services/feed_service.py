# services/feed_service.py

import RPi.GPIO as GPIO
import asyncio
import logging
from datetime import datetime, timedelta
from services.settings_service import settings_service
import concurrent.futures
import time

logger = logging.getLogger(__name__)

SERVO_PIN = 18  # 급식용 서보모터 (PIN 12, hardware PWM)
PWM_FREQUENCY = 50

# 전역 변수
pwm = None
_initialized = False
_gpio_initialized = False
feeding_lock = asyncio.Lock()
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

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

async def set_angle(angle):
    """서보모터 각도 설정 (비동기)"""
    try:
        if not init_feed_servo():
            logger.error("❌ 서보모터 초기화 실패")
            return False
        
        if pwm is None:
            logger.error("❌ PWM 객체가 초기화되지 않음")
            return False
        
        duty = angle / 18 + 2
        if duty < 2 or duty > 12:
            logger.warning(f"⚠️ 듀티사이클 {duty}%는 비정상입니다.")
            return False
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(_executor, pwm.ChangeDutyCycle, duty)
        await asyncio.sleep(0.1)
        await loop.run_in_executor(_executor, pwm.ChangeDutyCycle, 0)
        logger.info(f"✅ 급식 서보 각도 설정: {angle}도")
        return True
    except Exception as e:
        logger.error(f"❌ 급식 서보 각도 설정 실패: {e}")
        return False

async def feed_once():
    """급식 한 번 실행 (비동기)"""
    global feeding_lock
    async with feeding_lock:
        try:
            logger.info("🍽 급식 서보모터 동작 시작")
            if not await set_angle(30):
                logger.error("❌ 첫 번째 각도 설정 실패")
                return False
            await asyncio.sleep(0.3)
            if not await set_angle(150):
                logger.error("❌ 두 번째 각도 설정 실패")
                return False
            await asyncio.sleep(0.2)
            logger.info("✅ 급식 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 급식 실행 실패: {e}")
            return False

async def feed_multiple(count: int):
    """여러 번 급식 실행 (비동기)"""
    global feeding_lock
    async with feeding_lock:
        try:
            logger.info(f"🍽 {count}회 급식 시작")
            for i in range(count):
                if i > 0:
                    await asyncio.sleep(0.2)
                success = await feed_once()
                if not success:
                    logger.error(f"❌ {i+1}번째 급식 실패")
                    return False
            logger.info(f"✅ {count}회 급식 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 다중 급식 실행 실패: {e}")
            return False

def cleanup():
    """급식 서보모터 리소스 정리"""
    global pwm, _initialized, _executor
    
    try:
        if pwm:
            pwm.stop()
            pwm = None
        _initialized = False
        _executor.shutdown(wait=False)
        logger.info("🧹 급식 서보모터 정리 완료")
    except Exception as e:
        logger.error(f"⚠️ 급식 서보모터 정리 중 오류: {e}")

def get_feed_status():
    try:
        # TODO: 실제 센서값/잔량 판단 로직으로 교체
        # 예시: feed_level = read_sensor()
        # if feed_level < 임계값:
        #     return {"status": "empty"}
        # else:
        #     return {"status": "ok"}
        return {"status": "ok", "message": "정상"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def feed_once_sync():
    """급식 한 번 실행 (동기 버전)"""
    try:
        if not init_feed_servo():
            logger.error("❌ 서보모터 초기화 실패")
            return False
            
        # 30도로 이동
        duty = 30 / 18 + 2
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)
        pwm.ChangeDutyCycle(0)
        
        # 150도로 이동
        duty = 150 / 18 + 2
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.2)
        pwm.ChangeDutyCycle(0)
        
        logger.info("✅ 급식 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 급식 실행 실패: {e}")
        return False
