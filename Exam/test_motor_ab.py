import time
import sys
sys.path.append('..')
from services import motor_service

print('--- 모터 A(우측) 테스트: 전진 2초, 후진 2초, 정지 ---')
motor_service.set_right_motor(100, 0)  # 전진
print('A 전진')
time.sleep(2)
motor_service.set_right_motor(100, 1)  # 후진
print('A 후진')
time.sleep(2)
motor_service.set_right_motor(0, 0)   # 정지
print('A 정지')
time.sleep(1)

print('--- 모터 B(좌측) 테스트: 전진 2초, 후진 2초, 정지 ---')
motor_service.set_left_motor(100, 0)   # 전진
print('B 전진')
time.sleep(2)
motor_service.set_left_motor(100, 1)   # 후진
print('B 후진')
time.sleep(2)
motor_service.set_left_motor(0, 0)    # 정지
print('B 정지')
time.sleep(1)

print('테스트 완료!')
motor_service.cleanup() 