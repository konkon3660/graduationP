# services/microphone_sender_service.py
import asyncio
import websockets
import pyaudio

class MicrophoneSender:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.running = False
        self.task = None

    async def _run(self):
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

        try:
            async with websockets.connect(self.ws_url) as websocket:
                print("🎤 마이크 송출 시작")
                while self.running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    await websocket.send(data)
                    await asyncio.sleep(0.01)
        except Exception as e:
            print(f"[오류] 마이크 송출 실패: {e}")
        finally:
            print("🎤 마이크 송출 종료")
            stream.stop_stream()
            stream.close()
            p.terminate()

    def start(self):
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._run())

    def stop(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
