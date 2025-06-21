# 🔧 JSON 명령 시스템

## 개요
이 시스템은 기존 문자열 명령과 함께 JSON 형태의 명령을 처리할 수 있는 확장된 명령 시스템입니다. 클라이언트에서 JSON 형태로 명령을 보내면 서버가 이를 파싱하여 적절한 하드웨어 제어를 수행합니다.

## 🚀 주요 기능

### 1. 이중 명령 처리
- **문자열 명령**: 기존 호환성 유지
- **JSON 명령**: 새로운 구조화된 명령 형식

### 2. 자동 명령 감지
- WebSocket으로 받은 메시지가 JSON인지 자동 감지
- JSON 파싱 실패 시 문자열 명령으로 처리

### 3. 구조화된 응답
- JSON 명령에 대해 구조화된 응답 제공
- 성공/실패 상태 및 메시지 포함

## 📋 지원하는 JSON 명령

### 🍽 급식 명령

#### 기본 급식
```json
{
    "type": "feed",
    "amount": 1
}
```

#### 즉시 급식
```json
{
    "type": "feed_now"
}
```

#### 다중 급식
```json
{
    "type": "feed_multiple",
    "amount": 3
}
```

#### 클라이언트 호환성 급식 명령
```json
{
    "type": "feeding",
    "amount": 1
}
```

```json
{
    "type": "give_food",
    "amount": 1
}
```

```json
{
    "type": "food",
    "amount": 1
}
```

```json
{
    "type": "dispense",
    "amount": 1
}
```

```json
{
    "type": "servo",
    "action": "feed",
    "amount": 1
}
```

### 🔴 레이저 명령

#### 레이저 ON/OFF
```json
{
    "type": "laser",
    "action": "on"
}
```
```json
{
    "type": "laser",
    "action": "off"
}
```

#### X축 제어
```json
{
    "type": "laser",
    "action": "x",
    "x": 90
}
```

#### Y축 제어
```json
{
    "type": "laser",
    "action": "y",
    "y": 90
}
```

#### XY 좌표 제어
```json
{
    "type": "laser",
    "action": "xy",
    "x": 90,
    "y": 90
}
```

### 🕹️ 모터 명령

#### 기본 방향 제어
```json
{
    "type": "motor",
    "direction": "forward",
    "speed": 70
}
```

지원하는 방향:
- `"forward"` - 전진
- `"backward"` - 후진
- `"left"` - 좌회전
- `"right"` - 우회전
- `"stop"` - 정지

### 🎯 서보 명령

```json
{
    "type": "servo",
    "angle": 90
}
```

### 🔥 솔레노이드 명령

```json
{
    "type": "fire"
}
```

### 🔄 시스템 명령

```json
{
    "type": "reset"
}
```

## 📡 WebSocket 응답 형식

### JSON 명령 응답
```json
{
    "success": true,
    "command": {
        "type": "feed",
        "amount": 1
    },
    "message": "명령 처리 완료"
}
```

### 오류 응답
```json
{
    "success": false,
    "command": {
        "type": "unknown"
    },
    "message": "명령 처리 실패"
}
```

## 🧪 테스트 방법

### 1. 서버 실행
```bash
python main.py
```

### 2. JSON 명령 테스트 페이지 접속
```
http://localhost:8000/test_json_commands.html
```

### 3. WebSocket 직접 테스트
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// 급식 명령 전송
ws.send(JSON.stringify({
    "type": "feed",
    "amount": 2
}));

// 응답 수신
ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('응답:', response);
};
```

## 🔄 기존 호환성

### 문자열 명령 (기존)
```
feed_now
laser_on
motor:forward
servo:90
```

### JSON 명령 (새로운)
```json
{"type": "feed_now"}
{"type": "laser", "action": "on"}
{"type": "motor", "direction": "forward"}
{"type": "servo", "angle": 90}
```

## 📁 파일 구조

```
services/
└── command_service.py          # 명령 처리 서비스 (JSON 지원 추가)

routers/
└── ws_router.py               # WebSocket 라우터 (JSON 감지 추가)

test_json_commands.html        # JSON 명령 테스트 페이지
```

## 🛠️ 개발자 정보

### 명령 처리 흐름
1. WebSocket으로 메시지 수신
2. JSON 파싱 시도
3. 성공 시: JSON 명령 처리
4. 실패 시: 문자열 명령 처리
5. 적절한 응답 전송

### 로깅
- 모든 JSON 명령은 로그로 기록
- 파싱 오류 및 처리 실패 로그
- 성공적인 명령 실행 로그

### 오류 처리
- JSON 파싱 오류 처리
- 알 수 없는 명령 타입 처리
- 하드웨어 오류 처리
- 예외 상황 로깅

## 📝 사용 예시

### Python에서 JSON 명령 전송
```python
import json
import websockets

async def send_json_command():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # 급식 명령
        command = {"type": "feed", "amount": 2}
        await websocket.send(json.dumps(command))
        
        # 응답 수신
        response = await websocket.recv()
        print(f"응답: {response}")
```

### JavaScript에서 JSON 명령 전송
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// 급식 명령
ws.send(JSON.stringify({
    "type": "feed",
    "amount": 1
}));

// 레이저 명령
ws.send(JSON.stringify({
    "type": "laser",
    "action": "on"
}));

// 모터 명령
ws.send(JSON.stringify({
    "type": "motor",
    "direction": "forward",
    "speed": 80
}));
```

## ✅ 구현 완료

- ✅ JSON 명령 파싱 및 처리
- ✅ 급식 관련 JSON 명령 지원
- ✅ 레이저, 모터, 서보, 솔레노이드 JSON 명령 지원
- ✅ 기존 문자열 명령 호환성 유지
- ✅ 구조화된 응답 시스템
- ✅ 테스트 페이지 제공
- ✅ 오류 처리 및 로깅

이제 클라이언트에서 JSON 형태로 급식 명령을 보내면 서버가 정상적으로 인식하고 처리할 수 있습니다! 🎉 