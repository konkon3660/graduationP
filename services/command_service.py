# routers/ws_router.py - 텍스트 + 음성 통합 제어
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

@router.websocket("/ws")
async def control_ws(websocket: WebSocket):
    await websocket.accept()
    print("🎮 통합 제어 WebSocket 연결됨")

    try:
        while True:
            message = await websocket.receive_text()
            
            try:
                # JSON 메시지 파싱 시도
                data = json.loads(message)
                msg_type = data.get("type", "command")
                content = data.get("content", message)
                
                if msg_type == "text":
                    print(f"💬 텍스트 메시지: {content}")
                    response = f"서버가 받은 메시지: {content}"
                    
                elif msg_type == "command":
                    print(f"🎮 제어 명령: {content}")
                    from services.command_service import handle_command
                    response = await handle_command(content, websocket)
                    
                else:
                    response = f"알 수 없는 메시지 타입: {msg_type}"
                    
            except json.JSONDecodeError:
                # 일반 텍스트로 처리
                print(f"📝 일반 텍스트: {message}")
                from services.command_service import handle_command
                response = await handle_command(message, websocket)
            
            await websocket.send_text(response)
            
    except WebSocketDisconnect:
        print("🔌 통합 제어 WebSocket 연결 종료")
    except Exception as e:
        print(f"❌ WebSocket 오류: {e}")