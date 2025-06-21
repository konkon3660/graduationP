# services/feed_scheduler.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from services.settings_service import settings_service
from services.feed_service import feed_once

logger = logging.getLogger(__name__)

class FeedScheduler:
    def __init__(self):
        self.is_running = False
        self.next_feed_time: Optional[datetime] = None
        self.current_count = 0
        self.task: Optional[asyncio.Task] = None
    
    async def start(self):
        """스케줄러를 시작합니다."""
        if self.is_running:
            logger.info("🔄 스케줄러가 이미 실행 중입니다")
            return
        
        self.is_running = True
        logger.info("🚀 급식 스케줄러 시작됨")
        
        # 스케줄링 태스크 시작
        self.task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self):
        """스케줄러를 중지합니다."""
        if not self.is_running:
            logger.info("⏹ 스케줄러가 이미 중지되었습니다")
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("⏹ 급식 스케줄러 중지됨")
    
    async def _scheduler_loop(self):
        """메인 스케줄링 루프"""
        while self.is_running:
            try:
                # 설정 확인
                settings = settings_service.get_settings()
                mode = settings.get("mode", "manual")
                
                if mode != "auto":
                    # 자동 모드가 아니면 대기
                    await asyncio.sleep(5)
                    continue
                
                interval = int(settings.get("interval", 60))
                amount = int(settings.get("amount", 1))
                
                # 다음 급식 시간 설정
                if self.next_feed_time is None:
                    self.next_feed_time = datetime.now() + timedelta(minutes=interval)
                    self.current_count = 0
                    logger.info(f"⏳ 다음 급식 예정: {self.next_feed_time.strftime('%H:%M:%S')}")
                    await asyncio.sleep(5)
                    continue
                
                # 급식 시간 확인
                now = datetime.now()
                if now >= self.next_feed_time:
                    logger.info(f"✅ 급식 시간 도달: {now.strftime('%H:%M:%S')}")
                    
                    # 설정된 양만큼 급식 실행
                    for i in range(amount):
                        logger.info(f"🍽 급식 실행 {i+1}/{amount}")
                        feed_once()
                        if i < amount - 1:  # 마지막이 아니면 잠시 대기
                            await asyncio.sleep(1)
                    
                    # 다음 급식 시간 설정
                    self.next_feed_time = now + timedelta(minutes=interval)
                    self.current_count += 1
                    logger.info(f"📆 다음 급식 시간: {self.next_feed_time.strftime('%H:%M:%S')}")
                
                # 5초마다 체크
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                logger.info("🔄 스케줄러 루프 취소됨")
                break
            except Exception as e:
                logger.error(f"❌ 스케줄러 오류: {e}")
                await asyncio.sleep(10)  # 오류 시 10초 대기
    
    def reset_schedule(self):
        """스케줄을 리셋합니다."""
        self.next_feed_time = None
        self.current_count = 0
        logger.info("🔄 급식 스케줄 리셋됨")
    
    def get_status(self) -> dict:
        """현재 스케줄러 상태를 반환합니다."""
        return {
            "is_running": self.is_running,
            "next_feed_time": self.next_feed_time.isoformat() if self.next_feed_time else None,
            "current_count": self.current_count,
            "settings": settings_service.get_settings()
        }

# 전역 인스턴스
feed_scheduler = FeedScheduler() 