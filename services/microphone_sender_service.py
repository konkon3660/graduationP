import asyncio
import pyaudio
import os
import sys
import contextlib
from services.audio_service import get_audio_streaming

# 🔇 ALSA 경고 로그 억제
@contextlib.contextmanager
def suppress_alsa_stderr():
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

class MicrophoneSender:
    def __init__(self):
        self.running = False
        self.task = None
        self.clients = set()

    def register(self, websocket):
        self.clients.add(websocket)
        print(f"✅ 클라이언트 등록됨 (총 {len(self.clients)}명)")

    def unregister(self, websocket):
        self.clients.discard(websocket)
        print(f"❎ 클라이언트 해제됨 (총 {len(self.clients)}명)")

    async def broadcast(self, data: bytes):
        if not get_audio_streaming():
            return
        disconnected = []
        for ws in self.clients:
            try:
                await ws.send_bytes(data)
            except:
                disconnected.append(ws)
        for ws in disconnected:
            self.clients.discard(ws)

    def find_input_device(self, p):
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                print(f"🎙️ 선택된 마이크: [{i}] {info['name']}")
                return i
        print("❌ 사용 가능한 마이크 장치 없음")
        return None

    async def _run(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024

        with suppress_alsa_stderr():
            p = pyaudio.PyAudio()
            index = self.find_input_device(p)
            if index is None:
                return

            try:
                stream = p.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                input_device_index=index,
                                frames_per_buffer=CHUNK)
                print("🎤 서버 마이크 송출 시작")

                while self.running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    await self.broadcast(data)
                    await asyncio.sleep(0.005)

            except Exception as e:
                print(f"⚠️ 마이크 송출 중 오류 발생: {e}")

            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
                print("🛑 마이크 송출 종료")

    def start(self):
        if not self.running:
            print("🚀 마이크 송출 태스크 시작")
            self.running = True
            self.task = asyncio.create_task(self._run())

    def stop(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
                print("🛑 마이크 송출 태스크 취소됨")
