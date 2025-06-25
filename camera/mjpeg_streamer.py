from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
import cv2
import threading
import time
import logging

logger = logging.getLogger(__name__)

# 전역 변수
cap = None
latest_frame = None
lock = threading.Lock()
capture_thread = None
capture_thread_running = False
active_connections = 0  # 활성 연결 수 추적

# --------------------------------------------------------
def wait_for_camera_ready(device="/dev/video0", timeout=3):
    start = time.time()
    while time.time() - start < timeout:
        temp_cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
        if temp_cap.isOpened():
            return temp_cap
        time.sleep(0.1)
    return None

# --------------------------------------------------------
def camera_capture_thread():
    global cap, latest_frame, capture_thread_running
    logger.info("📹 카메라 캡처 스레드 시작")
    while capture_thread_running:
        if cap is None:
            break
        ret, frame = cap.read()
        if not ret:
            continue
        with lock:
            latest_frame = frame
        time.sleep(1 / 30)  # 30fps 제한
    logger.info("📹 카메라 캡처 스레드 종료")

# --------------------------------------------------------
def _force_release_camera():
    global cap, capture_thread_running, capture_thread
    capture_thread_running = False
    if capture_thread and capture_thread.is_alive():
        capture_thread.join(timeout=2)
        if capture_thread.is_alive():
            logging.warning("⚠️ 카메라 스레드 강제 종료")
    capture_thread = None
    if cap:
        cap.release()
        cap = None
        logging.info("📹 (내부) 카메라 자원 강제 정리 완료")

# --------------------------------------------------------
def start_capture():
    global cap, capture_thread, capture_thread_running, active_connections

    # 이전 자원 정리 (active_connections는 건드리지 않음)
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
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 15)

    capture_thread_running = True
    capture_thread = threading.Thread(target=camera_capture_thread, daemon=True)
    capture_thread.start()
    logger.info("📹 카메라 스트리밍 시작")

# --------------------------------------------------------
def stop_capture():
    global cap, capture_thread_running, capture_thread, active_connections
    
    active_connections -= 1
    if active_connections < 0:
        logging.warning(f"⚠️ active_connections가 0 미만! 강제로 0으로 보정")
        active_connections = 0
    logging.info(f"📹 카메라 연결 해제 요청 (활성 연결: {active_connections})")
    
    # 활성 연결이 있으면 카메라를 끄지 않음
    if active_connections > 0:
        logging.info(f"📹 다른 클라이언트가 연결되어 있어 카메라 유지 (활성 연결: {active_connections})")
        return
    
    logging.info("📹 모든 클라이언트 연결 해제됨 - 카메라 자원 정리 시작")
    capture_thread_running = False

    if capture_thread and capture_thread.is_alive():
        capture_thread.join(timeout=2)
        if capture_thread.is_alive():
            logging.warning("⚠️ 카메라 스레드 강제 종료")
    capture_thread = None

    if cap:
        cap.release()
        cap = None
        logging.info("📹 카메라 자원 정리 완료")

# --------------------------------------------------------
def generate_mjpeg():
    start_capture()

    try:
        while True:
            with lock:
                frame = latest_frame.copy() if latest_frame is not None else None

            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame)
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
                )
            time.sleep(1 / 30)

    except Exception as e:
        logger.error(f"❌ MJPEG 생성 중 예외 발생: {e}")

    finally:
        logger.info("📹 클라이언트 연결 종료 - stop_capture() 호출")
        stop_capture()
