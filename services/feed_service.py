# services/feed_service.py

import RPi.GPIO as GPIO
import time
import asyncio
from datetime import datetime, timedelta
from services.settings_service import settings_service

SERVO_PIN = 18  # 급식용 서보모터 (PIN 12, hardware PWM)
PWM_FREQUENCY = 50

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
pwm.start(0)

def set_angle(angle):
    duty = angle / 18 + 2
    if duty < 2 or duty > 12:
        print(f"⚠️ 듀티사이클 {duty}%는 비정상입니다.")
        return
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

def feed_once():
    """한 번의 급식을 실행합니다."""
    print("🍽 서보모터 동작")
    set_angle(70)
    time.sleep(1)
    set_angle(190)
    time.sleep(0.5)

def feed_multiple(amount: int):
    """지정된 횟수만큼 급식을 실행합니다."""
    print(f"🍽 급식 시작: {amount}회")
    for i in range(amount):
        feed_once()
    print(f"✅ 급식 완료: {amount}회")

def cleanup():
    """GPIO 정리를 수행합니다."""
    pwm.stop()
    GPIO.cleanup()
    print("🧹 GPIO 정리 완료")
