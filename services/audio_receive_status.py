# services/audio_receive_status.py
class AudioReceiveStatus:
    def __init__(self):
        self.on = False
        self.ws_clients = set()

audio_receive_status = AudioReceiveStatus()
