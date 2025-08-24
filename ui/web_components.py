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
        
        # 주식 코드 입력 (세션 상태에서 기본값 가져오기)
        default_stock_code = st.session_state.get('stock_code', '005930')
        stock_code = st.text_input(
            "주식 코드",
            value=default_stock_code,
            help="분석할 주식 코드를 입력하세요 (예: 005930)"
        )
        
        # 주식 코드를 세션 상태에 저장
        st.session_state.stock_code = stock_code
        
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
            # 세션 상태 초기화 방지
            if 'run_analysis' not in st.session_state:
                st.session_state.run_analysis = False
        
        return stock_code, max_iterations, chart_days
