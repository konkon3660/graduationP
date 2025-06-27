# routers/ws_router.py
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.command_service import handle_command_async
from services.ultrasonic_service import get_distance_data
from services.auto_play_service import auto_play_service
from services.settings_service import settings_service
from services.feed_scheduler import feed_scheduler
from services.feed_service import feed_multiple
import asyncio
import weakref

logger = logging.getLogger(__name__)

router = APIRouter()
observer_websockets = weakref.WeakSet()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("🔗 WebSocket 연결 시도 감지")
    
    try:
        await websocket.accept()
    except Exception as e:
        logger.error(f"❌ WebSocket accept 실패: {e}")
        return
    role = "client"
    try:
        # 최초 메시지로 observer 등록 요청이 오면 observer로 처리
        try:
            first_msg = await asyncio.wait_for(websocket.receive_text(), timeout=1)
            try:
                first_data = json.loads(first_msg)
                if first_data.get("type") == "register" and first_data.get("role") == "observer":
                    role = "observer"
                    observer_websockets.add(websocket)
                    logger.info("👀 observer로 등록된 클라이언트 (총 %d명)", len(observer_websockets))
            except Exception as e:
                logger.warning(f"observer 등록 파싱 실패: {e}")
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.error(f"❌ observer 등록 대기 중 예외: {e}")
    except Exception as e:
        logger.error(f"❌ observer 등록 예외: {e}")

    if role == "client":
        try:
            auto_play_service.register_client(websocket)
            logger.info("👤 자동 놀이 서비스에 클라이언트 등록됨")
        except Exception as e:
            logger.error(f"❌ 클라이언트 등록 예외: {e}")

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
    try:
        while True:
            try:
                if message_count == 0 and role == "observer":
                    message_count += 1
                    continue
                try:
                    message = await websocket.receive_text()
                except Exception as e:
                    logger.error(f"❌ receive_text 예외: {e}")
                    break
                message_count += 1
                try:
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
                    if command_data.get("type") == "ultrasonic" and command_data.get("action") in ["get_distance", "get_distance_data"]:
                        distance_data = get_distance_data()
                        if distance_data.get("distance") is not None:
                            response = {"type": "ultrasonic", "distance": distance_data["distance"]}
                        else:
                            error_msg = distance_data.get("error", "측정 실패")
                            response = {"type": "ultrasonic", "error": error_msg}
                        await websocket.send_text(json.dumps(response, ensure_ascii=False))
                        logger.info(f"📏 초음파 센서 데이터 전송: {response}")
                        continue

                    # 급식 설정 명령 처리
                    if "mode" in command_data:
                        try:
                            # 설정 업데이트
                            new_settings = {
                                "mode": command_data["mode"],
                                "amount": int(command_data.get("amount", 1)),
                            }
                            
                            if command_data["mode"] == "auto" and "interval" in command_data:
                                new_settings["interval"] = int(command_data["interval"])
                            
                            # 설정 저장
                            settings_service.update_settings(new_settings)
                            
                            if command_data["mode"] == "auto":
                                # 자동 모드 시작
                                await feed_scheduler.start()
                                feed_scheduler.reset_schedule()  # 스케줄 초기화
                            else:
                                # 수동 모드: amount만큼 급식
                                await feed_multiple(new_settings["amount"])
                                # 자동 스케줄러 중지
                                await feed_scheduler.stop()
                            
                            # 안드로이드 앱을 위한 ack 응답
                            await websocket.send_text(f"ack:settings_updated")
                            
                            # observer들에게 표정 변경 알림
                            face_msg = {"type": "face", "state": "food-on"}
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg))
                                    logger.info(f"🟢 observer에게 표정(food-on) 전송")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                            
                            continue
                        except Exception as e:
                            logger.error(f"❌ 급식 설정 처리 실패: {e}")
                            await websocket.send_text(f"ack:error:{str(e)}")
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

                    # 명령 처리 후 표정 관련 브로드캐스트 예시
                    if role == "client":
                        # 예: 레이저 ON
                        if command_data.get("type") == "laser" and command_data.get("action") == "on":
                            face_msg = {"type": "face", "state": "laser-on"}
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg, ensure_ascii=False))
                                    logger.info(f"🟢 observer에게 표정(laser-on) 전송: {obs_ws}")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                                    try:
                                        observer_websockets.discard(obs_ws)
                                    except Exception:
                                        pass
                        # 예: 레이저 OFF
                        if command_data.get("type") == "laser" and command_data.get("action") == "off":
                            face_msg = {"type": "face", "state": "happy"}
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg, ensure_ascii=False))
                                    logger.info(f"🟢 observer에게 표정(happy) 전송: {obs_ws}")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                                    try:
                                        observer_websockets.discard(obs_ws)
                                    except Exception:
                                        pass
                        # 예: 솔레노이드/공 발사
                        if command_data.get("type") in ["fire", "solenoid"]:
                            face_msg = {"type": "face", "state": "ball-fired"}
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg, ensure_ascii=False))
                                    logger.info(f"🟢 observer에게 표정(ball-fired) 전송: {obs_ws}")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                                    try:
                                        observer_websockets.discard(obs_ws)
                                    except Exception:
                                        pass
                        # 예: 밥 주기
                        if command_data.get("type") in ["food", "feed", "feed_now", "dispense"]:
                            face_msg = {"type": "face", "state": "food-on"}
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg, ensure_ascii=False))
                                    logger.info(f"🟢 observer에게 표정(food-on) 전송: {obs_ws}")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                                    try:
                                        observer_websockets.discard(obs_ws)
                                    except Exception:
                                        pass
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 문자열 명령 처리
                    logger.info(f"📨 문자열 명령 수신: {message}")
                    logger.info(f"🔍 현재 role: {role}, observer 수: {len(observer_websockets)}")
                    try:
                        success = await handle_command_async(message)
                    except Exception as e:
                        logger.error(f"❌ 문자열 명령 처리 중 예외: {e}")
                        await websocket.send_text(json.dumps({"success": False, "error": str(e), "command": message, "message": "문자열 명령 처리 중 예외"}, ensure_ascii=False))
                        continue
                    # 기존 호환성을 위해 그대로 응답
                    await websocket.send_text(json.dumps({"success": success, "command": message, "message": "명령 처리 완료" if success else "명령 처리 실패"}, ensure_ascii=False))
                    logger.info(f"✅ 문자열 명령 처리 완료: {success}")

                    # 문자열 명령 처리 후 표정 관련 브로드캐스트
                    if role == "client":
                        logger.info(f"🎭 클라이언트 명령으로 표정 브로드캐스트 시도 (observer 수: {len(observer_websockets)})")
                        # 레이저 ON
                        if message == "laser_on":
                            face_msg = {"type": "face", "state": "laser-on"}
                            logger.info(f"🔴 레이저 ON 표정 브로드캐스트 시작")
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg, ensure_ascii=False))
                                    logger.info(f"🟢 observer에게 표정(laser-on) 전송")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                                    try:
                                        observer_websockets.discard(obs_ws)
                                    except Exception:
                                        pass
                        # 레이저 OFF
                        elif message == "laser_off":
                            face_msg = {"type": "face", "state": "happy"}
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg, ensure_ascii=False))
                                    logger.info(f"🟢 observer에게 표정(happy) 전송")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                                    try:
                                        observer_websockets.discard(obs_ws)
                                    except Exception:
                                        pass
                        # 급식 명령
                        elif message == "feed" or message.startswith("feed:"):
                            face_msg = {"type": "face", "state": "food-on"}
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg, ensure_ascii=False))
                                    logger.info(f"🟢 observer에게 표정(food-on) 전송")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                                    try:
                                        observer_websockets.discard(obs_ws)
                                    except Exception:
                                        pass
                        # 발사 명령
                        elif message == "fire":
                            face_msg = {"type": "face", "state": "ball-fired"}
                            for obs_ws in list(observer_websockets):
                                try:
                                    await obs_ws.send_text(json.dumps(face_msg, ensure_ascii=False))
                                    logger.info(f"🟢 observer에게 표정(ball-fired) 전송")
                                except Exception as e:
                                    logger.warning(f"❌ observer 전송 실패: {e}")
                                    try:
                                        observer_websockets.discard(obs_ws)
                                    except Exception:
                                        pass
                        else:
                            logger.info(f"📝 표정 매핑되지 않은 명령: {message}")
                    else:
                        logger.info(f"👀 observer 명령이므로 표정 브로드캐스트 건너뜀")
                except Exception as e:
                    logger.error(f"❌ 메시지 처리 중 오류: {e}")
                    continue
            except Exception as e:
                logger.error(f"❌ 메시지 루프 최상위 예외: {e}")
                break
    finally:
        try:
            if role == "observer":
                try:
                    observer_websockets.discard(websocket)
                except Exception:
                    pass
                logger.info("👀 observer 해제 (총 %d명)", len(observer_websockets))
            if role == "client":
                try:
                    auto_play_service.unregister_client(websocket)
                except Exception as e:
                    logger.error(f"❌ 클라이언트 해제 중 오류: {e}")
                logger.info("👤 자동 놀이 서비스에서 클라이언트 해제됨")
        except Exception as e:
            logger.error(f"❌ 클라이언트 해제 최상위 예외: {e}")
        logger.info(f"🔗 WebSocket 연결 종료 (총 {message_count}개 메시지 처리)")
