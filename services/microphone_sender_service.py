import asyncio
import websockets
import pyaudio

# 오디오 입력 설정
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

async def send_microphone_audio(ws_url: str):
    async with websockets.connect(ws_url) as websocket:
        print("🎤 마이크 전송 시작")
        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                await websocket.send(data)
        except Exception as e:
            print(f"마이크 송신 중 오류 발생: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    ws_address = "ws://localhost:8000/ws/audio"  # 서버 주소에 맞게 수정
    asyncio.run(send_microphone_audio(ws_address))
