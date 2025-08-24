import requests
import random
from utils.logger import get_logger
from config.setting import AUTH_CONFIG, API_CONFIG

logger = get_logger(__name__)

def get_kis_token():
    """KIS API 토큰을 발급받습니다."""
    try:
        url = f"{API_CONFIG['KIS']['BASE_URL']}/oauth2/tokenP"
        headers = {
            "content-type": "application/json"
        }
        body = {
            "grant_type": "client_credentials",
            "appkey": AUTH_CONFIG["APP_KEY"],
            "appsecret": AUTH_CONFIG["APP_SECRET"]
        }
        
        response = requests.post(url, headers=headers, data=str(body))
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
        else:
            logger.error(f"KIS token request failed: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting KIS token: {e}")
        return None

def get_real_stock_price(stock_code):
    """실제 KIS API를 사용하여 주식 가격을 조회합니다."""
    try:
        token = get_kis_token()
        if not token:
            logger.warning("Failed to get KIS token, using dummy data")
            return get_stock_price(stock_code)
        
        url = f"{API_CONFIG['KIS']['BASE_URL']}/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": AUTH_CONFIG["APP_KEY"],
            "appsecret": AUTH_CONFIG["APP_SECRET"],
            "tr_id": "FHKST01010100"
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('rt_cd') == '0':
                output = data.get('output', {})
                price = output.get('stck_prpr', '0')  # 현재가
                change = output.get('prdy_vrss', '0')  # 전일대비
                change_rate = output.get('prdy_ctrt', '0')  # 전일대비등락율
                
                return f"{stock_code} 현재 주가는 : '{int(price):,}원' 입니다. (전일대비 {change:+,}원, {change_rate:+.2f}%)"
            else:
                logger.error(f"KIS API error: {data.get('msg1')}")
                return get_stock_price(stock_code)  # 더미 데이터로 폴백
        else:
            logger.error(f"KIS API request failed: {response.status_code}")
            return get_stock_price(stock_code)  # 더미 데이터로 폴백
            
    except Exception as e:
        logger.error(f"Error fetching real stock price: {e}")
        return get_stock_price(stock_code)  # 더미 데이터로 폴백

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

# 현재 주식 가격 조회 Tool (더미 데이터)
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
    'fetch_price': get_real_stock_price,  # 실제 KIS API 사용
    'fetch_news': get_stock_news,
    'fetch_report': get_stock_reports
}
