"""
급등주 전략 (브레이크아웃 전략)

급격한 가격 상승과 거래량 급증을 포착하는 전략입니다.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

from .base_strategy import BaseStrategy, Signal, MarketData

logger = logging.getLogger(__name__)

class BreakoutStrategy(BaseStrategy):
    """급등주 전략 (브레이크아웃 전략)"""
    
    def __init__(self, 
                 price_change_threshold: float = 0.05,  # 5% 이상 상승
                 volume_surge_threshold: float = 3.0,   # 거래량 3배 이상
                 resistance_break_threshold: float = 0.02,  # 저항선 돌파 2% 이상
                 max_holding_days: int = 5):  # 최대 보유 기간
        super().__init__(
            name="급등주 전략",
            description="급격한 가격 상승과 거래량 급증을 포착하는 전략"
        )
        
        self.price_change_threshold = price_change_threshold
        self.volume_surge_threshold = volume_surge_threshold
        self.resistance_break_threshold = resistance_break_threshold
        self.max_holding_days = max_holding_days
        
        # 가격 및 거래량 이력 저장
        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[int]] = {}
        self.high_history: Dict[str, List[float]] = {}
        self.entry_dates: Dict[str, datetime] = {}
        
        self.parameters = {
            'price_change_threshold': price_change_threshold,
            'volume_surge_threshold': volume_surge_threshold,
            'resistance_break_threshold': resistance_break_threshold,
            'max_holding_days': max_holding_days
        }
    
    def update_parameters(self, parameters: Dict) -> None:
        """전략 파라미터를 업데이트합니다."""
        if 'price_change_threshold' in parameters:
            self.price_change_threshold = parameters['price_change_threshold']
        if 'volume_surge_threshold' in parameters:
            self.volume_surge_threshold = parameters['volume_surge_threshold']
        if 'resistance_break_threshold' in parameters:
            self.resistance_break_threshold = parameters['resistance_break_threshold']
        if 'max_holding_days' in parameters:
            self.max_holding_days = parameters['max_holding_days']
        
        self.parameters.update(parameters)
        self.logger.info(f"급등주 전략 파라미터 업데이트: {parameters}")
    
    def generate_signal(self, market_data: MarketData) -> Signal:
        """급등주 신호를 생성합니다."""
        stock_code = market_data.stock_code
        current_price = market_data.current_price
        current_volume = market_data.volume
        current_high = market_data.high_price
        
        # 이력 업데이트
        if stock_code not in self.price_history:
            self.price_history[stock_code] = []
        if stock_code not in self.volume_history:
            self.volume_history[stock_code] = []
        if stock_code not in self.high_history:
            self.high_history[stock_code] = []
        
        self.price_history[stock_code].append(current_price)
        self.volume_history[stock_code].append(current_volume)
        self.high_history[stock_code].append(current_high)
        
        # 이력이 충분하지 않으면 HOLD
        if len(self.price_history[stock_code]) < 20:
            return Signal(
                stock_code=stock_code,
                action="HOLD",
                confidence=0.0,
                reason="충분한 가격 이력이 없음"
            )
        
        # 이력 유지 (메모리 효율성)
        if len(self.price_history[stock_code]) > 50:
            self.price_history[stock_code] = self.price_history[stock_code][-30:]
            self.volume_history[stock_code] = self.volume_history[stock_code][-30:]
            self.high_history[stock_code] = self.high_history[stock_code][-30:]
        
        # 보유 중인 종목인지 확인
        if stock_code in self.entry_dates:
            holding_days = (market_data.timestamp - self.entry_dates[stock_code]).days
            if holding_days >= self.max_holding_days:
                # 최대 보유 기간 도달 = 매도
                return Signal(
                    stock_code=stock_code,
                    action="SELL",
                    confidence=0.8,
                    price=current_price,
                    quantity=self._calculate_quantity(current_price, 0.8),
                    reason=f"최대 보유 기간 도달 ({holding_days}일)"
                )
        
        # 브레이크아웃 조건 확인
        breakout_detected = self._detect_breakout(stock_code, current_price, current_volume)
        
        if breakout_detected:
            # 급등 신호 감지 = 매수
            confidence = min(0.9, breakout_detected * 0.8)
            self.entry_dates[stock_code] = market_data.timestamp
            
            return Signal(
                stock_code=stock_code,
                action="BUY",
                confidence=confidence,
                price=current_price,
                quantity=self._calculate_quantity(current_price, confidence),
                reason=f"급등 신호 감지 (가격변동: {self._calculate_price_change(stock_code):.2%}, 거래량증가: {self._calculate_volume_surge(stock_code):.1f}배)"
            )
        
        # 급락 확인 (손절)
        if stock_code in self.entry_dates:
            entry_price = self._get_entry_price(stock_code)
            if entry_price and current_price < entry_price * 0.95:  # 5% 손절
                return Signal(
                    stock_code=stock_code,
                    action="SELL",
                    confidence=0.7,
                    price=current_price,
                    quantity=self._calculate_quantity(current_price, 0.7),
                    reason=f"손절 조건 (진입가: {entry_price:,.0f}원, 현재가: {current_price:,.0f}원)"
                )
        
        return Signal(
            stock_code=stock_code,
            action="HOLD",
            confidence=0.3,
            reason="브레이크아웃 조건 미충족"
        )
    
    def _detect_breakout(self, stock_code: str, current_price: float, current_volume: int) -> float:
        """브레이크아웃을 감지합니다."""
        # 가격 변동률 계산
        price_change = self._calculate_price_change(stock_code)
        
        # 거래량 급증 확인
        volume_surge = self._calculate_volume_surge(stock_code)
        
        # 저항선 돌파 확인
        resistance_break = self._check_resistance_break(stock_code, current_price)
        
        # 종합 점수 계산
        breakout_score = 0.0
        
        if price_change > self.price_change_threshold:
            breakout_score += 0.4
        if volume_surge > self.volume_surge_threshold:
            breakout_score += 0.3
        if resistance_break:
            breakout_score += 0.3
        
        return breakout_score
    
    def _calculate_price_change(self, stock_code: str) -> float:
        """가격 변동률을 계산합니다."""
        prices = self.price_history[stock_code]
        if len(prices) < 2:
            return 0.0
        
        # 전일 대비 변동률
        return (prices[-1] - prices[-2]) / prices[-2]
    
    def _calculate_volume_surge(self, stock_code: str) -> float:
        """거래량 급증률을 계산합니다."""
        volumes = self.volume_history[stock_code]
        if len(volumes) < 10:
            return 1.0
        
        # 최근 거래량과 10일 평균 거래량 비교
        recent_volume = volumes[-1]
        avg_volume = np.mean(volumes[-10:-1])
        
        return recent_volume / avg_volume if avg_volume > 0 else 1.0
    
    def _check_resistance_break(self, stock_code: str, current_price: float) -> bool:
        """저항선 돌파를 확인합니다."""
        highs = self.high_history[stock_code]
        if len(highs) < 20:
            return False
        
        # 최근 20일간의 최고가
        recent_high = max(highs[-20:])
        
        # 현재가가 최고가를 돌파했는지 확인
        return current_price > recent_high * (1 + self.resistance_break_threshold)
    
    def _get_entry_price(self, stock_code: str) -> Optional[float]:
        """진입 가격을 가져옵니다."""
        if stock_code in self.entry_dates:
            # 진입일의 종가를 찾기 (간단한 구현)
            return self.price_history[stock_code][-1] if self.price_history[stock_code] else None
        return None
    
    def _calculate_quantity(self, price: float, confidence: float) -> int:
        """매매 수량을 계산합니다."""
        # 급등주는 소량으로 시작
        base_amount = 500000  # 50만원
        quantity = int(base_amount / price)
        
        # 신뢰도에 따라 수량 조정
        adjusted_quantity = int(quantity * confidence)
        
        # 최소 1주, 최대 50주 (급등주는 리스크가 높으므로)
        return max(1, min(50, adjusted_quantity))
