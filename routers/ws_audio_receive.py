from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from services import mic_service  # 서버의 마이크에서 PCM을 읽어오는 모듈

router = APIRouter()

# ✅ 서버가 갖고 있는 마이크에서 음성 데이터를 주기적으로 읽고 보내는 WebSocket
@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎙️ 서버 마이크 → 클라이언트 스피커 연결됨 (/ws/audio_receive)")

    try:
        while True:
            pcm_chunk = mic_service.get_next_pcm_chunk()  # 예: 2048 bytes
            if pcm_chunk:
                await websocket.send_bytes(pcm_chunk)
            else:
                print("⚠️ PCM 데이터 없음")
            await asyncio.sleep(0.05)  # 20fps 정도의 텀
    except WebSocketDisconnect:
        print("🔌 클라이언트 스피커 연결 종료됨")
