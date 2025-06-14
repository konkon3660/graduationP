import asyncio
from .audio_service import set_audio_streaming,get_audio_streaming
import laser_service
import moter_service  # 모터 제어 모듈 import
import sol_service
from . import mic_service
from services import microphone_sender_instance
from services.microphone_sender_instance import mic_streamer

async def handle_command(command: str) -> str:
    if command == "laser_on":
        laser_service.laser_on()
        return "ack: laser_on 실행됨"

    elif command == "laser_off":
        laser_service.laser_off()
        return "ack: laser_off 실행됨"

    elif command == "fire":
        sol_service.fire()
        return "ack: fire 실행됨"

    elif command == "forward":
        moter_service.set_right_motor(80, 0)  # 80% 속도, 정방향
        moter_service.set_left_motor(80, 0)
        return "ack: forward 이동"

    elif command == "backward":
        moter_service.set_right_motor(80, 1)  # 역방향
        moter_service.set_left_motor(80, 1)
        return "ack: backward 이동"

    elif command == "left":
        moter_service.set_right_motor(80, 0)
        moter_service.set_left_motor(80, 1)
        return "ack: left 회전"

    elif command == "right":
        moter_service.set_right_motor(80, 1)
        moter_service.set_left_motor(80, 0)
        return "ack: right 회전"

    elif command == "stop":
        moter_service.stop_motors()
        return "ack: 정지됨"

    elif command == "audio_send":
        mic_streamer.start()
        return "ack: 음성 전송 시작됨"
    
    elif command == "audio_send_stop":
        mic_streamer.start()
        return "ack: 음성 전송 시작됨"

    elif command == "audio_receive_on":
        microphone_sender_instance.mic_streamer.start()
        set_audio_streaming(True)
        return "ack: 음성 수신 ON"

    elif command == "audio_receive_off":
        microphone_sender_instance.mic_streamer.stop()
        set_audio_streaming(False)
        return "ack: 음성 수신 OFF"

    else:
        return f"ack: 알 수 없는 명령: {command}"
