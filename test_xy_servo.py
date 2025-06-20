#!/usr/bin/env python3
# test_xy_servo.py - XY 서보모터 테스트 스크립트

import time
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.xy_servo import (
    init_xy_servo, 
    set_xy_servo_angles, 
    handle_laser_xy, 
    get_servo_status,
    reset_to_center,
    cleanup
)

def test_xy_servo():
    """XY 서보모터 테스트"""
    print("🎯 XY 서보모터 테스트 시작")
    
    try:
        # 1. 초기화
        print("1️⃣ 서보모터 초기화...")
        if not init_xy_servo():
            print("❌ 초기화 실패")
            return False
        print("✅ 초기화 성공")
        
        # 2. 상태 확인
        print("2️⃣ 현재 상태 확인...")
        status = get_servo_status()
        print(f"   상태: {status}")
        
        # 3. 중앙 위치로 리셋
        print("3️⃣ 중앙 위치로 리셋...")
        if reset_to_center():
            print("✅ 중앙 위치 리셋 성공")
        else:
            print("❌ 중앙 위치 리셋 실패")
        
        time.sleep(2)
        
        # 4. 다양한 위치 테스트
        test_positions = [
            (0, 0),      # 좌상단
            (180, 0),    # 우상단
            (180, 180),  # 우하단
            (0, 180),    # 좌하단
            (90, 90),    # 중앙
            (45, 45),    # 대각선
            (135, 135),  # 대각선
        ]
        
        print("4️⃣ 다양한 위치 테스트...")
        for i, (x, y) in enumerate(test_positions, 1):
            print(f"   {i}. 위치 ({x}, {y})로 이동...")
            if set_xy_servo_angles(x, y):
                print(f"   ✅ 위치 ({x}, {y}) 이동 성공")
            else:
                print(f"   ❌ 위치 ({x}, {y}) 이동 실패")
            time.sleep(1)
        
        # 5. laser_xy 명령 테스트
        print("5️⃣ laser_xy 명령 테스트...")
        test_coordinates = [
            (50, 100),
            (120, 80),
            (90, 150),
            (30, 60)
        ]
        
        for i, (x, y) in enumerate(test_coordinates, 1):
            print(f"   {i}. laser_xy:({x}, {y}) 명령 실행...")
            if handle_laser_xy(x, y):
                print(f"   ✅ laser_xy({x}, {y}) 성공")
            else:
                print(f"   ❌ laser_xy({x}, {y}) 실패")
            time.sleep(1)
        
        # 6. 최종 중앙 위치로
        print("6️⃣ 최종 중앙 위치로...")
        reset_to_center()
        time.sleep(1)
        
        print("🎉 모든 테스트 완료!")
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False
    finally:
        print("🧹 리소스 정리 중...")
        cleanup()

if __name__ == "__main__":
    print("=" * 50)
    print("🎯 XY 서보모터 테스트 프로그램")
    print("=" * 50)
    
    success = test_xy_servo()
    
    if success:
        print("✅ 테스트 성공적으로 완료!")
    else:
        print("❌ 테스트 실패!")
    
    print("=" * 50) 