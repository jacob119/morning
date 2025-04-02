import requests
import json
import os
import time
import logging
from datetime import datetime
from config import APP_KEY, APP_SECRET

TOKEN_FILE = "access_token.json"
TOKEN_EXPIRY_DURATION = 3600  # 1 hour in seconds
STOCK_CODES = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "신풍제약": "019170"
}
REQUEST_INTERVAL = 10  # seconds
LOG_FILE = "app.log"  # 로그 파일 경로


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(LOG_FILE),
    logging.StreamHandler()
])
def load_cached_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data.get("access_token"), data.get("timestamp", 0)
    return None, 0

def save_token(token):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({"access_token": token, "timestamp": time.time()}, f)

def get_access_token(app_key, app_secret):
    cached_token, cached_time = load_cached_token()
    now = time.time()

    # Use valid cached token if available (1 hour validity)
    if cached_token and (now - cached_time < TOKEN_EXPIRY_DURATION):
        return cached_token

    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }
    try:
        res = requests.post(url, headers=headers, data=json.dumps(body))
        res.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        token = res.json().get('access_token')
        if token:
            save_token(token)
            return token
        else:
            raise Exception("Token not found in response")
    except requests.exceptions.RequestException as e:
        logging.error(f"Token request failed: {e}")
    except Exception as e:
        logging.error(f"Exception occurred: {e}")

    if cached_token:
        logging.warning("Using cached token as fallback")
        return cached_token

    raise Exception("Failed to obtain access token and no cached token available")

def get_stock_price(access_token, app_key, app_secret, stock_code):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {access_token}",
        "appkey": app_key,
        "appsecret": app_secret,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code
    }
    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        return res.json().get('output', {})
    except requests.exceptions.RequestException as e:
        logging.error(f"Price request failed: {e}")
        raise

def format_price_won(value):
    try:
        value = int(value)
        return f"{value / 1000000000:.2f}천억 원"
    except (ValueError, TypeError):
        return "N/A"

def format_number(value):
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return "N/A"

def format_change(value):
    try:
        ivalue = int(value)
        sign = '+' if ivalue > 0 else ('-' if ivalue < 0 else '')
        return sign, f"{abs(ivalue):,}"
    except (ValueError, TypeError):
        return '', "N/A"

def format_percent(value):
    try:
        fvalue = float(value)
        sign = '+' if fvalue > 0 else ('-' if fvalue < 0 else '')
        return sign, f"{abs(fvalue):.2f}"
    except (ValueError, TypeError):
        return '', "N/A"

def color_text(text, sign):
    if sign == '+':
        return f"\033[91m{text}\033[0m"  # Red
    elif sign == '-':
        return f"\033[94m{text}\033[0m"  # Blue
    else:
        return text

def check_buy_signal(current_price, ma5, ma20):
    try:
        current = float(current_price)
        ma_5 = float(ma5)
        ma_20 = float(ma20)
        return ma_5 > ma_20 and current > ma_5
    except (ValueError, TypeError):
        return False

def print_stock_info(stock_name, stock_code, app_key, app_secret):
    access_token = get_access_token(app_key, app_secret)
    stock_data = get_stock_price(access_token, app_key, app_secret, stock_code)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {stock_name} 주식 정보")
    print(f"현재가: {format_number(stock_data.get('stck_prpr', 0))}원")

    chg_sign, chg_val = format_change(stock_data.get('prdy_vrss', 0))
    pct_sign, pct_val = format_percent(stock_data.get('prdy_ctrt', 0))
    chg_str = color_text(f"{chg_sign}{chg_val}원", chg_sign)
    pct_str = color_text(f"{pct_sign}{pct_val}%", pct_sign)
    print(f"전일대비: {chg_str} ({pct_str})")

    print(f"거래량: {format_number(stock_data.get('acml_vol', 0))}주")
    print(f"거래대금: {format_price_won(stock_data.get('acml_tr_pbmn', 0))}")

    if check_buy_signal(stock_data.get('stck_prpr', 0), stock_data.get('avrg_vol_5', 0), stock_data.get('avrg_vol_20', 0)):
        print("\033[92m[AI 매수 신호 발생 - 이동 평균 돌파]\033[0m")

    print("----------------------------")

def run_realtime_monitoring():
    while True:
        for stock_name, stock_code in STOCK_CODES.items():
            print_stock_info(stock_name, stock_code, APP_KEY, APP_SECRET)
        time.sleep(REQUEST_INTERVAL)

if __name__ == "__main__":
    logging.info("test")
    run_realtime_monitoring()
