import pyaudio

p = pyaudio.PyAudio()

def find_output_device(keyword="UAC"):
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if keyword.lower() in info["name"].lower() and info["maxOutputChannels"] > 0:
            print(f"🔊 선택된 스피커: {info['name']} (index={i})")
            return i
    print("❗ 지정된 키워드를 가진 출력 장치를 찾지 못했습니다.")
    return None

device_index = find_output_device()

try:
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True,
                    output_device_index=device_index if device_index is not None else None)
except Exception as e:
    print(f"❌ 스피커 열기 실패: {e}")
    stream = None

def play_audio_chunk(chunk: bytes):
    """
    PCM 오디오 데이터를 실시간으로 스피커로 출력합니다.
    """
    if stream:
        stream.write(chunk)

def close_audio_stream():
    if stream:
        stream.stop_stream()
        stream.close()
    p.terminate()
