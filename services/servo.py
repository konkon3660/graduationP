import RPi.GPIO as GPIO
import time

# 서보모터 제어 핀 번호 (BCM 기준)
SERVO_PIN = 21

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM 객체 생성 (50Hz: 서보모터에 적합한 주기)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# 각도를 PWM 듀티사이클로 변환하는 함수
def set_servo_angle(angle):
    duty = 2 + (angle / 18)  # 보통 0도=2.5%, 180도=12.5%
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # 움직일 시간 대기
    pwm.ChangeDutyCycle(0)  # 떨림 방지

try:
    while True:
        angle = int(input("각도 입력 (0~180): "))
        if 0 <= angle <= 180:
            set_servo_angle(angle)
        else:
            print("0~180 사이의 값을 입력해주세요.")
except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()
