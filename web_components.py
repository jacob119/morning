import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time
from agent.tools import TOOLS

def create_stock_metrics(stock_code: str):
    """주식 메트릭 카드를 생성합니다."""
    # 주식명 조회
    stock_name = ""
    try:
        if 'get_stock_name' in TOOLS:
            stock_name = TOOLS['get_stock_name'](stock_code)
    except Exception as e:
        st.error(f"주식명 조회 중 오류: {e}")
    
    # 주식명 표시
    if stock_name:
        st.markdown(f"### 📊 {stock_name}({stock_code}) 분석")
    else:
        st.markdown(f"### 📊 {stock_code} 분석")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 실제 데이터 대신 더미 데이터 사용
    current_price = 72000 + random.randint(-5000, 5000)
    change = random.randint(-2000, 2000)
    change_percent = (change / current_price) * 100
    
    with col1:
        st.metric(
            label="현재가",
            value=f"{current_price:,}원",
            delta=f"{change:+,}원 ({change_percent:+.1f}%)"
        )
    
    with col2:
        volume = random.randint(10000000, 50000000)
        volume_change = random.randint(-5000000, 5000000)
        st.metric(
            label="거래량",
            value=f"{volume:,}",
            delta=f"{volume_change:+,}"
        )
    
    with col3:
        market_cap = current_price * random.randint(1000000000, 5000000000)
        st.metric(
            label="시가총액",
            value=f"{market_cap/1000000000000:.1f}조원"
        )
    
    with col4:
        per = random.uniform(10, 25)
        st.metric(
            label="PER",
            value=f"{per:.1f}"
        )

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
    portfolio = [
        {
            "종목코드": "005930",
            "종목명": "삼성전자",
            "보유수량": "100주",
            "평균단가": "70,000원",
            "현재가": "72,000원",
            "수익률": "+2.86%",
            "평가손익": "+200,000원"
        },
        {
            "종목코드": "000660",
            "종목명": "SK하이닉스",
            "보유수량": "50주",
            "평균단가": "120,000원",
            "현재가": "125,000원",
            "수익률": "+4.17%",
            "평가손익": "+250,000원"
        }
    ]
    
    return pd.DataFrame(portfolio)

def display_analysis_result(result):
    """분석 결과를 표시합니다."""
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

def create_sidebar_config():
    """사이드바 설정을 생성합니다."""
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 주식 코드 입력
        stock_code = st.text_input(
            "주식 코드",
            value="005930",
            help="분석할 주식 코드를 입력하세요 (예: 005930)"
        )
        
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
        else:
            st.session_state.run_analysis = False
        
        return stock_code, max_iterations, chart_days
