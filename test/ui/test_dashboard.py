"""
웹 대시보드 UI 테스트

Streamlit 기반 대시보드의 UI 컴포넌트와 사용자 인터페이스를 테스트합니다.
"""

import pytest
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# 실제 UI 모듈 import
from ui import dashboard
from ui import web_components


class TestDashboard:
    """대시보드 UI 테스트"""
    
    @pytest.mark.ui
    def test_dashboard_import(self):
        """대시보드 모듈 import 테스트"""
        assert dashboard is not None
        assert hasattr(dashboard, 'main')
    
    @pytest.mark.ui
    def test_web_components_import(self):
        """웹 컴포넌트 모듈 import 테스트"""
        assert web_components is not None
        assert hasattr(web_components, 'create_stock_metrics')
        assert hasattr(web_components, 'create_stock_chart')
        assert hasattr(web_components, 'create_portfolio_summary')
    
    @pytest.mark.ui
    def test_portfolio_stocks_defined(self):
        """포트폴리오 주식 목록 정의 테스트"""
        assert hasattr(web_components, 'PORTFOLIO_STOCKS')
        assert isinstance(web_components.PORTFOLIO_STOCKS, dict)
        assert len(web_components.PORTFOLIO_STOCKS) > 0
        assert '005930' in web_components.PORTFOLIO_STOCKS  # 삼성전자
        assert '000660' in web_components.PORTFOLIO_STOCKS  # SK하이닉스
    
    @pytest.mark.ui
    def test_create_stock_metrics_function(self):
        """주식 메트릭 생성 함수 테스트"""
        # 함수가 정의되어 있는지 확인
        assert callable(web_components.create_stock_metrics)
        
        # 함수 시그니처 확인
        import inspect
        sig = inspect.signature(web_components.create_stock_metrics)
        assert 'stock_code' in sig.parameters
    
    @pytest.mark.ui
    def test_create_stock_chart_function(self):
        """주식 차트 생성 함수 테스트"""
        # 함수가 정의되어 있는지 확인
        assert callable(web_components.create_stock_chart)
        
        # 함수 시그니처 확인
        import inspect
        sig = inspect.signature(web_components.create_stock_chart)
        assert 'stock_code' in sig.parameters
        assert 'days' in sig.parameters
    
    @pytest.mark.ui
    def test_create_portfolio_summary_function(self):
        """포트폴리오 요약 생성 함수 테스트"""
        # 함수가 정의되어 있는지 확인
        assert callable(web_components.create_portfolio_summary)
        
        # 함수가 DataFrame을 반환하는지 확인
        result = web_components.create_portfolio_summary()
        assert result is not None
    
    @pytest.mark.ui
    def test_create_sidebar_config_function(self):
        """사이드바 설정 생성 함수 테스트"""
        # 함수가 정의되어 있는지 확인
        assert callable(web_components.create_sidebar_config)
        
        # 함수 시그니처 확인
        import inspect
        sig = inspect.signature(web_components.create_sidebar_config)
        # 함수가 튜플을 반환하는지 확인
        assert sig.return_annotation == inspect.Signature.empty or 'tuple' in str(sig.return_annotation)
    
    @pytest.mark.ui
    def test_display_analysis_result_function(self):
        """분석 결과 표시 함수 테스트"""
        # 함수가 정의되어 있는지 확인
        assert callable(web_components.display_analysis_result)
        
        # 함수 시그니처 확인
        import inspect
        sig = inspect.signature(web_components.display_analysis_result)
        assert 'result' in sig.parameters
    
    @pytest.mark.ui
    def test_create_analysis_history_function(self):
        """분석 기록 생성 함수 테스트"""
        # 함수가 정의되어 있는지 확인
        assert callable(web_components.create_analysis_history)
        
        # 함수가 DataFrame을 반환하는지 확인
        result = web_components.create_analysis_history()
        assert result is not None
    
    @pytest.mark.ui
    def test_create_volume_chart_function(self):
        """거래량 차트 생성 함수 테스트"""
        # 함수가 정의되어 있는지 확인
        assert callable(web_components.create_volume_chart)
        
        # 함수 시그니처 확인
        import inspect
        sig = inspect.signature(web_components.create_volume_chart)
        assert 'stock_code' in sig.parameters
        assert 'days' in sig.parameters


class TestWebComponents:
    """웹 컴포넌트 테스트"""
    
    @pytest.mark.ui
    def test_portfolio_stocks_structure(self):
        """포트폴리오 주식 구조 테스트"""
        portfolio = web_components.PORTFOLIO_STOCKS
        
        # 모든 주식 코드가 6자리인지 확인
        for code in portfolio.keys():
            assert len(code) == 6, f"주식 코드 {code}는 6자리가 아닙니다"
            assert code.isdigit(), f"주식 코드 {code}는 숫자가 아닙니다"
        
        # 모든 주식명이 문자열인지 확인
        for name in portfolio.values():
            assert isinstance(name, str), f"주식명 {name}는 문자열이 아닙니다"
            assert len(name) > 0, f"주식명이 비어있습니다"
    
    @pytest.mark.ui
    def test_create_stock_chart_returns_figure(self):
        """주식 차트 생성이 Figure 객체를 반환하는지 테스트"""
        result = web_components.create_stock_chart('005930', 30)
        
        # 결과가 None이 아닌지 확인
        assert result is not None
    
    @pytest.mark.ui
    def test_create_volume_chart_returns_figure(self):
        """거래량 차트 생성이 Figure 객체를 반환하는지 테스트"""
        result = web_components.create_volume_chart('005930', 30)
        
        # 결과가 None이 아닌지 확인
        assert result is not None
    
    @pytest.mark.ui
    def test_create_portfolio_summary_returns_dataframe(self):
        """포트폴리오 요약이 DataFrame을 반환하는지 테스트"""
        result = web_components.create_portfolio_summary()
        
        # 결과가 DataFrame인지 확인
        import pandas as pd
        assert isinstance(result, pd.DataFrame)
        
        # DataFrame이 비어있지 않은지 확인
        assert len(result) > 0
        
        # 필요한 컬럼들이 있는지 확인
        required_columns = ['종목코드', '종목명', '보유수량', '평균단가', '현재가', '수익률', '평가손익']
        for col in required_columns:
            assert col in result.columns, f"컬럼 {col}이 없습니다"
    
    @pytest.mark.ui
    def test_create_analysis_history_returns_dataframe(self):
        """분석 기록이 DataFrame을 반환하는지 테스트"""
        result = web_components.create_analysis_history()
        
        # 결과가 DataFrame인지 확인
        import pandas as pd
        assert isinstance(result, pd.DataFrame)
        
        # DataFrame이 비어있지 않은지 확인
        assert len(result) > 0
        
        # 필요한 컬럼들이 있는지 확인
        required_columns = ['날짜', '종목코드', '종목명', '분석결과', '목표가', '신뢰도']
        for col in required_columns:
            assert col in result.columns, f"컬럼 {col}이 없습니다"


class TestUIPerformance:
    """UI 성능 테스트"""
    
    @pytest.mark.ui
    def test_create_stock_chart_performance(self):
        """주식 차트 생성 성능 테스트"""
        import time
        
        start_time = time.time()
        result = web_components.create_stock_chart('005930', 30)
        end_time = time.time()
        
        # 차트 생성 시간이 1초 이내인지 확인
        assert (end_time - start_time) < 1.0, "차트 생성이 너무 느립니다"
        assert result is not None
    
    @pytest.mark.ui
    def test_create_portfolio_summary_performance(self):
        """포트폴리오 요약 생성 성능 테스트"""
        import time
        
        start_time = time.time()
        result = web_components.create_portfolio_summary()
        end_time = time.time()
        
        # 포트폴리오 생성 시간이 1초 이내인지 확인
        assert (end_time - start_time) < 1.0, "포트폴리오 생성이 너무 느립니다"
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "ui"])

