import pyaudio

# PyAudio 초기화
p = pyaudio.PyAudio()

# 오디오 출력 스트림 생성 (16bit, 16000Hz, 모노)
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True)

def play_audio_chunk(chunk: bytes):
    """
    PCM 오디오 데이터를 실시간으로 스피커로 출력합니다.
    """
    stream.write(chunk)

def close_audio_stream():
    stream.stop_stream()
    stream.close()
    p.terminate()