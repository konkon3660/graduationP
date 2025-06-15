# motor_service.py
import RPi.GPIO as GPIO

# 핀 번호
ENA, INT1, INT2 = 25, 23, 24
ENB, INT3, INT4 = 22, 17, 18

# PWM 객체 초기화 전용 전역 변수
pwmA = None
pwmB = None
_initialized = False

def init_motor():
    """모터 핀 및 PWM 설정 (최초 1회만 호출)"""
    global pwmA, pwmB, _initialized
    if _initialized:
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup([ENA, INT1, INT2, ENB, INT3, INT4], GPIO.OUT)

    pwmA = GPIO.PWM(ENA, 8000)
    pwmB = GPIO.PWM(ENB, 8000)
    pwmA.start(0)
    pwmB.start(0)

    _initialized = True
    print("✅ 모터 초기화 완료")

def set_right_motor(speed: int, direction: int):
    init_motor()
    GPIO.output(INT1, GPIO.HIGH if direction == 0 else GPIO.LOW)
    GPIO.output(INT2, GPIO.LOW if direction == 0 else GPIO.HIGH)
    pwmA.ChangeDutyCycle(speed)

def set_left_motor(speed: int, direction: int):
    init_motor()
    GPIO.output(INT3, GPIO.HIGH if direction == 0 else GPIO.LOW)
    GPIO.output(INT4, GPIO.LOW if direction == 0 else GPIO.HIGH)
    pwmB.ChangeDutyCycle(speed)

def stop_motors():
    init_motor()
    GPIO.output(INT1, GPIO.LOW)
    GPIO.output(INT2, GPIO.LOW)
    GPIO.output(INT3, GPIO.LOW)
    GPIO.output(INT4, GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

def cleanup():
    global _initialized
    stop_motors()
    pwmA.stop()
    pwmB.stop()
    GPIO.cleanup()
    _initialized = False
    print("🧼 GPIO 정리 완료")
