# services/microphone_sender_service.py

import asyncio
import websockets
import pyaudio

class MicrophoneSender:
    def __init__(self, ws_url, keyword="Brio"):
        self.ws_url = ws_url
        self.keyword = keyword
        self.running = False
        self.task = None

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

        p = pyaudio.PyAudio()
        device_index = self.find_input_device()

        if device_index is None:
            print("❌ 마이크 장치가 없어 송출을 중단합니다.")
            return

        try:
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=CHUNK)
        except Exception as e:
            print(f"[마이크 초기화 오류] {e}")
            p.terminate()
            return

        try:
            async with websockets.connect(self.ws_url) as websocket:
                print(f"🎤 마이크 송출 시작 → {self.ws_url}")
                while self.running:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    await websocket.send(data)
                    await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            print("🛑 마이크 송출 작업이 취소되었습니다.")
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
            print("🚀 마이크 송출 태스크 시작")
            self.task = asyncio.create_task(self._run())
        else:
            print("⚠️ 마이크 송출은 이미 실행 중입니다.")

    def stop(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
                print("🛑 마이크 송출 태스크 중단 요청됨")
