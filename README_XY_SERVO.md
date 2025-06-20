# 🎯 XY 서보모터 제어 시스템

## 개요
스마트 반려동물 케어 로봇의 레이저 포인터를 2축(X축, Y축)으로 제어하는 서보모터 시스템입니다.

## 🔧 하드웨어 구성

### 서보모터
- **X축 서보모터**: 좌우 방향 제어 (GPIO 19, PIN 35)
- **Y축 서보모터**: 상하 방향 제어 (GPIO 13, PIN 33)
- **PWM 주파수**: 50Hz
- **각도 범위**: 0° ~ 180°

### 연결 방법
```
X축 서보모터:
- 신호선: GPIO 19 (BCM, PIN 35)
- 전원: 5V
- 접지: GND

Y축 서보모터:
- 신호선: GPIO 13 (BCM, PIN 33)
- 전원: 5V
- 접지: GND
```

## 📋 주요 기능

### 1. 초기화
```python
from services.xy_servo import init_xy_servo

# 서보모터 초기화
success = init_xy_servo()
```

### 2. 개별 축 제어
```python
from services.xy_servo import set_servo_angle

# X축 서보모터를 90도로 설정
set_servo_angle(90, "x")

# Y축 서보모터를 45도로 설정
set_servo_angle(45, "y")
```

### 3. 동시 제어
```python
from services.xy_servo import set_xy_servo_angles

# X축 90도, Y축 120도로 동시 설정
set_xy_servo_angles(90, 120)
```

### 4. 레이저 XY 좌표 제어
```python
from services.xy_servo import handle_laser_xy

# 레이저를 좌표 (100, 80)로 이동
handle_laser_xy(100, 80)
```

### 5. 중앙 위치 리셋
```python
from services.xy_servo import reset_to_center

# 서보모터를 중앙 위치(90, 90)로 리셋
reset_to_center()
```

### 6. 상태 조회
```python
from services.xy_servo import get_servo_status

# 현재 서보모터 상태 조회
status = get_servo_status()
print(status)
# 출력 예시:
# {
#     "initialized": True,
#     "current_x_angle": 90,
#     "current_y_angle": 120,
#     "pins": {"x_servo": 21, "y_servo": 20},
#     "pwm_frequency": 50
# }
```

## 🌐 WebSocket 명령

### 클라이언트에서 전송할 명령
```javascript
// 레이저 XY 좌표 제어
const x = 100;  // X 좌표 (0~180)
const y = 80;   // Y 좌표 (0~180)
const cmd = `laser_xy:${x},${y}`;

// WebSocket으로 명령 전송
websocket.send(cmd);
```

### 지원하는 명령 형식
```
laser_xy:X,Y
- X: X축 좌표 (0~180)
- Y: Y축 좌표 (0~180)
- 예시: laser_xy:90,120
```

## 🧪 테스트

### 테스트 스크립트 실행
```bash
python test_xy_servo.py
```

### 테스트 내용
1. **초기화 테스트**: 서보모터 초기화 확인
2. **상태 조회**: 현재 상태 정보 출력
3. **중앙 리셋**: 중앙 위치(90, 90)로 이동
4. **다양한 위치 테스트**: 
   - 좌상단 (0, 0)
   - 우상단 (180, 0)
   - 우하단 (180, 180)
   - 좌하단 (0, 180)
   - 중앙 (90, 90)
   - 대각선 위치들
5. **laser_xy 명령 테스트**: 다양한 좌표로 레이저 이동
6. **최종 리셋**: 테스트 완료 후 중앙 위치로 복귀

## ⚠️ 주의사항

### 1. 전원 공급
- 서보모터는 충분한 전원이 필요합니다
- 5V 전원을 안정적으로 공급하세요
- 전류 부족 시 서보모터가 제대로 동작하지 않을 수 있습니다

### 2. 각도 제한
- 각도는 0° ~ 180° 범위 내에서만 설정 가능
- 범위를 벗어나는 값은 자동으로 제한됩니다

### 3. 동작 시간
- 서보모터 이동에는 약 0.3초의 시간이 소요됩니다
- 연속적인 명령 전송 시 적절한 딜레이를 두세요

### 4. 리소스 정리
- 프로그램 종료 시 자동으로 GPIO 리소스가 정리됩니다
- 수동으로 정리하려면 `cleanup()` 함수를 호출하세요

## 🔧 문제 해결

### 서보모터가 움직이지 않는 경우
1. **전원 확인**: 5V 전원이 안정적으로 공급되는지 확인
2. **연결 확인**: GPIO 핀 연결 상태 확인
3. **초기화 확인**: `init_xy_servo()` 함수가 성공적으로 실행되었는지 확인
4. **로그 확인**: 콘솔 로그에서 오류 메시지 확인

### 서보모터가 떨리는 경우
1. **전원 안정성**: 전원 공급이 안정적인지 확인
2. **PWM 설정**: PWM 주파수가 50Hz로 설정되어 있는지 확인
3. **기계적 마찰**: 서보모터 기어에 마찰이 없는지 확인

### 각도가 정확하지 않은 경우
1. **중립점 조정**: 서보모터의 중립점을 조정
2. **각도 보정**: 실제 각도와 설정 각도의 차이를 보정
3. **기계적 백래시**: 기계적 백래시를 고려한 보정

## 📝 예제 코드

### Android 앱에서 사용 예시
```kotlin
class LaserControlActivity {
    private lateinit var webSocket: WebSocket
    
    fun moveLaser(x: Int, y: Int) {
        val command = "laser_xy:$x,$y"
        webSocket.send(command)
    }
    
    fun centerLaser() {
        moveLaser(90, 90)
    }
    
    fun moveToCorner() {
        moveLaser(0, 0)  // 좌상단
    }
}
```

### JavaScript에서 사용 예시
```javascript
class LaserController {
    constructor(websocket) {
        this.websocket = websocket;
    }
    
    moveLaser(x, y) {
        const command = `laser_xy:${x},${y}`;
        this.websocket.send(command);
    }
    
    centerLaser() {
        this.moveLaser(90, 90);
    }
    
    // 원형 패턴으로 레이저 이동
    moveInCircle(radius = 30) {
        for (let angle = 0; angle < 360; angle += 10) {
            const x = 90 + radius * Math.cos(angle * Math.PI / 180);
            const y = 90 + radius * Math.sin(angle * Math.PI / 180);
            this.moveLaser(Math.round(x), Math.round(y));
        }
    }
}
```

## 🔄 업데이트 내역

### v2.0 (현재)
- 2축 서보모터 지원 추가
- `handle_laser_xy()` 함수 추가
- 동시 제어 기능 추가
- 상태 조회 기능 추가
- 테스트 스크립트 추가

### v1.0 (이전)
- 단일 서보모터 제어
- 기본적인 각도 설정 기능 