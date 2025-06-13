import cv2
import torch

# 1. YOLO 모델 설정
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # GPU 사용 가능하면 사용, 아니면 CPU 사용
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True, device=device)  # yolov5n 모델 사용
model.classes = [0]  # COCO 데이터셋에서 사람(0) 클래스만 사용
model.conf = 0.25  # 객체 탐지 신뢰도 임계값
model.iou = 0.45  # NMS IoU 임계값
model.eval() # 평가 모드로 설정

# 2. OpenCV 최적화
cv2.setUseOptimized(True)
cv2.setNumThreads(4)  # 라즈베리 파이의 코어 수에 맞춰 스레드 수 설정

# 3. 카메라 설정
cap = cv2.VideoCapture(0)  # 0번 카메라 사용 (라즈베리 파이 카메라 모듈)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)  # 해상도 너비 설정
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 900)  # 해상도 높이 설정
cap.set(cv2.CAP_PROP_FPS, 60)  # 프레임 속도 설정

# 4. 프레임 건너뛰기 설정
frame_count = 0
skip_frames = 1  # 1 프레임마다 하나씩 건너뜀 (총 2프레임당 1프레임 처리)

# 5. 메인 루프
try:
    with torch.no_grad(): # 기울기 계산 비활성화
        while True:
            # 프레임 읽기
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 프레임 건너뛰기
            if frame_count % (skip_frames + 1) == 0:
                # 6. 이미지 전처리 최적화
                frame = cv2.resize(frame, (1600, 900), interpolation=cv2.INTER_AREA)

                # YOLO 모델로 객체 감지
                results = model(frame)

                # Show the results
                cv2.imshow('YOLO', results.render()[0])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except KeyboardInterrupt:
    print("Program stopped")
finally:
    cap.release()
    cv2.destroyAllWindows()