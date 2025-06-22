#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
초음파 센서 테스트 코드
라즈베리 파이에서 초음파 센서의 거리 측정 기능을 테스트합니다.
"""

import time
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ultrasonic_service import UltrasonicSensor, get_distance, get_distance_data

def test_ultrasonic_sensor():
    """초음파 센서 기본 테스트"""
    print("🔧 초음파 센서 테스트 시작")
    print("=" * 50)
    
    try:
        # 초음파 센서 인스턴스 생성
        sensor = UltrasonicSensor()
        print("✅ 초음파 센서 초기화 완료")
        
        # 5회 거리 측정 테스트
        print("\n📏 거리 측정 테스트 (5회)")
        print("-" * 30)
        
        for i in range(5):
            distance = sensor.measure_distance()
            if distance is not None:
                print(f"측정 {i+1}: {distance}cm")
            else:
                print(f"측정 {i+1}: 측정 실패")
            time.sleep(1)  # 1초 대기
        
        # 전역 함수 테스트
        print("\n🔧 전역 함수 테스트")
        print("-" * 30)
        
        distance = get_distance()
        if distance is not None:
            print(f"get_distance(): {distance}cm")
        else:
            print("get_distance(): 측정 실패")
        
        # 클라이언트 전송용 데이터 테스트
        print("\n📊 클라이언트 데이터 테스트")
        print("-" * 30)
        
        distance_data = get_distance_data()
        print(f"get_distance_data(): {distance_data}")
        
        # 센서 정리
        sensor.cleanup()
        print("\n✅ 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False
    
    return True

def test_continuous_measurement():
    """연속 측정 테스트"""
    print("\n🔄 연속 측정 테스트 (10초간)")
    print("=" * 50)
    
    try:
        sensor = UltrasonicSensor()
        start_time = time.time()
        count = 0
        
        while time.time() - start_time < 10:
            distance = sensor.measure_distance()
            count += 1
            
            if distance is not None:
                print(f"측정 {count}: {distance}cm", end="\r")
            else:
                print(f"측정 {count}: 실패", end="\r")
            
            time.sleep(0.5)  # 0.5초 간격
        
        print(f"\n총 {count}회 측정 완료")
        sensor.cleanup()
        
    except Exception as e:
        print(f"❌ 연속 측정 테스트 중 오류: {e}")
        return False
    
    return True

def test_error_handling():
    """오류 처리 테스트"""
    print("\n⚠️ 오류 처리 테스트")
    print("=" * 50)
    
    try:
        # 잘못된 핀 번호로 테스트 (시뮬레이션)
        print("잘못된 핀 번호 테스트는 실제 하드웨어에서 수행할 수 없습니다.")
        print("대신 정상적인 센서 동작을 확인합니다.")
        
        sensor = UltrasonicSensor()
        
        # 여러 번 빠르게 측정하여 오류 상황 시뮬레이션
        for i in range(3):
            distance = sensor.measure_distance()
            print(f"빠른 측정 {i+1}: {distance}cm" if distance else f"빠른 측정 {i+1}: 실패")
            time.sleep(0.1)  # 0.1초 간격
        
        sensor.cleanup()
        print("✅ 오류 처리 테스트 완료")
        
    except Exception as e:
        print(f"❌ 오류 처리 테스트 중 예외: {e}")
        return False
    
    return True

def main():
    """메인 테스트 함수"""
    print("🚀 초음파 센서 종합 테스트")
    print("=" * 60)
    
    # 하드웨어 확인
    print("⚠️  초음파 센서가 다음 핀에 연결되어 있는지 확인하세요:")
    print("   - TRIG: GPIO 6 (PIN 31)")
    print("   - ECHO: GPIO 7 (PIN 26)")
    print("   - VCC: 5V")
    print("   - GND: GND")
    print()
    
    input("엔터를 눌러 테스트를 시작하세요...")
    
    # 테스트 실행
    tests = [
        ("기본 테스트", test_ultrasonic_sensor),
        ("연속 측정 테스트", test_continuous_measurement),
        ("오류 처리 테스트", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name} 실행 중...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} 성공")
            else:
                print(f"❌ {test_name} 실패")
        except Exception as e:
            print(f"❌ {test_name} 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n총 {len(results)}개 테스트 중 {passed}개 성공")
    
    if passed == len(results):
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 하드웨어 연결을 확인하세요.")

if __name__ == "__main__":
    main() 