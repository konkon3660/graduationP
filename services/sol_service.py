import RPi.GPIO as GPIO
import time

RELAY_PIN = 5

def fire():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    try:
        GPIO.output(RELAY_PIN, GPIO.LOW)  
        time.sleep(0.3)
        GPIO.output(RELAY_PIN, GPIO.HIGH)  
    finally:
        GPIO.cleanup()
