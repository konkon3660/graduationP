import RPi.GPIO as GPIO
import time

# 모터 A (오른쪽 모터)
ENA = 25
INT1 = 23
INT2 = 24

# 모터 B (왼쪽 모터)
ENB = 22
INT3 = 17
INT4 = 18

# 초기 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([ENA, INT1, INT2, ENB, INT3, INT4], GPIO.OUT)

# PWM 설정
pwmA = GPIO.PWM(ENA, 8000)  # 오른쪽
pwmB = GPIO.PWM(ENB, 8000)  # 왼쪽
pwmA.start(0)
pwmB.start(0)

def set_right_motor(speed: int, direction: int):
    """
    오른쪽 모터 제어
    speed: 0~100
    direction: 0 (정방향), 1 (역방향)
    """
    if direction == 0:
        GPIO.output(INT1, GPIO.HIGH)
        GPIO.output(INT2, GPIO.LOW)
    elif direction == 1:
        GPIO.output(INT1, GPIO.LOW)
        GPIO.output(INT2, GPIO.HIGH)
    else:
        GPIO.output(INT1, GPIO.LOW)
        GPIO.output(INT2, GPIO.LOW)

    pwmA.ChangeDutyCycle(speed)

def set_left_motor(speed: int, direction: int):
    """
    왼쪽 모터 제어
    speed: 0~100
    direction: 0 (정방향), 1 (역방향)
    """
    if direction == 0:
        GPIO.output(INT3, GPIO.HIGH)
        GPIO.output(INT4, GPIO.LOW)
    elif direction == 1:
        GPIO.output(INT3, GPIO.LOW)
        GPIO.output(INT4, GPIO.HIGH)
    else:
        GPIO.output(INT3, GPIO.LOW)
        GPIO.output(INT4, GPIO.LOW)

    pwmB.ChangeDutyCycle(speed)

def stop_motors():
    """양쪽 모터 정지"""

    GPIO.output(INT1, GPIO.LOW)
    GPIO.output(INT2, GPIO.LOW)
    GPIO.output(INT3, GPIO.LOW)
    GPIO.output(INT4, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

def cleanup():
    """모터 종료 및 GPIO 정리"""
    stop_motors()
    pwmA.stop()
    pwmB.stop()
    GPIO.cleanup()

set_left_motor(80,0)
set_right_motor(80,0)
time.sleep(2)
stop_motors()
cleanup()