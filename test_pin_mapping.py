#!/usr/bin/env python3
# test_pin_mapping.py - 하드웨어 핀 매핑 테스트 스크립트

import sys
import os
import time

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pin_mapping():
    """하드웨어 핀 매핑 테스트"""
    print("🔌 하드웨어 핀 매핑 테스트 시작")
    print("=" * 60)
    
    # 핀 매핑 정보
    pin_mapping = {
        "모터 드라이버 (SMG-A)": {
            "ENA": {"gpio": 12, "pin": 32, "description": "우측 모터 PWM"},
            "INT1": {"gpio": 23, "pin": 16, "description": "우측 모터 방향1"},
            "INT2": {"gpio": 24, "pin": 18, "description": "우측 모터 방향2"},
            "ENB": {"gpio": 26, "pin": 37, "description": "좌측 모터 PWM"},
            "INT3": {"gpio": 27, "pin": 13, "description": "좌측 모터 방향1"},
            "INT4": {"gpio": 22, "pin": 15, "description": "좌측 모터 방향2"}
        },
        "서보모터 (급식용)": {
            "SERVO": {"gpio": 18, "pin": 12, "description": "급식 서보모터 (hardware PWM)"}
        },
        "서보모터 (레이저용)": {
            "X_SERVO": {"gpio": 19, "pin": 35, "description": "X축 서보모터 (좌우)"},
            "Y_SERVO": {"gpio": 13, "pin": 33, "description": "Y축 서보모터 (상하)"}
        },
        "레이저 포인터": {
            "LASER": {"gpio": 17, "pin": 11, "description": "레이저 ON/OFF"}
        },
        "릴레이 (공 발사용)": {
            "RELAY": {"gpio": 5, "pin": 29, "description": "릴레이 제어"}
        }
    }
    
    # 핀 매핑 정보 출력
    print("📋 현재 핀 매핑 정보:")
    for category, pins in pin_mapping.items():
        print(f"\n🔧 {category}:")
        for name, info in pins.items():
            print(f"   {name}: GPIO {info['gpio']} (PIN {info['pin']}) - {info['description']}")
    
    print("\n" + "=" * 60)
    
    # 소프트웨어 파일에서 핀 번호 확인
    print("🔍 소프트웨어 파일 핀 번호 확인:")
    
    try:
        # motor_service.py 확인
        from services.motor_service import ENA, INT1, INT2, ENB, INT3, INT4
        print(f"✅ motor_service.py:")
        print(f"   ENA={ENA}, INT1={INT1}, INT2={INT2}")
        print(f"   ENB={ENB}, INT3={INT3}, INT4={INT4}")
    except Exception as e:
        print(f"❌ motor_service.py 확인 실패: {e}")
    
    try:
        # feed_service.py 확인
        from services.feed_service import SERVO_PIN
        print(f"✅ feed_service.py: SERVO_PIN={SERVO_PIN}")
    except Exception as e:
        print(f"❌ feed_service.py 확인 실패: {e}")
    
    try:
        # xy_servo.py 확인
        from services.xy_servo import X_SERVO_PIN, Y_SERVO_PIN
        print(f"✅ xy_servo.py: X_SERVO_PIN={X_SERVO_PIN}, Y_SERVO_PIN={Y_SERVO_PIN}")
    except Exception as e:
        print(f"❌ xy_servo.py 확인 실패: {e}")
    
    try:
        # laser_service.py 확인
        from services.laser_service import LASER_PIN
        print(f"✅ laser_service.py: LASER_PIN={LASER_PIN}")
    except Exception as e:
        print(f"❌ laser_service.py 확인 실패: {e}")
    
    try:
        # sol_service.py 확인
        from services.sol_service import RELAY_PIN
        print(f"✅ sol_service.py: RELAY_PIN={RELAY_PIN}")
    except Exception as e:
        print(f"❌ sol_service.py 확인 실패: {e}")
    
    print("\n" + "=" * 60)
    
    # 핀 충돌 검사
    print("⚠️ 핀 충돌 검사:")
    all_gpios = []
    
    for category, pins in pin_mapping.items():
        for name, info in pins.items():
            all_gpios.append(info['gpio'])
    
    # 중복된 GPIO 번호 찾기
    duplicates = []
    seen = set()
    for gpio in all_gpios:
        if gpio in seen:
            duplicates.append(gpio)
        seen.add(gpio)
    
    if duplicates:
        print(f"❌ 중복된 GPIO 번호 발견: {duplicates}")
        print("   하나의 GPIO에 여러 부품이 연결되어 있습니다!")
    else:
        print("✅ GPIO 번호 중복 없음")
    
    # PWM 핀 확인
    pwm_pins = [12, 13, 18, 19]  # 하드웨어 PWM 지원 핀
    pwm_used = []
    
    for gpio in all_gpios:
        if gpio in pwm_pins:
            pwm_used.append(gpio)
    
    print(f"✅ PWM 핀 사용: {pwm_used}")
    
    print("\n" + "=" * 60)
    
    # 권장사항
    print("💡 권장사항:")
    print("1. 모든 핀 연결 상태를 물리적으로 확인하세요")
    print("2. 전원 공급이 안정적인지 확인하세요")
    print("3. GND 연결이 제대로 되어 있는지 확인하세요")
    print("4. 각 부품별로 개별 테스트를 실행하세요")
    
    print("\n" + "=" * 60)
    print("🎉 핀 매핑 테스트 완료!")

if __name__ == "__main__":
    test_pin_mapping() 