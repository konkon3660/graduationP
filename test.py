import time
from audio_output_service import init_audio_stream, play_audio_chunk

PCM_FILE = "received_audio_20250614_193443.pcm"  # 실제 파일명으로 수정

def play_pcm_file():
    init_audio_stream()

    try:
        with open(PCM_FILE, "rb") as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                play_audio_chunk(chunk)
                time.sleep(1024 / (16000 * 2))  # 1024 byte / (샘플레이트 * 바이트수)
    except Exception as e:
        print(f"❌ PCM 파일 재생 오류: {e}")

if __name__ == "__main__":
    play_pcm_file()