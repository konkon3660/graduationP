import RPi.GPIO as GPIO
import time
import requests
import schedule

# --- 설정 값 ---
SERVER_URL = "https://your-server.com/api/servo_settings"  # 서버 API URL
SERVO_PIN = 18  # 서브모터 제어 핀 (BCM 번호)
PWM_FREQUENCY = 50  # PWM 주파수 (Hz)

# --- 초기화 ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
pwm.start(0)  # PWM 시작 (듀티 사이클 0으로 초기화)

# --- 함수 정의 ---

def get_servo_settings():
    """서버에서 시간 간격 및 동작 횟수 설정 값을 가져옵니다."""
    try:
        response = requests.get(SERVER_URL)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        data = response.json()
        interval = data.get("interval")
        repetitions = data.get("repetitions")

        if interval is None or repetitions is None:
            print("경고: 서버에서 interval 또는 repetitions 값을 찾을 수 없습니다.")
            return None, None

        return int(interval), int(repetitions)  # 시간 간격, 총 동작 횟수 반환 (정수 변환)
    except requests.exceptions.RequestException as e:
        print(f"오류: 서버에서 데이터를 가져오는 중 오류 발생: {e}")
        return None, None
    except ValueError as e:
        print(f"오류: 서버에서 받은 데이터를 정수로 변환하는 중 오류 발생: {e}")
        return None, None
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return None, None

def set_angle(angle):
    """서브모터의 각도를 설정합니다."""
    # 서브모터마다 듀티 사이클 범위가 다를 수 있습니다. 테스트 후 조정하세요.
    duty = angle / 18 + 2  # 각도를 듀티 사이클로 변환 (일반적인 서보모터)

    # 듀티사이클 값 검사
    if duty < 2 or duty > 12: # 통상적인 듀티사이클 범위 2~12%
        print(f"경고: 듀티 사이클 {duty}는 범위를 벗어났습니다. 서브모터가 손상될 수 있습니다.")
        return

    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # 모터가 움직일 시간 확보
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0) # 듀티사이클 0으로 변경해서 서보모터 멈추게 함.

def operate_servo():
    """서브모터를 동작시키는 함수."""
    global current_count, interval, repetitions
    if interval is None or repetitions is None:
        print("오류: 서버에서 설정 값을 가져오지 못했습니다. 동작을 건너뜁니다.")
        return

    if current_count < repetitions:
        print(f"동작 {current_count + 1}/{repetitions} 시작")
        try:
            set_angle(90)  # 예시: 90도로 회전
            time.sleep(1)
            set_angle(0)   # 예시: 0도로 회전
            time.sleep(0.5) # 모터 멈추는 시간 확보
        except Exception as e:
            print(f"오류: 서브모터 제어 중 오류 발생: {e}")

        current_count += 1
        print(f"동작 {current_count}/{repetitions} 완료")
    else:
        print("모든 동작 완료. 스케줄 중단.")
        schedule.clear()  # 스케줄 중단

def cleanup():
    """GPIO 자원을 해제합니다."""
    pwm.stop()
    GPIO.cleanup()
    print("정리 완료.")

# --- 메인 루프 ---
if __name__ == "__main__":
    current_count = 0  # 현재 동작 횟수 초기화
    interval, repetitions = get_servo_settings()  # 서버에서 설정값 가져오기

    if interval is not None and repetitions is not None:
        print(f"서버 설정: 시간 간격 = {interval}시간, 총 동작 횟수 = {repetitions}회")
        schedule.every(interval).hours.do(operate_servo) # 스케줄 설정
    else:
        print("오류: 서버에서 설정 값을 가져오지 못했습니다. 스케줄을 시작할 수 없습니다.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # 1초마다 스케줄 확인
    except KeyboardInterrupt:
        print("프로그램 종료 요청 감지.")
    finally:
        cleanup()  # 종료 시 정리 작업 실행