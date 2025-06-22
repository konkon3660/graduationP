# 🍽 급식 설정 시스템

## 개요
이 시스템은 반려동물 급식기의 자동/수동 급식 기능을 WebSocket을 통해 제어할 수 있는 설정 시스템입니다.

## 🚀 주요 기능

### 1. WebSocket 설정 엔드포인트
- **엔드포인트**: `/ws/settings`
- **프로토콜**: WebSocket
- **기능**: 실시간 설정 변경 및 급식 제어

### 2. 설정 관리
- **모드**: `manual` (수동) / `auto` (자동)
- **간격**: 1~1440분 (자동 모드에서 급식 간격)
- **급식량**: 1~10회 (한 번에 주는 급식 횟수)

### 3. 자동 급식 스케줄링
- 설정된 간격마다 자동으로 급식 실행
- 실시간 스케줄 상태 모니터링
- 설정 변경 시 즉시 스케줄 리셋

## 📁 파일 구조

```
services/
├── settings_service.py      # 설정 관리 서비스
├── feed_scheduler.py        # 급식 스케줄러
├── feed_service.py          # 급식 하드웨어 제어
└── feed_setting.py          # 기존 코드 호환성

routers/
└── ws_settings_router.py    # 설정 WebSocket 라우터

test_settings.html           # 설정 테스트 페이지
```

## 🔧 WebSocket 메시지 형식

### 클라이언트 → 서버

#### 설정 업데이트
```json
{
    "type": "update_settings",
    "settings": {
        "mode": "auto",
        "interval": 60,
        "amount": 2
    }
}
```

#### 설정 조회
```json
{
    "type": "get_settings"
}
```

#### 스케줄러 시작
```json
{
    "type": "start_scheduler"
}
```

#### 스케줄러 중지
```json
{
    "type": "stop_scheduler"
}
```

#### 수동 급식
```json
{
    "type": "manual_feed",
    "amount": 1
}
```

### 서버 → 클라이언트

#### 초기 설정
```json
{
    "type": "init",
    "settings": {
        "mode": "manual",
        "interval": 60,
        "amount": 1
    },
    "scheduler_status": {
        "is_running": false,
        "next_feed_time": null,
        "current_count": 0
    }
}
```

#### 설정 업데이트 완료
```json
{
    "type": "settings_updated",
    "settings": {
        "mode": "auto",
        "interval": 60,
        "amount": 2
    },
    "success": true
}
```

#### 오류 응답
```json
{
    "type": "error",
    "message": "오류 메시지",
    "success": false
}
```

## 🧪 테스트 방법

1. 서버 실행:
```bash
python main.py
```

2. 브라우저에서 테스트 페이지 열기:
```
http://localhost:8000/test_settings.html
```

3. WebSocket 연결 확인 및 기능 테스트

## ⚙️ 설정 파일

설정은 `feed_settings.json` 파일에 자동으로 저장됩니다:

```json
{
    "mode": "manual",
    "interval": 60,
    "amount": 1
}
```

## 🔄 기존 코드 호환성

기존 `feed_setting.py`의 `feed_config`와 `update_settings()` 함수는 새로운 시스템과 호환됩니다.

## 🛠️ 개발자 정보

### 의존성
- FastAPI
- WebSocket
- RPi.GPIO (하드웨어 제어)
- asyncio (비동기 처리)

### 로깅
모든 작업은 로그로 기록되며, 콘솔에서 실시간으로 확인할 수 있습니다.

### 오류 처리
- 설정 유효성 검사
- WebSocket 연결 오류 처리
- 하드웨어 오류 처리
- 자동 재연결 기능

## 📝 사용 예시

### Python에서 설정 변경
```python
from services.settings_service import settings_service

# 설정 업데이트
new_settings = {
    "mode": "auto",
    "interval": 30,
    "amount": 2
}
settings_service.update_settings(new_settings)
```

### WebSocket 클라이언트 예시
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/settings');

ws.onopen = function() {
    // 설정 업데이트
    ws.send(JSON.stringify({
        type: 'update_settings',
        settings: {
            mode: 'auto',
            interval: 60,
            amount: 1
        }
    }));
};
``` 