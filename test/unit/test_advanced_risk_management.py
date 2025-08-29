"""
고급 리스크 관리 시스템 단위 테스트

VaR, CVaR, 스트레스 테스트 등을 테스트합니다.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from strategy.risk_management import (
    AdvancedRiskManager,
    VaRCalculator,
    StressTester,
    ScenarioAnalyzer,
    LiquidityManager
)


class TestVaRCalculator:
    """VaR 계산기 테스트"""
    
    @pytest.fixture
    def var_calculator(self):
        """VaRCalculator 인스턴스 생성"""
        return VaRCalculator()
    
    @pytest.fixture
    def sample_returns(self):
        """샘플 수익률 데이터"""
        np.random.seed(42)
        returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
        return returns
    
    @pytest.mark.unit
    def test_historical_var(self, var_calculator, sample_returns):
        """역사적 VaR 계산 테스트"""
        confidence_level = 0.95
        
        # 테스트 실행
        var = var_calculator.calculate_historical_var(sample_returns, confidence_level)
        
        # 검증
        assert var is not None
        assert var < 0  # VaR은 일반적으로 음수
        assert abs(var) > 0
    
    @pytest.mark.unit
    def test_parametric_var(self, var_calculator, sample_returns):
        """모수적 VaR 계산 테스트"""
        confidence_level = 0.99
        
        # 테스트 실행
        var = var_calculator.calculate_parametric_var(sample_returns, confidence_level)
        
        # 검증
        assert var is not None
        assert var < 0
        assert abs(var) > 0
    
    @pytest.mark.unit
    def test_monte_carlo_var(self, var_calculator, sample_returns):
        """몬테카를로 VaR 계산 테스트"""
        confidence_level = 0.95
        num_simulations = 10000
        
        # 테스트 실행
        var = var_calculator.calculate_monte_carlo_var(
            sample_returns, confidence_level, num_simulations
        )
        
        # 검증
        assert var is not None
        assert var < 0
        assert abs(var) > 0
    
    @pytest.mark.unit
    def test_cvar_calculation(self, var_calculator, sample_returns):
        """CVaR 계산 테스트"""
        confidence_level = 0.95
        
        # 테스트 실행
        cvar = var_calculator.calculate_cvar(sample_returns, confidence_level)
        
        # 검증
        assert cvar is not None
        assert cvar < 0
        assert abs(cvar) > 0
        
        # CVaR은 VaR보다 더 극단적이어야 함
        var = var_calculator.calculate_historical_var(sample_returns, confidence_level)
        assert cvar <= var


class TestStressTester:
    """스트레스 테스터 테스트"""
    
    @pytest.fixture
    def stress_tester(self):
        """StressTester 인스턴스 생성"""
        return StressTester()
    
    @pytest.fixture
    def sample_portfolio(self):
        """샘플 포트폴리오"""
        return {
            "005930": {"quantity": 100, "price": 70000, "weight": 0.4},
            "000660": {"quantity": 20, "price": 250000, "weight": 0.3},
            "035420": {"quantity": 50, "price": 220000, "weight": 0.3}
        }
    
    @pytest.mark.unit
    def test_market_crash_scenario(self, stress_tester, sample_portfolio):
        """시장 폭락 시나리오 테스트"""
        # 시장 폭락 시나리오 설정
        scenario = {
            "005930": -0.30,  # 30% 하락
            "000660": -0.25,  # 25% 하락
            "035420": -0.20   # 20% 하락
        }
        
        # 테스트 실행
        result = stress_tester.run_scenario(sample_portfolio, scenario)
        
        # 검증
        assert result is not None
        assert "portfolio_value" in result
        assert "loss" in result
        assert "loss_percentage" in result
        assert result["loss"] > 0
        assert result["loss_percentage"] > 0
    
    @pytest.mark.unit
    def test_interest_rate_shock(self, stress_tester, sample_portfolio):
        """금리 충격 시나리오 테스트"""
        # 금리 상승 시나리오
        scenario = {
            "interest_rate_change": 0.02,  # 2% 상승
            "market_impact": -0.15  # 15% 시장 하락
        }
        
        # 테스트 실행
        result = stress_tester.run_interest_rate_scenario(sample_portfolio, scenario)
        
        # 검증
        assert result is not None
        assert "portfolio_value" in result
        assert "duration_impact" in result
        assert "market_impact" in result
    
    @pytest.mark.unit
    def test_liquidity_crisis_scenario(self, stress_tester, sample_portfolio):
        """유동성 위기 시나리오 테스트"""
        # 유동성 위기 시나리오
        scenario = {
            "liquidity_premium": 0.05,  # 5% 유동성 프리미엄
            "volume_reduction": 0.7,     # 거래량 70% 감소
            "price_impact": -0.10        # 10% 가격 하락
        }
        
        # 테스트 실행
        result = stress_tester.run_liquidity_scenario(sample_portfolio, scenario)
        
        # 검증
        assert result is not None
        assert "liquidity_cost" in result
        assert "execution_risk" in result
        assert "portfolio_value" in result
    
    @pytest.mark.unit
    def test_correlation_breakdown(self, stress_tester, sample_portfolio):
        """상관관계 붕괴 시나리오 테스트"""
        # 상관관계 붕괴 시나리오
        scenario = {
            "correlation_increase": 0.5,  # 상관관계 0.5 증가
            "volatility_increase": 0.3    # 변동성 30% 증가
        }
        
        # 테스트 실행
        result = stress_tester.run_correlation_scenario(sample_portfolio, scenario)
        
        # 검증
        assert result is not None
        assert "diversification_loss" in result
        assert "portfolio_volatility" in result


class TestScenarioAnalyzer:
    """시나리오 분석기 테스트"""
    
    @pytest.fixture
    def scenario_analyzer(self):
        """ScenarioAnalyzer 인스턴스 생성"""
        return ScenarioAnalyzer()
    
    @pytest.mark.unit
    def test_scenario_generation(self, scenario_analyzer):
        """시나리오 생성 테스트"""
        # 시나리오 파라미터
        params = {
            "market_shock": [-0.1, -0.2, -0.3],  # 10%, 20%, 30% 하락
            "volatility_increase": [0.2, 0.4, 0.6],  # 변동성 증가
            "correlation_change": [0.1, 0.2, 0.3]  # 상관관계 변화
        }
        
        # 테스트 실행
        scenarios = scenario_analyzer.generate_scenarios(params)
        
        # 검증
        assert scenarios is not None
        assert len(scenarios) > 0
        assert all(isinstance(s, dict) for s in scenarios)
    
    @pytest.mark.unit
    def test_probability_assignment(self, scenario_analyzer):
        """확률 할당 테스트"""
        scenarios = [
            {"market_shock": -0.1, "probability": 0.5},
            {"market_shock": -0.2, "probability": 0.3},
            {"market_shock": -0.3, "probability": 0.2}
        ]
        
        # 테스트 실행
        weighted_result = scenario_analyzer.calculate_weighted_impact(scenarios)
        
        # 검증
        assert weighted_result is not None
        assert "expected_loss" in weighted_result
        assert "worst_case_loss" in weighted_result
        assert "confidence_interval" in weighted_result


class TestLiquidityManager:
    """유동성 관리자 테스트"""
    
    @pytest.fixture
    def liquidity_manager(self):
        """LiquidityManager 인스턴스 생성"""
        return LiquidityManager()
    
    @pytest.mark.unit
    def test_liquidity_measurement(self, liquidity_manager):
        """유동성 측정 테스트"""
        # 거래량 데이터
        volume_data = {
            "005930": {"avg_volume": 5000000, "current_volume": 4000000},
            "000660": {"avg_volume": 2000000, "current_volume": 1500000},
            "035420": {"avg_volume": 1000000, "current_volume": 800000}
        }
        
        # 테스트 실행
        liquidity_scores = liquidity_manager.calculate_liquidity_scores(volume_data)
        
        # 검증
        assert liquidity_scores is not None
        assert all(0 <= score <= 1 for score in liquidity_scores.values())
    
    @pytest.mark.unit
    def test_liquidity_cost_estimation(self, liquidity_manager):
        """유동성 비용 추정 테스트"""
        # 거래 정보
        trade_info = {
            "stock_code": "005930",
            "quantity": 1000,
            "current_price": 70000,
            "avg_volume": 5000000
        }
        
        # 테스트 실행
        cost = liquidity_manager.estimate_liquidity_cost(trade_info)
        
        # 검증
        assert cost is not None
        assert cost >= 0
        assert "market_impact" in cost
        assert "slippage" in cost
        assert "total_cost" in cost
    
    @pytest.mark.unit
    def test_optimal_execution_strategy(self, liquidity_manager):
        """최적 실행 전략 테스트"""
        # 거래 요구사항
        trade_requirements = {
            "stock_code": "005930",
            "total_quantity": 5000,
            "urgency": "medium",  # low, medium, high
            "time_horizon": 5  # 일
        }
        
        # 테스트 실행
        strategy = liquidity_manager.optimize_execution_strategy(trade_requirements)
        
        # 검증
        assert strategy is not None
        assert "execution_schedule" in strategy
        assert "expected_cost" in strategy
        assert "risk_metrics" in strategy


class TestAdvancedRiskManager:
    """고급 리스크 관리자 테스트"""
    
    @pytest.fixture
    def advanced_risk_manager(self):
        """AdvancedRiskManager 인스턴스 생성"""
        return AdvancedRiskManager()
    
    @pytest.mark.unit
    def test_comprehensive_risk_assessment(self, advanced_risk_manager, sample_portfolio):
        """종합 리스크 평가 테스트"""
        # 테스트 실행
        risk_assessment = advanced_risk_manager.comprehensive_risk_assessment(sample_portfolio)
        
        # 검증
        assert risk_assessment is not None
        assert "var_95" in risk_assessment
        assert "cvar_95" in risk_assessment
        assert "stress_test_results" in risk_assessment
        assert "liquidity_risk" in risk_assessment
        assert "concentration_risk" in risk_assessment
    
    @pytest.mark.unit
    def test_risk_limit_monitoring(self, advanced_risk_manager):
        """리스크 한도 모니터링 테스트"""
        # 리스크 한도 설정
        risk_limits = {
            "var_limit": -1000000,  # 100만원
            "concentration_limit": 0.3,  # 30%
            "liquidity_limit": 0.1  # 10%
        }
        
        # 현재 포트폴리오 상태
        current_risk = {
            "var_95": -800000,
            "max_concentration": 0.25,
            "liquidity_score": 0.15
        }
        
        # 테스트 실행
        alerts = advanced_risk_manager.check_risk_limits(current_risk, risk_limits)
        
        # 검증
        assert alerts is not None
        assert isinstance(alerts, list)
    
    @pytest.mark.unit
    def test_dynamic_risk_adjustment(self, advanced_risk_manager, sample_portfolio):
        """동적 리스크 조정 테스트"""
        # 시장 상황 변화
        market_conditions = {
            "volatility_regime": "high",
            "correlation_regime": "increasing",
            "liquidity_regime": "decreasing"
        }
        
        # 테스트 실행
        adjustments = advanced_risk_manager.dynamic_risk_adjustment(
            sample_portfolio, market_conditions
        )
        
        # 검증
        assert adjustments is not None
        assert "position_adjustments" in adjustments
        assert "risk_limits_adjustments" in adjustments
        assert "hedging_recommendations" in adjustments


class TestAdvancedRiskManagementIntegration:
    """고급 리스크 관리 통합 테스트"""
    
    @pytest.mark.integration
    def test_complete_risk_management_workflow(self, sample_portfolio):
        """완전한 리스크 관리 워크플로우 테스트"""
        risk_manager = AdvancedRiskManager()
        
        # 1. 종합 리스크 평가
        risk_assessment = risk_manager.comprehensive_risk_assessment(sample_portfolio)
        
        # 2. 스트레스 테스트 실행
        stress_tester = StressTester()
        stress_results = stress_tester.run_multiple_scenarios(sample_portfolio)
        
        # 3. 유동성 분석
        liquidity_manager = LiquidityManager()
        liquidity_analysis = liquidity_manager.analyze_portfolio_liquidity(sample_portfolio)
        
        # 4. 리스크 한도 검사
        risk_limits = {
            "var_limit": -1000000,
            "concentration_limit": 0.3,
            "liquidity_limit": 0.1
        }
        alerts = risk_manager.check_risk_limits(risk_assessment, risk_limits)
        
        # 검증
        assert risk_assessment is not None
        assert stress_results is not None
        assert liquidity_analysis is not None
        assert alerts is not None
    
    @pytest.mark.integration
    def test_risk_monitoring_and_alerting(self, sample_portfolio):
        """리스크 모니터링 및 알림 테스트"""
        risk_manager = AdvancedRiskManager()
        
        # 모니터링 설정
        monitoring_config = {
            "check_interval": 300,  # 5분
            "alert_thresholds": {
                "var_breach": 0.8,  # VaR 한도의 80% 도달 시
                "concentration_breach": 0.25,
                "liquidity_breach": 0.15
            }
        }
        
        # 테스트 실행
        monitoring_result = risk_manager.setup_monitoring(
            sample_portfolio, monitoring_config
        )
        
        # 검증
        assert monitoring_result is not None
        assert "monitoring_active" in monitoring_result
        assert "alert_channels" in monitoring_result
