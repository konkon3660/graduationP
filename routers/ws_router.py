# ws_router.py
import asyncio
import json
import logging
import websockets
from websockets.exceptions import ConnectionClosed
import threading
from queue import Queue, Empty
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ws_router')

class WebSocketRouter:
    def __init__(self):
        self.command_client = None
        self.audio_client = None
        self.server_ws = None
        self.command_queue = Queue()
        self.audio_queue = Queue()
        self.running = False
        
    async def connect_to_server(self, server_uri):
        """서버에 연결"""
        try:
            self.server_ws = await websockets.connect(server_uri)
            logger.info(f"서버에 연결됨: {server_uri}")
            return True
        except Exception as e:
            logger.error(f"서버 연결 실패: {e}")
            return False
    
    async def handle_command_client(self, websocket, path):
        """명령 클라이언트 처리 - 수정된 부분"""
        logger.info("명령 클라이언트 연결됨")
        self.command_client = websocket
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"클라이언트로부터 명령 수신: {data}")
                    
                    # 서버로 명령 전송
                    if self.server_ws:
                        await self.server_ws.send(message)
                        logger.info(f"서버로 명령 전송: {data}")
                        
                        # 서버 응답 대기 및 처리
                        try:
                            response = await asyncio.wait_for(self.server_ws.recv(), timeout=5.0)
                            response_data = json.loads(response)
                            logger.info(f"서버 응답 수신: {response_data}")
                            
                            # 응답을 클라이언트로 전송 (필터링 없이 원본 그대로)
                            await websocket.send(response)
                            logger.info(f"클라이언트로 응답 전송: {response_data}")
                            
                        except asyncio.TimeoutError:
                            error_msg = {"type": "error", "message": "서버 응답 시간 초과"}
                            await websocket.send(json.dumps(error_msg))
                            logger.warning("서버 응답 시간 초과")
                        except Exception as e:
                            error_msg = {"type": "error", "message": f"서버 응답 처리 오류: {str(e)}"}
                            await websocket.send(json.dumps(error_msg))
                            logger.error(f"서버 응답 처리 오류: {e}")
                    else:
                        error_msg = {"type": "error", "message": "서버에 연결되지 않음"}
                        await websocket.send(json.dumps(error_msg))
                        logger.warning("서버에 연결되지 않음")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 파싱 오류: {e}")
                    error_msg = {"type": "error", "message": "잘못된 JSON 형식"}
                    await websocket.send(json.dumps(error_msg))
                except Exception as e:
                    logger.error(f"메시지 처리 오류: {e}")
                    
        except ConnectionClosed:
            logger.info("명령 클라이언트 연결 종료")
        except Exception as e:
            logger.error(f"명령 클라이언트 처리 오류: {e}")
        finally:
            self.command_client = None
    
    async def handle_audio_client(self, websocket, path):
        """오디오 클라이언트 처리 - CORS 및 인증 문제 해결"""
        logger.info("오디오 클라이언트 연결 시도")
        
        # Origin 헤더 확인 및 허용
        origin = websocket.request_headers.get('Origin')
        logger.info(f"오디오 클라이언트 Origin: {origin}")
        
        # 필요시 여기서 Origin 검증 로직 추가
        # if origin not in allowed_origins:
        #     await websocket.close(code=1008, reason="Origin not allowed")
        #     return
        
        self.audio_client = websocket
        logger.info("오디오 클라이언트 연결됨")
        
        try:
            async for message in websocket:
                try:
                    if isinstance(message, bytes):
                        # 바이너리 오디오 데이터 처리
                        logger.debug(f"오디오 데이터 수신: {len(message)} bytes")
                        
                        # 서버로 오디오 데이터 전송
                        if self.server_ws:
                            await self.server_ws.send(message)
                            logger.debug("서버로 오디오 데이터 전송")
                        else:
                            logger.warning("오디오 데이터 전송 실패: 서버 연결 없음")
                    else:
                        # 텍스트 메시지 처리
                        try:
                            data = json.loads(message)
                            logger.info(f"오디오 클라이언트로부터 메시지: {data}")
                            
                            if self.server_ws:
                                await self.server_ws.send(message)
                                logger.info("서버로 오디오 메시지 전송")
                        except json.JSONDecodeError:
                            logger.warning(f"오디오 클라이언트로부터 잘못된 JSON: {message}")
                            
                except Exception as e:
                    logger.error(f"오디오 메시지 처리 오류: {e}")
                    
        except ConnectionClosed:
            logger.info("오디오 클라이언트 연결 종료")
        except Exception as e:
            logger.error(f"오디오 클라이언트 처리 오류: {e}")
        finally:
            self.audio_client = None
    
    async def handle_server_messages(self):
        """서버로부터 오는 메시지 처리 - 오디오 응답 라우팅 개선"""
        if not self.server_ws:
            return
            
        try:
            async for message in self.server_ws:
                try:
                    if isinstance(message, bytes):
                        # 바이너리 오디오 응답을 오디오 클라이언트로 전송
                        if self.audio_client:
                            await self.audio_client.send(message)
                            logger.debug(f"오디오 클라이언트로 바이너리 데이터 전송: {len(message)} bytes")
                        else:
                            logger.warning("오디오 응답을 받을 클라이언트가 없음")
                    else:
                        # 텍스트 메시지 처리
                        try:
                            data = json.loads(message)
                            message_type = data.get('type', '')
                            
                            logger.info(f"서버로부터 메시지 수신: {data}")
                            
                            # 오디오 관련 메시지는 오디오 클라이언트로
                            if message_type in ['audio_response', 'speech_start', 'speech_end', 'audio_status']:
                                if self.audio_client:
                                    await self.audio_client.send(message)
                                    logger.info(f"오디오 클라이언트로 메시지 전송: {message_type}")
                                else:
                                    logger.warning(f"오디오 메시지를 받을 클라이언트가 없음: {message_type}")
                            
                            # 명령 응답은 명령 클라이언트로 (이미 handle_command_client에서 처리됨)
                            elif message_type == 'command_response':
                                # 이미 handle_command_client에서 직접 처리하므로 여기서는 로깅만
                                logger.debug(f"명령 응답 처리됨: {data.get('command', 'unknown')}")
                            
                            # 기타 메시지는 적절한 클라이언트로 라우팅
                            else:
                                # 기본적으로 명령 클라이언트로 전송
                                if self.command_client:
                                    await self.command_client.send(message)
                                    logger.info(f"명령 클라이언트로 기타 메시지 전송: {message_type}")
                                    
                        except json.JSONDecodeError:
                            logger.warning(f"서버로부터 잘못된 JSON: {message}")
                            
                except Exception as e:
                    logger.error(f"서버 메시지 처리 오류: {e}")
                    
        except ConnectionClosed:
            logger.info("서버 연결 종료")
        except Exception as e:
            logger.error(f"서버 메시지 처리 오류: {e}")
    
    async def start_command_server(self, host='localhost', port=8765):
        """명령 서버 시작"""
        logger.info(f"명령 서버 시작: {host}:{port}")
        return await websockets.serve(
            self.handle_command_client, 
            host, 
            port,
            # CORS 설정 추가
            extra_headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    
    async def start_audio_server(self, host='localhost', port=8766):
        """오디오 서버 시작 - CORS 문제 해결"""
        logger.info(f"오디오 서버 시작: {host}:{port}")
        
        async def audio_handler(websocket, path):
            # CORS 헤더 설정
            websocket.response_headers['Access-Control-Allow-Origin'] = '*'
            websocket.response_headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            websocket.response_headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
            await self.handle_audio_client(websocket, path)
        
        return await websockets.serve(
            audio_handler,
            host, 
            port,
            # 추가 CORS 설정
            extra_headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS", 
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    
    async def run(self, server_uri, command_port=8765, audio_port=8766):
        """라우터 실행"""
        self.running = True
        
        # 서버 연결
        if not await self.connect_to_server(server_uri):
            logger.error("서버 연결 실패")
            return
        
        # 서버들 시작
        command_server = await self.start_command_server(port=command_port)
        audio_server = await self.start_audio_server(port=audio_port)
        
        logger.info("WebSocket 라우터가 시작되었습니다")
        logger.info(f"명령 서버: ws://localhost:{command_port}")
        logger.info(f"오디오 서버: ws://localhost:{audio_port}")
        
        try:
            # 서버 메시지 처리 태스크 시작
            server_task = asyncio.create_task(self.handle_server_messages())
            
            # 서버들이 계속 실행되도록 대기
            await asyncio.gather(
                server_task,
                command_server.wait_closed(),
                audio_server.wait_closed()
            )
        except KeyboardInterrupt:
            logger.info("사용자에 의해 중단됨")
        except Exception as e:
            logger.error(f"라우터 실행 오류: {e}")
        finally:
            self.running = False
            if self.server_ws:
                await self.server_ws.close()
            command_server.close()
            audio_server.close()
            logger.info("WebSocket 라우터가 종료되었습니다")

# 메인 실행
async def main():
    router = WebSocketRouter()
    server_uri = "ws://localhost:8080/ws"  # 실제 서버 주소로 변경
    
    await router.run(server_uri)

if __name__ == "__main__":
    asyncio.run(main())