import pyaudio

# 기본 설정 값 정의
FORMAT = pyaudio.paInt16
CHANNELS = 1
CHUNK = 1024

# PyAudio 초기화
p = pyaudio.PyAudio()

# 🔍 자동 샘플레이트 탐색 함수
def find_supported_rate(device_index=0):
    for rate in [48000, 44100, 32000, 22050, 16000]:
        try:
            if p.is_format_supported(rate,
                output_device=device_index,
                output_channels=CHANNELS,
                output_format=FORMAT):
                print(f"✅ 지원되는 샘플레이트: {rate}")
                return rate
        except ValueError:
            continue
    raise RuntimeError("❌ 지원 가능한 샘플레이트를 찾을 수 없습니다.")

# 실제 사용 샘플레이트 결정
RATE = find_supported_rate()

# 출력 스트림 생성
try:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True)
    print("✅ 오디오 출력 스트림 열기 성공")
except Exception as e:
    print(f"❌ 스피커 열기 실패: {e}")
    stream = None

# 오디오 청크 재생 함수
def play_audio_chunk(chunk: bytes):
    if stream:
        try:
            stream.write(chunk)
        except Exception as e:
            print(f"❌ 오디오 출력 실패: {e}")
    else:
        print("⚠️ stream is None: 출력 스트림이 초기화되지 않았습니다.")

# 종료 함수
def close_audio_stream():
    if stream:
        stream.stop_stream()
        stream.close()
    p.terminate()
