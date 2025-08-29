"""
기본 전략 클래스

모든 트레이딩 전략은 이 클래스를 상속받아야 합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Signal:
    """매매 신호 데이터 클래스"""
    stock_code: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0.0 ~ 1.0
    price: Optional[float] = None
    quantity: Optional[int] = None
    reason: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class MarketData:
    """시장 데이터 클래스"""
    stock_code: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: int
    timestamp: datetime
    additional_data: Dict = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}

class BaseStrategy(ABC):
    """모든 트레이딩 전략의 기본 클래스"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.is_active = True
        self.parameters = {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    @abstractmethod
    def generate_signal(self, market_data: MarketData) -> Signal:
        """
        시장 데이터를 기반으로 매매 신호를 생성합니다.
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            Signal: 매매 신호
        """
        pass
    
    @abstractmethod
    def update_parameters(self, parameters: Dict) -> None:
        """
        전략 파라미터를 업데이트합니다.
        
        Args:
            parameters: 새로운 파라미터 딕셔너리
        """
        pass
    
    def validate_signal(self, signal: Signal) -> bool:
        """
        생성된 신호의 유효성을 검증합니다.
        
        Args:
            signal: 검증할 신호
            
        Returns:
            bool: 유효성 여부
        """
        if not signal.stock_code:
            return False
        if signal.action not in ['BUY', 'SELL', 'HOLD']:
            return False
        if not (0.0 <= signal.confidence <= 1.0):
            return False
        return True
    
    def get_strategy_info(self) -> Dict:
        """
        전략 정보를 반환합니다.
        
        Returns:
            Dict: 전략 정보
        """
        return {
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'parameters': self.parameters
        }
    
    def activate(self) -> None:
        """전략을 활성화합니다."""
        self.is_active = True
        self.logger.info(f"전략 '{self.name}' 활성화됨")
    
    def deactivate(self) -> None:
        """전략을 비활성화합니다."""
        self.is_active = False
        self.logger.info(f"전략 '{self.name}' 비활성화됨")
