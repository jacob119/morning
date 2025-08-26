#!/bin/bash

echo "=== Slack Bot 시작 ==="

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다."
    echo "💡 SLACK_SETUP.md 파일을 참고하여 .env 파일을 생성해주세요."
    exit 1
fi

# Slack 봇 실행
echo "🚀 Slack Bot 시작 중..."
python slack_bot.py
