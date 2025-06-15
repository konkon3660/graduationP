# routers/ws_router.py - 강화된 디버깅
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

@router.websocket("/ws")
async def control_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎮 [WS_ROUTER] 통합 제어 WebSocket 연결됨")
    print(f"🔗 [WS_ROUTER] 클라이언트 주소: {websocket.client}")

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
                    
                    # 명령어별 처리
                    if content == "laser_on":
                        print("🔴 [WS_ROUTER] 레이저 ON 명령 처리")
                        response = "레이저가 켜졌습니다"
                    elif content == "laser_off":
                        print("⚫ [WS_ROUTER] 레이저 OFF 명령 처리")
                        response = "레이저가 꺼졌습니다"
                    elif content.startswith("joystick"):
                        print(f"🕹️ [WS_ROUTER] 조이스틱 명령: {content}")
                        response = f"조이스틱 명령 처리됨: {content}"
                    else:
                        # 기존 command_service 사용
                        try:
                            from services.command_service import handle_command
                            response = await handle_command(content, websocket)
                        except ImportError:
                            print("⚠️ [WS_ROUTER] command_service 모듈 없음")
                            response = f"명령 처리됨: {content}"
                else:
                    response = f"알 수 없는 메시지 타입: {msg_type}"
                    
            except json.JSONDecodeError:
                # 일반 텍스트로 처리
                print(f"📝 [WS_ROUTER] 일반 텍스트 처리: {message}")
                
                if message == "laser_on":
                    print("🔴 [WS_ROUTER] 레이저 ON (일반 텍스트)")
                    response = "레이저가 켜졌습니다"
                elif message == "laser_off":
                    print("⚫ [WS_ROUTER] 레이저 OFF (일반 텍스트)")
                    response = "레이저가 꺼졌습니다"
                elif message.startswith("joystick"):
                    print(f"🕹️ [WS_ROUTER] 조이스틱 (일반 텍스트): {message}")
                    response = f"조이스틱 명령 처리됨: {message}"
                else:
                    try:
                        from services.command_service import handle_command
                        response = await handle_command(message, websocket)
                    except ImportError:
                        print("⚠️ [WS_ROUTER] command_service 모듈 없음")
                        response = f"명령 처리됨: {message}"
            
            print(f"📤 [WS_ROUTER] 응답 전송: {response}")
            await websocket.send_text(response)
            
    except WebSocketDisconnect:
        print("🔌 [WS_ROUTER] 통합 제어 WebSocket 연결 종료")
    except Exception as e:
        print(f"❌ [WS_ROUTER] WebSocket 오류: {e}")
