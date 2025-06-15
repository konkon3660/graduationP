import asyncio
import pyaudio
from services.audio_service import get_audio_streaming
import contextlib
import os
import sys

# 🔇 ALSA / JACK 로그 제거
@contextlib.contextmanager
def suppress_alsa_errors():
    fd = os.open(os.devnull, os.O_WRONLY)
    stderr_fd = sys.stderr.fileno()
    saved_stderr = os.dup(stderr_fd)
    os.dup2(fd, stderr_fd)
    try:
        yield
    finally:
        os.dup2(saved_stderr, fd)
        os.close(fd)
        os.close(saved_stderr)


class MicrophoneSender:
    def __init__(self):
        self.running = False
        self.task = None
        self.clients = set()

    def register(self, websocket):
        self.clients.add(websocket)

    def unregister(self, websocket):
        self.clients.discard(websocket)

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
                return i
        return None

    async def _run(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024

        with suppress_alsa_errors():
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

                while self.running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    await self.broadcast(data)
                    await asyncio.sleep(0.01)

            except Exception as e:
                pass  # 필요 시 로깅 가능
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()

    def start(self):
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._run())

    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
