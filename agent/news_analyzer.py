"""
포트폴리오 뉴스 분석 모듈

포트폴리오에 포함된 주식들의 뉴스를 수집하고 분석하는 기능을 제공합니다.
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
import json
import time

# OpenAI API
import openai
from config.setting import API_CONFIG

# OpenAI API 키 설정
OPENAI_API_KEY = API_CONFIG["OPENAI"]["ACCESS_KEY"]

logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """뉴스 아이템 데이터 클래스"""
    title: str
    content: str
    source: str
    published_at: datetime
    stock_code: str
    stock_name: str
    sentiment: Optional[str] = None
    impact_score: Optional[float] = None
    summary: Optional[str] = None

@dataclass
class PortfolioNewsAnalysis:
    """포트폴리오 뉴스 분석 결과"""
    stock_code: str
    stock_name: str
    news_count: int
    positive_news: int
    negative_news: int
    neutral_news: int
    overall_sentiment: str
    key_insights: List[str]
    investment_recommendation: str
    risk_level: str
    last_updated: datetime

class PortfolioNewsAnalyzer:
    """포트폴리오 뉴스 분석기"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.news_cache = {}
        self.analysis_cache = {}
        self.cache_ttl = 300  # 5분 캐시
        
    async def fetch_stock_news(self, stock_code: str, stock_name: str, days: int = 7) -> List[NewsItem]:
        """주식별 뉴스를 가져옵니다."""
        try:
            # 실제 뉴스 API 대신 시뮬레이션 데이터 사용
            news_items = await self._simulate_news_fetch(stock_code, stock_name, days)
            return news_items
        except Exception as e:
            logger.error(f"뉴스 가져오기 실패 ({stock_code}): {e}")
            return []
    
    async def _simulate_news_fetch(self, stock_code: str, stock_name: str, days: int) -> List[NewsItem]:
        """뉴스 데이터 시뮬레이션"""
        await asyncio.sleep(0.1)  # API 호출 시뮬레이션
        
        # 주식별 뉴스 템플릿
        news_templates = {
            '005930': [  # 삼성전자
                {
                    'title': f"{stock_name} 실적 개선 기대감 확산",
                    'content': f"{stock_name}의 최근 실적 발표에서 예상보다 높은 매출 성장을 기록했다. 메모리 반도체 수요 증가와 스마트폰 판매 호조가 주요 원인으로 분석된다.",
                    'sentiment': 'positive'
                },
                {
                    'title': f"{stock_name} 신기술 개발 투자 확대",
                    'content': f"{stock_name}이 AI 반도체 분야에 대규모 투자를 확정했다. 향후 3년간 50조원 규모의 투자 계획을 발표했다.",
                    'sentiment': 'positive'
                },
                {
                    'title': f"{stock_name} 글로벌 경쟁 심화",
                    'content': f"중국 반도체 업체들의 기술 발전으로 {stock_name}의 시장 점유율에 대한 우려가 제기되고 있다.",
                    'sentiment': 'negative'
                }
            ],
            '000660': [  # SK하이닉스
                {
                    'title': f"{stock_name} 메모리 가격 상승세 지속",
                    'content': f"{stock_name}의 주요 제품인 DRAM과 NAND 가격이 지속적으로 상승하고 있어 실적 개선이 예상된다.",
                    'sentiment': 'positive'
                },
                {
                    'title': f"{stock_name} HBM 기술 선도",
                    'content': f"{stock_name}이 고대역폭 메모리(HBM) 기술에서 글로벌 선도적 위치를 확보했다.",
                    'sentiment': 'positive'
                },
                {
                    'title': f"{stock_name} 원자재 가격 상승 영향",
                    'content': f"실리콘 웨이퍼 등 원자재 가격 상승으로 {stock_name}의 원가 부담이 증가할 것으로 예상된다.",
                    'sentiment': 'negative'
                }
            ]
        }
        
        # 기본 뉴스 템플릿
        default_news = [
            {
                'title': f"{stock_name} 시장 동향 분석",
                'content': f"{stock_name}의 최근 주가 동향과 시장 전망에 대한 분석이 나왔다.",
                'sentiment': 'neutral'
            }
        ]
        
        templates = news_templates.get(stock_code, default_news)
        news_items = []
        
        for i, template in enumerate(templates):
            # 날짜 생성 (최근 days일 내)
            days_ago = days - i
            if days_ago < 0:
                days_ago = 0
            published_at = datetime.now() - timedelta(days=days_ago)
            
            news_item = NewsItem(
                title=template['title'],
                content=template['content'],
                source=f"뉴스{i+1}",
                published_at=published_at,
                stock_code=stock_code,
                stock_name=stock_name,
                sentiment=template['sentiment']
            )
            news_items.append(news_item)
        
        return news_items
    
    async def analyze_news_sentiment(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """뉴스 감정 분석을 수행합니다."""
        try:
            for news_item in news_items:
                if not news_item.sentiment:
                    # OpenAI API 키 확인
                    api_key = self.openai_client.api_key
                    if (not api_key or 
                        api_key == "your openai accesskey" or 
                        "your" in api_key.lower()):
                        # 오프라인 감정 분석 (키워드 기반)
                        sentiment = self._analyze_sentiment_offline(news_item.content)
                        news_item.sentiment = sentiment
                        
                        # 영향도 점수 계산
                        news_item.impact_score = self._calculate_impact_score(news_item)
                        
                        # 요약 생성
                        news_item.summary = self._generate_summary_offline(news_item.content)
                    else:
                        # OpenAI를 사용한 감정 분석
                        sentiment = await self._analyze_sentiment_with_openai(news_item.content)
                        news_item.sentiment = sentiment
                        
                        # 영향도 점수 계산
                        news_item.impact_score = self._calculate_impact_score(news_item)
                        
                        # 요약 생성
                        news_item.summary = await self._generate_summary(news_item.content)
            
            return news_items
        except Exception as e:
            logger.error(f"뉴스 감정 분석 실패: {e}")
            return news_items
    
    async def _analyze_sentiment_with_openai(self, content: str) -> str:
        """OpenAI를 사용한 감정 분석"""
        try:
            # API 키 상태 로깅
            api_key = self.openai_client.api_key
            logger.info(f"🔑 뉴스 감정 분석 - OpenAI API 키 상태:")
            logger.info(f"   - API 키 존재: {bool(api_key)}")
            logger.info(f"   - API 키 길이: {len(api_key) if api_key else 0}")
            
            # API 호출 로깅
            logger.info(f"📰 뉴스 감정 분석 API 호출:")
            logger.info(f"   - 뉴스 내용: {content[:100]}{'...' if len(content) > 100 else ''}")
            logger.info(f"   - 모델: gpt-3.5-turbo")
            logger.info(f"   - 최대 토큰: 10")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "주식 투자 관점에서 뉴스의 감정을 분석해주세요. positive, negative, neutral 중 하나로 답변해주세요."
                    },
                    {
                        "role": "user",
                        "content": f"다음 뉴스의 감정을 분석해주세요: {content[:500]}"
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            logger.info(f"✅ 뉴스 감정 분석 완료: {sentiment}")
            
            if sentiment in ['positive', 'negative', 'neutral']:
                return sentiment
            else:
                logger.warning(f"⚠️ 예상치 못한 감정 분석 결과: {sentiment}, neutral로 처리")
                return 'neutral'
                
        except Exception as e:
            logger.error(f"❌ OpenAI 감정 분석 실패: {e}")
            return 'neutral'
    
    def _calculate_impact_score(self, news_item: NewsItem) -> float:
        """뉴스 영향도 점수 계산"""
        base_score = 0.5
        
        # 제목 길이에 따른 가중치
        title_length = len(news_item.title)
        if title_length > 50:
            base_score += 0.2
        elif title_length > 30:
            base_score += 0.1
        
        # 내용 길이에 따른 가중치
        content_length = len(news_item.content)
        if content_length > 200:
            base_score += 0.2
        elif content_length > 100:
            base_score += 0.1
        
        # 감정에 따른 가중치
        if news_item.sentiment == 'positive':
            base_score += 0.1
        elif news_item.sentiment == 'negative':
            base_score += 0.15  # 부정적 뉴스가 더 큰 영향
        
        return min(base_score, 1.0)
    
    async def _generate_summary(self, content: str) -> str:
        """뉴스 요약 생성"""
        try:
            # API 호출 로깅
            logger.info(f"📋 뉴스 요약 생성 API 호출:")
            logger.info(f"   - 뉴스 내용: {content[:100]}{'...' if len(content) > 100 else ''}")
            logger.info(f"   - 모델: gpt-3.5-turbo")
            logger.info(f"   - 최대 토큰: 100")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "투자자 관점에서 뉴스를 간단히 요약해주세요. 핵심 포인트만 2-3문장으로 작성해주세요."
                    },
                    {
                        "role": "user",
                        "content": f"다음 뉴스를 요약해주세요: {content}"
                    }
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"✅ 뉴스 요약 생성 완료: {summary[:100]}{'...' if len(summary) > 100 else ''}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 뉴스 요약 생성 실패: {e}")
            return content[:100] + "..."
    
    def _analyze_sentiment_offline(self, content: str) -> str:
        """오프라인 감정 분석 (키워드 기반)"""
        try:
            content_lower = content.lower()
            
            # 긍정 키워드
            positive_keywords = ['상승', '증가', '성장', '개선', '호조', '긍정', '강세', '돌파', '상향', '매수', '실적', '이익']
            # 부정 키워드
            negative_keywords = ['하락', '감소', '부진', '악화', '부정', '약세', '하향', '매도', '리스크', '위험', '손실', '실적부진']
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in content_lower)
            negative_count = sum(1 for keyword in negative_keywords if keyword in content_lower)
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"오프라인 감정 분석 실패: {e}")
            return "neutral"
    
    def _generate_summary_offline(self, content: str) -> str:
        """오프라인 요약 생성"""
        try:
            # 간단한 요약 로직
            if len(content) <= 100:
                return content
            
            # 첫 번째 문장과 마지막 문장을 조합
            sentences = content.split('.')
            if len(sentences) >= 2:
                summary = sentences[0] + '. ' + sentences[-1] + '.'
                return summary[:150] + "..." if len(summary) > 150 else summary
            else:
                return content[:100] + "..."
                
        except Exception as e:
            logger.error(f"오프라인 요약 생성 실패: {e}")
            return content[:100] + "..." if len(content) > 100 else content
    
    async def analyze_portfolio_news(self, portfolio_stocks: Dict[str, str], days: int = 7) -> List[PortfolioNewsAnalysis]:
        """포트폴리오 전체 뉴스 분석"""
        try:
            all_analyses = []
            
            for stock_code, stock_name in portfolio_stocks.items():
                # 뉴스 가져오기
                news_items = await self.fetch_stock_news(stock_code, stock_name, days)
                
                # 감정 분석
                analyzed_news = await self.analyze_news_sentiment(news_items)
                
                # 분석 결과 생성
                analysis = self._create_portfolio_analysis(stock_code, stock_name, analyzed_news)
                all_analyses.append(analysis)
            
            return all_analyses
            
        except Exception as e:
            logger.error(f"포트폴리오 뉴스 분석 실패: {e}")
            return []
    
    def _create_portfolio_analysis(self, stock_code: str, stock_name: str, news_items: List[NewsItem]) -> PortfolioNewsAnalysis:
        """포트폴리오 분석 결과 생성"""
        # 감정별 뉴스 수 계산
        positive_count = len([n for n in news_items if n.sentiment == 'positive'])
        negative_count = len([n for n in news_items if n.sentiment == 'negative'])
        neutral_count = len([n for n in news_items if n.sentiment == 'neutral'])
        
        # 전체 감정 결정
        if positive_count > negative_count:
            overall_sentiment = 'positive'
        elif negative_count > positive_count:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # 핵심 인사이트 생성
        key_insights = self._generate_key_insights(news_items)
        
        # 투자 추천 생성
        investment_recommendation = self._generate_investment_recommendation(
            overall_sentiment, positive_count, negative_count, news_items
        )
        
        # 리스크 레벨 결정
        risk_level = self._determine_risk_level(negative_count, len(news_items))
        
        return PortfolioNewsAnalysis(
            stock_code=stock_code,
            stock_name=stock_name,
            news_count=len(news_items),
            positive_news=positive_count,
            negative_news=negative_count,
            neutral_news=neutral_count,
            overall_sentiment=overall_sentiment,
            key_insights=key_insights,
            investment_recommendation=investment_recommendation,
            risk_level=risk_level,
            last_updated=datetime.now()
        )
    
    def _generate_key_insights(self, news_items: List[NewsItem]) -> List[str]:
        """핵심 인사이트 생성"""
        insights = []
        
        # 긍정적 뉴스에서 인사이트 추출
        positive_news = [n for n in news_items if n.sentiment == 'positive']
        if positive_news:
            insights.append(f"긍정적 뉴스 {len(positive_news)}건: 실적 개선 및 성장 전망")
        
        # 부정적 뉴스에서 인사이트 추출
        negative_news = [n for n in news_items if n.sentiment == 'negative']
        if negative_news:
            insights.append(f"부정적 뉴스 {len(negative_news)}건: 리스크 요인 주의 필요")
        
        # 높은 영향도 뉴스에서 인사이트 추출
        high_impact_news = [n for n in news_items if n.impact_score and n.impact_score > 0.7]
        if high_impact_news:
            insights.append(f"높은 영향도 뉴스 {len(high_impact_news)}건: 시장 변동성 예상")
        
        return insights[:3]  # 최대 3개 인사이트
    
    def _generate_investment_recommendation(self, sentiment: str, positive: int, negative: int, news_items: List[NewsItem]) -> str:
        """투자 추천 생성"""
        if sentiment == 'positive':
            if positive >= 3:
                return "강력 매수 추천 - 긍정적 뉴스가 지속적으로 나오고 있음"
            else:
                return "매수 고려 - 긍정적 전망이 우세함"
        elif sentiment == 'negative':
            if negative >= 3:
                return "매도 고려 - 부정적 뉴스가 지속되고 있음"
            else:
                return "관망 - 부정적 요인 주의 필요"
        else:
            return "중립 - 뚜렷한 방향성 없음"
    
    def _determine_risk_level(self, negative_count: int, total_count: int) -> str:
        """리스크 레벨 결정"""
        if total_count == 0:
            return "낮음"
        
        negative_ratio = negative_count / total_count
        
        if negative_ratio >= 0.6:
            return "높음"
        elif negative_ratio >= 0.3:
            return "보통"
        else:
            return "낮음"
    
    async def get_real_time_news_feed(self, portfolio_stocks: Dict[str, str]) -> List[NewsItem]:
        """실시간 뉴스 피드 가져오기"""
        try:
            all_news = []
            
            for stock_code, stock_name in portfolio_stocks.items():
                # 최근 1일 뉴스만 가져오기
                news_items = await self.fetch_stock_news(stock_code, stock_name, days=1)
                all_news.extend(news_items)
            
            # 시간순 정렬 (최신순)
            all_news.sort(key=lambda x: x.published_at, reverse=True)
            
            return all_news[:20]  # 최신 20개 뉴스만 반환
            
        except Exception as e:
            logger.error(f"실시간 뉴스 피드 가져오기 실패: {e}")
            return []

# 싱글톤 인스턴스
news_analyzer = PortfolioNewsAnalyzer()
