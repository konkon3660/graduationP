from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.microphone_sender_instance import mic_streamer  # ✅ 싱글톤 mic_streamer 객체 import

router = APIRouter()

@router.websocket("/ws/audio_receive")
async def audio_receive_ws(websocket: WebSocket):
    await websocket.accept()
    print("🔈 클라이언트 스피커 연결됨 (/ws/audio_receive)")

    mic_streamer.register(websocket)  # 클라이언트를 송신 대상에 등록

    try:
        while True:
            # 연결 유지용: 클라이언트에서 데이터를 보내지 않아도 연결을 끊지 않기 위함
            await websocket.receive_text()

    except WebSocketDisconnect:
        print("🔌 클라이언트 스피커 연결 종료")

    finally:
        mic_streamer.unregister(websocket)
        print("❎ 클라이언트 해제됨")
