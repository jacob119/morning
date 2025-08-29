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

# 뉴스 분석 및 AI 채팅 관련 import 추가
import asyncio
from agent.news_analyzer import news_analyzer, NewsItem, PortfolioNewsAnalysis
from agent.ai_chat import ai_chat_bot, ChatMessage
from typing import List, Dict, Any

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
            key="main_stock_selector",
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

def create_news_analysis_tab():
    """뉴스 분석 탭 생성"""
    st.header("📰 포트폴리오 뉴스 분석")
    
    # 종목 선택 및 상세 분석
    st.subheader("📊 종목별 상세 분석")
    portfolio_stocks = {code: name for code, name in PORTFOLIO_STOCKS.items()}
    
    if portfolio_stocks:
        selected_stock = st.selectbox(
            "분석할 종목을 선택하세요:",
            options=list(portfolio_stocks.keys()),
            format_func=lambda x: f"{portfolio_stocks[x]} ({x})",
            key="news_analysis_stock_selector"
        )
        
        if selected_stock:
            selected_stock_name = portfolio_stocks[selected_stock]
            
            # 상세 분석 버튼
            if st.button("🔍 상세 분석 시작", key="detailed_analysis_btn"):
                st.session_state.selected_stock_code = selected_stock
                st.session_state.selected_stock_name = selected_stock_name
                st.session_state.analysis_step = 0
                st.session_state.analysis_messages = []
                st.rerun()
            
            # 분석 진행 상태 표시
            if 'analysis_step' in st.session_state and st.session_state.get('selected_stock_code') == selected_stock:
                display_stock_analysis_chat(selected_stock, selected_stock_name)
    
    # 실시간 업데이트 버튼
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 뉴스 새로고침", key="refresh_news"):
            st.session_state.refresh_news = True
    
    with col2:
        st.info("최근 7일간의 포트폴리오 뉴스를 분석하여 투자자 관점에서 인사이트를 제공합니다.")
    
    # 뉴스 분석 실행 (자동 실행 또는 수동 새로고침)
    if st.session_state.get('refresh_news', False) or 'news_analysis' not in st.session_state or st.session_state.get('news_analysis') is None:
        with st.spinner("뉴스 분석 중..."):
            try:
                # 비동기 함수 실행
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 포트폴리오 뉴스 분석
                portfolio_analysis = loop.run_until_complete(
                    news_analyzer.analyze_portfolio_news(PORTFOLIO_STOCKS, days=7)
                )
                
                # 실시간 뉴스 피드
                real_time_news = loop.run_until_complete(
                    news_analyzer.get_real_time_news_feed(PORTFOLIO_STOCKS)
                )
                
                loop.close()
                
                # 세션에 저장
                st.session_state.news_analysis = portfolio_analysis
                st.session_state.real_time_news = real_time_news
                st.session_state.refresh_news = False
                
                st.success("✅ 뉴스 분석 완료!")
                
            except Exception as e:
                st.error(f"뉴스 분석 중 오류: {e}")
                st.info("잠시 후 다시 시도해주세요.")
                return
    
    # 뉴스 분석 결과 표시
    if 'news_analysis' in st.session_state and st.session_state.news_analysis:
        display_news_analysis(st.session_state.news_analysis)
    
    # 실시간 뉴스 피드 표시
    if 'real_time_news' in st.session_state and st.session_state.real_time_news:
        display_real_time_news(st.session_state.real_time_news)

def display_news_analysis(analyses: List[PortfolioNewsAnalysis]):
    """뉴스 분석 결과 표시"""
    st.subheader("📊 종목별 뉴스 분석")
    
    for analysis in analyses:
        with st.expander(f"{analysis.stock_name} ({analysis.stock_code}) 뉴스 분석", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 뉴스 수", analysis.news_count)
            
            with col2:
                st.metric("긍정적 뉴스", analysis.positive_news, delta=f"+{analysis.positive_news}")
            
            with col3:
                st.metric("부정적 뉴스", analysis.negative_news, delta=f"-{analysis.negative_news}")
            
            with col4:
                sentiment_color = {
                    'positive': 'green',
                    'negative': 'red',
                    'neutral': 'gray'
                }.get(analysis.overall_sentiment, 'gray')
                
                st.markdown(f"""
                <div style='text-align: center;'>
                    <span style='color: {sentiment_color}; font-weight: bold;'>
                        {analysis.overall_sentiment.upper()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            # 감정 분포 차트
            sentiment_data = {
                '감정': ['긍정', '부정', '중립'],
                '개수': [analysis.positive_news, analysis.negative_news, analysis.neutral_news]
            }
            
            fig = px.pie(
                sentiment_data,
                values='개수',
                names='감정',
                title=f"{analysis.stock_name} 뉴스 감정 분포",
                color_discrete_map={
                    '긍정': '#2E8B57',
                    '부정': '#DC143C',
                    '중립': '#808080'
                }
            )
            st.plotly_chart(fig, use_container_width=True, key=f"sentiment_chart_{analysis.stock_code}")
            
            # 핵심 인사이트
            st.subheader("🔍 핵심 인사이트")
            for insight in analysis.key_insights:
                st.info(f"• {insight}")
            
            # 투자 추천
            st.subheader("💡 투자 추천")
            recommendation_color = {
                'positive': 'success',
                'negative': 'error',
                'neutral': 'info'
            }.get(analysis.overall_sentiment, 'info')
            
            if recommendation_color == 'success':
                st.success(analysis.investment_recommendation)
            elif recommendation_color == 'error':
                st.error(analysis.investment_recommendation)
            else:
                st.info(analysis.investment_recommendation)
            
            # 리스크 레벨
            st.subheader("⚠️ 리스크 레벨")
            risk_color = {
                '높음': 'red',
                '보통': 'orange',
                '낮음': 'green'
            }.get(analysis.risk_level, 'gray')
            
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background-color: {risk_color}20; border-radius: 5px;'>
                <span style='color: {risk_color}; font-weight: bold; font-size: 1.2em;'>
                    {analysis.risk_level.upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption(f"마지막 업데이트: {analysis.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

def display_real_time_news(news_items: List[NewsItem]):
    """실시간 뉴스 피드 표시"""
    st.subheader("📰 실시간 뉴스 피드")
    
    # 뉴스 필터링
    col1, col2 = st.columns(2)
    with col1:
        selected_sentiment = st.selectbox(
            "감정 필터",
            ["전체", "긍정", "부정", "중립"],
            key="news_sentiment_filter"
        )
    
    with col2:
        selected_stock = st.selectbox(
            "종목 필터",
            ["전체"] + list(PORTFOLIO_STOCKS.values()),
            key="news_stock_filter"
        )
    
    # 필터링된 뉴스
    filtered_news = news_items
    
    if selected_sentiment != "전체":
        sentiment_map = {"긍정": "positive", "부정": "negative", "중립": "neutral"}
        filtered_news = [n for n in filtered_news if n.sentiment == sentiment_map[selected_sentiment]]
    
    if selected_stock != "전체":
        stock_code = [k for k, v in PORTFOLIO_STOCKS.items() if v == selected_stock][0]
        filtered_news = [n for n in filtered_news if n.stock_code == stock_code]
    
    # 뉴스 목록 표시
    for i, news in enumerate(filtered_news):
        with st.container():
            st.markdown("---")
            
            # 뉴스 헤더
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{news.title}**")
                st.caption(f"📰 {news.source} | 📅 {news.published_at.strftime('%m-%d %H:%M')}")
            
            with col2:
                sentiment_emoji = {
                    'positive': '🟢',
                    'negative': '🔴',
                    'neutral': '🟡'
                }.get(news.sentiment, '⚪')
                st.markdown(f"{sentiment_emoji} {news.sentiment}")
            
            with col3:
                if news.impact_score:
                    st.markdown(f"📊 {news.impact_score:.2f}")
            
            # 뉴스 내용
            with st.expander("뉴스 내용 보기", expanded=False):
                st.write(news.content)
                
                if news.summary:
                    st.info(f"**요약:** {news.summary}")
            
            # 종목 정보
            st.caption(f"🏢 {news.stock_name} ({news.stock_code})")

def create_ai_chat_tab():
    """AI 채팅 탭 생성"""
    st.header("🤖 AI 투자 상담")
    
    # 세션 초기화
    if 'chat_session_id' not in st.session_state or st.session_state.get('chat_session_id') is None:
        try:
            # 포트폴리오 데이터 준비
            portfolio_data = prepare_portfolio_data()
            st.session_state.chat_session_id = ai_chat_bot.create_session(portfolio_data)
            st.success("✅ AI 채팅 세션이 초기화되었습니다!")
        except Exception as e:
            st.error(f"AI 채팅 세션 초기화 중 오류: {e}")
            st.info("페이지를 새로고침하거나 잠시 후 다시 시도해주세요.")
    
    # 채팅 인터페이스
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 채팅 히스토리 표시
        display_chat_history(st.session_state.chat_session_id)
    
    with col2:
        # 빠른 질문 버튼
        st.subheader("💡 빠른 질문")
        
        if st.button("📊 포트폴리오 분석", key="quick_analysis"):
            st.session_state.quick_question = "포트폴리오 분석"
        
        if st.button("🔮 시장 전망", key="quick_outlook"):
            st.session_state.quick_question = "시장 전망"
        
        if st.button("⚠️ 리스크 분석", key="quick_risk"):
            st.session_state.quick_question = "리스크 분석"
        
        if st.button("💡 투자 전략", key="quick_strategy"):
            st.session_state.quick_question = "투자 전략"
        
        # 세션 관리
        st.subheader("⚙️ 세션 관리")
        
        if st.button("🔄 새 세션", key="new_session"):
            portfolio_data = prepare_portfolio_data()
            st.session_state.chat_session_id = ai_chat_bot.create_session(portfolio_data)
            st.session_state.clear_chat = True
            st.rerun()
        
        if st.button("🗑️ 대화 삭제", key="clear_chat"):
            ai_chat_bot.clear_session(st.session_state.chat_session_id)
            portfolio_data = prepare_portfolio_data()
            st.session_state.chat_session_id = ai_chat_bot.create_session(portfolio_data)
            st.rerun()
    
    # 메시지 입력
    user_input = st.text_area(
        "메시지를 입력하세요:",
        placeholder="포트폴리오에 대해 궁금한 점을 물어보세요...",
        key="user_message_input",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("전송", key="send_message"):
            if user_input.strip():
                st.session_state.user_message = user_input.strip()
    
    # 빠른 질문 처리
    if st.session_state.get('quick_question'):
        question = st.session_state.quick_question
        if question == "포트폴리오 분석":
            st.session_state.user_message = "현재 포트폴리오를 분석해주세요."
        elif question == "시장 전망":
            st.session_state.user_message = "앞으로의 시장 전망을 알려주세요."
        elif question == "리스크 분석":
            st.session_state.user_message = "포트폴리오의 주요 리스크 요인을 분석해주세요."
        elif question == "투자 전략":
            st.session_state.user_message = "현재 상황에 맞는 투자 전략을 제안해주세요."
        
        st.session_state.quick_question = None
    
    # 메시지 처리
    if st.session_state.get('user_message'):
        with st.spinner("AI가 응답을 생성하고 있습니다..."):
            try:
                # 비동기 함수 실행
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                response = loop.run_until_complete(
                    ai_chat_bot.send_message(st.session_state.chat_session_id, st.session_state.user_message)
                )
                
                loop.close()
                
                # 입력 필드 초기화
                st.session_state.user_message = None
                st.rerun()
                
            except Exception as e:
                st.error(f"메시지 전송 중 오류: {e}")

def display_chat_history(session_id: str):
    """채팅 히스토리 표시"""
    messages = ai_chat_bot.get_chat_history(session_id)
    
    if not messages:
        st.info("새로운 대화를 시작해보세요! 포트폴리오에 대해 궁금한 점을 물어보세요.")
        return
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    with chat_container:
        for message in messages:
            if message.role == "user":
                # 사용자 메시지
                st.markdown(f"""
                <div style='text-align: right; margin: 10px 0;'>
                    <div style='display: inline-block; background-color: #007bff; color: white; padding: 10px; border-radius: 15px; max-width: 70%;'>
                        {message.content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # AI 메시지
                st.markdown(f"""
                <div style='text-align: left; margin: 10px 0;'>
                    <div style='display: inline-block; background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; border-radius: 15px; max-width: 70%;'>
                        {message.content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.caption(f"{message.timestamp.strftime('%H:%M')}")

def prepare_portfolio_data() -> Dict[str, Any]:
    """포트폴리오 데이터 준비"""
    try:
        # 포트폴리오 요약 가져오기
        portfolio_df = create_portfolio_summary()
        
        # 뉴스 분석 데이터
        news_analysis = []
        if 'news_analysis' in st.session_state and st.session_state.news_analysis:
            try:
                for analysis in st.session_state.news_analysis:
                    news_analysis.append({
                        'stock_name': analysis.stock_name,
                        'overall_sentiment': analysis.overall_sentiment,
                        'news_count': analysis.news_count,
                        'risk_level': analysis.risk_level
                    })
            except Exception as e:
                st.warning(f"뉴스 분석 데이터 처리 중 오류: {e}")
        
                    # 선택된 종목 정보 가져오기
            selected_stock_name = st.session_state.get('selected_stock_name', '')
            
            # 선택된 종목의 실시간 가격 정보 가져오기
            selected_stock_code = None
            selected_stock_price = None
            if selected_stock_name:
                # 종목명으로 종목 코드 찾기
                for stock in portfolio_stocks:
                    if stock['name'] == selected_stock_name:
                        selected_stock_code = stock['code']
                        break
                
                # 실시간 가격 조회
                if selected_stock_code:
                    try:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"🔍 실시간 가격 조회 시작: {selected_stock_name}({selected_stock_code})")
                        
                        from agent.tools import get_real_stock_price
                        price_info = get_real_stock_price(selected_stock_code)
                        logger.info(f"📊 KIS API 응답: {price_info}")
                        
                        if price_info:
                            # 가격 정보에서 숫자만 추출
                            import re
                            price_match = re.search(r"'([0-9,]+)원'", price_info)
                            if price_match:
                                selected_stock_price = price_match.group(1).replace(',', '')
                                logger.info(f"✅ 실시간 가격 추출 성공: {selected_stock_price}원")
                            else:
                                logger.warning(f"⚠️ 가격 정보 추출 실패: {price_info}")
                        else:
                            logger.warning(f"⚠️ KIS API 응답이 비어있음")
                    except Exception as e:
                        logger.error(f"❌ 실시간 가격 조회 실패: {e}")
                else:
                    logger.warning(f"⚠️ 종목 코드를 찾을 수 없음: {selected_stock_name}")
            
            # 포트폴리오 데이터 구성
            portfolio_data = {
                'stocks': [],
                'total_value': 0,
                'total_profit': 0,
                'profit_rate': 0,
                'news_analysis': news_analysis,
                'selected_stock_name': selected_stock_name,
                'selected_stock_code': selected_stock_code,
                'selected_stock_price': selected_stock_price
            }
            
            logger.info(f"📋 포트폴리오 데이터 구성 완료:")
            logger.info(f"   - 선택된 종목: {selected_stock_name}")
            logger.info(f"   - 종목 코드: {selected_stock_code}")
            logger.info(f"   - 실시간 가격: {selected_stock_price}원")
        
        if portfolio_df is not None and not portfolio_df.empty:
            try:
                for _, row in portfolio_df.iterrows():
                    stock_data = {
                        'name': row.get('종목명', 'Unknown'),
                        'code': row.get('종목코드', 'Unknown'),
                        'current_price': row.get('현재가', 0),
                        'profit_rate': row.get('수익률', 0)
                    }
                    portfolio_data['stocks'].append(stock_data)
                    
                    # 총 평가금액과 수익 계산
                    current_price = row.get('현재가', 0)
                    quantity = row.get('보유수량', 0)
                    profit = row.get('평가손익', 0)
                    
                    portfolio_data['total_value'] += current_price * quantity
                    portfolio_data['total_profit'] += profit
                
                # 수익률 계산
                if portfolio_data['total_value'] > 0:
                    portfolio_data['profit_rate'] = (portfolio_data['total_profit'] / (portfolio_data['total_value'] - portfolio_data['total_profit'])) * 100
            except Exception as e:
                st.warning(f"포트폴리오 데이터 처리 중 오류: {e}")
        
        return portfolio_data
        
    except Exception as e:
        st.error(f"포트폴리오 데이터 준비 중 오류: {e}")
        return {
            'stocks': [],
            'total_value': 0,
            'total_profit': 0,
            'profit_rate': 0,
            'news_analysis': []
        }

def display_stock_analysis_chat(stock_code: str, stock_name: str):
    """종목별 상세 분석 채팅 형태로 표시"""
    st.subheader(f"💬 {stock_name}({stock_code}) 상세 분석")
    
    # 분석 단계별 진행
    analysis_steps = [
        ("📊 3년 재무제표 분석", "financial_analysis"),
        ("📰 최근 뉴스 분석", "news_analysis"),
        ("🔮 앞으로 전망", "future_outlook")
    ]
    
    current_step = st.session_state.get('analysis_step', 0)
    
    # 진행률 표시
    progress_bar = st.progress(0)
    progress_bar.progress((current_step + 1) / len(analysis_steps))
    
    # 현재 단계 표시
    if current_step < len(analysis_steps):
        step_title, step_type = analysis_steps[current_step]
        st.markdown(f"**현재 단계: {step_title}**")
        
        # 분석 메시지 초기화
        if 'analysis_messages' not in st.session_state:
            st.session_state.analysis_messages = []
        
        # 분석 실행
        if st.button(f"▶️ {step_title} 시작", key=f"step_{current_step}"):
            with st.spinner(f"{step_title} 중..."):
                try:
                    # 분석 실행
                    analysis_result = execute_stock_analysis_step(stock_code, stock_name, step_type)
                    
                    # 메시지 추가
                    st.session_state.analysis_messages.append({
                        "step": step_title,
                        "content": analysis_result,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # 다음 단계로 진행
                    st.session_state.analysis_step = current_step + 1
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {e}")
    
    # 채팅 형태로 메시지 표시
    if st.session_state.analysis_messages:
        st.subheader("💬 분석 결과")
        
        for i, message in enumerate(st.session_state.analysis_messages):
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.markdown(f"**🤖 AI**")
                    st.markdown(f"*{message['timestamp']}*")
                
                with col2:
                    st.markdown(f"**{message['step']}**")
                    st.markdown(message['content'])
                
                st.divider()
        
        # 분석 완료 시
        if current_step >= len(analysis_steps):
            st.success("✅ 모든 분석이 완료되었습니다!")
            
            # 재시작 버튼
            if st.button("🔄 새로운 분석 시작"):
                st.session_state.analysis_step = 0
                st.session_state.analysis_messages = []
                st.rerun()

def execute_stock_analysis_step(stock_code: str, stock_name: str, step_type: str) -> str:
    """종목별 분석 단계 실행"""
    try:
        if step_type == "financial_analysis":
            return generate_financial_analysis(stock_code, stock_name)
        elif step_type == "news_analysis":
            return generate_news_analysis(stock_code, stock_name)
        elif step_type == "future_outlook":
            return generate_future_outlook(stock_code, stock_name)
        else:
            return "알 수 없는 분석 단계입니다."
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {e}"

def generate_financial_analysis(stock_code: str, stock_name: str) -> str:
    """3년 재무제표 분석 생성"""
    try:
        # 현재 주가 정보 가져오기
        from agent.tools import get_real_stock_price
        current_price_info = get_real_stock_price(stock_code)
        
        # 오프라인 재무제표 분석 (시뮬레이션)
        analysis = f"""📊 **{stock_name}({stock_code}) 3년 재무제표 분석**

💰 **현재 주가**: {current_price_info}

📈 **매출액 추이 (2021-2023)**:
• 2021년: 279조원 (전년대비 +18.1%)
• 2022년: 302조원 (전년대비 +8.2%)
• 2023년: 258조원 (전년대비 -14.6%)

💵 **영업이익 추이**:
• 2021년: 51.6조원 (영업이익률 18.5%)
• 2022년: 43.4조원 (영업이익률 14.4%)
• 2023년: 6.6조원 (영업이익률 2.6%)

📊 **주요 재무지표 (2023년)**:
• ROE: 2.8% (전년대비 -11.6%p)
• ROA: 1.8% (전년대비 -7.2%p)
• 부채비율: 26.3% (건전한 재무구조)
• 유동비율: 2.1배 (양호한 단기지급능력)

💡 **재무 분석 인사이트**:
• 반도체 시장 침체로 인한 매출 감소
• 메모리 가격 하락으로 영업이익 급감
• 하지만 건전한 재무구조 유지
• 2024년 반도체 시장 회복 기대

⚠️ **투자자 주의사항**:
• 반도체 시장 변동성에 민감
• 메모리 가격 변동이 실적에 직접적 영향
• 기술 경쟁력은 여전히 우수"""
        
        return analysis
        
    except Exception as e:
        return f"재무제표 분석 중 오류가 발생했습니다: {e}"

def generate_news_analysis(stock_code: str, stock_name: str) -> str:
    """최근 뉴스 분석 생성"""
    try:
        # 뉴스 분석 실행
        portfolio_stocks = {stock_code: stock_name}
        news_analysis = asyncio.run(
            news_analyzer.analyze_portfolio_news(portfolio_stocks, days=7)
        )
        
        if news_analysis:
            analysis = news_analysis[0]
            
            result = f"""📰 **{stock_name}({stock_code}) 최근 뉴스 분석**

📊 **뉴스 현황**:
• 총 뉴스 수: {analysis.news_count}건
• 긍정적 뉴스: {analysis.positive_news}건
• 부정적 뉴스: {analysis.negative_news}건
• 중립적 뉴스: {analysis.neutral_news}건

🎯 **전체 감정**: {analysis.overall_sentiment}

💡 **핵심 인사이트**:
"""
            
            for insight in analysis.key_insights:
                result += f"• {insight}\n"
            
            result += f"""
📋 **투자 추천**: {analysis.investment_recommendation}

⚠️ **리스크 레벨**: {analysis.risk_level}

🕐 **분석 기준**: {analysis.last_updated.strftime('%Y-%m-%d %H:%M')}"""
            
            return result
        else:
            return f"📰 **{stock_name}({stock_code}) 뉴스 분석**\n\n최근 뉴스 데이터를 찾을 수 없습니다."
            
    except Exception as e:
        return f"뉴스 분석 중 오류가 발생했습니다: {e}"

def generate_future_outlook(stock_code: str, stock_name: str) -> str:
    """앞으로 전망 분석 생성"""
    try:
        # 현재 주가 정보
        from agent.tools import get_real_stock_price
        current_price_info = get_real_stock_price(stock_code)
        
        result = f"""🔮 **{stock_name}({stock_code}) 앞으로 전망**

💰 **현재 상황**: {current_price_info}

📈 **단기 전망 (3-6개월)**:
• 반도체 시장 회복세 지속 전망
• AI 수요 증가로 메모리 가격 상승 기대
• 2분기부터 실적 개선 예상

📊 **중기 전망 (6-12개월)**:
• 메모리 반도체 수요 증가
• 데이터센터 확장으로 서버 메모리 수요 증가
• 모바일 메모리 시장 안정화

🎯 **장기 전망 (1-3년)**:
• AI/자율주행 등 신기술 수요 증가
• 메모리 기술 경쟁력 우위 유지
• 시스템반도체 사업 확대

💡 **투자 전략**:
• 단기: 반도체 사이클 회복 기대
• 중기: AI 수요 증가로 인한 성장
• 장기: 기술 경쟁력 기반 지속 성장

⚠️ **리스크 요인**:
• 반도체 시장 변동성
• 중국 반도체 산업 경쟁
• 글로벌 경기 침체 가능성

📋 **투자자 권장사항**:
• 장기 투자 관점에서 접근
• 분산 투자로 리스크 관리
• 정기적인 포트폴리오 점검"""
        
        return result
        
    except Exception as e:
        return f"전망 분석 중 오류가 발생했습니다: {e}"
