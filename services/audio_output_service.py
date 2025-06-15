# services/audio_output_service.py - 오디오 출력 스트림 문제 해결
import pyaudio
import threading

class AudioOutputManager:
    def __init__(self):
        self.output_stream = None
        self.pyaudio_instance = None
        self.is_initialized = False
        self.lock = threading.Lock()
        
    def initialize(self):
        with self.lock:
            if self.is_initialized:
                return
                
            try:
                # PyAudio 초기화
                self.pyaudio_instance = pyaudio.PyAudio()
                
                # 출력 스트림 생성
                self.output_stream = self.pyaudio_instance.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True,
                    frames_per_buffer=2048
                )
                
                self.is_initialized = True
                print("✅ [AUDIO_OUTPUT] 오디오 출력 스트림 초기화 완료")
                
            except Exception as e:
                print(f"❌ [AUDIO_OUTPUT] 초기화 실패: {e}")
                self.cleanup()
    
    def cleanup(self):
        with self.lock:
            try:
                if self.output_stream:
                    self.output_stream.stop_stream()
                    self.output_stream.close()
                if self.pyaudio_instance:
                    self.pyaudio_instance.terminate()
            except Exception as e:
                print(f"⚠️ [AUDIO_OUTPUT] 정리 중 오류: {e}")
            finally:
                self.output_stream = None
                self.pyaudio_instance = None
                self.is_initialized = False
                print("🛑 [AUDIO_OUTPUT] 오디오 출력 스트림 정리 완료")
    
    def play_chunk(self, chunk):
        if not self.is_initialized:
            self.initialize()
            
        if self.output_stream and self.is_initialized:
            try:
                self.output_stream.write(chunk)
            except Exception as e:
                print(f"❌ [AUDIO_OUTPUT] 재생 오류: {e}")
                # 스트림 재초기화 시도
                self.cleanup()
                self.initialize()
        else:
            print("⚠️ [AUDIO_OUTPUT] 출력 스트림이 초기화되지 않음")

# 전역 인스턴스
audio_output_manager = AudioOutputManager()

def play_audio_chunk(chunk):
    """오디오 청크 재생 함수"""
    audio_output_manager.play_chunk(chunk)