import RPi.GPIO as GPIO
import time

RELAY_PIN = 17  # GPIO17

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

try:
    GPIO.output(RELAY_PIN, GPIO.LOW)  # ������ ON �� �ַ����̵� �۵�
    time.sleep(1)
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # ������ OFF �� �ַ����̵� ����
finally:
    GPIO.cleanup()
