"""
시장 지능 시스템 단위 테스트

실시간 시장 데이터 분석 및 뉴스 감정 분석을 테스트합니다.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from strategy.market_intelligence import MarketIntelligence, NewsAnalyzer, SentimentAnalyzer


class TestMarketIntelligence:
    """시장 지능 시스템 테스트"""
    
    @pytest.fixture
    def market_intelligence(self):
        """MarketIntelligence 인스턴스 생성"""
        return MarketIntelligence()
    
    @pytest.mark.unit
    def test_real_time_data_collection(self, market_intelligence):
        """실시간 데이터 수집 테스트"""
        # 모킹 설정
        with patch('strategy.market_intelligence.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "success",
                "data": {
                    "005930": {
                        "price": 70000,
                        "volume": 5000000,
                        "change": 2.5,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
            mock_get.return_value = mock_response
            
            # 테스트 실행
            data = market_intelligence.collect_real_time_data(["005930"])
            
            # 검증
            assert data is not None
            assert "005930" in data
            assert data["005930"]["price"] == 70000
    
    @pytest.mark.unit
    def test_market_sentiment_analysis(self, market_intelligence):
        """시장 감정 분석 테스트"""
        # 테스트 데이터
        news_data = [
            "삼성전자 실적 개선 전망",
            "반도체 수요 증가로 긍정적 전망",
            "경제 불확실성 증가"
        ]
        
        # 테스트 실행
        sentiment = market_intelligence.analyze_market_sentiment(news_data)
        
        # 검증
        assert sentiment is not None
        assert "score" in sentiment
        assert "confidence" in sentiment
        assert -1 <= sentiment["score"] <= 1
    
    @pytest.mark.unit
    def test_technical_indicators(self, market_intelligence):
        """기술적 지표 계산 테스트"""
        # 샘플 가격 데이터
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        
        # 테스트 실행
        indicators = market_intelligence.calculate_technical_indicators(prices)
        
        # 검증
        assert "sma_5" in indicators
        assert "rsi" in indicators
        assert "macd" in indicators
        assert "bollinger_bands" in indicators


class TestNewsAnalyzer:
    """뉴스 분석기 테스트"""
    
    @pytest.fixture
    def news_analyzer(self):
        """NewsAnalyzer 인스턴스 생성"""
        return NewsAnalyzer()
    
    @pytest.mark.unit
    def test_news_collection(self, news_analyzer):
        """뉴스 수집 테스트"""
        with patch('strategy.market_intelligence.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = """
            <html>
                <body>
                    <h1>삼성전자 실적 개선</h1>
                    <p>메모리 반도체 수요 증가로 실적 개선 전망</p>
                </body>
            </html>
            """
            mock_get.return_value = mock_response
            
            # 테스트 실행
            news = news_analyzer.collect_news("005930")
            
            # 검증
            assert news is not None
            assert len(news) > 0
            assert "삼성전자" in str(news)
    
    @pytest.mark.unit
    def test_news_filtering(self, news_analyzer):
        """뉴스 필터링 테스트"""
        # 테스트 뉴스 데이터
        news_items = [
            {"title": "삼성전자 실적 개선", "content": "긍정적 전망", "date": "2024-01-01"},
            {"title": "일반 경제 뉴스", "content": "관련 없음", "date": "2024-01-01"},
            {"title": "SK하이닉스 관련", "content": "다른 종목", "date": "2024-01-01"}
        ]
        
        # 테스트 실행
        filtered = news_analyzer.filter_relevant_news(news_items, "005930")
        
        # 검증
        assert len(filtered) < len(news_items)
        assert all("삼성전자" in str(item) for item in filtered)


class TestSentimentAnalyzer:
    """감정 분석기 테스트"""
    
    @pytest.fixture
    def sentiment_analyzer(self):
        """SentimentAnalyzer 인스턴스 생성"""
        return SentimentAnalyzer()
    
    @pytest.mark.unit
    def test_text_sentiment_analysis(self, sentiment_analyzer):
        """텍스트 감정 분석 테스트"""
        # 테스트 텍스트
        positive_text = "삼성전자 실적 개선, 긍정적 전망"
        negative_text = "삼성전자 실적 악화, 부정적 전망"
        neutral_text = "삼성전자 실적 발표"
        
        # 테스트 실행
        pos_sentiment = sentiment_analyzer.analyze_text(positive_text)
        neg_sentiment = sentiment_analyzer.analyze_text(negative_text)
        neu_sentiment = sentiment_analyzer.analyze_text(neutral_text)
        
        # 검증
        assert pos_sentiment["score"] > 0
        assert neg_sentiment["score"] < 0
        assert abs(neu_sentiment["score"]) < 0.3
    
    @pytest.mark.unit
    def test_keyword_extraction(self, sentiment_analyzer):
        """키워드 추출 테스트"""
        text = "삼성전자 메모리 반도체 수요 증가로 실적 개선 전망"
        
        # 테스트 실행
        keywords = sentiment_analyzer.extract_keywords(text)
        
        # 검증
        assert "삼성전자" in keywords
        assert "메모리" in keywords
        assert "반도체" in keywords
        assert len(keywords) > 0


class TestMarketIntelligenceIntegration:
    """시장 지능 통합 테스트"""
    
    @pytest.mark.integration
    def test_complete_market_analysis(self):
        """완전한 시장 분석 테스트"""
        market_intelligence = MarketIntelligence()
        
        with patch('strategy.market_intelligence.requests.get') as mock_get:
            # 모킹 설정
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "success",
                "data": {"005930": {"price": 70000, "volume": 5000000}}
            }
            mock_response.text = "<html><body>긍정적 뉴스</body></html>"
            mock_get.return_value = mock_response
            
            # 테스트 실행
            analysis = market_intelligence.complete_analysis("005930")
            
            # 검증
            assert analysis is not None
            assert "price_data" in analysis
            assert "news_sentiment" in analysis
            assert "technical_indicators" in analysis
            assert "market_sentiment" in analysis
