# audio_output_service.py
import pyaudio

p = pyaudio.PyAudio()

# 기본 설정
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True)
# PyAudio 초기화

# 출력 장치 자동 선택 (기본 시스템 출력 사용)
try:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True)  # ✅ output_device_index 생략 = PulseAudio default 사용
    print("✅ 오디오 출력 스트림 열기 성공 (기본 출력 장치 사용)")
except Exception as e:
    print(f"❌ 스피커 열기 실패: {e}")
    stream = None

def play_audio_chunk(chunk: bytes):
    if stream:
        try:
            stream.write(chunk)
        except Exception as e:
            print(f"❌ 오디오 출력 실패: {e}")
    else:
        print("⚠️ stream is None: 출력 스트림이 초기화되지 않았습니다.")

# def close_audio_stream():
#     """
#     스트림 종료 및 자원 해제
#     """
#     if stream:
#         stream.stop_stream()
#         stream.close()
#     p.terminate()
