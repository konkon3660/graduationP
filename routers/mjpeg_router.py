from fastapi.responses import StreamingResponse
from fastapi import APIRouter, BackgroundTasks
from camera.mjpeg_streamer import generate_mjpeg, stop_capture
from services.camera_service import generate_async_mjpeg, async_camera_service
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/mjpeg")
def mjpeg(background_tasks: BackgroundTasks):
    """기존 동기 MJPEG 스트림 (하위 호환성)"""
    # 클라이언트 접속 종료 시 stop_capture 자동 호출
    background_tasks.add_task(stop_capture)
    
    return StreamingResponse(
        generate_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/mjpeg-async")
async def mjpeg_async():
    """비동기 MJPEG 스트림 (새로운 버전)"""
    try:
        logger.info("📹 비동기 MJPEG 스트림 시작")
        return StreamingResponse(
            generate_async_mjpeg(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        logger.error(f"❌ 비동기 MJPEG 스트림 생성 실패: {e}")
        raise

@router.get("/camera-info")
async def get_camera_info():
    """카메라 정보 조회"""
    try:
        info = await async_camera_service.get_camera_info()
        return info
    except Exception as e:
        logger.error(f"❌ 카메라 정보 조회 실패: {e}")
        return {"error": str(e)}

@router.post("/camera/initialize")
async def initialize_camera():
    """카메라 초기화"""
    try:
        success = await async_camera_service.initialize()
        return {"success": success, "message": "카메라 초기화 완료" if success else "카메라 초기화 실패"}
    except Exception as e:
        logger.error(f"❌ 카메라 초기화 실패: {e}")
        return {"success": False, "error": str(e)}

@router.post("/camera/capture")
async def capture_photo():
    """사진 촬영"""
    try:
        success = await async_camera_service.capture_photo("captured_photo.jpg")
        return {"success": success, "message": "사진 촬영 완료" if success else "사진 촬영 실패"}
    except Exception as e:
        logger.error(f"❌ 사진 촬영 실패: {e}")
        return {"success": False, "error": str(e)}

@router.post("/camera/stop")
async def stop_camera():
    """카메라 중지"""
    try:
        await async_camera_service.stop_streaming()
        return {"success": True, "message": "카메라 중지 완료"}
    except Exception as e:
        logger.error(f"❌ 카메라 중지 실패: {e}")
        return {"success": False, "error": str(e)}
