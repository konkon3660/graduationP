import pyaudio

# 기본 설정 값 정의
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024

# PyAudio 초기화
p = pyaudio.PyAudio()

# 출력 스트림 생성 (기본 출력 장치 사용)
try:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True)  # ✅ output_device_index 생략 → default
    print("✅ 오디오 출력 스트림 열기 성공 (기본 출력 장치 사용)")
except Exception as e:
    print(f"❌ 스피커 열기 실패: {e}")
    stream = None

# PCM 청크 재생 함수
def play_audio_chunk(chunk: bytes):
    if stream:
        try:
            stream.write(chunk)
        except Exception as e:
            print(f"❌ 오디오 출력 실패: {e}")
    else:
        print("⚠️ stream is None: 출력 스트림이 초기화되지 않았습니다.")

# 종료 함수 (필요 시 사용 가능)
def close_audio_stream():
    if stream:
        stream.stop_stream()
        stream.close()
    p.terminate()
