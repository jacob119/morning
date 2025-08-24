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
            logger.info(f"📁 토큰 캐시 파일 발견: {TOKEN_CACHE_FILE}")
            with open(TOKEN_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # 토큰 만료 시간 확인
            expires_at = datetime.fromisoformat(cache_data['expires_at'])
            current_time = datetime.now()
            
            logger.info(f"⏰ 토큰 만료 시간: {expires_at}")
            logger.info(f"🕐 현재 시간: {current_time}")
            
            if current_time < expires_at:
                remaining_time = expires_at - current_time
                logger.info(f"✅ 캐시된 KIS 토큰 사용 가능 (남은 시간: {remaining_time})")
                return cache_data['access_token']
            else:
                logger.info(f"⏰ 캐시된 KIS 토큰 만료됨 (만료 시간: {expires_at})")
                return None
        else:
            logger.info(f"📁 토큰 캐시 파일 없음: {TOKEN_CACHE_FILE}")
    except Exception as e:
        logger.error(f"💥 토큰 캐시 로드 실패: {e}")
    return None

def save_token_cache(access_token, expires_in=86400):
    """토큰을 캐시에 저장합니다."""
    try:
        logger.info(f"💾 KIS 토큰 캐시 저장 시작")
        
        # 캐시 디렉토리 생성
        cache_dir = os.path.dirname(TOKEN_CACHE_FILE)
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"📁 캐시 디렉토리 확인: {cache_dir}")
        
        # 만료 시간 계산 (현재 시간 + expires_in 초)
        current_time = datetime.now()
        expires_at = current_time + timedelta(seconds=expires_in)
        
        cache_data = {
            'access_token': access_token,
            'expires_at': expires_at.isoformat(),
            'cached_at': current_time.isoformat()
        }
        
        logger.info(f"⏰ 토큰 만료 시간: {expires_at}")
        logger.info(f"🕐 캐시 저장 시간: {current_time}")
        
        with open(TOKEN_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"✅ KIS 토큰 캐시 저장 완료: {TOKEN_CACHE_FILE}")
        logger.info(f"⏰ 토큰 만료 시간: {expires_at}")
        return True
    except Exception as e:
        logger.error(f"💥 토큰 캐시 저장 실패: {e}")
        return False

def get_kis_token():
    """KIS API 토큰을 발급받거나 캐시에서 로드합니다."""
    try:
        # 먼저 캐시에서 토큰 확인
        cached_token = load_token_cache()
        if cached_token:
            logger.info("✅ KIS 토큰 캐시 사용 - 정상")
            return cached_token
        
        # 캐시에 없거나 만료된 경우 새로 발급
        logger.info("🔄 새로운 KIS 토큰 발급 요청 시작")
        
        url = f"{API_CONFIG['KIS']['BASE_URL']}/oauth2/tokenP"
        headers = {
            "content-type": "application/json"
        }
        body = {
            "grant_type": "client_credentials",
            "appkey": AUTH_CONFIG["APP_KEY"],
            "appsecret": AUTH_CONFIG["APP_SECRET"]
        }
        
        logger.info(f"📡 KIS 토큰 요청 URL: {url}")
        logger.info(f"🔑 KIS APP_KEY: {AUTH_CONFIG['APP_KEY'][:20]}...")
        logger.info(f"🔐 KIS APP_SECRET: {AUTH_CONFIG['APP_SECRET'][:20]}...")
        
        # JSON 형식으로 요청
        logger.info("🚀 KIS API 토큰 요청 전송 중...")
        response = requests.post(url, headers=headers, data=json.dumps(body))
        logger.info(f"📊 KIS 토큰 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info("✅ KIS 토큰 발급 성공")
            
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 86400)
            
            logger.info(f"⏰ 토큰 만료 시간: {expires_in}초")
            
            # 토큰을 캐시에 저장
            save_token_cache(access_token, expires_in)
            
            return access_token
        else:
            logger.error(f"❌ KIS 토큰 요청 실패: {response.status_code}")
            logger.error(f"📄 KIS 토큰 응답 내용: {response.text}")
            return None
    except Exception as e:
        logger.error(f"💥 KIS 토큰 발급 중 오류: {e}")
        return None

def get_stock_name(stock_code):
    """KIS API를 사용하여 주식 코드로 주식명을 조회합니다."""
    try:
        logger.info(f"🏷️ 주식명 조회 시작: {stock_code}")
        
        # 주요 주식들의 매핑 테이블
        stock_name_mapping = {
            '005930': '삼성전자',
            '000660': 'SK하이닉스',
            '035420': 'NAVER',
            '051910': 'LG화학',
            '006400': '삼성SDI',
            '207940': '삼성바이오로직스',
            '068270': '셀트리온',
            '323410': '카카오',
            '035720': '카카오',
            '051900': 'LG생활건강',
            '373220': 'LG에너지솔루션',
            '005380': '현대차',
            '000270': '기아',
            '006980': '우성사료',
            '017670': 'SK텔레콤',
            '015760': '한국전력',
            '034020': '두산에너빌리티',
            '010130': '고려아연',
            '011070': 'LG이노텍',
            '009150': '삼성전기',
            '012330': '현대모비스',
            '028260': '삼성물산',
            '010950': 'S-Oil',
            '018260': '삼성에스디에스',
            '032830': '삼성생명',
            '086790': '하나금융지주',
            '055550': '신한지주',
            '105560': 'KB금융',
            '316140': '우리금융지주',
            '138930': 'BNK금융지주',
            '024110': '기업은행',
            '004170': '신세계',
            '023530': '롯데쇼핑',
            '035250': '강원랜드'
        }
        
        # 매핑 테이블에서 주식명 찾기
        if stock_code in stock_name_mapping:
            stock_name = stock_name_mapping[stock_code]
            logger.info(f"✅ 주식명 조회 성공 (매핑 테이블): {stock_code} -> {stock_name}")
            return stock_name
        
        logger.info(f"🔍 매핑 테이블에 없음, KIS API 조회 시도: {stock_code}")
        
        # 매핑 테이블에 없는 경우 KIS API 시도
        token = get_kis_token()
        if not token:
            logger.warning("❌ KIS 토큰 획득 실패 (주식명 조회)")
            raise Exception("KIS API 토큰을 가져올 수 없습니다.")
        
        # 주식명 검색 API 사용
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
        
        logger.info(f"📡 주식명 API 요청 URL: {url}")
        logger.info(f"🔍 조회 주식 코드: {stock_code}")
        
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"📊 주식명 API 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"📄 KIS API 응답 코드: {data.get('rt_cd')}")
            
            if data.get('rt_cd') == '0':
                output = data.get('output', {})
                
                # 여러 필드에서 주식명 찾기
                stock_name = (
                    output.get('hts_kor_isnm', '') or  # 한글 종목명
                    output.get('bstp_kor_isnm', '') or  # 업종명 (임시)
                    ''
                )
                
                logger.info(f"📋 API 응답 주식명 필드: hts_kor_isnm='{output.get('hts_kor_isnm', '')}', bstp_kor_isnm='{output.get('bstp_kor_isnm', '')}'")
                
                if stock_name and stock_name not in ['전기·전자', 'IT 서비스', '화학', '의약품', '자동차', '철강금속']:  # 업종명이 아닌 경우만
                    logger.info(f"✅ 주식명 조회 성공 (KIS API): {stock_code} -> {stock_name}")
                    return stock_name
                else:
                    logger.warning(f"⚠️ 주식명을 찾을 수 없음: {stock_code} (응답: {stock_name})")
                    return None
            else:
                error_msg = data.get('msg1', '알 수 없는 오류')
                logger.error(f"❌ KIS API 오류 (주식명 조회): {error_msg}")
                logger.error(f"📄 전체 응답: {data}")
                raise Exception(f"KIS API 오류: {error_msg}")
        else:
            logger.error(f"❌ KIS API 요청 실패 (주식명 조회): {response.status_code}")
            logger.error(f"📄 응답 내용: {response.text}")
            raise Exception(f"KIS API 요청 실패: {response.status_code}")
            
    except Exception as e:
        logger.error(f"💥 주식명 조회 중 오류: {e}")
        raise Exception(f"주식명 조회 실패: {e}")

def get_real_stock_price(stock_code):
    """실제 KIS API를 사용하여 주식 가격을 조회합니다."""
    try:
        logger.info(f"📈 주식 가격 조회 시작: {stock_code}")
        
        token = get_kis_token()
        if not token:
            logger.warning("❌ KIS 토큰 획득 실패")
            raise Exception("KIS API 토큰을 가져올 수 없습니다.")
        
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
        
        logger.info(f"📡 주식 가격 API 요청 URL: {url}")
        logger.info(f"🔍 조회 주식 코드: {stock_code}")
        
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"📊 주식 가격 API 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"📄 KIS API 응답 코드: {data.get('rt_cd')}")
            
            if data.get('rt_cd') == '0':
                output = data.get('output', {})
                price = output.get('stck_prpr', '0')  # 현재가
                change = output.get('prdy_vrss', '0')  # 전일대비
                change_rate = output.get('prdy_ctrt', '0')  # 전일대비등락율
                stock_name = output.get('hts_kor_isnm', '')  # 한글 종목명
                
                logger.info(f"✅ 주식 가격 조회 성공: {stock_code}")
                logger.info(f"💰 현재가: {price}원")
                logger.info(f"📈 전일대비: {change}원 ({change_rate}%)")
                
                # 문자열을 정수로 변환
                try:
                    price_int = int(price)
                    change_int = int(change)
                    change_rate_float = float(change_rate)
                    
                    # 추가 정보 추출
                    volume = output.get('acml_vol', '0')  # 거래량
                    trade_amount = output.get('acml_tr_pbmn', '0')  # 거래대금
                    
                    logger.info(f"📊 거래량: {volume}주")
                    logger.info(f"💵 거래대금: {trade_amount}원")
                    
                    # 주식명 조회
                    stock_name_display = get_stock_name(stock_code)
                    name_display = f"{stock_name_display}({stock_code})" if stock_name_display else stock_code
                    
                    # 현재 시간 추가
                    current_time = datetime.now().strftime("%H:%M:%S")
                    
                    result = f"[{current_time}] {name_display} 현재 주가는 : '{price_int:,}원' 입니다. (전일대비 {change_int:+,}원, {change_rate_float:+.2f}%) | 거래량: {int(volume):,}주"
                    logger.info(f"📋 최종 결과: {result}")
                    return result
                except (ValueError, TypeError) as e:
                    logger.warning(f"⚠️ 데이터 변환 실패: {e}")
                    # 변환 실패 시 기본 형식으로 반환
                    stock_name_display = get_stock_name(stock_code)
                    name_display = f"{stock_name_display}({stock_code})" if stock_name_display else stock_code
                    current_time = datetime.now().strftime("%H:%M:%S")
                    return f"[{current_time}] {name_display} 현재 주가는 : '{price}원' 입니다. (전일대비 {change}원, {change_rate}%)"
            else:
                error_msg = data.get('msg1', '알 수 없는 오류')
                logger.error(f"❌ KIS API 오류: {error_msg}")
                logger.error(f"📄 전체 응답: {data}")
                raise Exception(f"KIS API 오류: {error_msg}")
        else:
            logger.error(f"❌ KIS API 요청 실패: {response.status_code}")
            logger.error(f"📄 응답 내용: {response.text}")
            raise Exception(f"KIS API 요청 실패: {response.status_code}")
            
    except Exception as e:
        logger.error(f"💥 주식 가격 조회 중 오류: {e}")
        raise Exception(f"주식 가격 조회 실패: {e}")

# 증권사 리포트 조회 Tool
def get_stock_reports(stock_code):
    """증권사 리포트를 조회합니다."""
    try:
        logger.info(f"📊 증권사 리포트 조회 시작: {stock_code}")
        
        # 주식명 조회
        stock_name = get_stock_name(stock_code)
        stock_display = f"{stock_name}({stock_code})" if stock_name else stock_code
        
        # OpenAI API 키 확인
        if API_CONFIG['OPENAI']['ACCESS_KEY'] == "your openai accesskey":
            logger.warning("⚠️ OpenAI API 키가 설정되지 않음 - 더미 리포트 사용")
            # 더미 리포트 반환
            reports = [
                "Buy, 목표가 80,000원",
                "Hold, 목표가 75,000원", 
                "Strong Buy, 목표가 85,000원",
                "Outperform, 목표가 82,000원"
            ]
            report = random.choice(reports)
            return f"{stock_display} 관련 증권사 리포트: '{report}' 입니다."
        
        # OpenAI API를 사용한 리포트 생성
        try:
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                model=API_CONFIG['OPENAI']['MODEL_NAME'],
                temperature=0.6,
                openai_api_key=API_CONFIG['OPENAI']['ACCESS_KEY']
            )
            
            # 증권사 리포트 생성 프롬프트
            prompt = f"""
            다음 주식에 대한 증권사 리포트를 생성해주세요:
            
            주식: {stock_display}
            
            다음 조건을 만족하는 리포트를 생성해주세요:
            1. 투자의견 (Buy, Hold, Sell, Strong Buy, Outperform 중 하나)
            2. 목표가 (현실적인 주가 범위)
            3. 간단한 투자 근거
            
            예시 형식:
            - "Buy, 목표가 85,000원 (기술 혁신으로 성장 기대)"
            - "Hold, 목표가 75,000원 (안정적 성장세 유지)"
            - "Strong Buy, 목표가 90,000원 (신제품 출시로 실적 개선)"
            - "Outperform, 목표가 82,000원 (해외 시장 진출 확대)"
            
            리포트 내용만 간단히 답변해주세요.
            """
            
            logger.info(f"🤖 OpenAI에 리포트 생성 요청: {stock_display}")
            response = llm.invoke(prompt)
            report_content = response.content.strip()
            
            # 응답 정리 (따옴표 제거 등)
            report_content = report_content.replace('"', '').replace("'", "").strip()
            
            logger.info(f"✅ 리포트 생성 완료: {report_content}")
            
            return f"{stock_display} 관련 증권사 리포트: '{report_content}' 입니다."
            
        except Exception as openai_error:
            logger.error(f"❌ OpenAI API 오류: {openai_error}")
            logger.info("🔄 더미 리포트로 대체")
            
            # OpenAI 오류 시 더미 리포트 반환
            reports = [
                "Buy, 목표가 80,000원",
                "Hold, 목표가 75,000원", 
                "Strong Buy, 목표가 85,000원",
                "Outperform, 목표가 82,000원"
            ]
            report = random.choice(reports)
            return f"{stock_display} 관련 증권사 리포트: '{report}' 입니다."
            
    except Exception as e:
        logger.error(f"💥 증권사 리포트 조회 중 오류: {e}")
        return f"{stock_code} 리포트 조회 중 오류가 발생했습니다."

# 뉴스 조회 Tool
def get_stock_news(stock_code):
    """주식 관련 뉴스를 조회합니다."""
    try:
        logger.info(f"📰 주식 뉴스 조회 시작: {stock_code}")
        
        # 주식명 조회
        stock_name = get_stock_name(stock_code)
        stock_display = f"{stock_name}({stock_code})" if stock_name else stock_code
        
        # OpenAI API 키 확인
        if API_CONFIG['OPENAI']['ACCESS_KEY'] == "your openai accesskey":
            logger.warning("⚠️ OpenAI API 키가 설정되지 않음 - 더미 뉴스 사용")
            # 더미 뉴스 반환
            news_list = [
                "시장 점유율 확대 중",
                "신제품 출시 발표",
                "분기 실적 호조",
                "해외 진출 확대",
                "기술 혁신으로 경쟁력 강화",
                "ESG 경영 강화",
                "디지털 전환 가속화",
                "글로벌 시장 진출 확대"
            ]
            news = random.choice(news_list)
            return f"{stock_display} 관련 최신 뉴스: '{news}' 입니다."
        
        # OpenAI API를 사용한 뉴스 생성
        try:
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                model=API_CONFIG['OPENAI']['MODEL_NAME'],
                temperature=0.7,
                openai_api_key=API_CONFIG['OPENAI']['ACCESS_KEY']
            )
            
            # 주식 관련 뉴스 생성 프롬프트
            prompt = f"""
            다음 주식에 대한 최신 뉴스를 생성해주세요:
            
            주식: {stock_display}
            
            다음 조건을 만족하는 뉴스를 생성해주세요:
            1. 해당 기업의 최근 동향이나 성과를 반영
            2. 투자자들이 관심을 가질 만한 내용
            3. 간결하고 명확한 문장
            4. 긍정적이거나 중립적인 톤
            5. 20자 이내의 짧은 뉴스
            
            예시 형식:
            - "신제품 출시로 매출 성장 기대"
            - "해외 시장 진출 확대로 실적 개선"
            - "기술 혁신으로 경쟁력 강화"
            - "ESG 경영 강화로 브랜드 가치 상승"
            
            뉴스 내용만 간단히 답변해주세요.
            """
            
            logger.info(f"🤖 OpenAI에 뉴스 생성 요청: {stock_display}")
            response = llm.invoke(prompt)
            news_content = response.content.strip()
            
            # 응답 정리 (따옴표 제거 등)
            news_content = news_content.replace('"', '').replace("'", "").strip()
            
            logger.info(f"✅ 뉴스 생성 완료: {news_content}")
            
            return f"{stock_display} 관련 최신 뉴스: '{news_content}' 입니다."
            
        except Exception as openai_error:
            logger.error(f"❌ OpenAI API 오류: {openai_error}")
            logger.info("🔄 더미 뉴스로 대체")
            
            # OpenAI 오류 시 더미 뉴스 반환
            news_list = [
                "시장 점유율 확대 중",
                "신제품 출시 발표",
                "분기 실적 호조",
                "해외 진출 확대",
                "기술 혁신으로 경쟁력 강화",
                "ESG 경영 강화",
                "디지털 전환 가속화",
                "글로벌 시장 진출 확대"
            ]
            news = random.choice(news_list)
            return f"{stock_display} 관련 최신 뉴스: '{news}' 입니다."
            
    except Exception as e:
        logger.error(f"💥 주식 뉴스 조회 중 오류: {e}")
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
    'fetch_report': get_stock_reports,
    'get_stock_name': get_stock_name  # 주식명 조회 기능 추가
}
