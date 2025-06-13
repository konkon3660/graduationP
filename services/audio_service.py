is_audio_streaming = False

def set_audio_streaming(flag: bool):
    global is_audio_streaming
    is_audio_streaming = flag
    print(f"[AUDIO] 수신 상태 변경: {flag}")

def get_audio_streaming() -> bool:
    return is_audio_streaming