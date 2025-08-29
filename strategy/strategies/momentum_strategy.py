"""
모멘텀 전략

가격 모멘텀을 기반으로 매매 신호를 생성하는 전략입니다.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

from .base_strategy import BaseStrategy, Signal, MarketData

logger = logging.getLogger(__name__)

class MomentumStrategy(BaseStrategy):
    """모멘텀 전략"""
    
    def __init__(self, 
                 lookback_period: int = 20,
                 momentum_threshold: float = 0.05,
                 volume_threshold: float = 1.5):
        super().__init__(
            name="모멘텀 전략",
            description="가격 모멘텀과 거래량을 기반으로 한 매매 전략"
        )
        
        self.lookback_period = lookback_period
        self.momentum_threshold = momentum_threshold
        self.volume_threshold = volume_threshold
        
        # 가격 이력 저장
        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[int]] = {}
        
        self.parameters = {
            'lookback_period': lookback_period,
            'momentum_threshold': momentum_threshold,
            'volume_threshold': volume_threshold
        }
    
    def update_parameters(self, parameters: Dict) -> None:
        """전략 파라미터를 업데이트합니다."""
        if 'lookback_period' in parameters:
            self.lookback_period = parameters['lookback_period']
        if 'momentum_threshold' in parameters:
            self.momentum_threshold = parameters['momentum_threshold']
        if 'volume_threshold' in parameters:
            self.volume_threshold = parameters['volume_threshold']
        
        self.parameters.update(parameters)
        self.logger.info(f"모멘텀 전략 파라미터 업데이트: {parameters}")
    
    def generate_signal(self, market_data: MarketData) -> Signal:
        """모멘텀 기반 매매 신호를 생성합니다."""
        stock_code = market_data.stock_code
        current_price = market_data.current_price
        current_volume = market_data.volume
        
        # 가격 이력 업데이트
        if stock_code not in self.price_history:
            self.price_history[stock_code] = []
        if stock_code not in self.volume_history:
            self.volume_history[stock_code] = []
        
        self.price_history[stock_code].append(current_price)
        self.volume_history[stock_code].append(current_volume)
        
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
            self.volume_history[stock_code] = self.volume_history[stock_code][-self.lookback_period:]
        
        # 모멘텀 계산
        price_momentum = self._calculate_momentum(stock_code)
        volume_momentum = self._calculate_volume_momentum(stock_code)
        
        # 매매 신호 생성
        if price_momentum > self.momentum_threshold and volume_momentum > self.volume_threshold:
            # 강한 상승 모멘텀 + 거래량 증가 = 매수
            confidence = min(0.9, (price_momentum / self.momentum_threshold) * 0.7)
            return Signal(
                stock_code=stock_code,
                action="BUY",
                confidence=confidence,
                price=current_price,
                quantity=self._calculate_quantity(current_price, confidence),
                reason=f"모멘텀 상승 ({price_momentum:.2%}), 거래량 증가 ({volume_momentum:.1f}배)"
            )
        
        elif price_momentum < -self.momentum_threshold:
            # 하락 모멘텀 = 매도
            confidence = min(0.8, abs(price_momentum / self.momentum_threshold) * 0.6)
            return Signal(
                stock_code=stock_code,
                action="SELL",
                confidence=confidence,
                price=current_price,
                quantity=self._calculate_quantity(current_price, confidence),
                reason=f"모멘텀 하락 ({price_momentum:.2%})"
            )
        
        else:
            # 중립 = HOLD
            return Signal(
                stock_code=stock_code,
                action="HOLD",
                confidence=0.5,
                reason=f"모멘텀 중립 ({price_momentum:.2%})"
            )
    
    def _calculate_momentum(self, stock_code: str) -> float:
        """가격 모멘텀을 계산합니다."""
        prices = self.price_history[stock_code]
        if len(prices) < self.lookback_period:
            return 0.0
        
        # 최근 가격과 과거 가격 비교
        recent_price = prices[-1]
        past_price = prices[-self.lookback_period]
        
        return (recent_price - past_price) / past_price
    
    def _calculate_volume_momentum(self, stock_code: str) -> float:
        """거래량 모멘텀을 계산합니다."""
        volumes = self.volume_history[stock_code]
        if len(volumes) < self.lookback_period:
            return 1.0
        
        # 최근 거래량과 평균 거래량 비교
        recent_volume = volumes[-1]
        avg_volume = np.mean(volumes[-self.lookback_period:-1])
        
        return recent_volume / avg_volume if avg_volume > 0 else 1.0
    
    def _calculate_quantity(self, price: float, confidence: float) -> int:
        """매매 수량을 계산합니다."""
        # 기본 수량 (100만원 기준)
        base_amount = 1000000
        quantity = int(base_amount / price)
        
        # 신뢰도에 따라 수량 조정
        adjusted_quantity = int(quantity * confidence)
        
        # 최소 1주, 최대 100주
        return max(1, min(100, adjusted_quantity))
