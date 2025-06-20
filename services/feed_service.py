# services/feed_service.py

import RPi.GPIO as GPIO
import time
import asyncio
from datetime import datetime, timedelta
from services.feed_setting import feed_config

SERVO_PIN = 18  # 급식용 서보모터 (PIN 12, hardware PWM)
PWM_FREQUENCY = 50

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
pwm.start(0)

next_feed_time = None
current_count = 0

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
    print("🍽 서보모터 동작")
    set_angle(90)
    time.sleep(1)
    set_angle(0)
    time.sleep(0.5)

async def auto_feed_loop():
    global next_feed_time, current_count

    print("🔁 자동 급식 루프 시작됨")
    while True:
        await asyncio.sleep(5)

        if feed_config["mode"] != "auto":
            continue

        interval = int(feed_config.get("interval", 60))
        amount = int(feed_config.get("amount", 1))

        if next_feed_time is None:
            next_feed_time = datetime.now() + timedelta(minutes=interval)
            current_count = 0
            print(f"⏳ 다음 급식 예정: {next_feed_time.strftime('%H:%M:%S')}")
            continue

        now = datetime.now()
        if now >= next_feed_time:
            print(f"✅ 급식 시간 도달: {now.strftime('%H:%M:%S')}")
            for _ in range(amount):
                feed_once()
            next_feed_time = now + timedelta(minutes=interval)
            print(f"📆 다음 급식 시간: {next_feed_time.strftime('%H:%M:%S')}")

def cleanup():
    pwm.stop()
    GPIO.cleanup()
    print("🧹 GPIO 정리 완료")
