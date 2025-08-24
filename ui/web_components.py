import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agent.tools import TOOLS
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.info("시스템을 재시작해주세요.")
    st.stop()

# 주요 보유 주식 목록
PORTFOLIO_STOCKS = {
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

def create_stock_metrics(stock_code: str):
    """주식 메트릭 카드를 생성합니다."""
    try:
        # 주식 코드 유효성 검사
        if not stock_code or stock_code.strip() == "":
            st.info("주식 코드를 입력해주세요.")
            return
        
        # 주식명 조회
        stock_name = ""
        try:
            if 'get_stock_name' in TOOLS:
                stock_name = TOOLS['get_stock_name'](stock_code)
        except Exception as e:
            st.warning(f"주식명 조회 중 오류: {e}")
        
        # 주식명 표시
        if stock_name:
            st.markdown(f"### 📊 {stock_name}({stock_code}) 실시간 분석")
        else:
            st.markdown(f"### 📊 {stock_code} 실시간 분석")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # 실제 KIS API 데이터 사용
        if 'fetch_price' in TOOLS:
            try:
                price_result = TOOLS['fetch_price'](stock_code)
                # 결과에서 가격 정보 추출
                import re
                price_match = re.search(r"'([0-9,]+)원'", price_result)
                change_match = re.search(r"전일대비 ([+-][0-9,]+)원", price_result)
                percent_match = re.search(r"([+-][0-9.]+)%", price_result)
                volume_match = re.search(r"거래량: ([0-9,]+)주", price_result)
                
                if price_match and change_match and percent_match:
                    current_price = int(price_match.group(1).replace(',', ''))
                    change = int(change_match.group(1).replace(',', ''))
                    change_percent = float(percent_match.group(1))
                    
                    with col1:
                        st.metric(
                            label="현재가",
                            value=f"{current_price:,}원",
                            delta=f"{change:+,}원 ({change_percent:+.1f}%)"
                        )
                        # 실시간 업데이트 시간 표시
                        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')} 업데이트")
                    
                    with col2:
                        if volume_match:
                            volume = int(volume_match.group(1).replace(',', ''))
                            st.metric(
                                label="거래량",
                                value=f"{volume:,}주"
                            )
                        else:
                            st.metric(
                                label="거래량",
                                value="조회 중..."
                            )
                    
                    with col3:
                        # 시가총액은 현재가 * 발행주식수 (대략적 계산)
                        market_cap = current_price * 1000000000  # 10억주 기준
                        st.metric(
                            label="시가총액",
                            value=f"{market_cap/1000000000000:.1f}조원"
                        )
                    
                    with col4:
                        # PER은 현재가 / EPS (대략적 계산)
                        eps = current_price / 15  # PER 15 기준
                        per = current_price / eps if eps > 0 else 0
                        st.metric(
                            label="PER",
                            value=f"{per:.1f}"
                        )
                else:
                    st.warning("실시간 데이터를 가져올 수 없습니다.")
                    st.info("주식 코드를 확인하거나 잠시 후 다시 시도해주세요.")
                    
            except Exception as e:
                st.warning(f"데이터 조회 중 일시적 오류가 발생했습니다.")
                st.info("잠시 후 다시 시도해주세요.")
        else:
            st.warning("API 도구를 찾을 수 없습니다.")
            st.info("시스템 설정을 확인해주세요.")
            
    except Exception as e:
        st.error(f"주식 메트릭 생성 중 오류가 발생했습니다: {e}")
        st.info("KIS API 연결 상태를 확인해주세요.")

def create_stock_chart(stock_code: str, days: int = 30):
    """주식 차트를 생성합니다."""
    # 샘플 데이터 생성
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 가격 데이터 생성 (더 현실적인 패턴)
    base_price = 72000
    prices = []
    for i in range(len(dates)):
        if i == 0:
            price = base_price
        else:
            # 이전 가격에 랜덤 변동 추가
            change = random.randint(-2000, 2000)
            price = prices[-1] + change
            price = max(price, 50000)  # 최소 가격 보장
        prices.append(price)
    
    # 캔들스틱 데이터 생성
    open_prices = [p - random.randint(0, 1000) for p in prices]
    high_prices = [p + random.randint(0, 1000) for p in prices]
    low_prices = [p - random.randint(0, 1000) for p in prices]
    close_prices = prices
    
    # 캔들스틱 차트
    fig = go.Figure(data=[go.Candlestick(
        x=dates,
        open=open_prices,
        high=high_prices,
        low=low_prices,
        close=close_prices,
        name="주가"
    )])
    
    # 주식명 조회
    stock_name = ""
    try:
        if 'get_stock_name' in TOOLS:
            stock_name = TOOLS['get_stock_name'](stock_code)
    except Exception:
        pass
    
    # 차트 제목 설정
    if stock_name:
        chart_title = f"{stock_name}({stock_code}) 주가 차트 ({days}일)"
    else:
        chart_title = f"{stock_code} 주가 차트 ({days}일)"
    
    fig.update_layout(
        title=chart_title,
        xaxis_title="날짜",
        yaxis_title="가격 (원)",
        height=500,
        template="plotly_white"
    )
    
    return fig

def create_volume_chart(stock_code: str, days: int = 30):
    """거래량 차트를 생성합니다."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 거래량 데이터 생성
    volumes = [random.randint(1000000, 5000000) for _ in range(len(dates))]
    
    fig = px.bar(
        x=dates, 
        y=volumes, 
        title=f"{stock_code} 거래량",
        labels={'x': '날짜', 'y': '거래량'}
    )
    
    fig.update_layout(
        height=300,
        template="plotly_white"
    )
    
    return fig

def create_analysis_history():
    """분석 기록을 생성합니다."""
    history = [
        {
            "날짜": "2024-08-24 11:53:49",
            "종목코드": "005930",
            "종목명": "삼성전자",
            "분석결과": "매수 추천",
            "목표가": "80,000원",
            "신뢰도": "85%"
        },
        {
            "날짜": "2024-08-24 11:53:56", 
            "종목코드": "000660",
            "종목명": "SK하이닉스",
            "분석결과": "관망",
            "목표가": "75,000원",
            "신뢰도": "72%"
        },
        {
            "날짜": "2024-08-24 10:30:15",
            "종목코드": "035420",
            "종목명": "NAVER",
            "분석결과": "매도 추천",
            "목표가": "180,000원",
            "신뢰도": "78%"
        }
    ]
    
    return pd.DataFrame(history)

def create_portfolio_summary():
    """포트폴리오 요약을 생성합니다."""
    portfolio = []
    
    # 주요 주식들을 포트폴리오에 추가
    for stock_code, stock_name in PORTFOLIO_STOCKS.items():
        # 랜덤한 보유 수량과 평균 단가 생성
        quantity = random.randint(10, 200)
        avg_price = random.randint(50000, 300000)
        current_price = avg_price + random.randint(-20000, 20000)
        
        # 수익률 계산
        profit_rate = ((current_price - avg_price) / avg_price) * 100
        profit_amount = (current_price - avg_price) * quantity
        
        portfolio.append({
            "종목코드": stock_code,
            "종목명": stock_name,
            "보유수량": f"{quantity}주",
            "평균단가": f"{avg_price:,}원",
            "현재가": f"{current_price:,}원",
            "수익률": f"{profit_rate:+.2f}%",
            "평가손익": f"{profit_amount:+,}원"
        })
    
    return pd.DataFrame(portfolio)

def display_analysis_result(result):
    """분석 결과를 표시합니다."""
    try:
        if not result or not hasattr(result, 'info_log'):
            st.warning("분석 결과가 없습니다.")
            return
        
        # 주식명 표시
        if hasattr(result, 'stock_name') and result.stock_name:
            st.subheader(f"📋 분석 결과 - {result.stock_name}({result.stock_code})")
        else:
            st.subheader(f"📋 분석 결과 - {result.stock_code}")
        
        # 진행률 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, log in enumerate(result.info_log):
            # 진행률 업데이트
            progress = (i + 1) / len(result.info_log)
            progress_bar.progress(progress)
            status_text.text(f"결과 표시 중... {i+1}/{len(result.info_log)}")
            
            # 결과 표시
            if "LLM 결정:" in log:
                st.markdown(f"**🤖 {log}**")
            else:
                st.markdown(f'<div class="analysis-result">{log}</div>', unsafe_allow_html=True)
            
            # 약간의 지연으로 애니메이션 효과
            time.sleep(0.1)
        
        # 완료
        progress_bar.progress(100)
        status_text.text("✅ 분석 완료!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"분석 결과 표시 중 오류가 발생했습니다: {e}")
        st.info("KIS API 연결 상태를 확인해주세요.")
        
        # 에러 시 기본 정보 표시
        if result and hasattr(result, 'stock_code'):
            st.subheader(f"📋 분석 결과 - {result.stock_code}")
            st.warning("분석 중 오류가 발생했습니다. KIS API 연결을 확인해주세요.")
        else:
            st.warning("분석 결과를 불러올 수 없습니다.")

def create_sidebar_config():
    """사이드바 설정을 생성합니다."""
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 보유 주식 목록 선택
        st.subheader("📋 보유 주식 목록")
        stock_options = {f"{name}({code})": code for code, name in PORTFOLIO_STOCKS.items()}
        
        # 현재 선택된 주식 코드
        current_stock_code = st.session_state.get('stock_code', '005930')
        
        # 현재 주식 코드에 해당하는 인덱스 찾기
        current_index = 0
        for i, (display_name, code) in enumerate(stock_options.items()):
            if code == current_stock_code:
                current_index = i
                break
        
        # 드롭다운에서 주식 선택
        selected_stock = st.selectbox(
            "주식 선택",
            options=list(stock_options.keys()),
            index=current_index,
            key="stock_selector",
            help="분석할 주식을 선택하세요"
        )
        
        # 선택된 주식 코드 추출
        selected_code = stock_options[selected_stock]
        
        # 주식 코드 입력 (선택된 주식 코드로 설정)
        stock_code = st.text_input(
            "주식 코드 (직접 입력)",
            value=selected_code,
            key="stock_code_input",
            help="분석할 주식 코드를 직접 입력하세요 (예: 005930)"
        )
        
        # 주식 코드를 세션 상태에 저장
        st.session_state.stock_code = stock_code
        
        # 주식 선택이 변경되었는지 확인하고 자동 분석 실행
        if 'last_selected_code' not in st.session_state:
            st.session_state.last_selected_code = selected_code
        
        # 선택된 주식이 변경되었으면 자동 분석 실행
        if st.session_state.last_selected_code != selected_code:
            st.session_state.stock_code = selected_code
            st.session_state.last_selected_code = selected_code
            st.session_state.run_analysis = True
            st.session_state.analysis_result = None
            st.success(f"🔄 {selected_code} 주식 분석을 시작합니다...")
            st.rerun()  # 페이지 재실행으로 즉시 반영
        
        # 텍스트 박스에서 직접 입력한 경우
        if 'last_input_code' not in st.session_state:
            st.session_state.last_input_code = stock_code
        
        if st.session_state.last_input_code != stock_code:
            st.session_state.run_analysis = True
            st.session_state.analysis_result = None
            st.session_state.last_input_code = stock_code
            st.success(f"🔄 {stock_code} 주식 분석을 시작합니다...")
            st.rerun()  # 페이지 재실행으로 즉시 반영
        
        # 분석 옵션
        st.subheader("📊 분석 옵션")
        auto_analyze = st.checkbox("자동 분석", value=True)
        max_iterations = st.slider("최대 반복 횟수", 1, 20, 10)
        
        # 차트 옵션
        st.subheader("📈 차트 옵션")
        chart_days = st.selectbox("차트 기간", [7, 30, 90, 180, 365], index=1)
        
        # 분석 실행 버튼
        if st.button("🚀 분석 시작", type="primary"):
            st.session_state.run_analysis = True
            st.session_state.analysis_result = None
        else:
            if 'run_analysis' not in st.session_state:
                st.session_state.run_analysis = False
        
        # 현재 선택된 주식 정보 표시
        st.subheader("📋 현재 선택된 주식")
        if stock_code in PORTFOLIO_STOCKS:
            st.info(f"**{PORTFOLIO_STOCKS[stock_code]}({stock_code})**")
        else:
            st.info(f"**{stock_code}**")
        
        return stock_code, max_iterations, chart_days
