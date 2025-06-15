import os
import sys
import pyaudio
import contextlib

# 🔇 ALSA / JACK 경고 로그 제거
@contextlib.contextmanager
def suppress_alsa_errors():
    fd = os.open(os.devnull, os.O_WRONLY)
    stderr_fd = sys.stderr.fileno()
    saved_stderr = os.dup(stderr_fd)
    os.dup2(fd, stderr_fd)
    try:
        yield
    finally:
        os.dup2(saved_stderr, stderr_fd)
        os.close(fd)
        os.close(saved_stderr)

# 🔍 USB 출력 장치 탐색 (우선순위 선택)
def find_output_device(p: pyaudio.PyAudio) -> int:
    print("🔍 출력 장치 자동 탐색 중...")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = info["name"].lower()
        if info["maxOutputChannels"] > 0:
            print(f"  🎧 [{i}] {info['name']} (채널 수: {info['maxOutputChannels']})")
            if "usb" in name or "speaker" in name:
                return i
    print("⚠️ USB 출력 장치를 찾지 못했습니다. 기본 장치 사용")
    return p.get_default_output_device_info()["index"]

# 🔧 설정 값
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024

# 🔌 PyAudio 및 스트림 초기화
p = pyaudio.PyAudio()
stream = None

with suppress_alsa_errors():
    try:
        output_device_index = find_output_device(p)
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        output_device_index=output_device_index)
        print(f"✅ 출력 스트림 열기 성공 (장치 번호: {output_device_index})")
    except Exception as e:
        print(f"❌ 스피커 열기 실패: {e}")
        stream = None

# ▶️ PCM 청크 재생 함수
def play_audio_chunk(chunk: bytes):
    if stream:
        try:
            stream.write(chunk)
        except Exception as e:
            print(f"❌ 오디오 출력 실패: {e}")
    else:
        print("⚠️ 출력 스트림이 없습니다.")

# 🛑 종료 함수
def close_audio_stream():
    if stream:
        stream.stop_stream()
        stream.close()
    p.terminate()
    print("🛑 출력 스트림 종료됨")
