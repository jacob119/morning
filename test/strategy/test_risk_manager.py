"""
리스크 관리 모듈 테스트

리스크 관리 기능을 테스트합니다.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import unittest
from datetime import datetime, timedelta

from strategy.risk_management import RiskManager, RiskRule
from strategy.strategies import Signal, MarketData

class TestRiskManager(unittest.TestCase):
    """리스크 관리자 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.risk_manager = RiskManager()
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertIsNotNone(self.risk_manager.rules)
        self.assertEqual(self.risk_manager.daily_buy_amount, 0.0)
        self.assertIsNotNone(self.risk_manager.positions)
        self.assertIsNotNone(self.risk_manager.trade_history)
        
        # 기본 규칙들이 설정되었는지 확인
        expected_rules = [
            "일일 매수 한도",
            "최대 보유 종목 수", 
            "손절 규칙",
            "익절 규칙",
            "단일 종목 투자 한도"
        ]
        
        for rule_name in expected_rules:
            self.assertIn(rule_name, self.risk_manager.rules)
    
    def test_add_rule(self):
        """규칙 추가 테스트"""
        new_rule = RiskRule(
            name="테스트 규칙",
            rule_type="test_type",
            parameters={"test_param": 100}
        )
        
        self.risk_manager.add_rule(new_rule)
        self.assertIn("테스트 규칙", self.risk_manager.rules)
        self.assertEqual(self.risk_manager.rules["테스트 규칙"], new_rule)
    
    def test_remove_rule(self):
        """규칙 제거 테스트"""
        # 기존 규칙 제거
        initial_count = len(self.risk_manager.rules)
        self.risk_manager.remove_rule("일일 매수 한도")
        
        self.assertNotIn("일일 매수 한도", self.risk_manager.rules)
        self.assertEqual(len(self.risk_manager.rules), initial_count - 1)
    
    def test_update_rule(self):
        """규칙 업데이트 테스트"""
        # 기존 규칙 업데이트
        new_params = {"max_daily_buy": 20000000}  # 2천만원으로 변경
        self.risk_manager.update_rule("일일 매수 한도", new_params)
        
        updated_rule = self.risk_manager.rules["일일 매수 한도"]
        self.assertEqual(updated_rule.parameters["max_daily_buy"], 20000000)
    
    def test_daily_limit_validation(self):
        """일일 매수 한도 검증 테스트"""
        # 매수 신호 생성
        signal = Signal(
            stock_code="005930",
            action="BUY",
            confidence=0.8,
            price=10000,
            quantity=100
        )
        
        market_data = MarketData(
            stock_code="005930",
            current_price=10000,
            open_price=9900,
            high_price=10100,
            low_price=9800,
            volume=1000000,
            timestamp=datetime.now()
        )
        
        # 일일 매수 한도 초과 시나리오
        self.risk_manager.daily_buy_amount = 15000000  # 1천5백만원 이미 사용
        
        # 1천만원 매수 시도 (총 2천5백만원 > 1천만원 한도)
        is_valid = self.risk_manager.validate_signal(signal, market_data)
        self.assertFalse(is_valid)
        
        # 한도 내 매수 시도
        self.risk_manager.daily_buy_amount = 5000000  # 5백만원 사용
        is_valid = self.risk_manager.validate_signal(signal, market_data)
        self.assertTrue(is_valid)
    
    def test_position_limit_validation(self):
        """최대 보유 종목 수 검증 테스트"""
        # 최대 보유 종목 수를 2개로 설정
        self.risk_manager.update_rule("최대 보유 종목 수", {"max_positions": 2})
        
        # 이미 2개 종목 보유 중인 상황 시뮬레이션
        self.risk_manager.positions = {
            "005930": {"quantity": 10, "avg_price": 70000, "current_value": 700000},
            "000660": {"quantity": 5, "avg_price": 250000, "current_value": 1250000}
        }
        
        # 새로운 종목 매수 시도
        signal = Signal(
            stock_code="035420",
            action="BUY",
            confidence=0.8,
            price=220000,
            quantity=3
        )
        
        market_data = MarketData(
            stock_code="035420",
            current_price=220000,
            open_price=218000,
            high_price=222000,
            low_price=216000,
            volume=500000,
            timestamp=datetime.now()
        )
        
        is_valid = self.risk_manager.validate_signal(signal, market_data)
        self.assertFalse(is_valid)
    
    def test_stop_loss_validation(self):
        """손절 규칙 검증 테스트"""
        # 포지션 설정 (평균단가 10000원)
        self.risk_manager.positions["005930"] = {
            "quantity": 10,
            "avg_price": 10000,
            "current_value": 95000  # 5% 손실
        }
        
        # 손절 신호 (현재가 9000원, 10% 손실)
        signal = Signal(
            stock_code="005930",
            action="SELL",
            confidence=0.7,
            price=9000,
            quantity=10
        )
        
        market_data = MarketData(
            stock_code="005930",
            current_price=9000,
            open_price=9200,
            high_price=9300,
            low_price=8900,
            volume=1000000,
            timestamp=datetime.now()
        )
        
        # 손절은 허용되어야 함
        is_valid = self.risk_manager.validate_signal(signal, market_data)
        self.assertTrue(is_valid)
    
    def test_take_profit_validation(self):
        """익절 규칙 검증 테스트"""
        # 포지션 설정 (평균단가 10000원)
        self.risk_manager.positions["005930"] = {
            "quantity": 10,
            "avg_price": 10000,
            "current_value": 125000  # 25% 수익
        }
        
        # 익절 신호 (현재가 12500원, 25% 수익)
        signal = Signal(
            stock_code="005930",
            action="SELL",
            confidence=0.8,
            price=12500,
            quantity=10
        )
        
        market_data = MarketData(
            stock_code="005930",
            current_price=12500,
            open_price=12300,
            high_price=12600,
            low_price=12200,
            volume=1000000,
            timestamp=datetime.now()
        )
        
        # 익절은 허용되어야 함
        is_valid = self.risk_manager.validate_signal(signal, market_data)
        self.assertTrue(is_valid)
    
    def test_record_trade(self):
        """거래 기록 테스트"""
        signal = Signal(
            stock_code="005930",
            action="BUY",
            confidence=0.8,
            price=70000,
            quantity=10
        )
        
        executed_price = 70000
        executed_quantity = 10
        
        initial_trade_count = len(self.risk_manager.trade_history)
        initial_daily_amount = self.risk_manager.daily_buy_amount
        
        self.risk_manager.record_trade(signal, executed_price, executed_quantity)
        
        # 거래 이력 증가 확인
        self.assertEqual(len(self.risk_manager.trade_history), initial_trade_count + 1)
        
        # 일일 매수 금액 증가 확인
        expected_amount = initial_daily_amount + (executed_price * executed_quantity)
        self.assertEqual(self.risk_manager.daily_buy_amount, expected_amount)
        
        # 포지션 업데이트 확인
        self.assertIn("005930", self.risk_manager.positions)
        position = self.risk_manager.positions["005930"]
        self.assertEqual(position["quantity"], 10)
        self.assertEqual(position["avg_price"], 70000)
    
    def test_position_update(self):
        """포지션 업데이트 테스트"""
        # 매수 후 매도 시나리오
        buy_signal = Signal(
            stock_code="005930",
            action="BUY",
            confidence=0.8,
            price=70000,
            quantity=10
        )
        
        # 매수 실행
        self.risk_manager.record_trade(buy_signal, 70000, 10)
        
        # 포지션 확인
        position = self.risk_manager.positions["005930"]
        self.assertEqual(position["quantity"], 10)
        self.assertEqual(position["avg_price"], 70000)
        
        # 매도 신호
        sell_signal = Signal(
            stock_code="005930",
            action="SELL",
            confidence=0.7,
            price=75000,
            quantity=5
        )
        
        # 매도 실행
        self.risk_manager.record_trade(sell_signal, 75000, 5)
        
        # 포지션 업데이트 확인
        position = self.risk_manager.positions["005930"]
        self.assertEqual(position["quantity"], 5)  # 10 - 5 = 5
        self.assertEqual(position["avg_price"], 70000)  # 평균단가는 유지
    
    def test_reset_daily_limits(self):
        """일일 한도 리셋 테스트"""
        # 일일 매수 금액 설정
        self.risk_manager.daily_buy_amount = 5000000
        
        # 리셋 실행
        self.risk_manager.reset_daily_limits()
        
        # 확인
        self.assertEqual(self.risk_manager.daily_buy_amount, 0.0)
    
    def test_get_risk_status(self):
        """리스크 상태 조회 테스트"""
        status = self.risk_manager.get_risk_status()
        
        # 필수 키들이 있는지 확인
        required_keys = [
            "daily_buy_amount",
            "total_positions", 
            "active_positions",
            "total_trades",
            "rules"
        ]
        
        for key in required_keys:
            self.assertIn(key, status)

if __name__ == '__main__':
    unittest.main()
