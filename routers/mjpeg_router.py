from fastapi.responses import StreamingResponse
from fastapi import APIRouter, BackgroundTasks
from camera.mjpeg_streamer import generate_mjpeg, stop_capture

router = APIRouter()

@router.get("/mjpeg")
def mjpeg(background_tasks: BackgroundTasks):
    # 클라이언트 접속 종료 시 stop_capture 자동 호출
    background_tasks.add_task(stop_capture)
    
    return StreamingResponse(
        generate_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
