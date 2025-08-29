"""
전략 엔진

여러 전략을 관리하고 실행하는 메인 엔진입니다.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..strategies.base_strategy import BaseStrategy, Signal, MarketData
from ..risk_management.risk_manager import RiskManager

logger = logging.getLogger(__name__)

class StrategyEngine:
    """전략 엔진 - 여러 전략을 관리하고 실행"""
    
    def __init__(self, risk_manager: Optional[RiskManager] = None):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.risk_manager = risk_manager or RiskManager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.signal_callbacks: List[Callable[[Signal], None]] = []
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
    def add_strategy(self, strategy: BaseStrategy) -> None:
        """
        전략을 엔진에 추가합니다.
        
        Args:
            strategy: 추가할 전략
        """
        if strategy.name in self.strategies:
            self.logger.warning(f"전략 '{strategy.name}'이 이미 존재합니다. 덮어씁니다.")
        
        self.strategies[strategy.name] = strategy
        self.logger.info(f"전략 '{strategy.name}' 추가됨")
    
    def remove_strategy(self, strategy_name: str) -> None:
        """
        전략을 엔진에서 제거합니다.
        
        Args:
            strategy_name: 제거할 전략 이름
        """
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            self.logger.info(f"전략 '{strategy_name}' 제거됨")
        else:
            self.logger.warning(f"전략 '{strategy_name}'이 존재하지 않습니다.")
    
    def get_strategy(self, strategy_name: str) -> Optional[BaseStrategy]:
        """
        특정 전략을 가져옵니다.
        
        Args:
            strategy_name: 전략 이름
            
        Returns:
            BaseStrategy: 전략 객체 또는 None
        """
        return self.strategies.get(strategy_name)
    
    def get_all_strategies(self) -> Dict[str, BaseStrategy]:
        """
        모든 전략을 반환합니다.
        
        Returns:
            Dict[str, BaseStrategy]: 전략 딕셔너리
        """
        return self.strategies.copy()
    
    def get_active_strategies(self) -> Dict[str, BaseStrategy]:
        """
        활성화된 전략만 반환합니다.
        
        Returns:
            Dict[str, BaseStrategy]: 활성화된 전략 딕셔너리
        """
        return {name: strategy for name, strategy in self.strategies.items() 
                if strategy.is_active}
    
    def add_signal_callback(self, callback: Callable[[Signal], None]) -> None:
        """
        신호 콜백 함수를 추가합니다.
        
        Args:
            callback: 신호가 생성될 때 호출될 함수
        """
        self.signal_callbacks.append(callback)
        self.logger.info(f"신호 콜백 추가됨: {callback.__name__}")
    
    def remove_signal_callback(self, callback: Callable[[Signal], None]) -> None:
        """
        신호 콜백 함수를 제거합니다.
        
        Args:
            callback: 제거할 콜백 함수
        """
        if callback in self.signal_callbacks:
            self.signal_callbacks.remove(callback)
            self.logger.info(f"신호 콜백 제거됨: {callback.__name__}")
    
    def process_market_data(self, market_data: MarketData) -> List[Signal]:
        """
        시장 데이터를 모든 활성 전략에 전달하여 신호를 생성합니다.
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            List[Signal]: 생성된 신호 리스트
        """
        signals = []
        active_strategies = self.get_active_strategies()
        
        if not active_strategies:
            self.logger.warning("활성화된 전략이 없습니다.")
            return signals
        
        for strategy_name, strategy in active_strategies.items():
            try:
                signal = strategy.generate_signal(market_data)
                
                if signal and strategy.validate_signal(signal):
                    # price가 설정되지 않은 경우 현재 가격으로 설정
                    if signal.price is None:
                        signal.price = market_data.current_price
                    
                    # quantity가 설정되지 않은 경우 기본값 설정
                    if signal.quantity is None:
                        signal.quantity = 1
                    
                    # 리스크 관리 검증
                    if self.risk_manager.validate_signal(signal, market_data):
                        signals.append(signal)
                        self.logger.info(f"전략 '{strategy_name}' 신호 생성: {signal.action} {signal.stock_code}")
                        
                        # 콜백 함수들 호출
                        for callback in self.signal_callbacks:
                            try:
                                callback(signal)
                            except Exception as e:
                                self.logger.error(f"콜백 실행 중 오류: {e}")
                    else:
                        self.logger.warning(f"전략 '{strategy_name}' 신호가 리스크 관리 규칙에 의해 거부됨")
                else:
                    self.logger.warning(f"전략 '{strategy_name}'에서 유효하지 않은 신호 생성됨")
                    
            except Exception as e:
                self.logger.error(f"전략 '{strategy_name}' 실행 중 오류: {e}")
        
        return signals
    
    async def process_market_data_async(self, market_data: MarketData) -> List[Signal]:
        """
        시장 데이터를 비동기로 처리합니다.
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            List[Signal]: 생성된 신호 리스트
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.process_market_data, market_data)
    
    def start(self) -> None:
        """전략 엔진을 시작합니다."""
        self.is_running = True
        self.logger.info("전략 엔진 시작됨")
    
    def stop(self) -> None:
        """전략 엔진을 중지합니다."""
        self.is_running = False
        self.executor.shutdown(wait=True)
        self.logger.info("전략 엔진 중지됨")
    
    def get_engine_status(self) -> Dict:
        """
        엔진 상태를 반환합니다.
        
        Returns:
            Dict: 엔진 상태 정보
        """
        return {
            'is_running': self.is_running,
            'total_strategies': len(self.strategies),
            'active_strategies': len(self.get_active_strategies()),
            'signal_callbacks': len(self.signal_callbacks),
            'strategies': {name: strategy.get_strategy_info() 
                          for name, strategy in self.strategies.items()}
        }
