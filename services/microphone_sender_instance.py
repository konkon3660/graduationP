# microphone_sender_instance.py
from services.microphone_sender_service import MicrophoneSender

mic_streamer = MicrophoneSender("wss://srg2361.ngrok.app/ws/audio")
