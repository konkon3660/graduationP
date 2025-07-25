# 🕹️ 자동 놀이 기능 안내

## 개요
자동 놀이 기능은 고양이와의 상호작용을 위해 모터, 레이저, 오디오 등을 자동으로 제어하는 기능입니다.

## 주요 기능
- 모터를 이용한 장난감 이동(전진, 후진, 좌/우회전)
- 레이저 포인터 자동 제어
- 다양한 소리 자동 재생

## 사용 방법
1. 웹 UI 또는 API를 통해 자동 놀이를 시작할 수 있습니다.
2. 자동 놀이 중에는 모터가 항상 최대 속도로 동작합니다. (속도 조절 불가)
3. 대기 시간, 놀이 패턴 등은 설정할 수 있습니다.

## 주의사항
- L298N 모터 드라이버의 ENA/ENB는 점퍼로 5V에 연결되어 있으므로, 소프트웨어에서 속도(PWM) 제어가 불가능합니다.
- 모터는 항상 최대 속도로 동작합니다.

## 예시
- 전진/후진/좌회전/우회전 명령은 모두 최대 속도로 실행됩니다.

---

기타 문의사항은 개발자에게 문의하세요. 