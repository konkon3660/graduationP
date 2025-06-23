# services/audio_playback_service.py - 음성 재생 서비스
import pygame
import os
import logging
import asyncio
from typing import Optional, List
import random

logger = logging.getLogger(__name__)

class AudioPlaybackService:
    def __init__(self, audio_dir: str = "sounds"):
        """
        음성 재생 서비스 초기화
        
        Args:
            audio_dir: 음성 파일이 저장된 디렉토리 경로
        """
        self.audio_dir = audio_dir
        self.current_sound: Optional[pygame.mixer.Sound] = None
        self.is_playing = False
        self.volume = 0.7  # 기본 볼륨 (0.0 ~ 1.0)
        self.sound_queue = []  # 다음에 재생할 음성 큐
        self.sound_history = set()  # 이미 재생한 음성 파일
        
        # pygame 초기화
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            logger.info("✅ 오디오 재생 서비스 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 오디오 재생 서비스 초기화 실패: {e}")
        
        # 실제 mp3 파일명에 맞게 매핑
        self.default_sounds = {
            "happy": "Water Sound.mp3",
            "excited": "Hello Baby Girl Sound.mp3",
            "playful": "Laughing Kookaburra Birds Sound.mp3",
            "curious": "Cat Meow 2 Sound.mp3",
            "surprised": "Panic Sound.mp3",
            "laser": "ping sound.mp3",
            "fire": "Nature Fire Fireworks 08.mp3",
            "feed": "Catoon Duck.mp3",
            "move": "Spin Jump Sound.mp3",
            "bark": "Black Crows Cawing Sound.mp3",
            "meow": "Cat Meow 2 Sound.mp3",
            "purr": "Mosquito Buzzing Sound.mp3"
        }
        
        # 오디오 디렉토리 생성
        self._ensure_audio_directory()
    
    def _ensure_audio_directory(self):
        """오디오 디렉토리 생성"""
        try:
            if not os.path.exists(self.audio_dir):
                os.makedirs(self.audio_dir)
                logger.info(f"📁 오디오 디렉토리 생성: {self.audio_dir}")
        except Exception as e:
            logger.error(f"❌ 오디오 디렉토리 생성 실패: {e}")
    
    def set_volume(self, volume: float):
        """
        볼륨 설정
        
        Args:
            volume: 볼륨 (0.0 ~ 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.current_sound:
            self.current_sound.set_volume(self.volume)
        logger.info(f"🔊 볼륨 설정: {self.volume}")
    
    def get_volume(self) -> float:
        """현재 볼륨 반환"""
        return self.volume
    
    def play_sound(self, sound_name: str, async_play: bool = True):
        """
        음성 재생
        
        Args:
            sound_name: 재생할 음성 파일명 또는 기본 음성 이름
            async_play: 비동기 재생 여부
        """
        try:
            # 파일 경로 결정
            if sound_name in self.default_sounds:
                file_path = os.path.join(self.audio_dir, self.default_sounds[sound_name])
            else:
                file_path = os.path.join(self.audio_dir, sound_name)
            
            # 파일 존재 확인
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ 음성 파일을 찾을 수 없음: {file_path}")
                return False
            
            # 이전 재생 중지
            self.stop_sound()
            
            # 새 음성 로드 및 재생
            self.current_sound = pygame.mixer.Sound(file_path)
            self.current_sound.set_volume(self.volume)
            
            if async_play:
                # 비동기 재생
                asyncio.create_task(self._play_async())
            else:
                # 동기 재생
                self.current_sound.play()
                self.is_playing = True
            
            logger.info(f"🎵 음성 재생 시작: {sound_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 음성 재생 실패: {e}")
            return False
    
    async def _play_async(self):
        """비동기 음성 재생"""
        try:
            self.current_sound.play()
            self.is_playing = True
            
            # 재생 완료까지 대기
            while self.is_playing and pygame.mixer.get_busy():
                await asyncio.sleep(0.1)
            
            self.is_playing = False
            logger.debug("🎵 음성 재생 완료")
            
        except Exception as e:
            logger.error(f"❌ 비동기 음성 재생 실패: {e}")
            self.is_playing = False
    
    def stop_sound(self):
        """음성 재생 중지"""
        try:
            if self.current_sound and self.is_playing:
                self.current_sound.stop()
                self.is_playing = False
                logger.info("⏹ 음성 재생 중지")
        except Exception as e:
            logger.error(f"❌ 음성 재생 중지 실패: {e}")
    
    def play_happy_sound(self):
        """행복한 소리 재생"""
        return self.play_sound("happy")
    
    def play_excited_sound(self):
        """흥분한 소리 재생"""
        return self.play_sound("excited")
    
    def play_playful_sound(self):
        """장난스러운 소리 재생"""
        return self.play_sound("playful")
    
    def play_curious_sound(self):
        """호기심 많은 소리 재생"""
        return self.play_sound("curious")
    
    def play_surprised_sound(self):
        """놀란 소리 재생"""
        return self.play_sound("surprised")
    
    def play_laser_sound(self):
        """레이저 소리 재생"""
        return self.play_sound("laser")
    
    def play_fire_sound(self):
        """발사 소리 재생"""
        return self.play_sound("fire")
    
    def play_feed_sound(self):
        """급식 소리 재생"""
        return self.play_sound("feed")
    
    def play_move_sound(self):
        """이동 소리 재생"""
        return self.play_sound("move")
    
    def play_bark_sound(self):
        """개 짖는 소리 재생"""
        return self.play_sound("bark")
    
    def play_meow_sound(self):
        """고양이 울음소리 재생"""
        return self.play_sound("meow")
    
    def play_purr_sound(self):
        """고양이 골골거리는 소리 재생"""
        return self.play_sound("purr")
    
    def get_available_sounds(self) -> List[str]:
        """사용 가능한 음성 파일 목록 반환"""
        try:
            if not os.path.exists(self.audio_dir):
                return []
            
            files = []
            for file in os.listdir(self.audio_dir):
                if file.lower().endswith(('.wav', '.mp3', '.ogg')):
                    files.append(file)
            
            return sorted(files)
        except Exception as e:
            logger.error(f"❌ 음성 파일 목록 조회 실패: {e}")
            return []
    
    def get_next_sound(self) -> str:
        """
        다음에 재생할 음성 파일명을 반환한다.
        모든 파일을 1회씩 재생한 후에는 셔플 반복한다.
        """
        available = self.get_available_sounds()
        # 아직 한 번도 재생하지 않은 파일 우선
        not_played = [f for f in available if f not in self.sound_history]
        if not_played:
            next_sound = not_played[0]
            self.sound_history.add(next_sound)
            return next_sound
        # 모두 재생했다면 큐에서 꺼내기, 큐가 비면 셔플
        if not self.sound_queue:
            self.sound_queue = available[:]
            random.shuffle(self.sound_queue)
        next_sound = self.sound_queue.pop(0)
        return next_sound
    
    def get_status(self):
        """서비스 상태 조회"""
        return {
            "is_playing": self.is_playing,
            "volume": self.volume,
            "audio_directory": self.audio_dir,
            "available_sounds": self.get_available_sounds(),
            "default_sounds": list(self.default_sounds.keys())
        }
    
    def cleanup(self):
        """리소스 정리"""
        try:
            self.stop_sound()
            pygame.mixer.quit()
            logger.info("🧹 오디오 재생 서비스 정리 완료")
        except Exception as e:
            logger.error(f"⚠️ 오디오 재생 서비스 정리 중 오류: {e}")

# 전역 인스턴스
audio_playback_service = AudioPlaybackService() 