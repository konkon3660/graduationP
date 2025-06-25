# services/auto_play_service.py - 자동 놀이 기능 서비스 (확장 버전)
import asyncio
import random
import logging
import math
from typing import Set, Optional
from services.laser_service import laser_on, laser_off
from services.xy_servo import set_xy_servo_angles, reset_to_center
from services.motor_service import move_forward, move_backward, turn_left, turn_right, stop_motors
from services.sol_service import fire
from services.audio_playback_service import audio_playback_service

logger = logging.getLogger(__name__)

class AutoPlayService:
    def __init__(self, auto_play_delay: int = 70):
        """
        자동 놀이 서비스 초기화
        
        Args:
            auto_play_delay: 클라이언트 연결 종료 후 자동 놀이 시작까지의 대기 시간 (초)
        """
        self.auto_play_delay = auto_play_delay
        self.connected_clients: Set = set()
        self.auto_play_task: Optional[asyncio.Task] = None
        self.is_auto_playing = False
        self.auto_play_running = False
        
        # 모터 속도 설정
        self.motor_speed = 60        # 모터 속도 (0-100)
        
        logger.info(f"🎮 자동 놀이 서비스 초기화 (대기시간: {auto_play_delay}초)")
    
    def register_client(self, websocket):
        """클라이언트 등록"""
        self.connected_clients.add(websocket)
        logger.info(f"👤 클라이언트 등록됨 (총 {len(self.connected_clients)}명)")
        
        # 자동 놀이 중지 (클라이언트가 연결되면)
        if self.is_auto_playing:
            self.stop_auto_play()
    
    def unregister_client(self, websocket):
        """클라이언트 해제"""
        self.connected_clients.discard(websocket)
        logger.info(f"👤 클라이언트 해제됨 (총 {len(self.connected_clients)}명)")
        
        # 모든 클라이언트가 연결 해제되면 자동 놀이 타이머 시작
        if len(self.connected_clients) == 0:
            self.schedule_auto_play_sync()
    
    async def schedule_auto_play(self):
        """자동 놀이 스케줄링 (비동기)"""
        try:
            # 기존 태스크가 있으면 안전하게 취소
            if self.auto_play_task and not self.auto_play_task.done():
                self.auto_play_task.cancel()
                try:
                    await self.auto_play_task
                except asyncio.CancelledError:
                    pass
            
            logger.info(f"⏰ {self.auto_play_delay}초 후 자동 놀이 시작 예정")
            self.auto_play_task = asyncio.create_task(self._delayed_auto_play())
            
        except Exception as e:
            logger.error(f"❌ 자동 놀이 스케줄링 실패: {e}")
    
    def schedule_auto_play_sync(self):
        """자동 놀이 스케줄링 (동기 래퍼)"""
        try:
            # 현재 이벤트 루프에서 태스크 생성
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.schedule_auto_play())
            else:
                logger.warning("⚠️ 이벤트 루프가 실행되지 않아 자동 놀이 스케줄링을 건너뜁니다")
        except Exception as e:
            logger.error(f"❌ 자동 놀이 스케줄링 래퍼 실패: {e}")
    
    async def _delayed_auto_play(self):
        """지연된 자동 놀이 실행"""
        try:
            logger.info(f"⏳ {self.auto_play_delay}초 대기 시작...")
            await asyncio.sleep(self.auto_play_delay)
            
            # 대기 시간이 지난 후에도 클라이언트가 없으면 자동 놀이 시작
            if len(self.connected_clients) == 0:
                logger.info("🎮 자동 놀이 시작!")
                await self.start_auto_play()
            else:
                logger.info("🎮 클라이언트가 다시 연결되어 자동 놀이 취소됨")
                
        except asyncio.CancelledError:
            logger.info("⏹ 자동 놀이 스케줄 취소됨")
        except Exception as e:
            logger.error(f"❌ 자동 놀이 스케줄링 오류: {e}")
            # 오류 발생 시 10초 후 재시도
            try:
                await asyncio.sleep(10)
                if len(self.connected_clients) == 0:
                    logger.info("🔄 자동 놀이 재시도...")
                    await self.start_auto_play()
            except Exception as retry_e:
                logger.error(f"❌ 자동 놀이 재시도 실패: {retry_e}")
    
    async def start_auto_play(self):
        """자동 놀이 시작"""
        if self.is_auto_playing:
            logger.info("🎮 자동 놀이가 이미 실행 중입니다")
            return
        
        # 클라이언트가 연결되어 있으면 자동 놀이 시작하지 않음
        if len(self.connected_clients) > 0:
            logger.info(f"🎮 클라이언트 {len(self.connected_clients)}명이 연결되어 자동 놀이를 시작하지 않습니다")
            return
        
        self.is_auto_playing = True
        self.auto_play_running = True
        
        logger.info("🎮 자동 놀이 모드 시작")
        
        try:
            # 시작 음성 재생 (볼륨 크게)
            original_volume = audio_playback_service.get_volume()
            audio_playback_service.set_volume(1.0)
            audio_playback_service.play_excited_sound()
            await asyncio.sleep(1)
            audio_playback_service.set_volume(original_volume)
            
            # 레이저 켜기
            laser_on()
            logger.info("🔴 레이저 포인터 켜짐")
            
            # 중앙 위치로 이동
            reset_to_center()
            await asyncio.sleep(1)
            
            # 자동 놀이 루프
            pattern_count = 0
            while self.auto_play_running and len(self.connected_clients) == 0:
                pattern_count += 1
                logger.info(f"🎮 자동 놀이 패턴 {pattern_count} 실행 중...")
                await self._play_advanced_pattern()
                
        except Exception as e:
            logger.error(f"❌ 자동 놀이 중 오류: {e}")
        finally:
            # 정리
            laser_off()
            stop_motors()
            reset_to_center()
            self.is_auto_playing = False
            logger.info(f"🎮 자동 놀이 모드 종료 (총 {pattern_count}개 패턴 실행)")
    
    def stop_auto_play(self):
        """자동 놀이 중지"""
        if not self.is_auto_playing:
            return
        
        self.auto_play_running = False
        logger.info("⏹ 자동 놀이 중지 요청됨")
    
    async def _play_advanced_pattern(self):
        patterns = [
            self._laser_play_pattern,
            self._mobile_play_pattern,
            self._solenoid_play_pattern,
            self._exploration_pattern,
            self._dance_pattern,
            self._circle_pattern,
            self._figure_eight_pattern,
            self._random_movement_pattern,
            self._wave_pattern,
            self._spiral_pattern,
            self._zigzag_pattern,
            self._heart_pattern,
            self._sound_pattern,
            self._combo_pattern
        ]
        pattern = random.choice(patterns)
        # --- 효과음 재생 및 딜레이 추가 ---
        next_sound = audio_playback_service.get_next_sound()
        audio_playback_service.play_sound(next_sound)
        await asyncio.sleep(random.uniform(1, 3))
        # --- 기존 패턴 실행 (패턴 내 효과음 재생 코드 추가) ---
        await pattern()
        await asyncio.sleep(random.uniform(1, 3))
    
    async def _sound_pattern(self):
        logger.info("🔊 소리만 반복 재생 패턴 시작")
        for _ in range(random.randint(3, 6)):
            audio_playback_service.play_sound(audio_playback_service.get_next_sound())
            await asyncio.sleep(random.uniform(1, 2))
    
    async def _combo_pattern(self):
        logger.info("🎲 콤보 패턴 시작 (움직임+소리+레이저+솔레노이드)")
        # 랜덤하게 여러 동작을 조합
        actions = [
            self._laser_play_pattern,
            self._mobile_play_pattern,
            self._solenoid_play_pattern,
            self._sound_pattern,
            self._circle_pattern,
            self._random_movement_pattern
        ]
        random.shuffle(actions)
        for act in actions[:random.randint(2, 5)]:
            await act()
            audio_playback_service.play_sound(audio_playback_service.get_next_sound())
            await asyncio.sleep(random.uniform(0.5, 2))
    
    async def _safe_move_forward(self, duration: float = 2.0):
        """안전한 전진 (제한된 시간과 거리)"""
        try:
            # 이동 음성 재생
            audio_playback_service.play_move_sound()
            
            # 전진 (짧은 시간으로 제한)
            move_forward(self.motor_speed)
            await asyncio.sleep(duration)
            stop_motors()
            
            logger.info(f"🚗 안전한 전진 완료 ({duration}초)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 안전한 전진 실패: {e}")
            stop_motors()
            return False
    
    async def _safe_turn(self, direction: str = "random"):
        """안전한 회전"""
        try:
            if direction == "random":
                direction = random.choice(["left", "right"])
            
            # 회전 음성 재생
            audio_playback_service.play_curious_sound()
            
            if direction == "left":
                turn_left(self.motor_speed)
                logger.info("⬅️ 좌회전")
            else:
                turn_right(self.motor_speed)
                logger.info("➡️ 우회전")
            
            await asyncio.sleep(random.uniform(1.0, 2.0))
            stop_motors()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 안전한 회전 실패: {e}")
            stop_motors()
            return False
    
    async def _laser_play_pattern(self):
        logger.info("🎯 레이저 놀이 패턴 시작")
        patterns = [
            self._circle_pattern,
            self._figure_eight_pattern,
            self._random_movement_pattern,
            self._wave_pattern,
            self._spiral_pattern,
            self._zigzag_pattern,
            self._heart_pattern
        ]
        num_patterns = random.randint(2, 4)
        for _ in range(num_patterns):
            if not self.auto_play_running:
                break
            pattern = random.choice(patterns)
            await pattern()
            audio_playback_service.play_sound(audio_playback_service.get_next_sound())
            await asyncio.sleep(1)
    
    async def _mobile_play_pattern(self):
        logger.info("🚗 이동 놀이 패턴 시작")
        for _ in range(random.randint(3, 6)):
            if not self.auto_play_running:
                break
            action = random.choice(["forward", "turn"])
            if action == "forward":
                await self._safe_move_forward(random.uniform(0.5, 1.5))
            else:
                await self._safe_turn()
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def _solenoid_play_pattern(self):
        logger.info("🔥 솔레노이드 놀이 패턴 시작")
        for i in range(random.randint(2, 4)):
            if not self.auto_play_running:
                break
            fire()
            logger.info(f"🔥 솔레노이드 발사 {i+1}회")
            await asyncio.sleep(random.uniform(1.0, 2.0))
    
    async def _exploration_pattern(self):
        logger.info("🔍 탐험 패턴 시작")
        for _ in range(random.randint(4, 8)):
            if not self.auto_play_running:
                break
            await self._safe_turn()
            await self._safe_move_forward(random.uniform(0.3, 0.8))
            await asyncio.sleep(random.uniform(0.3, 0.8))
    
    async def _dance_pattern(self):
        logger.info("💃 춤 패턴 시작")
        for _ in range(random.randint(2, 4)):
            if not self.auto_play_running:
                break
            turn_left(self.motor_speed)
            await asyncio.sleep(1.0)
            stop_motors()
            turn_right(self.motor_speed)
            await asyncio.sleep(1.0)
            stop_motors()
            await asyncio.sleep(0.5)
    
    # 기존 레이저 패턴들 (수정 없음)
    async def _play_pattern(self):
        """놀이 패턴 실행"""
        patterns = [
            self._circle_pattern,
            self._figure_eight_pattern,
            self._random_movement_pattern,
            self._wave_pattern,
            self._spiral_pattern,
            self._zigzag_pattern,
            self._heart_pattern
        ]
        
        # 랜덤하게 패턴 선택
        pattern = random.choice(patterns)
        await pattern()
        
        # 패턴 간 잠시 대기
        await asyncio.sleep(random.uniform(2, 5))
    
    async def _circle_pattern(self):
        """원 그리기 패턴"""
        logger.info("⭕ 원 그리기 패턴 시작")
        
        center_x, center_y = 90, 90
        radius = random.randint(20, 40)
        
        for angle in range(0, 360, 8):
            if not self.auto_play_running:
                break
                
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            
            x = max(0, min(180, x))
            y = max(0, min(180, y))
            
            # 비동기 서보 제어 사용
            await set_xy_servo_angles(int(x), int(y))
            await asyncio.sleep(0.05)
    
    async def _figure_eight_pattern(self):
        """8자 그리기 패턴"""
        logger.info("8️⃣ 8자 그리기 패턴 시작")
        
        center_x, center_y = 90, 90
        radius = 25
        
        # 첫 번째 원 (위쪽)
        for angle in range(0, 360, 10):
            if not self.auto_play_running:
                break
                
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y - radius + radius * math.sin(rad)
            
            x = max(0, min(180, x))
            y = max(0, min(180, y))
            
            # 비동기 서보 제어 사용
            await set_xy_servo_angles(int(x), int(y))
            await asyncio.sleep(0.05)
        
        # 두 번째 원 (아래쪽)
        for angle in range(0, 360, 10):
            if not self.auto_play_running:
                break
                
            rad = math.radians(angle)
            x = center_x - radius + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            
            x = max(0, min(180, x))
            y = max(0, min(180, y))
            
            # 비동기 서보 제어 사용
            await set_xy_servo_angles(int(x), int(y))
            await asyncio.sleep(0.05)
    
    async def _random_movement_pattern(self):
        """랜덤 움직임 패턴"""
        logger.info("🎲 랜덤 움직임 패턴 시작")
        
        current_x, current_y = 90, 90
        
        for _ in range(25):
            if not self.auto_play_running:
                break
                
            # 현재 위치에서 랜덤한 방향으로 이동
            target_x = random.randint(30, 150)
            target_y = random.randint(30, 150)
            
            # 부드러운 이동을 위해 단계별로 이동
            steps = random.randint(5, 15)
            for step in range(steps + 1):
                if not self.auto_play_running:
                    break
                    
                progress = step / steps
                x = current_x + (target_x - current_x) * progress
                y = current_y + (target_y - current_y) * progress
                
                # 비동기 서보 제어 사용
                await set_xy_servo_angles(int(x), int(y))
                await asyncio.sleep(0.1)
            
            current_x, current_y = target_x, target_y
    
    async def _wave_pattern(self):
        """파도 패턴"""
        logger.info("🌊 파도 패턴 시작")
        
        center_x, center_y = 90, 90
        amplitude = random.randint(15, 30)
        frequency = random.uniform(0.5, 1.5)
        
        for i in range(0, 200, 3):
            if not self.auto_play_running:
                break
                
            x = center_x + i * 0.5
            y = center_y + amplitude * math.sin(i * frequency * 0.1)
            
            x = max(0, min(180, x))
            y = max(0, min(180, y))
            
            # 비동기 서보 제어 사용
            await set_xy_servo_angles(int(x), int(y))
            await asyncio.sleep(0.05)
    
    async def _spiral_pattern(self):
        """나선 패턴"""
        logger.info("🌀 나선 패턴 시작")
        
        center_x, center_y = 90, 90
        
        for i in range(0, 150, 2):
            if not self.auto_play_running:
                break
                
            angle = i * 8
            radius = i * 0.3
            
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            
            x = max(0, min(180, x))
            y = max(0, min(180, y))
            
            # 비동기 서보 제어 사용
            await set_xy_servo_angles(int(x), int(y))
            await asyncio.sleep(0.05)
    
    async def _zigzag_pattern(self):
        """지그재그 패턴"""
        logger.info("⚡ 지그재그 패턴 시작")
        
        start_x, start_y = 30, 30
        width = 120
        height = 120
        
        for i in range(0, width, 5):
            if not self.auto_play_running:
                break
                
            x = start_x + i
            y = start_y + (i % 20) * (height / 20)
            
            x = max(0, min(180, x))
            y = max(0, min(180, y))
            
            # 비동기 서보 제어 사용
            await set_xy_servo_angles(int(x), int(y))
            await asyncio.sleep(0.05)
    
    async def _heart_pattern(self):
        """하트 패턴"""
        logger.info("💖 하트 패턴 시작")
        
        center_x, center_y = 90, 90
        scale = 20
        
        for angle in range(0, 360, 5):
            if not self.auto_play_running:
                break
                
            rad = math.radians(angle)
            
            # 하트 방정식
            x = 16 * math.sin(rad) ** 3
            y = -(13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad))
            
            # 스케일링 및 이동
            x = center_x + x * scale
            y = center_y + y * scale
            
            x = max(0, min(180, x))
            y = max(0, min(180, y))
            
            # 비동기 서보 제어 사용
            await set_xy_servo_angles(int(x), int(y))
            await asyncio.sleep(0.05)
    
    def get_status(self):
        """서비스 상태 조회"""
        task_status = "none"
        if self.auto_play_task:
            if self.auto_play_task.done():
                task_status = "done"
            elif self.auto_play_task.cancelled():
                task_status = "cancelled"
            else:
                task_status = "running"
        
        return {
            "connected_clients": len(self.connected_clients),
            "is_auto_playing": self.is_auto_playing,
            "auto_play_delay": self.auto_play_delay,
            "auto_play_running": self.auto_play_running,
            "motor_speed": self.motor_speed,
            "task_status": task_status,
            "has_task": self.auto_play_task is not None
        }
    
    def set_auto_play_delay(self, delay: int):
        """자동 놀이 대기 시간 설정"""
        self.auto_play_delay = delay
        logger.info(f"⏰ 자동 놀이 대기 시간 변경: {delay}초")
    
    def set_motor_speed(self, speed: int):
        """모터 속도 설정"""
        self.motor_speed = max(0, min(100, speed))
        logger.info(f"🚗 모터 속도 변경: {self.motor_speed}")

# 전역 인스턴스
auto_play_service = AutoPlayService() 