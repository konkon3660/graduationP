import pyaudio

p = pyaudio.PyAudio()
print("🎙️ 사용 가능한 입력 장치:")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        print(f"  [{i}] {info['name']}")

# 강제로 열기 시도 (올바른 장치 번호로!)
index = 1  # 예시
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=index,
                frames_per_buffer=2048)
print("✅ 마이크 열기 성공")
