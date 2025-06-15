# routers/ws_router.py - 수정된 버전
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws")
async def control_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎮 [WS_ROUTER] 통합 제어 WebSocket 연결됨")
    print(f"🔗 [WS_ROUTER] 클라이언트 주소: {websocket.client}")

    # 앱 상태에서 인스턴스 가져오기
    try:
        mic_sender = websocket.app.state.mic_sender
        mic_streamer = websocket.app.state.mic_streamer
        print("✅ [WS_ROUTER] 앱 상태 인스턴스 로드 완료")
    except Exception as e:
        print(f"⚠️ [WS_ROUTER] 앱 상태 로드 실패: {e}")
        mic_sender = None
        mic_streamer = None

    try:
        while True:
            message = await websocket.receive_text()
            print(f"📨 [WS_ROUTER] 수신된 메시지: {message}")
            
            try:
                # JSON 메시지 파싱 시도
                data = json.loads(message)
                msg_type = data.get("type", "command")
                content = data.get("content", message)
                
                print(f"📋 [WS_ROUTER] 파싱됨 - 타입: {msg_type}, 내용: {content}")
                
                if msg_type == "text":
                    print(f"💬 [WS_ROUTER] 텍스트 메시지: {content}")
                    response = f"서버가 받은 메시지: {content}"
                    
                elif msg_type == "command":
                    print(f"🎮 [WS_ROUTER] 제어 명령: {content}")
                    response = await process_command(content)
                else:
                    response = f"알 수 없는 메시지 타입: {msg_type}"
                    
            except json.JSONDecodeError:
                # 일반 텍스트로 처리
                print(f"📝 [WS_ROUTER] 일반 텍스트 처리: {message}")
                response = await process_command(message)
            
            print(f"📤 [WS_ROUTER] 응답 전송: {response}")
            await websocket.send_text(response)
            
    except WebSocketDisconnect:
        print("🔌 [WS_ROUTER] 통합 제어 WebSocket 연결 종료")
    except Exception as e:
        print(f"❌ [WS_ROUTER] WebSocket 오류: {e}")
        logger.error(f"WebSocket 오류: {e}")

async def process_command(command: str) -> str:
    """명령 처리 함수"""
    try:
        if command == "laser_on":
            print("🔴 [WS_ROUTER] 레이저 ON 명령 처리")
            # 실제 레이저 제어 로직 추가 가능
            return "레이저가 켜졌습니다"
        elif command == "laser_off":
            print("⚫ [WS_ROUTER] 레이저 OFF 명령 처리")
            # 실제 레이저 제어 로직 추가 가능
            return "레이저가 꺼졌습니다"
        elif command.startswith("joystick"):
            print(f"🕹️ [WS_ROUTER] 조이스틱 명령: {command}")
            # 실제 조이스틱 제어 로직 추가 가능
            return f"조이스틱 명령 처리됨: {command}"
        else:
            print(f"📋 [WS_ROUTER] 기본 명령 처리: {command}")
            return f"명령 처리됨: {command}"
            
    except Exception as e:
        print(f"❌ [WS_ROUTER] 명령 처리 오류: {e}")
        return f"명령 처리 실패: {str(e)}"