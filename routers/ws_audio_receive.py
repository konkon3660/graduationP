# routers/ws_audio_receive.py
import asyncio
import json
import pyaudio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from collections import deque
import time
import threading

logger = logging.getLogger(__name__)

router = APIRouter()

class OptimizedAudioPlayer:
    """딜레이 최소화를 위한 최적화된 오디오 플레이어"""
    
    def __init__(self, sample_rate=16000, chunk_size=1024, buffer_size=5):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.buffer_size = buffer_size  # 버퍼 크기 줄임
        
        self.audio = None
        self.stream = None
        self.audio_buffer = deque(maxlen=buffer_size)
        self.is_playing = False
        self.playback_thread = None
        self.lock = threading.Lock()
        
        # 딜레이 모니터링
        self.last_received_time = 0
        self.stats = {
            "buffer_overruns": 0,
            "avg_latency": 0,
            "packet_count": 0
        }
    
    def initialize_audio(self):
        """오디오 시스템 초기화"""
        try:
            if self.audio is None:
                self.audio = pyaudio.PyAudio()
            
            if self.stream is None or not self.stream.is_active():
                # 더 작은 버퍼로 딜레이 최소화
                self.stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    output=True,
                    frames_per_buffer=self.chunk_size // 2,  # 버퍼 크기 절반으로 줄임
                    stream_callback=None
                )
            
            logger.info("🔊 오디오 출력 스트림 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 오디오 초기화 실패: {e}")
            return False
    
    def start_playback(self):
        """논블로킹 오디오 재생 시작"""
        if not self.is_playing and self.initialize_audio():
            self.is_playing = True
            self.playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
            self.playback_thread.start()
            logger.info("🎵 오디오 재생 시작")
    
    def stop_playback(self):
        """오디오 재생 중지"""
        self.is_playing = False
        
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)
        
        with self.lock:
            self.audio_buffer.clear()
        
        self._close_stream()
        logger.info("🔇 오디오 재생 중지")
    
    def add_audio_data(self, audio_data):
        """오디오 데이터 추가 (딜레이 최소화)"""
        current_time = time.time()
        
        with self.lock:
            # 버퍼가 가득 찬 경우 오래된 데이터 제거
            if len(self.audio_buffer) >= self.buffer_size:
                self.audio_buffer.popleft()  # 가장 오래된 데이터 제거
                self.stats["buffer_overruns"] += 1
            
            self.audio_buffer.append({
                'data': audio_data,
                'timestamp': current_time
            })
        
        # 통계 업데이트
        if self.last_received_time > 0:
            latency = current_time - self.last_received_time
            self.stats["avg_latency"] = (self.stats["avg_latency"] * self.stats["packet_count"] + latency) / (self.stats["packet_count"] + 1)
        
        self.stats["packet_count"] += 1
        self.last_received_time = current_time
        
        # 주기적으로 통계 로그 출력 (100패킷마다)
        if self.stats["packet_count"] % 100 == 0:
            logger.info(f"📊 오디오 통계 - 평균지연: {self.stats['avg_latency']:.3f}s, 버퍼오버런: {self.stats['buffer_overruns']}, 버퍼크기: {len(self.audio_buffer)}")
    
    def _playback_worker(self):
        """백그라운드 오디오 재생 워커"""
        while self.is_playing:
            try:
                audio_item = None
                with self.lock:
                    if self.audio_buffer:
                        audio_item = self.audio_buffer.popleft()
                
                if audio_item and self.stream:
                    # 실시간성을 위해 오래된 데이터는 스킵
                    data_age = time.time() - audio_item['timestamp']
                    if data_age < 0.5:  # 0.5초 이내 데이터만 재생
                        self.stream.write(audio_item['data'])
                    else:
                        logger.debug(f"⏭️ 오래된 오디오 데이터 스킵 (지연: {data_age:.3f}s)")
                else:
                    # 버퍼가 비어있으면 짧게 대기
                    time.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"❌ 오디오 재생 오류: {e}")
                time.sleep(0.1)
    
    def _close_stream(self):
        """오디오 스트림 정리"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if self.audio:
                self.audio.terminate()
                self.audio = None
                
        except Exception as e:
            logger.error(f"❌ 오디오 스트림 정리 오류: {e}")
    
    def get_stats(self):
        """현재 통계 반환"""
        with self.lock:
            return {
                **self.stats,
                "current_buffer_size": len(self.audio_buffer),
                "is_playing": self.is_playing
            }

# 전역 오디오 플레이어 인스턴스
audio_player = OptimizedAudioPlayer()

@router.websocket("/ws_audio_receive")
async def websocket_audio_receive(websocket: WebSocket):
    await websocket.accept()
    logger.info("🎧 오디오 수신 WebSocket 연결됨")
    
    try:
        while True:
            # 메시지 수신
            message = await websocket.receive()
            
            if message["type"] == "websocket.receive":
                if "bytes" in message:
                    # 바이너리 오디오 데이터
                    audio_data = message["bytes"]
                    audio_player.add_audio_data(audio_data)
                    
                elif "text" in message:
                    # 텍스트 제어 메시지
                    try:
                        control_message = json.loads(message["text"])
                        await _handle_audio_control(websocket, control_message)
                    except json.JSONDecodeError:
                        logger.warning("❓ 잘못된 JSON 제어 메시지")
            
    except WebSocketDisconnect:
        logger.info("🔌 오디오 수신 WebSocket 연결 해제됨")
        audio_player.stop_playback()
    except Exception as e:
        logger.error(f"❌ 오디오 수신 WebSocket 오류: {e}")
        audio_player.stop_playback()

async def _handle_audio_control(websocket: WebSocket, control_message: dict):
    """오디오 제어 메시지 처리"""
    command = control_message.get("command", "").lower()
    
    if command == "start_audio":
        audio_player.start_playback()
        await websocket.send_text(json.dumps({
            "type": "audio_control_response",
            "command": "start_audio",
            "status": "success",
            "message": "🎵 오디오 수신 시작됨"
        }))
        
    elif command == "stop_audio":
        audio_player.stop_playback()
        await websocket.send_text(json.dumps({
            "type": "audio_control_response", 
            "command": "stop_audio",
            "status": "success",
            "message": "🔇 오디오 수신 중지됨"
        }))
        
    elif command == "get_stats":
        stats = audio_player.get_stats()
        await websocket.send_text(json.dumps({
            "type": "audio_stats",
            "stats": stats
        }))
        
    else:
        logger.warning(f"❓ 알 수 없는 오디오 제어 명령: {command}")