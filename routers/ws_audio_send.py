# routers/ws_audio_send.py - 1:1 전용 간소화 버전
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.audio_output_service import play_audio_chunk
from datetime import datetime
import asyncio
import threading
from queue import Queue, Empty

router = APIRouter()

# 전역 오디오 출력 큐와 워커 상태
audio_queue = Queue()
audio_worker_thread = None
audio_worker_running = False

def audio_output_worker():
    """단순한 오디오 출력 워커"""
    global audio_worker_running
    print("🔊 오디오 출력 워커 시작")
    
    while audio_worker_running:
        try:
            chunk = audio_queue.get(timeout=0.5)  # 0.5초 타임아웃
            play_audio_chunk(chunk)
        except Empty:
            continue  # 타임아웃 시 계속 루프
        except Exception as e:
            print(f"❌ 오디오 재생 오류: {e}")
    
    print("🛑 오디오 출력 워커 종료")

@router.websocket("/ws/audio_send")
async def audio_send_ws(websocket: WebSocket):
    global audio_worker_thread, audio_worker_running
    
    await websocket.accept()
    print("🎤 클라이언트 마이크 → 서버 스피커 연결됨")

    # 오디오 워커 시작 (아직 실행 중이 아니라면)
    if not audio_worker_running:
        audio_worker_running = True
        audio_worker_thread = threading.Thread(target=audio_output_worker, daemon=True)
        audio_worker_thread.start()

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_audio_{now}.pcm"

    try:
        with open(filename, "wb") as f:
            while True:
                chunk = await websocket.receive_bytes()
                f.write(chunk)
                
                # 큐 오버플로우 방지 (간단한 방식)
                if audio_queue.qsize() > 5:
                    try:
                        audio_queue.get_nowait()  # 오래된 청크 제거
                    except Empty:
                        pass
                
                audio_queue.put(chunk)

    except WebSocketDisconnect:
        print("🔌 클라이언트 마이크 연결 종료")

    except Exception as e:
        print(f"❌ 오디오 송신 예외: {e}")

    finally:
        # 워커 종료
        audio_worker_running = False
        if audio_worker_thread and audio_worker_thread.is_alive():
            audio_worker_thread.join(timeout=1.0)
        
        # 큐 비우기
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
            except Empty:
                break
        
        print("🛑 오디오 송신 정리 완료")