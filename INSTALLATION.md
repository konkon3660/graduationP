# 📦 설치 가이드

## 🎯 개요
스마트 반려동물 케어 로봇의 의존성 패키지 설치 가이드를 제공합니다.

## 🔧 시스템 요구사항

### 하드웨어
- **Raspberry Pi 4** (권장: 4GB RAM 이상)
- **Python 3.8+**
- **Raspberry Pi OS** (Bullseye 이상)

### 소프트웨어
- **Python 3.8+**
- **pip** (Python 패키지 관리자)
- **git** (소스코드 관리)

## 📋 설치 방법

### 1. 기본 설치 (권장)

```bash
# 프로젝트 클론
git clone <repository-url>
cd graduationP

# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 기본 의존성 설치
pip install -r requirements.txt
```

### 2. 최소 설치 (제한된 리소스 환경)

```bash
# 최소 필수 패키지만 설치
pip install -r requirements-minimal.txt
```

### 3. 프로덕션 환경 설치

```bash
# 프로덕션용 패키지 설치
pip install -r requirements-prod.txt
```

### 4. 개발 환경 설치

```bash
# 개발 도구 포함 설치
pip install -r requirements-dev.txt
```

## 🔧 하드웨어 특화 설치

### Raspberry Pi 전용 패키지

```bash
# 시스템 패키지 업데이트
sudo apt update
sudo apt upgrade

# 필수 시스템 패키지 설치
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtcore4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjasper1 \
    libilmbase23 \
    libopenexr23 \
    libgstreamer1.0-0 \
    libavcodec58 \
    libavformat58 \
    libswscale5 \
    libv4l-0 \
    libxvidcore4 \
    libx264-163 \
    libgtk-3-0 \
    libgtk2.0-0 \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    libatlas-base-dev \
    libblas-dev \
    liblapack-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    python3-pyqt5 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgtk2.0-dev \
    libtiff4-dev \
    libjpeg-dev \
    libopenexr-dev \
    libwebp-dev \
    libtiff-dev \
    libjasper-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio \
    libgirepository1.0-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gstreamer-1.0 \
    gir1.2-glib-2.0 \
    libgirepository1.0-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gstreamer-1.0 \
    gir1.2-glib-2.0

# 오디오 관련 패키지
sudo apt install -y \
    portaudio19-dev \
    python3-pyaudio \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg

# GPIO 관련 패키지
sudo apt install -y \
    python3-gpiozero \
    python3-rpi.gpio

# I2C/SPI 통신
sudo apt install -y \
    python3-smbus \
    i2c-tools \
    python3-spidev

# 시스템 모니터링
sudo apt install -y \
    htop \
    iotop \
    nethogs
```

### 오디오 설정

```bash
# ALSA 설정
sudo nano /etc/asound.conf

# 다음 내용 추가:
pcm.!default {
    type hw
    card 1
}

ctl.!default {
    type hw
    card 1
}
```

### I2C 활성화

```bash
# I2C 활성화
sudo raspi-config

# Interface Options > I2C > Enable
# Interface Options > SPI > Enable

# I2C 그룹에 사용자 추가
sudo usermod -a -G i2c $USER
sudo usermod -a -G spi $USER
sudo usermod -a -G gpio $USER
```

## 🐍 Python 패키지 설치

### 가상환경 사용 (권장)

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt
```

### 시스템 Python 사용 (비권장)

```bash
# 시스템 Python에 직접 설치
sudo pip3 install -r requirements.txt
```

## 🔍 설치 확인

### 1. 기본 기능 테스트

```bash
# Python 버전 확인
python3 --version

# 주요 패키지 확인
python3 -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"
python3 -c "import pyaudio; print('PyAudio 설치됨')"
python3 -c "import RPi.GPIO; print('RPi.GPIO 설치됨')"
```

### 2. 하드웨어 테스트

```bash
# GPIO 테스트
python3 test_pin_mapping.py

# 서보모터 테스트
python3 test_xy_servo.py

# 카메라 테스트
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('카메라 연결:', cap.isOpened())"
```

### 3. 오디오 테스트

```bash
# 마이크 테스트
python3 test.py

# 스피커 테스트
speaker-test -t wav -c 2 -l 1
```

## ⚠️ 문제 해결

### PyAudio 설치 실패

```bash
# Ubuntu/Debian
sudo apt install portaudio19-dev python3-pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Windows
pip install pipwin
pipwin install pyaudio
```

### OpenCV 설치 실패

```bash
# 시스템 의존성 설치
sudo apt install -y libopencv-dev python3-opencv

# 또는 pip로 설치
pip install opencv-python
```

### RPi.GPIO 설치 실패

```bash
# 시스템 패키지로 설치
sudo apt install python3-rpi.gpio

# 또는 pip로 설치
pip install RPi.GPIO
```

### 권한 문제

```bash
# GPIO 접근 권한
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER
sudo usermod -a -G spi $USER

# 재부팅 후 적용
sudo reboot
```

## 📝 환경 변수 설정

### .env 파일 생성

```bash
# 프로젝트 루트에 .env 파일 생성
cat > .env << EOF
# 서버 설정
HOST=0.0.0.0
PORT=8000
DEBUG=False

# 하드웨어 설정
GPIO_MODE=BCM
PWM_FREQUENCY=50
MOTOR_DEFAULT_SPEED=70

# 오디오 설정
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_CHUNK_SIZE=2048

# 카메라 설정
CAMERA_WIDTH=320
CAMERA_HEIGHT=240
CAMERA_FPS=15

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=app.log
EOF
```

## 🚀 실행

### 개발 모드

```bash
# 개발 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 프로덕션 모드

```bash
# 프로덕션 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 시스템 서비스로 등록

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/pet-care-robot.service

# 다음 내용 추가:
[Unit]
Description=Pet Care Robot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/graduationP
Environment=PATH=/home/pi/graduationP/venv/bin
ExecStart=/home/pi/graduationP/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

# 서비스 활성화
sudo systemctl enable pet-care-robot
sudo systemctl start pet-care-robot
```

## 📚 추가 문서

- [하드웨어 핀 매핑](./HARDWARE_PIN_MAPPING.md)
- [XY 서보모터 사용법](./README_XY_SERVO.md)
- [API 문서](./API_DOCUMENTATION.md) 