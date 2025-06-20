import RPi.GPIO as GPIO

LASER_PIN = 17  # 레이저 포인터 (PIN 11)

def laser_on():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LASER_PIN, GPIO.OUT)
    GPIO.output(LASER_PIN, GPIO.HIGH)

def laser_off():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LASER_PIN, GPIO.OUT)
    GPIO.output(LASER_PIN, GPIO.LOW)

laser_off()