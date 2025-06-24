import RPi.GPIO as GPIO
import time

# GPIO 핀 설정
motorA_IN1 = 17
motorA_IN2 = 18
motorB_IN3 = 23
motorB_IN4 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(motorA_IN1, GPIO.OUT)
GPIO.setup(motorA_IN2, GPIO.OUT)
GPIO.setup(motorB_IN3, GPIO.OUT)
GPIO.setup(motorB_IN4, GPIO.OUT)

def motorA_forward():
    GPIO.output(motorA_IN1, GPIO.HIGH)
    GPIO.output(motorA_IN2, GPIO.LOW)

def motorA_backward():
    GPIO.output(motorA_IN1, GPIO.LOW)
    GPIO.output(motorA_IN2, GPIO.HIGH)

def motorB_forward():
    GPIO.output(motorB_IN3, GPIO.HIGH)
    GPIO.output(motorB_IN4, GPIO.LOW)

def motorB_backward():
    GPIO.output(motorB_IN3, GPIO.LOW)
    GPIO.output(motorB_IN4, GPIO.HIGH)

def stop_all():
    GPIO.output(motorA_IN1, GPIO.LOW)
    GPIO.output(motorA_IN2, GPIO.LOW)
    GPIO.output(motorB_IN3, GPIO.LOW)
    GPIO.output(motorB_IN4, GPIO.LOW)

try:
    print("양쪽 모터 정방향")
    motorA_forward()
    motorB_forward()
    time.sleep(2)

    print("역방향")
    motorA_backward()
    motorB_backward()
    time.sleep(2)

    stop_all()

finally:
    GPIO.cleanup()
