# command_service.py
import asyncio
import json
from services import laser_service
import services.motor_service as motor_service
import sol_service
from . import mic_service
from services import microphone_sender_instance
from services.microphone_sender_instance import mic_streamer
from services import feed_settings  # 🔶 추가
from services.feed_service import feed_once

async def handle_command(command: str) -> str:
    # 먼저 JSON인지 시도
    try:
        data = json.loads(command)

        if isinstance(data, dict):
            # 급식 설정 명령인지 확인
            if "mode" in data and "interval" in data and "amount" in data:
                feed_settings.update_settings({
                    "mode": data["mode"],
                    "interval": int(data["interval"]),
                    "amount": int(data["amount"])
                })
                return f"ack: 급식 설정 적용됨 (mode={data['mode']}, interval={data['interval']}, amount={data['amount']})"
    except json.JSONDecodeError:
        pass  # JSON 형식 아님 → 문자열로 처리

    # 문자열 명령어 처리
    if command == "laser_on":
        laser_service.laser_on()
        return "ack: laser_on 실행됨"

    elif command == "laser_off":
        laser_service.laser_off()
        return "ack: laser_off 실행됨"

    elif command == "fire":
        sol_service.fire()
        return "ack: fire 실행됨"
    
    elif command == "feed_now":
        if feed_settings.feed_config["mode"] == "manual":
            feed_once()
            return "ack: 수동 급식 1회 실행됨"
        else:
            return "nak: 현재 자동 모드이므로 수동 급식 불가능"

    elif command == "forward":
        motor_service.set_right_motor(80, 0)
        motor_service.set_left_motor(80, 0)
        return "ack: forward 이동"

    elif command == "backward":
        motor_service.set_right_motor(80, 1)
        motor_service.set_left_motor(80, 1)
        return "ack: backward 이동"

    elif command == "left":
        motor_service.set_right_motor(80, 0)
        motor_service.set_left_motor(80, 1)
        return "ack: left 회전"

    elif command == "right":
        motor_service.set_right_motor(80, 1)
        motor_service.set_left_motor(80, 0)
        return "ack: right 회전"

    elif command == "stop":
        motor_service.stop_motors()
        return "ack: 정지됨"

    elif command == "audio_send":
        mic_streamer.start()
        return "ack: 음성 전송 시작됨"

    elif command == "audio_send_stop":
        mic_streamer.stop()
        return "ack: 음성 전송 중지됨"

    elif command == "audio_receive_on":
        microphone_sender_instance.mic_streamer.start()
        set_audio_streaming(True)
        return "ack: 음성 수신 ON"

    elif command == "audio_receive_off":
        microphone_sender_instance.mic_streamer.stop()
        set_audio_streaming(False)
        return "ack: 음성 수신 OFF"

    return f"ack: 알 수 없는 명령: {command}"
