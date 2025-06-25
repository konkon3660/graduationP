# routers/ws_router.py
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.command_service import handle_command_async
from services.ultrasonic_service import get_distance_data
from services.auto_play_service import auto_play_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("🔗 WebSocket 연결 시도 감지")
    
    try:
        await websocket.accept()
        logger.info("🔗 WebSocket 클라이언트 연결됨")
        
        # 자동 놀이 서비스에 클라이언트 등록
        auto_play_service.register_client(websocket)
        logger.info("👤 자동 놀이 서비스에 클라이언트 등록됨")
        
        # 연결 시 현재 상태 정보 전송
        try:
            status_info = {
                "type": "init",
                "auto_play_status": auto_play_service.get_status(),
                "message": "클라이언트 연결됨"
            }
            await websocket.send_text(json.dumps(status_info, ensure_ascii=False))
            logger.info("📊 초기 상태 정보 전송됨")
        except Exception as e:
            logger.error(f"❌ 초기 상태 전송 실패: {e}")
        
        # 메시지 수신 루프
        message_count = 0
        while True:
            try:
                # 클라이언트에서 받은 메시지
                message = await websocket.receive_text()
                message_count += 1
                logger.info(f"📨 메시지 #{message_count} 수신: {message[:100]}...")
                try:
                    # JSON 형식인지 확인
                    command_data = json.loads(message)
                    logger.info(f"📨 JSON 명령 수신: {command_data}")

                    # 자동 놀이 상태 조회 요청인지 확인
                    if command_data.get("type") == "get_auto_play_status":
                        status_info = {
                            "type": "auto_play_status",
                            "auto_play_status": auto_play_service.get_status()
                        }
                        await websocket.send_text(json.dumps(status_info, ensure_ascii=False))
                        logger.info("📊 자동 놀이 상태 정보 전송됨")
                        continue

                    # 초음파 센서 데이터 요청인지 확인
                    if command_data.get("type") == "ultrasonic" and command_data.get("action") == "get_distance_data":
                        distance_data = get_distance_data()
                        if distance_data.get("distance") is not None:
                            response = {"type": "ultrasonic", "distance": distance_data["distance"]}
                        else:
                            error_msg = distance_data.get("error", "측정 실패")
                            response = {"type": "ultrasonic", "error": error_msg}
                        await websocket.send_text(json.dumps(response, ensure_ascii=False))
                        logger.info(f"📏 초음파 센서 데이터 전송: {response}")
                        continue

                    # JSON 명령 처리
                    try:
                        success = await handle_command_async(command_data)
                    except Exception as e:
                        logger.error(f"❌ 명령 처리 중 예외: {e}")
                        await websocket.send_text(json.dumps({"success": False, "error": str(e), "command": command_data, "message": "명령 처리 중 예외"}, ensure_ascii=False))
                        continue

                    # 응답 전송
                    response = {
                        "success": success,
                        "command": command_data,
                        "message": "명령 처리 완료" if success else "명령 처리 실패"
                    }
                    if not success:
                        response["error"] = "명령 처리 실패"
                    await websocket.send_text(json.dumps(response, ensure_ascii=False))
                    logger.info(f"✅ JSON 명령 처리 완료: {success}")

                except json.JSONDecodeError:
                    # JSON이 아닌 경우 문자열 명령으로 처리
                    logger.info(f"📨 문자열 명령 수신: {message}")

                    # 초음파 센서 거리 측정 명령인지 확인
                    if message == "get_distance":
                        distance_data = get_distance_data()
                        if distance_data.get("distance") is not None:
                            response = {"type": "ultrasonic", "distance": distance_data["distance"]}
                        else:
                            error_msg = distance_data.get("error", "측정 실패")
                            response = {"type": "ultrasonic", "error": error_msg}
                        await websocket.send_text(json.dumps(response, ensure_ascii=False))
                        logger.info(f"📏 초음파 센서 데이터 전송: {response}")
                        continue

                    # 문자열 명령 처리
                    try:
                        success = await handle_command_async(message)
                    except Exception as e:
                        logger.error(f"❌ 문자열 명령 처리 중 예외: {e}")
                        await websocket.send_text(json.dumps({"success": False, "error": str(e), "command": message, "message": "명령 처리 중 예외"}, ensure_ascii=False))
                        continue

                    # 기존 호환성을 위해 그대로 응답
                    await websocket.send_text(json.dumps({"success": success, "command": message, "message": "명령 처리 완료" if success else "명령 처리 실패"}, ensure_ascii=False))
                    logger.info(f"✅ 문자열 명령 처리 완료: {success}")

            except WebSocketDisconnect:
                logger.info("🔌 WebSocket 클라이언트 연결 해제됨")
                break
            except Exception as e:
                logger.error(f"❌ 메시지 처리 중 오류: {e}")
                # 오류 발생 시에도 연결 유지, 클라이언트에 에러 메시지 전송
                try:
                    await websocket.send_text(json.dumps({"success": False, "error": str(e), "message": "서버 내부 오류"}, ensure_ascii=False))
                except Exception:
                    pass
                continue
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket 클라이언트 연결 해제됨")
    except Exception as e:
        logger.error(f"❌ WebSocket 연결/처리 오류: {e}")
    finally:
        # 자동 놀이 서비스에서 클라이언트 해제
        try:
            auto_play_service.unregister_client(websocket)
            logger.info("👤 자동 놀이 서비스에서 클라이언트 해제됨")
        except Exception as e:
            logger.error(f"❌ 클라이언트 해제 중 오류: {e}")
        logger.info(f"🔗 WebSocket 연결 종료 (총 {message_count}개 메시지 처리)")
