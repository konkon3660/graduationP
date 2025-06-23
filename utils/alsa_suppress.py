# utils/suppress_alsa.py
# 오디오 재생 시 발생하는 ALSA 오류를 억제하는 유틸리티
import os
import sys
import contextlib

@contextlib.contextmanager
def suppress_alsa_errors():
    fd = os.open(os.devnull, os.O_WRONLY)
    stderr_fd = sys.stderr.fileno()
    saved_stderr = os.dup(stderr_fd)
    os.dup2(fd, stderr_fd)
    try:
        yield
    finally:
        os.dup2(saved_stderr, stderr_fd)
        os.close(fd)
        os.close(saved_stderr)

async def handle_ultrasonic_command(command_data, websocket):
    if (
        command_data.get("type") == "ultrasonic" and command_data.get("action") in ["get_distance", "get_distance_data"]
    ):
        distance_data = get_distance_data()
        if distance_data.get("distance") is not None:
            response_text = f"distance: {distance_data['distance']}"
        else:
            error_msg = distance_data.get("error", "측정 실패")
            response_text = f"error: {error_msg}"
        await websocket.send_text(response_text)
        logger.info(f"📏 초음파 센서 데이터 전송: {response_text}")