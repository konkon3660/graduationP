# audio_output_service.py
import pyaudio

p = pyaudio.PyAudio()
stream = None

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # 클라이언트와 동일하게 맞추는 것이 중요함

def init_audio_stream():
    global stream
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True)
        print("✅ 오디오 출력 스트림 열기 성공 (기본 출력 장치 사용)")
    except Exception as e:
        print(f"❌ 출력 스트림 초기화 실패: {e}")
        stream = None

def play_audio_chunk(chunk: bytes):
    """
    PCM 오디오 데이터를 실시간으로 스피커로 출력합니다.
    """
    if stream:
        stream.write(chunk)
    else:
        print("⚠️ stream is None: 오디오 출력 스트림이 초기화되지 않았습니다.")

def close_audio_stream():
    if stream:
        stream.stop_stream()
        stream.close()
    p.terminate()
