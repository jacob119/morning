"""
모멘텀 전략 테스트

모멘텀 전략의 기능을 테스트합니다.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from strategy.strategies import MomentumStrategy, MarketData

class TestMomentumStrategy(unittest.TestCase):
    """모멘텀 전략 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.strategy = MomentumStrategy(
            lookback_period=5,
            momentum_threshold=0.03,
            volume_threshold=1.5
        )
        
        # 테스트용 가격 데이터 생성
        self.prices = [10000, 10100, 10200, 10300, 10400, 10500, 10600, 10700, 10800, 10900]
        self.volumes = [1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000, 1700000, 1800000, 1900000]
    
    def test_initialization(self):
        """전략 초기화 테스트"""
        self.assertEqual(self.strategy.name, "모멘텀 전략")
        self.assertTrue(self.strategy.is_active)
        self.assertEqual(self.strategy.lookback_period, 5)
        self.assertEqual(self.strategy.momentum_threshold, 0.03)
        self.assertEqual(self.strategy.volume_threshold, 1.5)
    
    def test_insufficient_history(self):
        """충분한 이력이 없을 때 테스트"""
        # 이력이 부족한 경우
        market_data = MarketData(
            stock_code="005930",
            current_price=10000,
            open_price=9900,
            high_price=10100,
            low_price=9800,
            volume=1000000,
            timestamp=datetime.now()
        )
        
        signal = self.strategy.generate_signal(market_data)
        self.assertEqual(signal.action, "HOLD")
        self.assertEqual(signal.confidence, 0.0)
        self.assertIn("충분한 가격 이력이 없음", signal.reason)
    
    def test_momentum_calculation(self):
        """모멘텀 계산 테스트"""
        # 충분한 이력 생성
        for i, (price, volume) in enumerate(zip(self.prices, self.volumes)):
            market_data = MarketData(
                stock_code="005930",
                current_price=price,
                open_price=price * 0.99,
                high_price=price * 1.01,
                low_price=price * 0.98,
                volume=volume,
                timestamp=datetime.now() + timedelta(days=i)
            )
            self.strategy.generate_signal(market_data)
        
        # 모멘텀 계산 테스트
        momentum = self.strategy._calculate_momentum("005930")
        expected_momentum = (self.prices[-1] - self.prices[-5]) / self.prices[-5]
        self.assertAlmostEqual(momentum, expected_momentum, places=5)
    
    def test_volume_momentum_calculation(self):
        """거래량 모멘텀 계산 테스트"""
        # 충분한 이력 생성
        for i, (price, volume) in enumerate(zip(self.prices, self.volumes)):
            market_data = MarketData(
                stock_code="005930",
                current_price=price,
                open_price=price * 0.99,
                high_price=price * 1.01,
                low_price=price * 0.98,
                volume=volume,
                timestamp=datetime.now() + timedelta(days=i)
            )
            self.strategy.generate_signal(market_data)
        
        # 거래량 모멘텀 계산 테스트
        volume_momentum = self.strategy._calculate_volume_momentum("005930")
        recent_volume = self.volumes[-1]
        avg_volume = np.mean(self.volumes[-5:-1])
        expected_volume_momentum = recent_volume / avg_volume
        self.assertAlmostEqual(volume_momentum, expected_volume_momentum, places=5)
    
    def test_buy_signal_generation(self):
        """매수 신호 생성 테스트"""
        # 상승 모멘텀과 거래량 증가 시나리오
        base_price = 10000
        for i in range(10):
            # 점진적 상승
            price = base_price * (1 + i * 0.02)
            # 거래량 증가
            volume = 1000000 * (1 + i * 0.1)
            
            market_data = MarketData(
                stock_code="005930",
                current_price=price,
                open_price=price * 0.99,
                high_price=price * 1.01,
                low_price=price * 0.98,
                volume=volume,
                timestamp=datetime.now() + timedelta(days=i)
            )
            signal = self.strategy.generate_signal(market_data)
            
            # 충분한 이력이 쌓인 후 매수 신호 확인
            if i >= 5 and signal.action == "BUY":
                self.assertGreater(signal.confidence, 0.0)
                self.assertIsNotNone(signal.price)
                self.assertIsNotNone(signal.quantity)
                break
    
    def test_sell_signal_generation(self):
        """매도 신호 생성 테스트"""
        # 하락 모멘텀 시나리오
        base_price = 10000
        for i in range(10):
            # 점진적 하락
            price = base_price * (1 - i * 0.02)
            volume = 1000000
            
            market_data = MarketData(
                stock_code="005930",
                current_price=price,
                open_price=price * 1.01,
                high_price=price * 1.02,
                low_price=price * 0.99,
                volume=volume,
                timestamp=datetime.now() + timedelta(days=i)
            )
            signal = self.strategy.generate_signal(market_data)
            
            # 충분한 이력이 쌓인 후 매도 신호 확인
            if i >= 5 and signal.action == "SELL":
                self.assertGreater(signal.confidence, 0.0)
                self.assertIsNotNone(signal.price)
                self.assertIsNotNone(signal.quantity)
                break
    
    def test_parameter_update(self):
        """파라미터 업데이트 테스트"""
        new_params = {
            'lookback_period': 10,
            'momentum_threshold': 0.05,
            'volume_threshold': 2.0
        }
        
        self.strategy.update_parameters(new_params)
        
        self.assertEqual(self.strategy.lookback_period, 10)
        self.assertEqual(self.strategy.momentum_threshold, 0.05)
        self.assertEqual(self.strategy.volume_threshold, 2.0)
        self.assertEqual(self.strategy.parameters['lookback_period'], 10)
    
    def test_quantity_calculation(self):
        """수량 계산 테스트"""
        price = 10000
        confidence = 0.8
        
        quantity = self.strategy._calculate_quantity(price, confidence)
        
        # 기본 수량: 1,000,000 / 10,000 = 100
        # 조정된 수량: 100 * 0.8 = 80
        expected_quantity = int((1000000 / price) * confidence)
        self.assertEqual(quantity, expected_quantity)
        
        # 최소/최대 범위 테스트
        self.assertGreaterEqual(quantity, 1)
        self.assertLessEqual(quantity, 100)

if __name__ == '__main__':
    unittest.main()
