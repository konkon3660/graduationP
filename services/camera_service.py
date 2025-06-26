import cv2
import asyncio
import threading
import time
import logging
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

# 전역 변수
_camera = None
_latest_frame = None
_camera_lock = threading.Lock()
_camera_running = False
_camera_thread = None

class AsyncCameraService:
    """비동기 카메라 서비스"""
    
    def __init__(self, device_id: int = 0, width: int = 640, height: int = 480, fps: int = 30):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.camera = None
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """카메라 초기화 (비동기)"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._init_camera_sync)
            self.is_initialized = result
            if result:
                logger.info(f"📹 카메라 초기화 성공 (해상도: {self.width}x{self.height}, FPS: {self.fps})")
            else:
                logger.error("❌ 카메라 초기화 실패")
            return result
        except Exception as e:
            logger.error(f"❌ 카메라 초기화 중 예외 발생: {e}")
            return False
    
    def _init_camera_sync(self) -> bool:
        """동기 카메라 초기화"""
        try:
            self.camera = cv2.VideoCapture(self.device_id)
            if not self.camera.isOpened():
                logger.error(f"❌ 카메라 {self.device_id} 열기 실패")
                return False
            
            # 카메라 설정
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
            # 실제 설정된 값 확인
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"📹 카메라 설정 완료 - 해상도: {actual_width}x{actual_height}, FPS: {actual_fps}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 카메라 초기화 실패: {e}")
            return False
    
    async def capture_frame(self) -> Optional[np.ndarray]:
        """프레임 캡처 (비동기)"""
        if not self.is_initialized or self.camera is None:
            logger.warning("⚠️ 카메라가 초기화되지 않음")
            return None
        
        try:
            loop = asyncio.get_event_loop()
            frame = await loop.run_in_executor(None, self._capture_frame_sync)
            return frame
        except Exception as e:
            logger.error(f"❌ 프레임 캡처 실패: {e}")
            return None
    
    def _capture_frame_sync(self) -> Optional[np.ndarray]:
        """동기 프레임 캡처"""
        try:
            ret, frame = self.camera.read()
            if ret:
                return frame
            else:
                logger.warning("⚠️ 프레임 읽기 실패")
                return None
        except Exception as e:
            logger.error(f"❌ 프레임 캡처 중 예외: {e}")
            return None
    
    async def capture_photo(self, filename: str = "photo.jpg") -> bool:
        """사진 촬영 (비동기)"""
        try:
            frame = await self.capture_frame()
            if frame is not None:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, cv2.imwrite, filename, frame)
                if result:
                    logger.info(f"📸 사진 저장 완료: {filename}")
                    return True
                else:
                    logger.error(f"❌ 사진 저장 실패: {filename}")
                    return False
            else:
                logger.error("❌ 프레임 캡처 실패로 사진 촬영 불가")
                return False
        except Exception as e:
            logger.error(f"❌ 사진 촬영 실패: {e}")
            return False
    
    async def get_frame_jpeg(self, quality: int = 80) -> Optional[bytes]:
        """JPEG 형식의 프레임 반환 (비동기)"""
        try:
            frame = await self.capture_frame()
            if frame is not None:
                loop = asyncio.get_event_loop()
                encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                _, jpeg_data = await loop.run_in_executor(None, cv2.imencode, '.jpg', frame, encode_params)
                return jpeg_data.tobytes()
            else:
                return None
        except Exception as e:
            logger.error(f"❌ JPEG 인코딩 실패: {e}")
            return None
    
    async def start_streaming(self) -> bool:
        """스트리밍 시작 (비동기)"""
        try:
            if not self.is_initialized:
                success = await self.initialize()
                if not success:
                    return False
            
            logger.info("📹 스트리밍 시작")
            return True
        except Exception as e:
            logger.error(f"❌ 스트리밍 시작 실패: {e}")
            return False
    
    async def stop_streaming(self):
        """스트리밍 중지 (비동기)"""
        try:
            if self.camera is not None:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._release_camera_sync)
                logger.info("📹 스트리밍 중지")
        except Exception as e:
            logger.error(f"❌ 스트리밍 중지 실패: {e}")
    
    def _release_camera_sync(self):
        """동기 카메라 해제"""
        try:
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                self.is_initialized = False
        except Exception as e:
            logger.error(f"❌ 카메라 해제 실패: {e}")
    
    async def get_camera_info(self) -> dict:
        """카메라 정보 반환 (비동기)"""
        if not self.is_initialized or self.camera is None:
            return {"error": "카메라가 초기화되지 않음"}
        
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._get_camera_info_sync)
            return info
        except Exception as e:
            logger.error(f"❌ 카메라 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def _get_camera_info_sync(self) -> dict:
        """동기 카메라 정보 조회"""
        try:
            return {
                "width": self.camera.get(cv2.CAP_PROP_FRAME_WIDTH),
                "height": self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT),
                "fps": self.camera.get(cv2.CAP_PROP_FPS),
                "device_id": self.device_id,
                "is_opened": self.camera.isOpened()
            }
        except Exception as e:
            return {"error": str(e)}

# 전역 비동기 카메라 서비스 인스턴스
async_camera_service = AsyncCameraService()

# 기존 함수들 (하위 호환성 유지)
def capture_photo(filename="photo.jpg"):
    """기존 동기 사진 촬영 함수 (하위 호환성)"""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
    cap.release()

def get_frame():
    """기존 동기 프레임 반환 함수 (하위 호환성)"""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

# 비동기 스트리밍 생성기
async def generate_async_mjpeg():
    """비동기 MJPEG 스트림 생성기"""
    try:
        # 카메라 서비스 초기화
        if not async_camera_service.is_initialized:
            await async_camera_service.initialize()
        
        while True:
            jpeg_data = await async_camera_service.get_frame_jpeg(quality=70)
            if jpeg_data:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpeg_data + b"\r\n"
                )
            else:
                # 프레임 캡처 실패 시 잠시 대기
                await asyncio.sleep(0.1)
            
            # FPS 제한
            await asyncio.sleep(1 / 30)  # 30fps
            
    except Exception as e:
        logger.error(f"❌ 비동기 MJPEG 생성 중 예외: {e}")
    finally:
        await async_camera_service.stop_streaming()
