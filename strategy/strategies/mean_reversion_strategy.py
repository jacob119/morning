"""
Mean Reversion 전략

평균 회귀 원리를 기반으로 매매 신호를 생성하는 전략입니다.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

from .base_strategy import BaseStrategy, Signal, MarketData

logger = logging.getLogger(__name__)

class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion 전략"""
    
    def __init__(self, 
                 lookback_period: int = 20,
                 std_dev_threshold: float = 2.0,
                 reversion_strength: float = 0.5):
        super().__init__(
            name="Mean Reversion 전략",
            description="평균 회귀 원리를 기반으로 한 매매 전략"
        )
        
        self.lookback_period = lookback_period
        self.std_dev_threshold = std_dev_threshold
        self.reversion_strength = reversion_strength
        
        # 가격 이력 저장
        self.price_history: Dict[str, List[float]] = {}
        
        self.parameters = {
            'lookback_period': lookback_period,
            'std_dev_threshold': std_dev_threshold,
            'reversion_strength': reversion_strength
        }
    
    def update_parameters(self, parameters: Dict) -> None:
        """전략 파라미터를 업데이트합니다."""
        if 'lookback_period' in parameters:
            self.lookback_period = parameters['lookback_period']
        if 'std_dev_threshold' in parameters:
            self.std_dev_threshold = parameters['std_dev_threshold']
        if 'reversion_strength' in parameters:
            self.reversion_strength = parameters['reversion_strength']
        
        self.parameters.update(parameters)
        self.logger.info(f"Mean Reversion 전략 파라미터 업데이트: {parameters}")
    
    def generate_signal(self, market_data: MarketData) -> Signal:
        """평균 회귀 기반 매매 신호를 생성합니다."""
        stock_code = market_data.stock_code
        current_price = market_data.current_price
        
        # 가격 이력 업데이트
        if stock_code not in self.price_history:
            self.price_history[stock_code] = []
        
        self.price_history[stock_code].append(current_price)
        
        # 이력이 충분하지 않으면 HOLD
        if len(self.price_history[stock_code]) < self.lookback_period:
            return Signal(
                stock_code=stock_code,
                action="HOLD",
                confidence=0.0,
                reason="충분한 가격 이력이 없음"
            )
        
        # 이력 유지 (메모리 효율성)
        if len(self.price_history[stock_code]) > self.lookback_period * 2:
            self.price_history[stock_code] = self.price_history[stock_code][-self.lookback_period:]
        
        # 평균과 표준편차 계산
        mean_price, std_price, z_score = self._calculate_statistics(stock_code)
        
        # 매매 신호 생성
        if z_score > self.std_dev_threshold:
            # 가격이 평균보다 많이 높음 = 매도 신호
            confidence = min(0.8, (z_score / self.std_dev_threshold) * 0.6)
            return Signal(
                stock_code=stock_code,
                action="SELL",
                confidence=confidence,
                price=current_price,
                quantity=self._calculate_quantity(current_price, confidence),
                reason=f"평균 대비 높음 (Z-score: {z_score:.2f}, 평균: {mean_price:,.0f}원)"
            )
        
        elif z_score < -self.std_dev_threshold:
            # 가격이 평균보다 많이 낮음 = 매수 신호
            confidence = min(0.8, abs(z_score / self.std_dev_threshold) * 0.6)
            return Signal(
                stock_code=stock_code,
                action="BUY",
                confidence=confidence,
                price=current_price,
                quantity=self._calculate_quantity(current_price, confidence),
                reason=f"평균 대비 낮음 (Z-score: {z_score:.2f}, 평균: {mean_price:,.0f}원)"
            )
        
        else:
            # 평균 근처 = HOLD
            return Signal(
                stock_code=stock_code,
                action="HOLD",
                confidence=0.5,
                reason=f"평균 근처 (Z-score: {z_score:.2f})"
            )
    
    def _calculate_statistics(self, stock_code: str) -> tuple:
        """통계값을 계산합니다."""
        prices = self.price_history[stock_code]
        if len(prices) < self.lookback_period:
            return 0.0, 0.0, 0.0
        
        # 최근 N일간의 가격 데이터
        recent_prices = prices[-self.lookback_period:]
        
        mean_price = np.mean(recent_prices)
        std_price = np.std(recent_prices)
        
        if std_price == 0:
            z_score = 0
        else:
            z_score = (prices[-1] - mean_price) / std_price
        
        return mean_price, std_price, z_score
    
    def _calculate_quantity(self, price: float, confidence: float) -> int:
        """매매 수량을 계산합니다."""
        # 기본 수량 (100만원 기준)
        base_amount = 1000000
        quantity = int(base_amount / price)
        
        # 신뢰도에 따라 수량 조정
        adjusted_quantity = int(quantity * confidence)
        
        # 최소 1주, 최대 100주
        return max(1, min(100, adjusted_quantity))
