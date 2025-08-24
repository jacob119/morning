import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
from datetime import datetime, timedelta
from agent.analytics import run, StockAnalyzer
from agent.tools import TOOLS
import time
from web_components import (
    create_stock_metrics, create_stock_chart, create_volume_chart,
    create_analysis_history, create_portfolio_summary, display_analysis_result,
    create_sidebar_config
)

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

# 사이드바 설정
stock_code, max_iterations, chart_days = create_sidebar_config()

# 메인 헤더
st.markdown('<h1 class="main-header">📈 Morning - 주식 분석 대시보드</h1>', unsafe_allow_html=True)

# 탭 생성
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 실시간 분석", "📈 차트", "💼 포트폴리오", "📋 분석 기록", "⚙️ 설정"])

with tab1:
    st.header("📊 실시간 주식 분석")
    
    # 주식 메트릭 카드
    create_stock_metrics(stock_code)
    
    # 분석 실행
    if st.session_state.get('run_analysis', False):
        with st.spinner("주식 분석 중..."):
            # 분석 실행
            analyzer = StockAnalyzer()
            analyzer.max_iterations = max_iterations
            result = analyzer.analyze(stock_code)
            
            # 결과 표시
            st.success("✅ 분석 완료!")
            
            # 분석 결과를 세션에 저장
            st.session_state.analysis_result = result
            st.session_state.run_analysis = False
    
    # 분석 결과 표시
    if hasattr(st.session_state, 'analysis_result'):
        display_analysis_result(st.session_state.analysis_result)

with tab2:
    st.header("📈 주식 차트")
    
    # 차트 컨테이너
    chart_container = st.container()
    
    with chart_container:
        # 주가 차트
        fig_stock = create_stock_chart(stock_code, chart_days)
        st.plotly_chart(fig_stock, use_container_width=True)
        
        # 거래량 차트
        fig_volume = create_volume_chart(stock_code, chart_days)
        st.plotly_chart(fig_volume, use_container_width=True)

with tab3:
    st.header("💼 포트폴리오")
    
    # 포트폴리오 요약
    portfolio_df = create_portfolio_summary()
    
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
    st.dataframe(portfolio_df, use_container_width=True)
    
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
    st.header("📋 분석 기록")
    
    # 분석 기록 표시
    history_df = create_analysis_history()
    st.dataframe(history_df, use_container_width=True)
    
    # 분석 통계
    st.subheader("📊 분석 통계")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 분석 횟수", "156회")
    
    with col2:
        st.metric("정확도", "78.5%")
    
    with col3:
        st.metric("평균 신뢰도", "81.2%")

with tab5:
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
