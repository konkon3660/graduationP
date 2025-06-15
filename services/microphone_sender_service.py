# microphone_sender_service.py
import asyncio
import pyaudio
from services.audio_service import get_audio_streaming  # 🔑 import

class MicrophoneSender:
    def __init__(self, keyword="Brio"):
        self.keyword = keyword
        self.running = False
        self.task = None
        self.connected_clients = set()

    def register(self, websocket):
        self.connected_clients.add(websocket)
        print(f"✅ 클라이언트 등록됨 (총 {len(self.connected_clients)}명)")

    def unregister(self, websocket):
        self.connected_clients.discard(websocket)
        print(f"❎ 클라이언트 해제됨 (총 {len(self.connected_clients)}명)")

    async def broadcast(self, data: bytes):
        disconnected = []
        if not get_audio_streaming():  # 🔍 조건 추가
            return
        for ws in self.connected_clients:
            try:
                await ws.send_bytes(data)
            except Exception as e:
                print(f"❌ 전송 실패: {e}")
                disconnected.append(ws)
        for ws in disconnected:
            self.connected_clients.discard(ws)

    def find_input_device(self):
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if self.keyword.lower() in info["name"].lower() and info["maxInputChannels"] > 0:
                print(f"🎙️ 선택된 마이크: {info['name']} (index={i})")
                return i
        print("❗ 지정된 키워드를 가진 마이크를 찾지 못했습니다.")
        p.terminate()
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
                print("🎤 서버 마이크 송출 시작")

                while self.running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    await self.broadcast(data)
                    await asyncio.sleep(0.01)

            except Exception as e:
                print(f"⚠️ 마이크 송출 중 오류 발생: {e}")
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
                print("🛑 마이크 송출 종료")

            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            CHUNK = 1024

            p = pyaudio.PyAudio()
            device_index = self.find_input_device()
            if device_index is None:
                print("❌ 마이크 장치 없음")
                return

            try:
                stream = p.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                input_device_index=device_index,
                                frames_per_buffer=CHUNK)
                print("🎤 서버 마이크 송출 시작")

                while self.running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    await self.broadcast(data)
                    await asyncio.sleep(0.01)

            except Exception as e:
                print(f"[마이크 오류] {e}")
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
                print("🛑 마이크 송출 종료")

    def start(self):
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._run())
            print("🚀 마이크 송출 태스크 시작")

    def stop(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
                print("🛑 마이크 송출 태스크 취소됨")
