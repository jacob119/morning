import requests
import random
import json
import os
import time
from datetime import datetime, timedelta
from utils.logger import get_logger
from config.setting import AUTH_CONFIG, API_CONFIG

logger = get_logger(__name__)

# 토큰 캐시 파일 경로
TOKEN_CACHE_FILE = "config/kis_token_cache.json"

def load_token_cache():
    """캐시된 토큰을 로드합니다."""
    try:
        if os.path.exists(TOKEN_CACHE_FILE):
            with open(TOKEN_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # 토큰 만료 시간 확인
            expires_at = datetime.fromisoformat(cache_data['expires_at'])
            if datetime.now() < expires_at:
                logger.info("캐시된 KIS 토큰 사용")
                return cache_data['access_token']
            else:
                logger.info("캐시된 KIS 토큰 만료됨")
                return None
    except Exception as e:
        logger.error(f"토큰 캐시 로드 실패: {e}")
    return None

def save_token_cache(access_token, expires_in=86400):
    """토큰을 캐시에 저장합니다."""
    try:
        # 캐시 디렉토리 생성
        os.makedirs(os.path.dirname(TOKEN_CACHE_FILE), exist_ok=True)
        
        # 만료 시간 계산 (현재 시간 + expires_in 초)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        cache_data = {
            'access_token': access_token,
            'expires_at': expires_at.isoformat(),
            'cached_at': datetime.now().isoformat()
        }
        
        with open(TOKEN_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"KIS 토큰 캐시 저장 완료 (만료: {expires_at})")
        return True
    except Exception as e:
        logger.error(f"토큰 캐시 저장 실패: {e}")
        return False

def get_kis_token():
    """KIS API 토큰을 발급받거나 캐시에서 로드합니다."""
    try:
        # 먼저 캐시에서 토큰 확인
        cached_token = load_token_cache()
        if cached_token:
            return cached_token
        
        # 캐시에 없거나 만료된 경우 새로 발급
        logger.info("새로운 KIS 토큰 발급 요청")
        
        url = f"{API_CONFIG['KIS']['BASE_URL']}/oauth2/tokenP"
        headers = {
            "content-type": "application/json"
        }
        body = {
            "grant_type": "client_credentials",
            "appkey": AUTH_CONFIG["APP_KEY"],
            "appsecret": AUTH_CONFIG["APP_SECRET"]
        }
        
        logger.info(f"KIS 토큰 요청 URL: {url}")
        logger.info(f"KIS APP_KEY: {AUTH_CONFIG['APP_KEY'][:20]}...")
        logger.info(f"KIS APP_SECRET: {AUTH_CONFIG['APP_SECRET'][:20]}...")
        
        # JSON 형식으로 요청
        response = requests.post(url, headers=headers, data=json.dumps(body))
        logger.info(f"KIS 토큰 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info(f"KIS 토큰 발급 성공")
            
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 86400)
            
            # 토큰을 캐시에 저장
            save_token_cache(access_token, expires_in)
            
            return access_token
        else:
            logger.error(f"KIS token request failed: {response.status_code}")
            logger.error(f"KIS token response: {response.text}")
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
                
                # 문자열을 정수로 변환
                try:
                    price_int = int(price)
                    change_int = int(change)
                    change_rate_float = float(change_rate)
                    
                    return f"{stock_code} 현재 주가는 : '{price_int:,}원' 입니다. (전일대비 {change_int:+,}원, {change_rate_float:+.2f}%)"
                except (ValueError, TypeError):
                    # 변환 실패 시 기본 형식으로 반환
                    return f"{stock_code} 현재 주가는 : '{price}원' 입니다. (전일대비 {change}원, {change_rate}%)"
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
