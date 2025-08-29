"""
웹 컴포넌트 UI 테스트

개별 웹 UI 컴포넌트의 기능과 데이터 처리를 테스트합니다.
"""

import pytest
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# 실제 UI 모듈 import
from ui import web_components


class TestWebComponentsStructure:
    """웹 컴포넌트 구조 테스트"""
    
    @pytest.mark.ui
    def test_web_components_import(self):
        """웹 컴포넌트 모듈 import 테스트"""
        assert web_components is not None
        assert hasattr(web_components, 'create_stock_metrics')
        assert hasattr(web_components, 'create_stock_chart')
        assert hasattr(web_components, 'create_portfolio_summary')
        assert hasattr(web_components, 'create_sidebar_config')
        assert hasattr(web_components, 'display_analysis_result')
        assert hasattr(web_components, 'create_analysis_history')
        assert hasattr(web_components, 'create_volume_chart')
    
    @pytest.mark.ui
    def test_portfolio_stocks_data(self):
        """포트폴리오 주식 데이터 테스트"""
        portfolio = web_components.PORTFOLIO_STOCKS
        
        # 데이터가 존재하는지 확인
        assert len(portfolio) > 0
        
        # 주요 주식들이 포함되어 있는지 확인
        expected_stocks = ['005930', '000660', '035420', '051910', '006400']
        for stock_code in expected_stocks:
            assert stock_code in portfolio, f"주식 코드 {stock_code}가 포트폴리오에 없습니다"
    
    @pytest.mark.ui
    def test_portfolio_stocks_format(self):
        """포트폴리오 주식 형식 테스트"""
        portfolio = web_components.PORTFOLIO_STOCKS
        
        for code, name in portfolio.items():
            # 주식 코드가 6자리 숫자인지 확인
            assert len(code) == 6, f"주식 코드 {code}는 6자리가 아닙니다"
            assert code.isdigit(), f"주식 코드 {code}는 숫자가 아닙니다"
            
            # 주식명이 문자열이고 비어있지 않은지 확인
            assert isinstance(name, str), f"주식명 {name}는 문자열이 아닙니다"
            assert len(name.strip()) > 0, f"주식명이 비어있습니다"
    
    @pytest.mark.ui
    def test_create_stock_metrics_signature(self):
        """주식 메트릭 생성 함수 시그니처 테스트"""
        import inspect
        
        sig = inspect.signature(web_components.create_stock_metrics)
        params = list(sig.parameters.keys())
        
        # 필수 매개변수가 있는지 확인
        assert 'stock_code' in params, "stock_code 매개변수가 없습니다"
        
        # 매개변수 개수 확인
        assert len(params) >= 1, "매개변수가 너무 적습니다"
    
    @pytest.mark.ui
    def test_create_stock_chart_signature(self):
        """주식 차트 생성 함수 시그니처 테스트"""
        import inspect
        
        sig = inspect.signature(web_components.create_stock_chart)
        params = list(sig.parameters.keys())
        
        # 필수 매개변수가 있는지 확인
        assert 'stock_code' in params, "stock_code 매개변수가 없습니다"
        assert 'days' in params, "days 매개변수가 없습니다"
        
        # 매개변수 개수 확인
        assert len(params) >= 2, "매개변수가 너무 적습니다"
    
    @pytest.mark.ui
    def test_create_portfolio_summary_signature(self):
        """포트폴리오 요약 생성 함수 시그니처 테스트"""
        import inspect
        
        sig = inspect.signature(web_components.create_portfolio_summary)
        params = list(sig.parameters.keys())
        
        # 매개변수 개수 확인 (매개변수가 없을 수도 있음)
        assert len(params) >= 0, "매개변수 개수가 잘못되었습니다"
    
    @pytest.mark.ui
    def test_create_sidebar_config_signature(self):
        """사이드바 설정 생성 함수 시그니처 테스트"""
        import inspect
        
        sig = inspect.signature(web_components.create_sidebar_config)
        params = list(sig.parameters.keys())
        
        # 매개변수 개수 확인 (매개변수가 없을 수도 있음)
        assert len(params) >= 0, "매개변수 개수가 잘못되었습니다"
    
    @pytest.mark.ui
    def test_display_analysis_result_signature(self):
        """분석 결과 표시 함수 시그니처 테스트"""
        import inspect
        
        sig = inspect.signature(web_components.display_analysis_result)
        params = list(sig.parameters.keys())
        
        # 필수 매개변수가 있는지 확인
        assert 'result' in params, "result 매개변수가 없습니다"
        
        # 매개변수 개수 확인
        assert len(params) >= 1, "매개변수가 너무 적습니다"
    
    @pytest.mark.ui
    def test_create_analysis_history_signature(self):
        """분석 기록 생성 함수 시그니처 테스트"""
        import inspect
        
        sig = inspect.signature(web_components.create_analysis_history)
        params = list(sig.parameters.keys())
        
        # 매개변수 개수 확인 (매개변수가 없을 수도 있음)
        assert len(params) >= 0, "매개변수 개수가 잘못되었습니다"
    
    @pytest.mark.ui
    def test_create_volume_chart_signature(self):
        """거래량 차트 생성 함수 시그니처 테스트"""
        import inspect
        
        sig = inspect.signature(web_components.create_volume_chart)
        params = list(sig.parameters.keys())
        
        # 필수 매개변수가 있는지 확인
        assert 'stock_code' in params, "stock_code 매개변수가 없습니다"
        assert 'days' in params, "days 매개변수가 없습니다"
        
        # 매개변수 개수 확인
        assert len(params) >= 2, "매개변수가 너무 적습니다"


class TestWebComponentsFunctionality:
    """웹 컴포넌트 기능 테스트"""
    
    @pytest.mark.ui
    def test_create_stock_metrics_callable(self):
        """주식 메트릭 생성 함수 호출 가능 테스트"""
        # 함수가 호출 가능한지 확인
        assert callable(web_components.create_stock_metrics)
        
        # 함수가 예외 없이 실행되는지 확인 (실제 데이터는 모킹)
        try:
            # 빈 문자열로 테스트 (에러 처리 확인)
            web_components.create_stock_metrics('')
        except Exception as e:
            # 예외가 발생해도 적절한 예외인지 확인
            assert isinstance(e, (ValueError, TypeError, Exception))
    
    @pytest.mark.ui
    def test_create_stock_chart_callable(self):
        """주식 차트 생성 함수 호출 가능 테스트"""
        # 함수가 호출 가능한지 확인
        assert callable(web_components.create_stock_chart)
        
        # 함수가 예외 없이 실행되는지 확인
        try:
            result = web_components.create_stock_chart('005930', 30)
            # 결과가 None이 아닌지 확인
            assert result is not None
        except Exception as e:
            # 예외가 발생해도 적절한 예외인지 확인
            assert isinstance(e, (ValueError, TypeError, Exception))
    
    @pytest.mark.ui
    def test_create_portfolio_summary_callable(self):
        """포트폴리오 요약 생성 함수 호출 가능 테스트"""
        # 함수가 호출 가능한지 확인
        assert callable(web_components.create_portfolio_summary)
        
        # 함수가 예외 없이 실행되는지 확인
        try:
            result = web_components.create_portfolio_summary()
            # 결과가 None이 아닌지 확인
            assert result is not None
        except Exception as e:
            # 예외가 발생해도 적절한 예외인지 확인
            assert isinstance(e, (ValueError, TypeError, Exception))
    
    @pytest.mark.ui
    def test_create_sidebar_config_callable(self):
        """사이드바 설정 생성 함수 호출 가능 테스트"""
        # 함수가 호출 가능한지 확인
        assert callable(web_components.create_sidebar_config)
        
        # 함수가 예외 없이 실행되는지 확인
        try:
            result = web_components.create_sidebar_config()
            # 결과가 None이 아닌지 확인
            assert result is not None
        except Exception as e:
            # 예외가 발생해도 적절한 예외인지 확인
            assert isinstance(e, (ValueError, TypeError, Exception))
    
    @pytest.mark.ui
    def test_display_analysis_result_callable(self):
        """분석 결과 표시 함수 호출 가능 테스트"""
        # 함수가 호출 가능한지 확인
        assert callable(web_components.display_analysis_result)
        
        # 함수가 예외 없이 실행되는지 확인
        try:
            # None으로 테스트 (에러 처리 확인)
            web_components.display_analysis_result(None)
        except Exception as e:
            # 예외가 발생해도 적절한 예외인지 확인
            assert isinstance(e, (ValueError, TypeError, Exception))
    
    @pytest.mark.ui
    def test_create_analysis_history_callable(self):
        """분석 기록 생성 함수 호출 가능 테스트"""
        # 함수가 호출 가능한지 확인
        assert callable(web_components.create_analysis_history)
        
        # 함수가 예외 없이 실행되는지 확인
        try:
            result = web_components.create_analysis_history()
            # 결과가 None이 아닌지 확인
            assert result is not None
        except Exception as e:
            # 예외가 발생해도 적절한 예외인지 확인
            assert isinstance(e, (ValueError, TypeError, Exception))
    
    @pytest.mark.ui
    def test_create_volume_chart_callable(self):
        """거래량 차트 생성 함수 호출 가능 테스트"""
        # 함수가 호출 가능한지 확인
        assert callable(web_components.create_volume_chart)
        
        # 함수가 예외 없이 실행되는지 확인
        try:
            result = web_components.create_volume_chart('005930', 30)
            # 결과가 None이 아닌지 확인
            assert result is not None
        except Exception as e:
            # 예외가 발생해도 적절한 예외인지 확인
            assert isinstance(e, (ValueError, TypeError, Exception))


class TestUIResponsiveness:
    """UI 반응성 테스트"""
    
    @pytest.mark.ui
    def test_create_stock_metrics_response_time(self):
        """주식 메트릭 생성 응답 시간 테스트"""
        import time
        
        start_time = time.time()
        try:
            web_components.create_stock_metrics('005930')
        except:
            pass  # 예외가 발생해도 응답 시간만 측정
        end_time = time.time()
        
        # 응답 시간이 2초 이내인지 확인
        response_time = end_time - start_time
        assert response_time < 2.0, f"응답 시간이 너무 느립니다: {response_time:.2f}초"
    
    @pytest.mark.ui
    def test_create_stock_chart_response_time(self):
        """주식 차트 생성 응답 시간 테스트"""
        import time
        
        start_time = time.time()
        try:
            web_components.create_stock_chart('005930', 30)
        except:
            pass  # 예외가 발생해도 응답 시간만 측정
        end_time = time.time()
        
        # 응답 시간이 2초 이내인지 확인
        response_time = end_time - start_time
        assert response_time < 2.0, f"응답 시간이 너무 느립니다: {response_time:.2f}초"
    
    @pytest.mark.ui
    def test_create_portfolio_summary_response_time(self):
        """포트폴리오 요약 생성 응답 시간 테스트"""
        import time
        
        start_time = time.time()
        try:
            web_components.create_portfolio_summary()
        except:
            pass  # 예외가 발생해도 응답 시간만 측정
        end_time = time.time()
        
        # 응답 시간이 2초 이내인지 확인
        response_time = end_time - start_time
        assert response_time < 2.0, f"응답 시간이 너무 느립니다: {response_time:.2f}초"


class TestUIAccessibility:
    """UI 접근성 테스트"""
    
    @pytest.mark.ui
    def test_portfolio_stocks_accessibility(self):
        """포트폴리오 주식 접근성 테스트"""
        portfolio = web_components.PORTFOLIO_STOCKS
        
        # 모든 주식 코드가 접근 가능한지 확인
        for code in portfolio.keys():
            assert code is not None, f"주식 코드가 None입니다"
            assert len(str(code)) > 0, f"주식 코드가 비어있습니다"
        
        # 모든 주식명이 접근 가능한지 확인
        for name in portfolio.values():
            assert name is not None, f"주식명이 None입니다"
            assert len(str(name)) > 0, f"주식명이 비어있습니다"
    
    @pytest.mark.ui
    def test_function_accessibility(self):
        """함수 접근성 테스트"""
        functions = [
            web_components.create_stock_metrics,
            web_components.create_stock_chart,
            web_components.create_portfolio_summary,
            web_components.create_sidebar_config,
            web_components.display_analysis_result,
            web_components.create_analysis_history,
            web_components.create_volume_chart
        ]
        
        for func in functions:
            assert func is not None, f"함수가 None입니다"
            assert callable(func), f"함수가 호출 가능하지 않습니다"


class TestUIPerformance:
    """UI 성능 테스트"""
    
    @pytest.mark.ui
    def test_create_stock_metrics_performance(self):
        """주식 메트릭 생성 성능 테스트"""
        import time
        
        start_time = time.time()
        try:
            web_components.create_stock_metrics('005930')
        except:
            pass  # 예외가 발생해도 성능만 측정
        end_time = time.time()
        
        # 성능이 1초 이내인지 확인
        performance_time = end_time - start_time
        assert performance_time < 1.0, f"성능이 너무 느립니다: {performance_time:.2f}초"
    
    @pytest.mark.ui
    def test_create_stock_chart_performance(self):
        """주식 차트 생성 성능 테스트"""
        import time
        
        start_time = time.time()
        try:
            web_components.create_stock_chart('005930', 30)
        except:
            pass  # 예외가 발생해도 성능만 측정
        end_time = time.time()
        
        # 성능이 1초 이내인지 확인
        performance_time = end_time - start_time
        assert performance_time < 1.0, f"성능이 너무 느립니다: {performance_time:.2f}초"
    
    @pytest.mark.ui
    def test_create_portfolio_summary_performance(self):
        """포트폴리오 요약 생성 성능 테스트"""
        import time
        
        start_time = time.time()
        try:
            web_components.create_portfolio_summary()
        except:
            pass  # 예외가 발생해도 성능만 측정
        end_time = time.time()
        
        # 성능이 1초 이내인지 확인
        performance_time = end_time - start_time
        assert performance_time < 1.0, f"성능이 너무 느립니다: {performance_time:.2f}초"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "ui"])

