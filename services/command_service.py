# services/command_service.py
import logging
import asyncio

logger = logging.getLogger(__name__)

def _laser_on():
    logger.info("🔴 레이저 ON (하드웨어 동작)")

def _laser_off():
    logger.info("⚫ 레이저 OFF (하드웨어 동작)")

def _fire():
    logger.info("🔥 발사 장치 동작 (하드웨어 동작)")

def _feed_now():
    logger.info("🍚 사료 배급 (하드웨어 동작)")

def _move_motor(direction):
    logger.info(f"🕹️ 모터 이동: {direction} (하드웨어 동작)")

def _laser_xy(x, y):
    logger.info(f"🎯 레이저 각도 이동: X={x}, Y={y} (하드웨어 동작)")

def _reset():
    logger.info("🔄 시스템 리셋 (하드웨어 동작)")

async def handle_command_async(command: str) -> None:
    """
    명령 문자열에 따라 실제 하드웨어 동작을 실행.
    어떤 명령이 와도 클라이언트에는 받은 명령을 그대로 반환함.
    """
    try:
        cmd = command.strip().lower()
        if cmd == "laser_on":
            _laser_on()
        elif cmd == "laser_off":
            _laser_off()
        elif cmd == "fire":
            _fire()
        elif cmd == "feed_now":
            _feed_now()
        elif cmd == "reset":
            _reset()
        elif cmd == "stop":
            _move_motor("stop")
        elif cmd in ["forward", "backward", "left", "right"]:
            _move_motor(cmd)
        elif cmd.startswith("laser_xy:"):
            # 예시: laser_xy:90,120
            try:
                value = cmd.split(":")[1]
                x_str, y_str = value.split(",")
                x = int(x_str)
                y = int(y_str)
                _laser_xy(x, y)
            except Exception as e:
                logger.error(f"레이저 XY 파싱 오류: {e}")
        elif cmd == "audio_receive_on":
            logger.info("🎧 오디오 수신 시작 (하드웨어 동작)")
        elif cmd == "audio_receive_off":
            logger.info("🎧 오디오 수신 종료 (하드웨어 동작)")
        else:
            logger.warning(f"알 수 없는 명령: {command}")
    except Exception as e:
        logger.error(f"명령 처리 오류: {e}")
