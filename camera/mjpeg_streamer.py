from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
import cv2
import threading
import time

app = FastAPI()

# 전역 변수
cap = None
latest_frame = None
lock = threading.Lock()
capture_thread = None
capture_thread_running = False

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
    while capture_thread_running:
        if cap is None:
            break
        ret, frame = cap.read()
        if not ret:
            continue
        with lock:
            latest_frame = frame
        time.sleep(1 / 30)  # 30fps 제한

# --------------------------------------------------------
def start_capture():
    global cap, capture_thread, capture_thread_running

    if capture_thread_running and capture_thread and capture_thread.is_alive():
        print("이미 스트리밍 중 - 기존 자원 사용")
        return

    stop_capture()  # 혹시 남아있는 이전 자원 정리

    cap = wait_for_camera_ready("/dev/video0")
    if not cap:
        print("카메라 열기 실패")
        return

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 15)

    capture_thread_running = True
    capture_thread = threading.Thread(target=camera_capture_thread, daemon=True)
    capture_thread.start()
    print("카메라 스트리밍 시작")

# --------------------------------------------------------
def stop_capture():
    global cap, capture_thread_running, capture_thread
    capture_thread_running = False

    if capture_thread and capture_thread.is_alive():
        capture_thread.join(timeout=2)
    capture_thread = None

    if cap:
        cap.release()
        cap = None
        print("카메라 자원 정리 완료")

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
        print(f"[예외 발생] {e}")

    finally:
        print("클라이언트 종료 또는 예외: stop_capture() 호출")
        stop_capture()

# --------------------------------------------------------
@app.get("/mjpeg")
def mjpeg_stream(background_tasks: BackgroundTasks):
    # 클라이언트 연결 종료 시 stop_capture() 실행
    background_tasks.add_task(stop_capture)
    return StreamingResponse(generate_mjpeg(), media_type="multipart/x-mixed-replace; boundary=frame")
