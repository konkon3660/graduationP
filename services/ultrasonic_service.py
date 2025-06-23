import RPi.GPIO as GPIO
import time
import logging

logger = logging.getLogger(__name__)

# 초음파 센서 핀 설정
TRIG_PIN = 6  # TRIG 핀 (PIN 31)
ECHO_PIN = 7  # ECHO 핀 (PIN 26)

class UltrasonicSensor:
    def __init__(self):
        self.trig_pin = TRIG_PIN
        self.echo_pin = ECHO_PIN
        self.setup_pins()
        
    def setup_pins(self):
        """초음파 센서 핀 초기화"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trig_pin, GPIO.LOW)
            logger.info("🔧 초음파 센서 핀 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 초음파 센서 핀 초기화 실패: {e}")
            
    def measure_distance(self):
        """거리 측정 (cm 단위)"""
        try:
            # TRIG 핀을 HIGH로 설정하여 초음파 발사
            GPIO.output(self.trig_pin, GPIO.HIGH)
            time.sleep(0.00001)  # 10 마이크로초 대기
            GPIO.output(self.trig_pin, GPIO.LOW)
            
            # ECHO 핀이 HIGH가 될 때까지 대기 (초음파 발사 시작)
            start_time = time.time()
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                start_time = time.time()
                if time.time() - start_time > 1:  # 1초 타임아웃
                    logger.warning("⚠️ 초음파 센서 타임아웃 (발사)")
                    return None
            
            # ECHO 핀이 LOW가 될 때까지 대기 (초음파 수신 완료)
            stop_time = time.time()
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                stop_time = time.time()
                if time.time() - start_time > 1:  # 1초 타임아웃
                    logger.warning("⚠️ 초음파 센서 타임아웃 (수신)")
                    return None
            
            # 거리 계산 (음속: 343m/s, 왕복 거리이므로 2로 나눔)
            duration = stop_time - start_time
            distance = (duration * 34300) / 2  # cm 단위
            
            # 유효한 거리 범위 확인 (2cm ~ 400cm)
            if 2 <= distance <= 400:
                logger.info(f"📏 거리 측정: {distance:.1f}cm")
                return round(distance, 1)
            else:
                logger.warning(f"⚠️ 측정된 거리가 범위를 벗어남: {distance:.1f}cm")
                return None
                
        except Exception as e:
            logger.error(f"❌ 거리 측정 실패: {e}")
            return None
    
    def get_distance_data(self):
        """클라이언트 전송용 거리 데이터 반환"""
        distance = self.measure_distance()
        if distance is not None:
            return {
                "type": "ultrasonic_distance",
                "distance": distance,
                "unit": "cm",
                "timestamp": time.time()
            }
        else:
            return {
                "type": "ultrasonic_distance",
                "distance": None,
                "error": "측정 실패",
                "timestamp": time.time()
            }
    
    def cleanup(self):
        """핀 정리"""
        try:
            GPIO.output(self.trig_pin, GPIO.LOW)
            logger.info("🧹 초음파 센서 핀 정리 완료")
        except Exception as e:
            logger.error(f"❌ 초음파 센서 핀 정리 실패: {e}")

# 전역 인스턴스
ultrasonic_sensor = UltrasonicSensor()

def get_distance():
    """거리 측정 함수 (외부 호출용)"""
    return ultrasonic_sensor.measure_distance()

def get_distance_data():
    """거리 데이터 반환 함수 (외부 호출용)"""
    return ultrasonic_sensor.get_distance_data()

def cleanup_ultrasonic():
    """초음파 센서 정리 함수 (외부 호출용)"""
    ultrasonic_sensor.cleanup()

# 아래 코드는 async 함수로 이동
async def handle_ultrasonic_command(command_data, websocket):
    if (
        command_data.get("type") == "ultrasonic" and command_data.get("action") in ["get_distance", "get_distance_data"]
    ):
        # 거리 데이터 측정 및 전송
        distance_data = get_distance_data()
        if distance_data.get("distance") is not None:
            response_text = f"distance: {distance_data['distance']}"
        else:
            error_msg = distance_data.get("error", "측정 실패")
            response_text = f"error: {error_msg}"
        await websocket.send_text(response_text)
        logger.info(f"📏 초음파 센서 데이터 전송: {response_text}") 