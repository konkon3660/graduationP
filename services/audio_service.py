# services/audio_service.py

is_audio_streaming = False

def start_audio_stream():
    global is_audio_streaming
    if not is_audio_streaming:
        is_audio_streaming = True
        print("[AUDIO] 클라이언트로 음성 전송 시작")
        # 예: subprocess로 ffmpeg 또는 PyAudio 전송 시작

def stop_audio_stream():
    global is_audio_streaming
    if is_audio_streaming:
        is_audio_streaming = False
        print("[AUDIO] 클라이언트로 음성 전송 중지")
        # 예: subprocess 종료 또는 플래그 비활성화
