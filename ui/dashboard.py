import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
import sys
import os
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agent.analytics import run, StockAnalyzer
    from agent.tools import TOOLS
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.info("시스템을 재시작해주세요.")
    st.stop()

import time
from ui.web_components import (
    create_stock_metrics, create_stock_chart, create_volume_chart,
    create_analysis_history, create_portfolio_summary, display_analysis_result,
    create_sidebar_config, create_news_analysis_tab, create_ai_chat_tab,
    PORTFOLIO_STOCKS
)

# Streamlit 캐싱 설정
@st.cache_data(ttl=300)  # 5분 캐시
def get_cached_data():
    """캐시된 데이터를 반환합니다."""
    return {
        'default_stock_code': '005930',
        'default_iterations': 10,
        'default_chart_days': 30
    }

# 페이지 설정
st.set_page_config(
    page_title="Morning - 주식 분석 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .analysis-result {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .portfolio-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# 캐시된 기본 데이터 가져오기
cached_data = get_cached_data()

# 세션 상태 초기화
if 'stock_code' not in st.session_state:
    st.session_state.stock_code = cached_data['default_stock_code']
if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'news_analysis' not in st.session_state:
    st.session_state.news_analysis = None
if 'real_time_news' not in st.session_state:
    st.session_state.real_time_news = None
if 'chat_session_id' not in st.session_state:
    st.session_state.chat_session_id = None

# 안전한 사이드바 설정
try:
    stock_code, max_iterations, chart_days = create_sidebar_config()
except Exception as e:
    st.error(f"사이드바 설정 중 오류: {e}")
    # 캐시된 기본값 사용
    stock_code = st.session_state.get('stock_code', cached_data['default_stock_code'])
    max_iterations = cached_data['default_iterations']
    chart_days = cached_data['default_chart_days']

# 메인 헤더
st.markdown('<h1 class="main-header">📈 Morning - 주식 분석 대시보드</h1>', unsafe_allow_html=True)

# 탭 생성
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 실시간 분석", "📈 차트", "💼 포트폴리오", "📰 뉴스 분석", "🤖 AI 상담", "📋 분석 기록", "⚙️ 설정"
])

with tab1:
    st.header("📊 실시간 주식 분석")
    
    # 현재 선택된 주식 정보 표시
    if stock_code in PORTFOLIO_STOCKS:
        st.info(f"**분석 대상: {PORTFOLIO_STOCKS[stock_code]}({stock_code})**")
    else:
        st.info(f"**분석 대상: {stock_code}**")
    
    # 안전한 주식 메트릭 카드 생성
    try:
        create_stock_metrics(stock_code)
    except Exception as e:
        st.error(f"주식 메트릭 생성 중 오류: {e}")
        st.info("페이지를 새로고침하거나 잠시 후 다시 시도해주세요.")
    
    # 분석 실행
    if st.session_state.get('run_analysis', False):
        try:
            with st.spinner(f"{stock_code} 주식 분석 중..."):
                # 분석 실행
                analyzer = StockAnalyzer()
                analyzer.max_iterations = max_iterations
                result = analyzer.analyze(stock_code)
                
                # 결과 표시
                st.success(f"✅ {stock_code} 분석 완료!")
                
                # 분석 결과를 세션에 저장
                st.session_state.analysis_result = result
                st.session_state.run_analysis = False
        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {e}")
            st.info("KIS API 연결을 확인해주세요.")
            
            # 에러 시 분석 실패 메시지만 표시
            st.warning("실시간 분석을 수행할 수 없습니다.")
            st.info("다음 사항을 확인해주세요:")
            st.info("1. KIS API 키가 올바르게 설정되었는지 확인")
            st.info("2. 인터넷 연결 상태 확인")
            st.info("3. KIS API 서비스 상태 확인")
            st.session_state.run_analysis = False
    
    # 분석 결과 표시
    if hasattr(st.session_state, 'analysis_result') and st.session_state.analysis_result:
        # 현재 주식 코드와 분석 결과의 주식 코드가 일치하는지 확인
        if hasattr(st.session_state.analysis_result, 'stock_code') and st.session_state.analysis_result.stock_code == stock_code:
            display_analysis_result(st.session_state.analysis_result)
        else:
            st.info("다른 주식의 분석 결과입니다. 새로운 분석을 실행해주세요.")
    else:
        st.info("분석 결과가 없습니다. '분석 시작' 버튼을 클릭하거나 주식을 선택해주세요.")

with tab2:
    st.header("📈 주식 차트")
    
    # 차트 컨테이너
    chart_container = st.container()
    
    with chart_container:
        try:
            # 주가 차트
            fig_stock = create_stock_chart(stock_code, chart_days)
            st.plotly_chart(fig_stock, use_container_width=True)
            
            # 거래량 차트
            fig_volume = create_volume_chart(stock_code, chart_days)
            st.plotly_chart(fig_volume, use_container_width=True)
        except Exception as e:
            st.error(f"차트 생성 중 오류: {e}")
            st.info("차트를 불러올 수 없습니다.")

with tab3:
    st.header("💼 포트폴리오")
    
    # 안전한 포트폴리오 요약
    try:
        portfolio_df = create_portfolio_summary()
    except Exception as e:
        st.error(f"포트폴리오 생성 중 오류: {e}")
        st.info("포트폴리오 정보를 불러올 수 없습니다.")
        portfolio_df = None
    
    # 포트폴리오 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_value = 7200000 + 6250000  # 삼성전자 + SK하이닉스
        st.metric(
            label="총 평가금액",
            value=f"{total_value:,}원"
        )
    
    with col2:
        total_profit = 200000 + 250000
        st.metric(
            label="총 평가손익",
            value=f"{total_profit:,}원",
            delta=f"+{total_profit:,}원"
        )
    
    with col3:
        profit_rate = (total_profit / (total_value - total_profit)) * 100
        st.metric(
            label="총 수익률",
            value=f"{profit_rate:.2f}%",
            delta=f"+{profit_rate:.2f}%"
        )
    
    with col4:
        st.metric(
            label="보유 종목 수",
            value="2종목"
        )
    
    # 포트폴리오 상세
    st.subheader("📋 보유 종목")
    if portfolio_df is not None:
        st.dataframe(portfolio_df, use_container_width=True)
    else:
        st.info("포트폴리오 데이터를 불러올 수 없습니다.")
    
    # 포트폴리오 차트
    st.subheader("📊 포트폴리오 분포")
    
    # 파이 차트 데이터
    portfolio_data = {
        '종목': ['삼성전자', 'SK하이닉스'],
        '비중': [53.5, 46.5]
    }
    
    fig_pie = px.pie(
        portfolio_data, 
        values='비중', 
        names='종목',
        title="포트폴리오 비중"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 수익률 차트
        profit_data = {
            '종목': ['삼성전자', 'SK하이닉스'],
            '수익률': [2.86, 4.17]
        }
        
        fig_bar = px.bar(
            profit_data,
            x='종목',
            y='수익률',
            title="종목별 수익률",
            color='수익률',
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)

with tab4:
    # 뉴스 분석 탭
    create_news_analysis_tab()

with tab5:
    # AI 채팅 탭
    create_ai_chat_tab()

with tab6:
    st.header("📋 분석 기록")
    
    # 안전한 분석 기록 표시
    try:
        history_df = create_analysis_history()
        st.dataframe(history_df, use_container_width=True)
    except Exception as e:
        st.error(f"분석 기록 생성 중 오류: {e}")
        st.info("분석 기록을 불러올 수 없습니다.")
    
    # 분석 통계
    st.subheader("📊 분석 통계")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 분석 횟수", "156회")
    
    with col2:
        st.metric("정확도", "78.5%")
    
    with col3:
        st.metric("평균 신뢰도", "81.2%")

with tab7:
    st.header("⚙️ 시스템 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔑 API 설정")
        openai_key = st.text_input("OpenAI API Key", type="password")
        kis_key = st.text_input("KIS API Key", type="password")
        
        if st.button("설정 저장", key="save_api"):
            st.success("API 설정이 저장되었습니다!")
    
    with col2:
        st.subheader("🔔 알림 설정")
        email_notify = st.checkbox("이메일 알림")
        price_alert = st.number_input("가격 알림 기준", value=70000)
        profit_alert = st.number_input("수익률 알림 기준 (%)", value=5.0)
        
        if st.button("알림 설정 저장", key="save_notify"):
            st.success("알림 설정이 저장되었습니다!")
    
    # 시스템 정보
    st.subheader("💻 시스템 정보")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Python 버전", "3.9.0")
    
    with col2:
        st.metric("Streamlit 버전", "1.48.1")
    
    with col3:
        st.metric("마지막 업데이트", "2024-08-24")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        📈 Morning - AI 기반 주식 분석 시스템<br>
        Made with ❤️ by Jacob Kim | 
        <a href='https://github.com/jacob119/morning' target='_blank'>GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)

# 실시간 모니터링 설정
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 실시간 모니터링")

# 자동 새로고침 설정
auto_refresh = st.sidebar.checkbox("자동 새로고침", value=False, key="auto_refresh")
if auto_refresh:
    refresh_interval = st.sidebar.selectbox(
        "새로고침 간격",
        ["30초", "1분", "5분", "10분"],
        key="refresh_interval"
    )
    
    # 간격을 초 단위로 변환
    interval_map = {"30초": 30, "1분": 60, "5분": 300, "10분": 600}
    refresh_seconds = interval_map[refresh_interval]
    
    # 자동 새로고침 실행
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    current_time = time.time()
    if current_time - st.session_state.last_refresh >= refresh_seconds:
        st.session_state.last_refresh = current_time
        st.session_state.refresh_news = True
        st.session_state.run_analysis = True
        st.rerun()

# 실시간 상태 표시
if auto_refresh:
    st.sidebar.success(f"🔄 {refresh_interval}마다 자동 새로고침")
    st.sidebar.caption(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")

def main():
    """대시보드 메인 함수"""
    # Streamlit 앱이 이미 실행 중이므로 추가 로직이 필요하면 여기에 작성
    pass

if __name__ == "__main__":
    main()
