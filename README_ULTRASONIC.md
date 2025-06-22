# 📏 초음파 센서 사용 가이드

## 🔧 하드웨어 연결

### 필요한 부품
- HC-SR04 초음파 센서 모듈
- 점퍼 와이어 4개
- 브레드보드 (선택사항)

### 핀 연결
| 초음파 센서 | 라즈베리 파이 | 설명 |
|------------|---------------|------|
| VCC | PIN 2 (5V) | 전원 공급 |
| TRIG | PIN 31 (GPIO 6) | 초음파 발사 신호 |
| ECHO | PIN 26 (GPIO 7) | 초음파 수신 신호 |
| GND | PIN 6 (GND) | 접지 |

### 연결 다이어그램
```
초음파 센서 HC-SR04
┌─────────────┐
│    VCC ──── 5V (PIN 2)     │
│   TRIG ──── GPIO 6 (PIN 31) │
│   ECHO ──── GPIO 7 (PIN 26) │
│    GND ──── GND (PIN 6)     │
└─────────────┘
```

## 🚀 소프트웨어 사용법

### 1. 기본 사용법

#### Python에서 직접 사용
```python
from services.ultrasonic_service import get_distance, get_distance_data

# 거리 측정 (cm 단위)
distance = get_distance()
if distance:
    print(f"거리: {distance}cm")
else:
    print("측정 실패")

# 클라이언트 전송용 데이터
data = get_distance_data()
print(data)
# 출력: {"type": "ultrasonic_distance", "distance": 25.3, "unit": "cm", "timestamp": 1234567890.123}
```

#### 클래스 사용
```python
from services.ultrasonic_service import UltrasonicSensor

# 센서 인스턴스 생성
sensor = UltrasonicSensor()

# 거리 측정
distance = sensor.measure_distance()
print(f"거리: {distance}cm")

# 정리
sensor.cleanup()
```

### 2. 웹소켓 명령

#### 문자열 명령
```
get_distance
```

#### JSON 명령
```json
{
    "type": "ultrasonic",
    "action": "get_distance"
}
```

```json
{
    "type": "ultrasonic",
    "action": "get_distance_data"
}
```

### 3. 웹소켓 응답 형식

#### 성공 시
```json
{
    "type": "ultrasonic_distance",
    "distance": 25.3,
    "unit": "cm",
    "timestamp": 1234567890.123
}
```

#### 실패 시
```json
{
    "type": "ultrasonic_distance",
    "distance": null,
    "error": "측정 실패",
    "timestamp": 1234567890.123
}
```

## 🧪 테스트

### 1. 하드웨어 테스트
```bash
python test_ultrasonic.py
```

### 2. 웹소켓 테스트
1. 서버 실행
2. 브라우저에서 `test_ultrasonic_websocket.html` 파일 열기
3. "연결" 버튼 클릭
4. "거리 측정" 버튼 클릭하여 실시간 거리 확인

## ⚙️ 설정 및 옵션

### 측정 범위
- **최소 거리**: 2cm
- **최대 거리**: 400cm
- **정확도**: ±1cm

### 타임아웃 설정
- **발사 타임아웃**: 1초
- **수신 타임아웃**: 1초

### 측정 주기
- **권장 간격**: 0.5초 이상
- **최소 간격**: 0.1초

## 🔍 문제 해결

### 1. 측정이 실패하는 경우
- **하드웨어 연결 확인**: TRIG, ECHO 핀이 올바르게 연결되었는지 확인
- **전원 공급 확인**: 5V 전원이 안정적으로 공급되는지 확인
- **센서 위치 확인**: 센서가 측정 대상과 수직으로 설치되었는지 확인

### 2. 측정값이 부정확한 경우
- **환경 요인**: 온도, 습도, 공기 흐름 등이 측정에 영향을 줄 수 있음
- **반사면**: 측정 대상의 표면이 초음파를 잘 반사하는지 확인
- **간섭**: 다른 초음파 센서나 소음원이 있는지 확인

### 3. 타임아웃 오류
- **거리 확인**: 측정 대상이 400cm 이내에 있는지 확인
- **센서 상태**: 센서가 손상되지 않았는지 확인
- **연결 상태**: 와이어 연결이 느슨하지 않은지 확인

## 📊 성능 최적화

### 1. 측정 정확도 향상
```python
# 여러 번 측정하여 평균값 사용
def get_average_distance(samples=5):
    distances = []
    for _ in range(samples):
        distance = get_distance()
        if distance:
            distances.append(distance)
        time.sleep(0.1)
    
    if distances:
        return sum(distances) / len(distances)
    return None
```

### 2. 연속 모니터링
```python
import time
from services.ultrasonic_service import get_distance

def monitor_distance(duration=60, interval=1):
    """지정된 시간 동안 거리를 모니터링"""
    start_time = time.time()
    
    while time.time() - start_time < duration:
        distance = get_distance()
        if distance:
            print(f"거리: {distance}cm")
        else:
            print("측정 실패")
        time.sleep(interval)
```

## 🔧 고급 설정

### 1. 핀 번호 변경
`services/ultrasonic_service.py` 파일에서 핀 번호를 수정할 수 있습니다:

```python
# 초음파 센서 핀 설정
TRIG_PIN = 6  # TRIG 핀 (PIN 31)
ECHO_PIN = 7  # ECHO 핀 (PIN 26)
```

### 2. 측정 범위 조정
```python
# 유효한 거리 범위 확인 (2cm ~ 400cm)
if 2 <= distance <= 400:
    return round(distance, 1)
```

### 3. 타임아웃 조정
```python
# 타임아웃 설정 (초 단위)
if time.time() - start_time > 1:  # 1초 타임아웃
    logger.warning("⚠️ 초음파 센서 타임아웃")
    return None
```

## 📝 주의사항

### 1. 하드웨어 주의사항
- **전압 레벨**: ECHO 핀은 3.3V 로직 레벨을 사용하므로 5V 신호를 직접 연결하지 마세요
- **전류 공급**: 센서는 약 15mA의 전류를 소모합니다
- **온도 영향**: 온도가 변하면 음속이 변하여 측정값에 영향을 줄 수 있습니다

### 2. 소프트웨어 주의사항
- **동시 사용**: 여러 프로세스에서 동시에 센서를 사용하지 마세요
- **리소스 정리**: 사용 후에는 `cleanup()` 함수를 호출하여 GPIO를 정리하세요
- **예외 처리**: 측정 실패 시 적절한 예외 처리를 구현하세요

### 3. 환경 주의사항
- **습도**: 높은 습도는 초음파 전파에 영향을 줄 수 있습니다
- **온도**: 극한 온도에서는 센서 성능이 저하될 수 있습니다
- **진동**: 센서가 진동하면 측정값이 불안정할 수 있습니다

## 🔗 관련 파일

- `services/ultrasonic_service.py`: 초음파 센서 서비스
- `services/command_service.py`: 명령 처리 서비스 (초음파 센서 명령 포함)
- `routers/ws_router.py`: 웹소켓 라우터 (초음파 센서 데이터 전송)
- `test_ultrasonic.py`: 하드웨어 테스트 코드
- `test_ultrasonic_websocket.html`: 웹소켓 테스트 페이지
- `HARDWARE_PIN_MAPPING.md`: 핀 매핑 문서

## 📞 지원

문제가 발생하거나 추가 기능이 필요한 경우, 다음을 확인하세요:

1. 하드웨어 연결 상태
2. 로그 메시지 확인
3. 테스트 코드 실행
4. 문서 재검토

초음파 센서는 안정적이고 정확한 거리 측정을 제공하며, 다양한 응용 분야에서 활용할 수 있습니다. 