# services/motor_service.py - DC 모터 제어 서비스 (개선된 버전)
import RPi.GPIO as GPIO
import logging
import time
import cv2
import threading

logger = logging.getLogger(__name__)

# 핀 번호 정의 (하드웨어 구성표에 맞게 수정)
INT1, INT2 = 23, 24  # 우측 모터 (IN1=PIN16, IN2=PIN18)
INT3, INT4 = 27, 22  # 좌측 모터 (IN3=PIN13, IN4=PIN15)

_initialized = False

# 기본 설정
DEFAULT_SPEED = 100  # 항상 100%로 동작


def init_motor():
    """모터 핀 설정 (최초 1회만 호출)"""    
    global _initialized
    if _initialized:
        return True
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # 핀 설정
        motor_pins = [INT1, INT2, INT3, INT4]
        GPIO.setup(motor_pins, GPIO.OUT)
        _initialized = True
        logger.info("✅ DC 모터 초기화 완료")
        return True
    except Exception as e:
        logger.error(f"❌ DC 모터 초기화 실패: {e}")
        return False

def set_right_motor(speed: int, direction: int):
    """
    우측 모터 제어 (speed 인자는 무시)
    Args:
        speed: (무시됨)
        direction: 회전 방향 (0=전진, 1=후진)
    """
    if not init_motor():
        return False
    try:
        GPIO.output(INT1, GPIO.HIGH if direction == 0 else GPIO.LOW)
        GPIO.output(INT2, GPIO.LOW if direction == 0 else GPIO.HIGH)
        logger.debug(f"우측 모터: 방향={'전진' if direction == 0 else '후진'}")
        return True
    except Exception as e:
        logger.error(f"❌ 우측 모터 제어 실패: {e}")
        return False

def set_left_motor(speed: int, direction: int):
    """
    좌측 모터 제어 (speed 인자는 무시)
    Args:
        speed: (무시됨)
        direction: 회전 방향 (0=전진, 1=후진)
    """
    if not init_motor():
        return False
    try:
        GPIO.output(INT3, GPIO.HIGH if direction == 0 else GPIO.LOW)
        GPIO.output(INT4, GPIO.LOW if direction == 0 else GPIO.HIGH)
        logger.debug(f"좌측 모터: 방향={'전진' if direction == 0 else '후진'}")
        return True
    except Exception as e:
        logger.error(f"❌ 좌측 모터 제어 실패: {e}")
        return False

def move_forward(speed: int = DEFAULT_SPEED):
    """전진 (speed 인자 무시)"""
    logger.info(f"🚗 전진")
    return set_right_motor(DEFAULT_SPEED, 0) and set_left_motor(DEFAULT_SPEED, 0)

def move_backward(speed: int = DEFAULT_SPEED):
    """후진 (speed 인자 무시)"""
    logger.info(f"🔄 후진")
    return set_right_motor(DEFAULT_SPEED, 1) and set_left_motor(DEFAULT_SPEED, 1)

def turn_left(speed: int = DEFAULT_SPEED):
    """좌회전 (speed 인자 무시)"""
    logger.info(f"⬅️ 좌회전")
    return set_right_motor(DEFAULT_SPEED, 0) and set_left_motor(DEFAULT_SPEED, 1)

def turn_right(speed: int = DEFAULT_SPEED):
    """우회전 (speed 인자 무시)"""
    logger.info(f"➡️ 우회전")
    return set_right_motor(DEFAULT_SPEED, 1) and set_left_motor(DEFAULT_SPEED, 0)

def stop_motors():
    """모터 정지"""
    if not init_motor():
        return False
    try:
        # 모든 제어 핀을 LOW로
        GPIO.output(INT1, GPIO.LOW)
        GPIO.output(INT2, GPIO.LOW)
        GPIO.output(INT3, GPIO.LOW)
        GPIO.output(INT4, GPIO.LOW)
        logger.info("🛑 모터 정지")
        return True
    except Exception as e:
        logger.error(f"❌ 모터 정지 실패: {e}")
        return False

def get_motor_status():
    """모터 상태 조회"""
    return {
        "initialized": _initialized,
        "pins": {
            "right_motor": {"control": [INT1, INT2]},
            "left_motor": {"control": [INT3, INT4]}
        }
    }

def cleanup():
    """모터 리소스 정리"""
    global _initialized
    try:
        if _initialized:
            stop_motors()
        GPIO.cleanup()
        _initialized = False
        logger.info("🧹 DC 모터 정리 완료")
    except Exception as e:
        logger.error(f"⚠️ DC 모터 정리 중 오류: {e}")

import atexit
atexit.register(cleanup)

def camera_capture_thread():
    global cap, latest_frame, capture_thread_running
    logger.info("📹 카메라 캡처 스레드 시작")
    frame_time = 1.0 / 30  # 30fps
    while capture_thread_running:
        if cap is None:
            break
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            continue
        with lock:
            latest_frame = frame
        # 정확한 프레임 타이밍 계산
        elapsed = time.time() - start_time
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)

def feed_once_sync():
    """급식 한 번 실행 (동기 버전)"""
    try:
        if not init_feed_servo():
            logger.error("❌ 서보모터 초기화 실패")
            return False
            
        # 30도로 이동 (더 짧은 대기 시간)
        duty = 30 / 18 + 2
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.2)  # 0.3 -> 0.2
        pwm.ChangeDutyCycle(0)
        
        # 150도로 이동 (더 짧은 대기 시간)
        duty = 150 / 18 + 2
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.15)  # 0.2 -> 0.15
        pwm.ChangeDutyCycle(0)
        
        logger.info("✅ 급식 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 급식 실행 실패: {e}")
        return False

def start_capture(width=320, height=240, fps=15):
    global cap, capture_thread, capture_thread_running, active_connections

    # 이전 자원 정리
    _force_release_camera()

    active_connections += 1
    logger.info(f"📹 카메라 연결 요청 (활성 연결: {active_connections})")

    if capture_thread_running and capture_thread and capture_thread.is_alive():
        logger.info("📹 이미 스트리밍 중 - 기존 자원 사용")
        return

    cap = wait_for_camera_ready("/dev/video0")
    if not cap:
        logger.error("❌ 카메라 열기 실패")
        return

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 버퍼 크기 최소화

    capture_thread_running = True
    capture_thread = threading.Thread(target=camera_capture_thread, daemon=True)
    capture_thread.start()
    logger.info(f"📹 카메라 스트리밍 시작 ({width}x{height} @{fps}fps)")