"""
Agent Analytics 단위 테스트

StockAnalyzer 클래스의 기능을 테스트합니다.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agent.analytics import StockAnalyzer


class TestStockAnalyzer:
    """StockAnalyzer 테스트 클래스"""
    
    @pytest.fixture
    def analyzer(self):
        """StockAnalyzer 인스턴스 생성"""
        return StockAnalyzer()
    
    @pytest.fixture
    def mock_tools(self):
        """도구들 모킹"""
        with patch('agent.analytics.TOOLS') as mock_tools:
            mock_tools.get = Mock()
            yield mock_tools
    
    def test_initialization(self, analyzer):
        """초기화 테스트"""
        assert analyzer is not None
        assert hasattr(analyzer, 'tools')
        assert hasattr(analyzer, 'llm')
    
    @pytest.mark.unit
    def test_fetch_price(self, analyzer, mock_tools, sample_stock_data):
        """가격 조회 테스트"""
        # 모킹 설정
        mock_tools.get.return_value = Mock(return_value=sample_stock_data["005930"])
        
        # 테스트 실행
        result = analyzer.fetch_price("005930")
        
        # 검증
        assert result is not None
        assert "current_price" in result
        assert result["current_price"] == 70000
    
    @pytest.mark.unit
    def test_fetch_news(self, analyzer, mock_tools):
        """뉴스 조회 테스트"""
        # 모킹 설정
        mock_news = "삼성전자, 메모리 반도체 수요 증가로 실적 개선 전망"
        mock_tools.get.return_value = Mock(return_value=mock_news)
        
        # 테스트 실행
        result = analyzer.fetch_news("005930")
        
        # 검증
        assert result is not None
        assert "삼성전자" in result
    
    @pytest.mark.unit
    def test_fetch_report(self, analyzer, mock_tools, mock_openai_response):
        """리포트 조회 테스트"""
        # 모킹 설정
        mock_report = "Buy, 목표가 75000원 (메모리 반도체 수요 증가 기대)"
        mock_tools.get.return_value = Mock(return_value=mock_report)
        
        # 테스트 실행
        result = analyzer.fetch_report("005930")
        
        # 검증
        assert result is not None
        assert "Buy" in result
        assert "목표가" in result
    
    @pytest.mark.unit
    def test_analyze_stock(self, analyzer, mock_tools):
        """주식 분석 테스트"""
        # 모킹 설정
        mock_tools.get.return_value = Mock(return_value="가격 조회 결과")
        
        # 테스트 실행
        result = analyzer.analyze_stock("005930")
        
        # 검증
        assert result is not None
        assert isinstance(result, dict)
    
    @pytest.mark.unit
    def test_invalid_stock_code(self, analyzer):
        """잘못된 주식 코드 테스트"""
        # 테스트 실행
        result = analyzer.fetch_price("INVALID")
        
        # 검증
        assert result is None or "error" in str(result).lower()
    
    @pytest.mark.unit
    def test_api_error_handling(self, analyzer, mock_tools):
        """API 오류 처리 테스트"""
        # 모킹 설정 - 예외 발생
        mock_tools.get.return_value = Mock(side_effect=Exception("API Error"))
        
        # 테스트 실행
        result = analyzer.fetch_price("005930")
        
        # 검증
        assert result is None or "error" in str(result).lower()


class TestStockAnalyzerIntegration:
    """StockAnalyzer 통합 테스트"""
    
    @pytest.mark.integration
    def test_full_analysis_workflow(self):
        """전체 분석 워크플로우 테스트"""
        analyzer = StockAnalyzer()
        
        # 실제 API 호출 없이 모킹
        with patch('agent.analytics.TOOLS') as mock_tools:
            mock_tools.get.return_value = Mock(return_value="테스트 결과")
            
            # 전체 분석 실행
            result = analyzer.analyze_stock("005930")
            
            # 검증
            assert result is not None
            assert isinstance(result, dict)
    
    @pytest.mark.integration
    def test_multiple_stock_analysis(self):
        """여러 주식 분석 테스트"""
        analyzer = StockAnalyzer()
        stock_codes = ["005930", "000660", "035420"]
        
        with patch('agent.analytics.TOOLS') as mock_tools:
            mock_tools.get.return_value = Mock(return_value="테스트 결과")
            
            results = []
            for code in stock_codes:
                result = analyzer.analyze_stock(code)
                results.append(result)
            
            # 검증
            assert len(results) == len(stock_codes)
            assert all(result is not None for result in results)
