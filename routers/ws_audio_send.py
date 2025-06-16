import asyncio
import threading
import os
import sys
import contextlib
from datetime import datetime
from queue import Queue, Empty
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import pyaudio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ALSA 오류 억제
@contextlib.contextmanager
def suppress_alsa_stderr():
    try:
        fd = os.open(os.devnull, os.O_WRONLY)
        stderr_fd = sys.stderr.fileno()
        saved_stderr = os.dup(stderr_fd)
        os.dup2(fd, stderr_fd)
        yield
    except Exception:
        yield
    finally:
        try:
            os.dup2(saved_stderr, stderr_fd)
            os.close(fd)
            os.close(saved_stderr)
        except:
            pass

class SafeAudioPlayer:
    """안전한 오디오 플레이어"""
    def __init__(self):
        self.output_stream = None
        self.pyaudio_instance = None
        self.is_initialized = False
        self.lock = threading.Lock()
        
    def initialize(self):
        """오디오 출력 초기화"""
        with self.lock:
            if self.is_initialized:
                print("✅ [AUDIO_PLAYER] 이미 초기화됨")
                return True
            try:
                with suppress_alsa_stderr():
                    self.pyaudio_instance = pyaudio.PyAudio()
                    output_device = self._find_output_device()
                    if output_device is None:
                        print("❌ [AUDIO_PLAYER] 사용 가능한 출력 장치 없음")
                        logger.error("사용 가능한 출력 장치 없음")
                        return False
                    self.output_stream = self.pyaudio_instance.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        output=True,
                        output_device_index=output_device,
                        frames_per_buffer=2048,
                        start=False
                    )
                    self.output_stream.start_stream()
                    self.is_initialized = True
                    print(f"✅ [AUDIO_PLAYER] 오디오 출력 초기화 성공 (장치: {output_device})")
                    logger.info(f"오디오 출력 초기화 성공 (장치: {output_device})")
                    return True
            except Exception as e:
                print(f"❌ [AUDIO_PLAYER] 오디오 출력 초기화 실패: {e}")
                logger.error(f"오디오 출력 초기화 실패: {e}")
                self.cleanup()
                return False
    
    def _find_output_device(self):
        """출력 장치 찾기"""
        if not self.pyaudio_instance:
            return None
        try:
            default_output = self.pyaudio_instance.get_default_output_device_info()
            print(f"🔍 [AUDIO_PLAYER] 기본 출력 장치: {default_output['name']} ({default_output['index']})")
            return default_output['index']
        except Exception:
            try:
                for i in range(self.pyaudio_instance.get_device_count()):
                    info = self.pyaudio_instance.get_device_info_by_index(i)
                    if info["maxOutputChannels"] > 0:
                        print(f"🔍 [AUDIO_PLAYER] 출력 장치 탐색: {info['name']} ({i})")
                        return i
            except Exception as e:
                print(f"❌ [AUDIO_PLAYER] 출력 장치 탐색 실패: {e}")
        print("❌ [AUDIO_PLAYER] 출력 장치 없음")
        return None
    
    def play_chunk(self, chunk):
        """오디오 청크 재생"""
        if not self.is_initialized:
            print("⚠️ [AUDIO_PLAYER] 미초기화 상태, 재초기화 시도")
            if not self.initialize():
                print("❌ [AUDIO_PLAYER] 재초기화 실패, chunk 무시")
                return False
        try:
            if self.output_stream and self.output_stream.is_active():
                self.output_stream.write(chunk)
                print(f"[AUDIO_PLAYER] 청크 재생 ({len(chunk)} bytes)")
                return True
        except Exception as e:
            print(f"❌ [AUDIO_PLAYER] 오디오 재생 실패: {e}")
            logger.warning(f"오디오 재생 실패: {e}")
            self.cleanup()
            return self.initialize()
        return False
    
    def cleanup(self):
        """리소스 정리"""
        with self.lock:
            try:
                if self.output_stream:
                    if self.output_stream.is_active():
                        self.output_stream.stop_stream()
                    self.output_stream.close()
                    print("🧹 [AUDIO_PLAYER] 출력 스트림 정리 완료")
                if self.pyaudio_instance:
                    self.pyaudio_instance.terminate()
                    print("🧹 [AUDIO_PLAYER] PyAudio 인스턴스 정리 완료")
            except Exception as e:
                print(f"⚠️ [AUDIO_PLAYER] 정리 중 오류: {e}")
                logger.warning(f"정리 중 오류: {e}")
            finally:
                self.output_stream = None
                self.pyaudio_instance = None
                self.is_initialized = False

# 전역 인스턴스들
audio_player = SafeAudioPlayer()
audio_queue = Queue()
audio_worker_thread = None
audio_worker_running = False

def audio_output_worker():
    """오디오 출력 워커 스레드"""
    global audio_worker_running
    print("🔊 [AUDIO_WORKER] 시작")
    while audio_worker_running:
        try:
            chunk = audio_queue.get(timeout=0.5)
            print(f"[AUDIO_WORKER] 큐에서 청크 획득 ({len(chunk)} bytes), 잔여: {audio_queue.qsize()}")
            if chunk and not audio_player.play_chunk(chunk):
                print("⚠️ [AUDIO_WORKER] play_chunk 실패, 0.1초 대기")
                threading.Event().wait(0.1)
        except Empty:
            continue
        except Exception as e:
            print(f"❌ [AUDIO_WORKER] 워커 오류: {e}")
            logger.error(f"워커 오류: {e}")
    print("🛑 [AUDIO_WORKER] 종료")

@router.websocket("/ws/audio_send")
async def audio_send_ws(websocket: WebSocket):
    global audio_worker_thread, audio_worker_running
    await websocket.accept()
    print("🎤 [AUDIO_SEND] 클라이언트 마이크 → 서버 스피커 연결됨")

    # 워커 스레드 시작
    if not audio_worker_running:
        audio_worker_running = True
        audio_worker_thread = threading.Thread(target=audio_output_worker, daemon=True)
        audio_worker_thread.start()
        print("🔊 [AUDIO_SEND] 워커 스레드 시작됨")

    # 파일 저장용
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_audio_{now}.pcm"

    try:
        with open(filename, "wb") as f:
            while True:
                chunk = await websocket.receive_bytes()
                print(f"[AUDIO_SEND] 데이터 수신: {len(chunk)} bytes")  # ⭐️ 핵심 로그
                print(f"[AUDIO_SEND] 큐 사이즈 (put 직전): {audio_queue.qsize()}")
                f.write(chunk)

                # 큐 크기 제한(10개 초과시 삭제)
                if audio_queue.qsize() > 10:
                    try:
                        audio_queue.get_nowait()
                        print(f"[AUDIO_SEND] 큐 초과, 가장 오래된 청크 삭제")
                    except Empty:
                        pass

                audio_queue.put(chunk)
                print(f"[AUDIO_SEND] 큐 사이즈 (put 후): {audio_queue.qsize()}")

    except WebSocketDisconnect:
        print("🔌 [AUDIO_SEND] 클라이언트 연결 종료")

    except Exception as e:
        print(f"❌ [AUDIO_SEND] 예외 발생: {e}")
        logger.error(f"오디오 전송 예외: {e}")

    finally:
        print("🛑 [AUDIO_SEND] 연결 정리 중... (워커 유지)")
        print("✅ [AUDIO_SEND] 정리 완료")
