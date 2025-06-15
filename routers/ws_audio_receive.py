# routers/ws_audio_receive.py - 안전한 버전 (서버 종료 방지)
import asyncio
import os
import sys
import contextlib
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import pyaudio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ALSA 오류 억제 컨텍스트 매니저
@contextlib.contextmanager
def suppress_alsa_stderr():
    """ALSA 오류 메시지 억제"""
    try:
        fd = os.open(os.devnull, os.O_WRONLY)
        stderr_fd = sys.stderr.fileno()
        saved_stderr = os.dup(stderr_fd)
        os.dup2(fd, stderr_fd)
        yield
    except Exception as e:
        logger.warning(f"ALSA 억제 실패: {e}")
        yield
    finally:
        try:
            os.dup2(saved_stderr, stderr_fd)
            os.close(fd)
            os.close(saved_stderr)
        except:
            pass

# 전역 오디오 스트림 상태 - 안전한 관리
class AudioStreamManager:
    def __init__(self):
        self.audio_stream = None
        self.pyaudio_instance = None
        self.is_active = False
    
    def initialize(self, device_index=None):
        """오디오 스트림 초기화"""
        if self.is_active:
            return True
            
        try:
            with suppress_alsa_stderr():
                self.pyaudio_instance = pyaudio.PyAudio()
                
                # 사용 가능한 입력 장치 찾기
                if device_index is None:
                    device_index = self._find_input_device()
                
                if device_index is None:
                    logger.error("사용 가능한 입력 장치 없음")
                    return False
                
                self.audio_stream = self.pyaudio_instance.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=2048,
                    start=False  # 수동 시작
                )
                
                self.audio_stream.start_stream()
                self.is_active = True
                logger.info(f"✅ 오디오 스트림 초기화 성공 (장치: {device_index})")
                return True
                
        except Exception as e:
            logger.error(f"❌ 오디오 스트림 초기화 실패: {e}")
            self.cleanup()
            return False
    
    def _find_input_device(self):
        """사용 가능한 입력 장치 찾기"""
        if not self.pyaudio_instance:
            return None
            
        try:
            for i in range(self.pyaudio_instance.get_device_count()):
                info = self.pyaudio_instance.get_device_info_by_index(i)
                if info["maxInputChannels"] > 0:
                    logger.info(f"🎙️ 입력 장치 발견: [{i}] {info['name']}")
                    return i
        except Exception as e:
            logger.error(f"입력 장치 검색 실패: {e}")
        
        return None
    
    def read_audio(self, chunk_size=2048):
        """오디오 데이터 읽기"""
        if not self.is_active or not self.audio_stream:
            return None
            
        try:
            return self.audio_stream.read(chunk_size, exception_on_overflow=False)
        except Exception as e:
            logger.error(f"오디오 읽기 실패: {e}")
            return None
    
    def cleanup(self):
        """리소스 정리"""
        try:
            if self.audio_stream:
                if self.audio_stream.is_active():
                    self.audio_stream.stop_stream()
                self.audio_stream.close()
                
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                
        except Exception as e:
            logger.warning(f"정리 중 오류: {e}")
        finally:
            self.audio_stream = None
            self.pyaudio_instance = None
            self.is_active = False
            logger.info("🛑 오디오 스트림 정리 완료")

# 전역 오디오 매니저
audio_manager = AudioStreamManager()

@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎙️ [AUDIO_RECEIVE] 서버 마이크 → 클라이언트 스피커 연결됨")
    
    # 오디오 초기화
    if not audio_manager.initialize():
        await websocket.close(code=1011, reason="오디오 초기화 실패")
        return

    try:
        print("✅ [AUDIO_RECEIVE] 실시간 전송 시작")
        
        while True:
            # 비동기로 오디오 읽기
            data = await asyncio.get_event_loop().run_in_executor(
                None, audio_manager.read_audio, 2048
            )
            
            if data:
                await websocket.send_bytes(data)
            else:
                # 오디오 읽기 실패 시 잠시 대기
                await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print("🔌 [AUDIO_RECEIVE] 클라이언트 연결 종료됨")

    except Exception as e:
        print(f"❌ [AUDIO_RECEIVE] 예외 발생: {e}")
        logger.error(f"오디오 수신 예외: {e}")

    finally:
        # 연결별로 정리하지 않고 전역 상태 유지
        print("🛑 [AUDIO_RECEIVE] WebSocket 연결 종료")