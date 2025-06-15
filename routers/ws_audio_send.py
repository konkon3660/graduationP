# routers/ws_audio_send.py - 오디오 출력 문제 해결
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
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
    """오디오 출력 워커 - 개선된 버전"""
    global audio_worker_running
    print("🔊 [AUDIO_WORKER] 오디오 출력 워커 시작")
    
    # 오디오 출력 관리자 초기화
    from services.audio_output_service import audio_output_manager
    audio_output_manager.initialize()
    
    while audio_worker_running:
        try:
            chunk = audio_queue.get(timeout=0.5)
            if chunk:
                audio_output_manager.play_chunk(chunk)
        except Empty:
            continue
        except Exception as e:
            print(f"❌ [AUDIO_WORKER] 오디오 재생 오류: {e}")
    
    # 정리
    audio_output_manager.cleanup()
    print("🛑 [AUDIO_WORKER] 오디오 출력 워커 종료")

@router.websocket("/ws/audio_send")
async def audio_send_ws(websocket: WebSocket):
    global audio_worker_thread, audio_worker_running
    
    await websocket.accept()
    print("🎤 [AUDIO_SEND] 클라이언트 마이크 → 서버 스피커 연결됨")

    # 오디오 워커 시작
    if not audio_worker_running:
        audio_worker_running = True
        audio_worker_thread = threading.Thread(target=audio_output_worker, daemon=True)
        audio_worker_thread.start()
        print("🔊 [AUDIO_SEND] 오디오 워커 시작됨")

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_audio_{now}.pcm"

    try:
        with open(filename, "wb") as f:
            while True:
                chunk = await websocket.receive_bytes()
                f.write(chunk)
                
                # 큐 오버플로우 방지
                if audio_queue.qsize() > 5:
                    try:
                        discarded = audio_queue.get_nowait()
                        print(f"⚠️ [AUDIO_SEND] 큐 오버플로우, 오래된 청크 제거 (큐 크기: {audio_queue.qsize()})")
                    except Empty:
                        pass
                
                audio_queue.put(chunk)

    except WebSocketDisconnect:
        print("🔌 [AUDIO_SEND] 클라이언트 연결 종료")

    except Exception as e:
        print(f"❌ [AUDIO_SEND] 예외 발생: {e}")

    finally:
        # 워커 종료
        print("🛑 [AUDIO_SEND] 정리 시작...")
        audio_worker_running = False
        
        if audio_worker_thread and audio_worker_thread.is_alive():
            audio_worker_thread.join(timeout=2.0)
        
        # 큐 비우기
        cleared_count = 0
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
                cleared_count += 1
            except Empty:
                break
        
        if cleared_count > 0:
            print(f"🧹 [AUDIO_SEND] 큐에서 {cleared_count}개 청크 정리됨")
        
        print("✅ [AUDIO_SEND] 정리 완료")