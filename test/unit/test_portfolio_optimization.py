"""
포트폴리오 최적화 시스템 단위 테스트

포트폴리오 최적화 및 자산 배분 전략을 테스트합니다.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from strategy.portfolio_optimization import (
    PortfolioOptimizer, 
    RiskParityOptimizer, 
    BlackLittermanOptimizer,
    AssetAllocation
)


class TestPortfolioOptimizer:
    """포트폴리오 최적화기 테스트"""
    
    @pytest.fixture
    def portfolio_optimizer(self):
        """PortfolioOptimizer 인스턴스 생성"""
        return PortfolioOptimizer()
    
    @pytest.fixture
    def sample_returns(self):
        """샘플 수익률 데이터"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=252, freq='D')
        returns = pd.DataFrame({
            '005930': np.random.normal(0.001, 0.02, 252),  # 삼성전자
            '000660': np.random.normal(0.0015, 0.025, 252),  # SK하이닉스
            '035420': np.random.normal(0.0008, 0.018, 252),  # NAVER
            '035720': np.random.normal(0.0012, 0.022, 252),  # 카카오
        }, index=dates)
        return returns
    
    @pytest.mark.unit
    def test_covariance_matrix_calculation(self, portfolio_optimizer, sample_returns):
        """공분산 행렬 계산 테스트"""
        # 테스트 실행
        cov_matrix = portfolio_optimizer.calculate_covariance_matrix(sample_returns)
        
        # 검증
        assert cov_matrix is not None
        assert cov_matrix.shape == (4, 4)
        assert np.all(np.diag(cov_matrix) >= 0)  # 분산은 항상 양수
        assert np.allclose(cov_matrix, cov_matrix.T)  # 대칭 행렬
    
    @pytest.mark.unit
    def test_expected_returns_calculation(self, portfolio_optimizer, sample_returns):
        """기대 수익률 계산 테스트"""
        # 테스트 실행
        expected_returns = portfolio_optimizer.calculate_expected_returns(sample_returns)
        
        # 검증
        assert expected_returns is not None
        assert len(expected_returns) == 4
        assert all(isinstance(ret, float) for ret in expected_returns)
    
    @pytest.mark.unit
    def test_sharpe_ratio_optimization(self, portfolio_optimizer, sample_returns):
        """샤프 비율 최적화 테스트"""
        # 테스트 실행
        weights = portfolio_optimizer.optimize_sharpe_ratio(sample_returns)
        
        # 검증
        assert weights is not None
        assert len(weights) == 4
        assert np.isclose(np.sum(weights), 1.0)  # 가중치 합 = 1
        assert all(w >= 0 for w in weights)  # 모든 가중치 >= 0
    
    @pytest.mark.unit
    def test_minimum_variance_optimization(self, portfolio_optimizer, sample_returns):
        """최소 분산 최적화 테스트"""
        # 테스트 실행
        weights = portfolio_optimizer.optimize_minimum_variance(sample_returns)
        
        # 검증
        assert weights is not None
        assert len(weights) == 4
        assert np.isclose(np.sum(weights), 1.0)
        assert all(w >= 0 for w in weights)
    
    @pytest.mark.unit
    def test_portfolio_performance_calculation(self, portfolio_optimizer, sample_returns):
        """포트폴리오 성과 계산 테스트"""
        weights = [0.25, 0.25, 0.25, 0.25]  # 균등 가중치
        
        # 테스트 실행
        performance = portfolio_optimizer.calculate_portfolio_performance(
            sample_returns, weights
        )
        
        # 검증
        assert performance is not None
        assert "return" in performance
        assert "volatility" in performance
        assert "sharpe_ratio" in performance
        assert "max_drawdown" in performance
        assert performance["volatility"] > 0
        assert performance["max_drawdown"] <= 0


class TestRiskParityOptimizer:
    """리스크 패리티 최적화기 테스트"""
    
    @pytest.fixture
    def risk_parity_optimizer(self):
        """RiskParityOptimizer 인스턴스 생성"""
        return RiskParityOptimizer()
    
    @pytest.mark.unit
    def test_risk_contribution_calculation(self, risk_parity_optimizer, sample_returns):
        """리스크 기여도 계산 테스트"""
        weights = [0.25, 0.25, 0.25, 0.25]
        
        # 테스트 실행
        risk_contrib = risk_parity_optimizer.calculate_risk_contribution(
            sample_returns, weights
        )
        
        # 검증
        assert risk_contrib is not None
        assert len(risk_contrib) == 4
        assert all(rc >= 0 for rc in risk_contrib)
        assert np.isclose(np.sum(risk_contrib), 1.0)
    
    @pytest.mark.unit
    def test_risk_parity_optimization(self, risk_parity_optimizer, sample_returns):
        """리스크 패리티 최적화 테스트"""
        # 테스트 실행
        weights = risk_parity_optimizer.optimize(sample_returns)
        
        # 검증
        assert weights is not None
        assert len(weights) == 4
        assert np.isclose(np.sum(weights), 1.0)
        assert all(w >= 0 for w in weights)
        
        # 리스크 기여도가 균등한지 확인
        risk_contrib = risk_parity_optimizer.calculate_risk_contribution(
            sample_returns, weights
        )
        target_contribution = 1.0 / 4
        assert all(abs(rc - target_contribution) < 0.1 for rc in risk_contrib)


class TestBlackLittermanOptimizer:
    """Black-Litterman 최적화기 테스트"""
    
    @pytest.fixture
    def black_litterman_optimizer(self):
        """BlackLittermanOptimizer 인스턴스 생성"""
        return BlackLittermanOptimizer()
    
    @pytest.mark.unit
    def test_market_equilibrium_returns(self, black_litterman_optimizer, sample_returns):
        """시장 균형 수익률 계산 테스트"""
        # 테스트 실행
        equilibrium_returns = black_litterman_optimizer.calculate_market_equilibrium_returns(
            sample_returns
        )
        
        # 검증
        assert equilibrium_returns is not None
        assert len(equilibrium_returns) == 4
        assert all(isinstance(ret, float) for ret in equilibrium_returns)
    
    @pytest.mark.unit
    def test_view_integration(self, black_litterman_optimizer, sample_returns):
        """투자자 관점 통합 테스트"""
        # 투자자 관점 설정
        views = {
            '005930': 0.02,  # 삼성전자 2% 상승 전망
            '000660': -0.01  # SK하이닉스 1% 하락 전망
        }
        confidence = 0.8
        
        # 테스트 실행
        weights = black_litterman_optimizer.optimize_with_views(
            sample_returns, views, confidence
        )
        
        # 검증
        assert weights is not None
        assert len(weights) == 4
        assert np.isclose(np.sum(weights), 1.0)
        assert all(w >= 0 for w in weights)


class TestAssetAllocation:
    """자산 배분 테스트"""
    
    @pytest.fixture
    def asset_allocation(self):
        """AssetAllocation 인스턴스 생성"""
        return AssetAllocation()
    
    @pytest.mark.unit
    def test_tactical_asset_allocation(self, asset_allocation, sample_returns):
        """전술적 자산 배분 테스트"""
        # 시장 상황 설정
        market_condition = "bull_market"  # 상승장
        
        # 테스트 실행
        allocation = asset_allocation.tactical_allocation(
            sample_returns, market_condition
        )
        
        # 검증
        assert allocation is not None
        assert "weights" in allocation
        assert "strategy" in allocation
        assert np.isclose(np.sum(allocation["weights"]), 1.0)
    
    @pytest.mark.unit
    def test_dynamic_rebalancing(self, asset_allocation, sample_returns):
        """동적 리밸런싱 테스트"""
        current_weights = [0.25, 0.25, 0.25, 0.25]
        target_weights = [0.3, 0.2, 0.3, 0.2]
        rebalancing_threshold = 0.05
        
        # 테스트 실행
        rebalance_decision = asset_allocation.should_rebalance(
            current_weights, target_weights, rebalancing_threshold
        )
        
        # 검증
        assert isinstance(rebalance_decision, bool)
        
        if rebalance_decision:
            new_weights = asset_allocation.calculate_rebalancing_trades(
                current_weights, target_weights
            )
            assert new_weights is not None
            assert len(new_weights) == 4
    
    @pytest.mark.unit
    def test_risk_budget_allocation(self, asset_allocation, sample_returns):
        """리스크 예산 배분 테스트"""
        risk_budget = {
            '005930': 0.3,  # 30% 리스크 예산
            '000660': 0.3,
            '035420': 0.2,
            '035720': 0.2
        }
        
        # 테스트 실행
        weights = asset_allocation.risk_budget_allocation(
            sample_returns, risk_budget
        )
        
        # 검증
        assert weights is not None
        assert len(weights) == 4
        assert np.isclose(np.sum(weights), 1.0)
        assert all(w >= 0 for w in weights)


class TestPortfolioOptimizationIntegration:
    """포트폴리오 최적화 통합 테스트"""
    
    @pytest.mark.integration
    def test_complete_optimization_workflow(self, sample_returns):
        """완전한 최적화 워크플로우 테스트"""
        optimizer = PortfolioOptimizer()
        
        # 1. 샤프 비율 최적화
        sharpe_weights = optimizer.optimize_sharpe_ratio(sample_returns)
        sharpe_performance = optimizer.calculate_portfolio_performance(
            sample_returns, sharpe_weights
        )
        
        # 2. 최소 분산 최적화
        minvar_weights = optimizer.optimize_minimum_variance(sample_returns)
        minvar_performance = optimizer.calculate_portfolio_performance(
            sample_returns, minvar_weights
        )
        
        # 3. 성과 비교
        assert sharpe_performance["sharpe_ratio"] >= minvar_performance["sharpe_ratio"]
        assert minvar_performance["volatility"] <= sharpe_performance["volatility"]
    
    @pytest.mark.integration
    def test_risk_parity_vs_traditional(self, sample_returns):
        """리스크 패리티 vs 전통적 최적화 비교 테스트"""
        traditional_optimizer = PortfolioOptimizer()
        risk_parity_optimizer = RiskParityOptimizer()
        
        # 전통적 최적화
        traditional_weights = traditional_optimizer.optimize_sharpe_ratio(sample_returns)
        traditional_risk_contrib = risk_parity_optimizer.calculate_risk_contribution(
            sample_returns, traditional_weights
        )
        
        # 리스크 패리티 최적화
        risk_parity_weights = risk_parity_optimizer.optimize(sample_returns)
        risk_parity_risk_contrib = risk_parity_optimizer.calculate_risk_contribution(
            sample_returns, risk_parity_weights
        )
        
        # 리스크 기여도 분산 비교
        traditional_variance = np.var(traditional_risk_contrib)
        risk_parity_variance = np.var(risk_parity_risk_contrib)
        
        # 리스크 패리티가 더 균등한 리스크 분산을 가져야 함
        assert risk_parity_variance <= traditional_variance
