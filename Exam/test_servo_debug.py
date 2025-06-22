#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
서보모터 디버깅 테스트 파일
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from services.command_service import command_handler

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_servo_commands():
    """서보모터 명령 테스트"""
    print("🎯 서보모터 디버깅 테스트 시작")
    
    try:
        # 하드웨어 초기화
        command_handler.initialize()
        print("✅ 하드웨어 초기화 완료")
        
        # 1. 급식용 서보모터 테스트 (GPIO 18)
        print("\n🍚 급식용 서보모터 테스트 (GPIO 18)")
        angles = [0, 45, 90, 135, 180]
        for angle in angles:
            print(f"  - {angle}도로 설정 시도...")
            success = command_handler.handle_feed_servo_angle(angle)
            print(f"    결과: {'성공' if success else '실패'}")
        
        # 2. 레이저용 서보모터 테스트 (GPIO 19, 13)
        print("\n🎯 레이저용 서보모터 테스트 (GPIO 19, 13)")
        for angle in angles:
            print(f"  - X축 {angle}도로 설정 시도...")
            success = command_handler.handle_laser_servo_angle(angle)
            print(f"    결과: {'성공' if success else '실패'}")
        
        # 3. 기존 서보 명령 테스트
        print("\n🔧 기존 서보 명령 테스트")
        for angle in angles:
            print(f"  - {angle}도로 설정 시도...")
            success = command_handler.handle_servo_angle(angle)
            print(f"    결과: {'성공' if success else '실패'}")
        
        print("\n✅ 모든 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        logger.exception("테스트 오류")
    
    finally:
        # 정리
        command_handler.cleanup()
        print("🧹 정리 완료")

if __name__ == "__main__":
    test_servo_commands() 