import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Slack 설정
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')

# 보유 주식 정보 (예시 데이터)
PORTFOLIO_STOCKS = {
    "005930": {"name": "삼성전자", "quantity": 10, "avg_price": 70000},
    "000660": {"name": "SK하이닉스", "quantity": 5, "avg_price": 250000},
    "035420": {"name": "NAVER", "quantity": 3, "avg_price": 220000},
    "035720": {"name": "카카오", "quantity": 8, "avg_price": 65000},
    "051910": {"name": "LG화학", "quantity": 2, "avg_price": 500000},
    "006400": {"name": "삼성SDI", "quantity": 4, "avg_price": 400000},
    "207940": {"name": "삼성바이오로직스", "quantity": 1, "avg_price": 800000},
    "068270": {"name": "셀트리온", "quantity": 2, "avg_price": 150000},
    "323410": {"name": "카카오뱅크", "quantity": 6, "avg_price": 30000},
    "035720": {"name": "카카오", "quantity": 8, "avg_price": 65000}
}

# Slack 메시지 템플릿
MESSAGE_TEMPLATES = {
    "portfolio_response": """
📊 *내 보유 주식 현황*

{stock_list}

💰 *총 투자금액*: {total_investment:,}원
📈 *현재 총액*: {current_total:,}원
📊 *수익률*: {profit_rate:+.2f}%
💵 *평가손익*: {profit_loss:+,}원
    """,
    
    "stock_item": """
• *{name}* ({code})
  📈 현재가: {current_price:,}원
  📊 보유수량: {quantity}주
  💰 평균단가: {avg_price:,}원
  📊 수익률: {profit_rate:+.2f}%
  💵 평가손익: {profit_loss:+,}원
    """
}
