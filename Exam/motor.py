import RPi.GPIO as GPIO
import time

# GPIO 핀 설정
motorA_IN1 = 17
motorA_IN2 = 18
motorA_EN = 22

motorB_IN3 = 23
motorB_IN4 = 24
motorB_EN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(motorA_IN1, GPIO.OUT)
GPIO.setup(motorA_IN2, GPIO.OUT)
GPIO.setup(motorA_EN, GPIO.OUT)

GPIO.setup(motorB_IN3, GPIO.OUT)
GPIO.setup(motorB_IN4, GPIO.OUT)
GPIO.setup(motorB_EN, GPIO.OUT)

# PWM 생성
pwmA = GPIO.PWM(motorA_EN, 8000)
pwmB = GPIO.PWM(motorB_EN, 8000)
pwmA.start(0)
pwmB.start(0)

def motorA_forward(speed=100):
    GPIO.output(motorA_IN1, GPIO.HIGH)
    GPIO.output(motorA_IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(speed)

def motorA_backward(speed=100):
    GPIO.output(motorA_IN1, GPIO.LOW)
    GPIO.output(motorA_IN2, GPIO.HIGH)
    pwmA.ChangeDutyCycle(speed)

def motorB_forward(speed=100):
    GPIO.output(motorB_IN3, GPIO.HIGH)
    GPIO.output(motorB_IN4, GPIO.LOW)
    pwmB.ChangeDutyCycle(speed)

def motorB_backward(speed=100):
    GPIO.output(motorB_IN3, GPIO.LOW)
    GPIO.output(motorB_IN4, GPIO.HIGH)
    pwmB.ChangeDutyCycle(speed)

def stop_all():
    GPIO.output(motorA_IN1, GPIO.LOW)
    GPIO.output(motorA_IN2, GPIO.LOW)
    GPIO.output(motorB_IN3, GPIO.LOW)
    GPIO.output(motorB_IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

try:
    print("양쪽 모터 정방향")
    motorA_forward(80)
    motorB_forward(80)
    time.sleep(2)

    print("역방향")
    motorA_backward(80)
    motorB_backward(80)
    time.sleep(2)

    stop_all()

finally:
    pwmA.stop()
    pwmB.stop()
    GPIO.cleanup()
