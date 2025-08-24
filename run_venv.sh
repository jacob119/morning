#!/bin/bash

# 가상환경 활성화 및 애플리케이션 실행 스크립트

echo "🚀 Morning Trading System 시작"
echo "================================"

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 작업 디렉토리: $SCRIPT_DIR"

# 가상환경 경로
VENV_PATH="$SCRIPT_DIR/venv"

# 가상환경 존재 확인
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ 가상환경을 찾을 수 없습니다: $VENV_PATH"
    echo "다음 명령어로 가상환경을 생성하세요:"
    echo "python3 -m venv venv"
    exit 1
fi

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source "$VENV_PATH/bin/activate"

# Python 경로 확인
echo "🐍 Python 경로: $(which python)"
echo "📦 Python 버전: $(python --version)"

# 필요한 패키지 설치 확인
echo "📦 패키지 설치 확인 중..."
pip install -q beautifulsoup4 requests

# 애플리케이션 실행
echo "🎯 애플리케이션 시작..."
echo "================================"

# 사용자 선택
echo "실행할 기능을 선택하세요:"
echo "1. 대시보드 실행 (streamlit)"
echo "2. 애널리스트 평점 테스트"
echo "3. 주식 가격 조회 테스트"
echo "4. 종료"

read -p "선택 (1-4): " choice

case $choice in
    1)
        echo "📊 대시보드 실행 중..."
        streamlit run dashboard.py
        ;;
    2)
        echo "📈 애널리스트 평점 테스트 실행 중..."
        python test_venv.py
        ;;
    3)
        echo "💰 주식 가격 조회 테스트 실행 중..."
        python -c "
import sys
sys.path.append('.')
from agent.tools import get_real_stock_price
print('삼성전자 현재가:', get_real_stock_price('005930'))
print('SK하이닉스 현재가:', get_real_stock_price('000660'))
"
        ;;
    4)
        echo "👋 종료합니다."
        exit 0
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo "✅ 완료!"
