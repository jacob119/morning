"""
리스크 관리 모듈

매매 신호의 리스크를 관리하고 검증합니다.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from ..strategies.base_strategy import Signal, MarketData

logger = logging.getLogger(__name__)

@dataclass
class RiskRule:
    """리스크 규칙 데이터 클래스"""
    name: str
    rule_type: str  # 'daily_limit', 'position_limit', 'stop_loss', 'take_profit'
    parameters: Dict
    is_active: bool = True

class RiskManager:
    """리스크 관리자"""
    
    def __init__(self):
        self.rules: Dict[str, RiskRule] = {}
        self.daily_buy_amount = 0.0  # 일일 매수 금액
        self.positions: Dict[str, Dict] = {}  # 보유 포지션
        self.trade_history: List[Dict] = []  # 거래 이력
        self.logger = logging.getLogger(__name__)
        
        # 기본 리스크 규칙 설정
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """기본 리스크 규칙을 설정합니다."""
        default_rules = [
            RiskRule(
                name="일일 매수 한도",
                rule_type="daily_limit",
                parameters={"max_daily_buy": 10000000}  # 1천만원
            ),
            RiskRule(
                name="최대 보유 종목 수",
                rule_type="position_limit", 
                parameters={"max_positions": 10}
            ),
            RiskRule(
                name="손절 규칙",
                rule_type="stop_loss",
                parameters={"stop_loss_pct": 0.05}  # 5%
            ),
            RiskRule(
                name="익절 규칙",
                rule_type="take_profit",
                parameters={"take_profit_pct": 0.20}  # 20%
            ),
            RiskRule(
                name="단일 종목 투자 한도",
                rule_type="single_stock_limit",
                parameters={"max_single_stock_pct": 0.30}  # 30%
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: RiskRule) -> None:
        """
        리스크 규칙을 추가합니다.
        
        Args:
            rule: 추가할 규칙
        """
        self.rules[rule.name] = rule
        self.logger.info(f"리스크 규칙 추가: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> None:
        """
        리스크 규칙을 제거합니다.
        
        Args:
            rule_name: 제거할 규칙 이름
        """
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.logger.info(f"리스크 규칙 제거: {rule_name}")
    
    def update_rule(self, rule_name: str, parameters: Dict) -> None:
        """
        리스크 규칙을 업데이트합니다.
        
        Args:
            rule_name: 업데이트할 규칙 이름
            parameters: 새로운 파라미터
        """
        if rule_name in self.rules:
            self.rules[rule_name].parameters.update(parameters)
            self.logger.info(f"리스크 규칙 업데이트: {rule_name}")
    
    def validate_signal(self, signal: Signal, market_data: MarketData) -> bool:
        """
        매매 신호의 리스크를 검증합니다.
        
        Args:
            signal: 검증할 신호
            market_data: 시장 데이터
            
        Returns:
            bool: 검증 통과 여부
        """
        if not self.rules:
            return True
        
        for rule_name, rule in self.rules.items():
            if not rule.is_active:
                continue
                
            if not self._check_rule(rule, signal, market_data):
                self.logger.warning(f"신호가 리스크 규칙 '{rule_name}'에 의해 거부됨")
                return False
        
        return True
    
    def _check_rule(self, rule: RiskRule, signal: Signal, market_data: MarketData) -> bool:
        """
        개별 규칙을 검사합니다.
        
        Args:
            rule: 검사할 규칙
            signal: 신호
            market_data: 시장 데이터
            
        Returns:
            bool: 규칙 통과 여부
        """
        if rule.rule_type == "daily_limit":
            return self._check_daily_limit(rule, signal, market_data)
        elif rule.rule_type == "position_limit":
            return self._check_position_limit(rule, signal, market_data)
        elif rule.rule_type == "stop_loss":
            return self._check_stop_loss(rule, signal, market_data)
        elif rule.rule_type == "take_profit":
            return self._check_take_profit(rule, signal, market_data)
        elif rule.rule_type == "single_stock_limit":
            return self._check_single_stock_limit(rule, signal, market_data)
        
        return True
    
    def _check_daily_limit(self, rule: RiskRule, signal: Signal, market_data: MarketData) -> bool:
        """일일 매수 한도 검사"""
        if signal.action != "BUY":
            return True
            
        max_daily_buy = rule.parameters.get("max_daily_buy", 10000000)
        buy_amount = signal.price * signal.quantity if signal.price and signal.quantity else 0
        
        if self.daily_buy_amount + buy_amount > max_daily_buy:
            self.logger.warning(f"일일 매수 한도 초과: {self.daily_buy_amount + buy_amount:,}원 > {max_daily_buy:,}원")
            return False
        
        return True
    
    def _check_position_limit(self, rule: RiskRule, signal: Signal, market_data: MarketData) -> bool:
        """최대 보유 종목 수 검사"""
        if signal.action != "BUY":
            return True
            
        max_positions = rule.parameters.get("max_positions", 10)
        current_positions = len([pos for pos in self.positions.values() if pos.get("quantity", 0) > 0])
        
        if signal.stock_code not in self.positions and current_positions >= max_positions:
            self.logger.warning(f"최대 보유 종목 수 초과: {current_positions} >= {max_positions}")
            return False
        
        return True
    
    def _check_stop_loss(self, rule: RiskRule, signal: Signal, market_data: MarketData) -> bool:
        """손절 규칙 검사"""
        if signal.stock_code not in self.positions:
            return True
            
        position = self.positions[signal.stock_code]
        avg_price = position.get("avg_price", 0)
        stop_loss_pct = rule.parameters.get("stop_loss_pct", 0.05)
        
        if avg_price > 0:
            loss_pct = (market_data.current_price - avg_price) / avg_price
            if loss_pct <= -stop_loss_pct:
                self.logger.info(f"손절 조건 만족: {signal.stock_code}, 손실률: {loss_pct:.2%}")
                return True  # 손절은 허용
        
        return True
    
    def _check_take_profit(self, rule: RiskRule, signal: Signal, market_data: MarketData) -> bool:
        """익절 규칙 검사"""
        if signal.stock_code not in self.positions:
            return True
            
        position = self.positions[signal.stock_code]
        avg_price = position.get("avg_price", 0)
        take_profit_pct = rule.parameters.get("take_profit_pct", 0.20)
        
        if avg_price > 0:
            profit_pct = (market_data.current_price - avg_price) / avg_price
            if profit_pct >= take_profit_pct:
                self.logger.info(f"익절 조건 만족: {signal.stock_code}, 수익률: {profit_pct:.2%}")
                return True  # 익절은 허용
        
        return True
    
    def _check_single_stock_limit(self, rule: RiskRule, signal: Signal, market_data: MarketData) -> bool:
        """단일 종목 투자 한도 검사"""
        if signal.action != "BUY":
            return True
            
        max_single_stock_pct = rule.parameters.get("max_single_stock_pct", 0.30)
        buy_amount = signal.price * signal.quantity if signal.price and signal.quantity else 0
        
        # 총 포트폴리오 가치 계산 (간단한 예시)
        total_portfolio_value = sum(pos.get("current_value", 0) for pos in self.positions.values())
        total_portfolio_value += buy_amount
        
        if total_portfolio_value > 0 and buy_amount / total_portfolio_value > max_single_stock_pct:
            self.logger.warning(f"단일 종목 투자 한도 초과: {buy_amount/total_portfolio_value:.2%} > {max_single_stock_pct:.2%}")
            return False
        
        return True
    
    def record_trade(self, signal: Signal, executed_price: float, executed_quantity: int) -> None:
        """
        거래를 기록합니다.
        
        Args:
            signal: 실행된 신호
            executed_price: 체결 가격
            executed_quantity: 체결 수량
        """
        trade_record = {
            "timestamp": datetime.now(),
            "stock_code": signal.stock_code,
            "action": signal.action,
            "price": executed_price,
            "quantity": executed_quantity,
            "amount": executed_price * executed_quantity
        }
        
        self.trade_history.append(trade_record)
        
        # 일일 매수 금액 업데이트
        if signal.action == "BUY":
            self.daily_buy_amount += trade_record["amount"]
        
        # 포지션 업데이트
        self._update_position(signal.stock_code, signal.action, executed_price, executed_quantity)
        
        self.logger.info(f"거래 기록: {signal.action} {signal.stock_code} {executed_quantity}주 @ {executed_price:,}원")
    
    def _update_position(self, stock_code: str, action: str, price: float, quantity: int) -> None:
        """포지션을 업데이트합니다."""
        if stock_code not in self.positions:
            self.positions[stock_code] = {
                "quantity": 0,
                "avg_price": 0,
                "current_value": 0
            }
        
        position = self.positions[stock_code]
        
        if action == "BUY":
            # 매수: 평균단가 계산
            total_quantity = position["quantity"] + quantity
            total_cost = position["quantity"] * position["avg_price"] + quantity * price
            
            if total_quantity > 0:
                position["avg_price"] = total_cost / total_quantity
            position["quantity"] = total_quantity
            
        elif action == "SELL":
            # 매도: 수량 감소
            position["quantity"] = max(0, position["quantity"] - quantity)
            if position["quantity"] == 0:
                position["avg_price"] = 0
    
    def reset_daily_limits(self) -> None:
        """일일 한도를 리셋합니다."""
        self.daily_buy_amount = 0.0
        self.logger.info("일일 매수 한도 리셋됨")
    
    def get_risk_status(self) -> Dict:
        """
        리스크 상태를 반환합니다.
        
        Returns:
            Dict: 리스크 상태 정보
        """
        return {
            "daily_buy_amount": self.daily_buy_amount,
            "total_positions": len(self.positions),
            "active_positions": len([pos for pos in self.positions.values() if pos.get("quantity", 0) > 0]),
            "total_trades": len(self.trade_history),
            "rules": {name: {"type": rule.rule_type, "active": rule.is_active, "parameters": rule.parameters}
                     for name, rule in self.rules.items()}
        }
