#!/bin/bash

# 🚀 스마트 반려동물 케어 로봇 - 자동 설치 스크립트

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 제목 출력
print_banner() {
    echo "=================================================="
    echo "🚀 스마트 반려동물 케어 로봇 - 자동 설치 스크립트"
    echo "=================================================="
    echo
}

# 시스템 확인
check_system() {
    log_info "시스템 환경 확인 중..."
    
    # OS 확인
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f /etc/os-release ]]; then
            . /etc/os-release
            if [[ "$ID" == "raspbian" || "$ID" == "debian" ]]; then
                log_success "Raspberry Pi OS / Debian 감지됨"
            else
                log_warning "지원되지 않는 Linux 배포판: $ID"
            fi
        fi
    else
        log_error "지원되지 않는 운영체제: $OSTYPE"
        exit 1
    fi
    
    # Python 버전 확인
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION 발견됨"
    else
        log_error "Python3가 설치되지 않았습니다."
        exit 1
    fi
    
    # pip 확인
    if command -v pip3 &> /dev/null; then
        log_success "pip3 발견됨"
    else
        log_error "pip3가 설치되지 않았습니다."
        exit 1
    fi
}

# 시스템 패키지 업데이트
update_system() {
    log_info "시스템 패키지 업데이트 중..."
    
    sudo apt update
    sudo apt upgrade -y
    
    log_success "시스템 패키지 업데이트 완료"
}

# 필수 시스템 패키지 설치
install_system_packages() {
    log_info "필수 시스템 패키지 설치 중..."
    
    # 기본 개발 도구
    sudo apt install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        curl \
        wget \
        htop \
        vim \
        nano
    
    # OpenCV 의존성
    sudo apt install -y \
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
        libcanberra-gtk3-module
    
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
    
    log_success "시스템 패키지 설치 완료"
}

# 가상환경 생성
create_venv() {
    log_info "Python 가상환경 생성 중..."
    
    if [[ -d "venv" ]]; then
        log_warning "기존 가상환경 발견됨. 삭제 후 재생성합니다."
        rm -rf venv
    fi
    
    python3 -m venv venv
    log_success "가상환경 생성 완료"
}

# 가상환경 활성화
activate_venv() {
    log_info "가상환경 활성화 중..."
    
    source venv/bin/activate
    
    # pip 업그레이드
    pip install --upgrade pip
    
    log_success "가상환경 활성화 완료"
}

# Python 패키지 설치
install_python_packages() {
    log_info "Python 패키지 설치 중..."
    
    # 기본 의존성 설치
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_success "기본 의존성 설치 완료"
    else
        log_error "requirements.txt 파일을 찾을 수 없습니다."
        exit 1
    fi
    
    # 개발 의존성 설치 (선택사항)
    if [[ "$1" == "--dev" ]] && [[ -f "requirements-dev.txt" ]]; then
        log_info "개발 의존성 설치 중..."
        pip install -r requirements-dev.txt
        log_success "개발 의존성 설치 완료"
    fi
}

# 하드웨어 설정
setup_hardware() {
    log_info "하드웨어 설정 중..."
    
    # I2C 활성화 확인
    if ! grep -q "i2c_arm=on" /boot/config.txt; then
        log_warning "I2C가 활성화되지 않았습니다. 수동으로 활성화해주세요:"
        echo "sudo raspi-config -> Interface Options -> I2C -> Enable"
    fi
    
    # SPI 활성화 확인
    if ! grep -q "spi=on" /boot/config.txt; then
        log_warning "SPI가 활성화되지 않았습니다. 수동으로 활성화해주세요:"
        echo "sudo raspi-config -> Interface Options -> SPI -> Enable"
    fi
    
    # 사용자 그룹 추가
    sudo usermod -a -G gpio $USER 2>/dev/null || true
    sudo usermod -a -G i2c $USER 2>/dev/null || true
    sudo usermod -a -G spi $USER 2>/dev/null || true
    
    log_success "하드웨어 설정 완료"
}

# 환경 변수 설정
setup_environment() {
    log_info "환경 변수 설정 중..."
    
    if [[ ! -f ".env" ]]; then
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
        log_success ".env 파일 생성 완료"
    else
        log_warning ".env 파일이 이미 존재합니다."
    fi
}

# 설치 확인
verify_installation() {
    log_info "설치 확인 중..."
    
    # Python 패키지 확인
    python3 -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" || log_error "FastAPI 설치 실패"
    python3 -c "import cv2; print('✅ OpenCV:', cv2.__version__)" || log_error "OpenCV 설치 실패"
    python3 -c "import pyaudio; print('✅ PyAudio 설치됨')" || log_error "PyAudio 설치 실패"
    python3 -c "import RPi.GPIO; print('✅ RPi.GPIO 설치됨')" || log_error "RPi.GPIO 설치 실패"
    
    # 하드웨어 테스트
    if [[ -f "test_pin_mapping.py" ]]; then
        log_info "핀 매핑 테스트 실행 중..."
        python3 test_pin_mapping.py || log_warning "핀 매핑 테스트 실패"
    fi
    
    log_success "설치 확인 완료"
}

# 실행 권한 설정
setup_permissions() {
    log_info "실행 권한 설정 중..."
    
    chmod +x *.py
    chmod +x *.sh
    
    log_success "실행 권한 설정 완료"
}

# 완료 메시지
print_completion() {
    echo
    echo "=================================================="
    echo "🎉 설치가 완료되었습니다!"
    echo "=================================================="
    echo
    echo "다음 단계:"
    echo "1. 가상환경 활성화: source venv/bin/activate"
    echo "2. 서버 실행: uvicorn main:app --host 0.0.0.0 --port 8000"
    echo "3. 브라우저에서 접속: http://localhost:8000"
    echo
    echo "추가 문서:"
    echo "- 설치 가이드: INSTALLATION.md"
    echo "- 하드웨어 매핑: HARDWARE_PIN_MAPPING.md"
    echo "- XY 서보모터: README_XY_SERVO.md"
    echo
}

# 메인 함수
main() {
    print_banner
    
    # 인수 처리
    DEV_MODE=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                DEV_MODE=true
                shift
                ;;
            --help)
                echo "사용법: $0 [--dev]"
                echo "  --dev: 개발 의존성도 함께 설치"
                exit 0
                ;;
            *)
                log_error "알 수 없는 인수: $1"
                exit 1
                ;;
        esac
    done
    
    # 설치 단계 실행
    check_system
    update_system
    install_system_packages
    create_venv
    activate_venv
    install_python_packages $([[ "$DEV_MODE" == true ]] && echo "--dev")
    setup_hardware
    setup_environment
    setup_permissions
    verify_installation
    print_completion
}

# 스크립트 실행
main "$@" 