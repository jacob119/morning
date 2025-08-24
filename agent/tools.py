import requests
import random
from utils.logger import get_logger

logger = get_logger(__name__)

# 증권사 리포트 조회 Tool
def get_stock_reports(stock_code):
    """증권사 리포트를 조회합니다."""
    try:
        logger.info(f"Fetching report for stock: {stock_code}")
        # Dummy Code : X-API 
        reports = [
            "Buy, 목표가 80,000원",
            "Hold, 목표가 75,000원", 
            "Strong Buy, 목표가 85,000원"
        ]
        report = random.choice(reports)
        return f"{stock_code} 관련 증권사 리포트: '{report}' 입니다."
    except Exception as e:
        logger.error(f"Error fetching report: {e}")
        return f"{stock_code} 리포트 조회 중 오류가 발생했습니다."

# 뉴스 조회 Tool
def get_stock_news(stock_code):
    """주식 관련 뉴스를 조회합니다."""
    try:
        logger.info(f"Fetching news for stock: {stock_code}")
        # Dummy Code : Crawling
        news_list = [
            "시장 점유율 확대 중",
            "신제품 출시 발표",
            "분기 실적 호조",
            "해외 진출 확대"
        ]
        news = random.choice(news_list)
        return f"{stock_code} 관련 최신 뉴스: '{news}' 입니다."
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return f"{stock_code} 뉴스 조회 중 오류가 발생했습니다."

# 현재 주식 가격 조회 Tool
def get_stock_price(stock_code):
    """현재 주식 가격을 조회합니다."""
    try:
        logger.info(f"Fetching price for stock: {stock_code}")
        # Dummy Code : 실제로는 KIS API 호출
        base_price = 72000
        variation = random.randint(-5000, 5000)
        price = base_price + variation
        return f"{stock_code} 현재 주가는 : '{price:,}원' 입니다."
    except Exception as e:
        logger.error(f"Error fetching price: {e}")
        return f"{stock_code} 가격 조회 중 오류가 발생했습니다."

# TOOLS 딕셔너리에 직접 등록
TOOLS = {
    'fetch_price': get_stock_price,
    'fetch_news': get_stock_news,
    'fetch_report': get_stock_reports
}
