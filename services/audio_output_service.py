# audio_output_service.py
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000  # 클라이언트와 맞춰야 함
CHUNK = 1024

p = pyaudio.PyAudio()
stream = None

def init_audio_stream():
    global stream
    try:
        output_index = None
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"[{i}] {info['name']} / 출력 채널: {info['maxOutputChannels']}")
            if info.get('maxOutputChannels', 0) > 0 and 'USB' in info['name']:
                output_index = i
                print(f"🎧 선택된 출력 장치: [{i}] {info['name']}")
                break

        if output_index is None:
            raise RuntimeError("❌ 출력 장치를 찾을 수 없습니다.")

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        output_device_index=output_index)
        print("✅ 오디오 출력 스트림 열기 성공")
    except Exception as e:
        print(f"❌ 출력 스트림 초기화 실패: {e}")
        stream = None


def play_audio_chunk(chunk: bytes):
    if stream:
        try:
            stream.write(chunk)
        except Exception as e:
            print(f"❌ 오디오 출력 실패: {e}")
    else:
        print("⚠️ stream is None: 출력 스트림이 초기화되지 않았습니다.")
