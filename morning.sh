#!/bin/bash

# Morning - 주식 분석 시스템 관리 스크립트
# 사용법: ./morning.sh [start|stop|status|restart|logs|clean]

APP_NAME="Morning"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${BLUE}=== $APP_NAME $1 ===${NC}"
}

# 가상환경 활성화 확인
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        log_warn "가상환경이 활성화되지 않았습니다."
        if [ -d "venv" ]; then
            log_info "가상환경을 활성화합니다..."
            source venv/bin/activate
        else
            log_error "venv 디렉토리를 찾을 수 없습니다."
            exit 1
        fi
    fi
    
    # Python 경로 확인
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        log_error "Python이 설치되지 않았거나 PATH에 없습니다."
        exit 1
    fi
    
    # Python 명령어 설정
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
}

# 명령어 실행
case "$1" in
    start)
        log_header "시작"
        check_venv
        cd "$SCRIPT_DIR"
        $PYTHON_CMD manage.py start
        ;;
    stop)
        log_header "중지"
        cd "$SCRIPT_DIR"
        check_venv
        $PYTHON_CMD manage.py stop
        ;;
    restart)
        log_header "재시작"
        check_venv
        cd "$SCRIPT_DIR"
        $PYTHON_CMD manage.py restart
        ;;
    status)
        log_header "상태 확인"
        cd "$SCRIPT_DIR"
        check_venv
        $PYTHON_CMD manage.py status
        ;;
    logs)
        log_header "로그 확인"
        cd "$SCRIPT_DIR"
        check_venv
        if [ -n "$2" ]; then
            $PYTHON_CMD manage.py logs "$2"
        else
            $PYTHON_CMD manage.py logs
        fi
        ;;
    clean)
        log_header "정리"
        cd "$SCRIPT_DIR"
        check_venv
        $PYTHON_CMD manage.py clean
        ;;
    *)
        echo -e "${BLUE}🌅 $APP_NAME - 주식 분석 시스템 관리 스크립트${NC}"
        echo ""
        echo "사용법: $0 [명령어]"
        echo ""
        echo "명령어:"
        echo "  start     - 애플리케이션 시작"
        echo "  stop      - 애플리케이션 중지"
        echo "  restart   - 애플리케이션 재시작"
        echo "  status    - 애플리케이션 상태 확인"
        echo "  logs      - 로그 확인 (최근 50줄)"
        echo "  logs 100  - 로그 확인 (최근 100줄)"
        echo "  clean     - 로그 파일 정리"
        echo ""
        echo "예시:"
        echo "  $0 start"
        echo "  $0 status"
        echo "  $0 logs 20"
        echo "  $0 stop"
        ;;
esac
