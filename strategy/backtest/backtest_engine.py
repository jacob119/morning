"""
백테스트 엔진

과거 데이터를 사용하여 전략의 성과를 검증합니다.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

from ..strategies.base_strategy import BaseStrategy, Signal, MarketData
from ..engines.strategy_engine import StrategyEngine
from ..risk_management.risk_manager import RiskManager

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """백테스트 결과 데이터 클래스"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    profitable_trades: int
    trade_history: List[Dict]
    daily_returns: List[float]
    equity_curve: List[float]

class BacktestEngine:
    """백테스트 엔진"""
    
    def __init__(self, initial_capital: float = 10000000):
        self.initial_capital = initial_capital
        self.strategy_engine = StrategyEngine()
        self.risk_manager = RiskManager()
        self.logger = logging.getLogger(__name__)
        
    def add_strategy(self, strategy: BaseStrategy) -> None:
        """
        백테스트에 전략을 추가합니다.
        
        Args:
            strategy: 추가할 전략
        """
        self.strategy_engine.add_strategy(strategy)
        self.logger.info(f"백테스트에 전략 추가: {strategy.name}")
    
    def run_backtest(self, 
                    historical_data: pd.DataFrame,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> BacktestResult:
        """
        백테스트를 실행합니다.
        
        Args:
            historical_data: 과거 데이터 (stock_code, date, open, high, low, close, volume 컬럼 필요)
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            BacktestResult: 백테스트 결과
        """
        # 데이터 필터링
        if start_date:
            historical_data = historical_data[historical_data['date'] >= start_date]
        if end_date:
            historical_data = historical_data[historical_data['date'] <= end_date]
        
        if historical_data.empty:
            raise ValueError("백테스트할 데이터가 없습니다.")
        
        # 백테스트 초기화
        current_capital = self.initial_capital
        positions = {}
        trade_history = []
        daily_returns = []
        equity_curve = [current_capital]
        
        # 날짜별로 데이터 정렬
        historical_data = historical_data.sort_values('date')
        
        # 각 날짜별로 전략 실행
        for date, day_data in historical_data.groupby('date'):
            signals = []
            
            # 각 종목에 대해 전략 실행
            for _, row in day_data.iterrows():
                market_data = MarketData(
                    stock_code=row['stock_code'],
                    current_price=row['close'],
                    open_price=row['open'],
                    high_price=row['high'],
                    low_price=row['low'],
                    volume=row['volume'],
                    timestamp=date
                )
                
                # 전략에서 신호 생성
                day_signals = self.strategy_engine.process_market_data(market_data)
                signals.extend(day_signals)
            
            # 신호 실행
            current_capital, positions, trades = self._execute_signals(
                signals, current_capital, positions, date
            )
            trade_history.extend(trades)
            
            # 포지션 가치 계산
            portfolio_value = self._calculate_portfolio_value(positions, day_data)
            total_value = current_capital + portfolio_value
            
            # 일일 수익률 계산
            if len(equity_curve) > 0:
                daily_return = (total_value - equity_curve[-1]) / equity_curve[-1]
                daily_returns.append(daily_return)
            
            equity_curve.append(total_value)
        
        # 결과 계산
        result = self._calculate_backtest_results(
            equity_curve, daily_returns, trade_history, start_date, end_date
        )
        
        return result
    
    def _execute_signals(self, 
                        signals: List[Signal], 
                        current_capital: float, 
                        positions: Dict,
                        date: datetime) -> Tuple[float, Dict, List[Dict]]:
        """
        신호를 실행합니다.
        
        Args:
            signals: 실행할 신호들
            current_capital: 현재 자본금
            positions: 현재 포지션
            date: 실행 날짜
            
        Returns:
            Tuple[float, Dict, List[Dict]]: (새로운 자본금, 새로운 포지션, 거래 이력)
        """
        trades = []
        
        for signal in signals:
            if signal.action == "BUY":
                # 매수 실행
                if signal.price and signal.quantity:
                    cost = signal.price * signal.quantity
                    if cost <= current_capital:
                        current_capital -= cost
                        
                        # 포지션 업데이트
                        if signal.stock_code not in positions:
                            positions[signal.stock_code] = {
                                'quantity': 0,
                                'avg_price': 0
                            }
                        
                        pos = positions[signal.stock_code]
                        total_quantity = pos['quantity'] + signal.quantity
                        total_cost = pos['quantity'] * pos['avg_price'] + cost
                        
                        if total_quantity > 0:
                            pos['avg_price'] = total_cost / total_quantity
                        pos['quantity'] = total_quantity
                        
                        # 거래 기록
                        trades.append({
                            'date': date,
                            'stock_code': signal.stock_code,
                            'action': 'BUY',
                            'price': signal.price,
                            'quantity': signal.quantity,
                            'amount': cost
                        })
                        
                        self.logger.info(f"매수 실행: {signal.stock_code} {signal.quantity}주 @ {signal.price:,}원")
            
            elif signal.action == "SELL":
                # 매도 실행
                if signal.stock_code in positions and signal.quantity:
                    pos = positions[signal.stock_code]
                    sell_quantity = min(signal.quantity, pos['quantity'])
                    
                    if sell_quantity > 0 and signal.price:
                        revenue = signal.price * sell_quantity
                        current_capital += revenue
                        
                        # 포지션 업데이트
                        pos['quantity'] -= sell_quantity
                        if pos['quantity'] == 0:
                            pos['avg_price'] = 0
                        
                        # 거래 기록
                        trades.append({
                            'date': date,
                            'stock_code': signal.stock_code,
                            'action': 'SELL',
                            'price': signal.price,
                            'quantity': sell_quantity,
                            'amount': revenue
                        })
                        
                        self.logger.info(f"매도 실행: {signal.stock_code} {sell_quantity}주 @ {signal.price:,}원")
        
        return current_capital, positions, trades
    
    def _calculate_portfolio_value(self, positions: Dict, day_data: pd.DataFrame) -> float:
        """
        포트폴리오 가치를 계산합니다.
        
        Args:
            positions: 현재 포지션
            day_data: 해당 날짜의 시장 데이터
            
        Returns:
            float: 포트폴리오 가치
        """
        portfolio_value = 0.0
        
        for stock_code, position in positions.items():
            if position['quantity'] > 0:
                # 해당 종목의 현재가 찾기
                stock_data = day_data[day_data['stock_code'] == stock_code]
                if not stock_data.empty:
                    current_price = stock_data.iloc[0]['close']
                    portfolio_value += position['quantity'] * current_price
        
        return portfolio_value
    
    def _calculate_backtest_results(self,
                                  equity_curve: List[float],
                                  daily_returns: List[float],
                                  trade_history: List[Dict],
                                  start_date: Optional[datetime],
                                  end_date: Optional[datetime]) -> BacktestResult:
        """
        백테스트 결과를 계산합니다.
        
        Args:
            equity_curve: 자본금 곡선
            daily_returns: 일일 수익률
            trade_history: 거래 이력
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            BacktestResult: 백테스트 결과
        """
        initial_capital = equity_curve[0]
        final_capital = equity_curve[-1]
        total_return = (final_capital - initial_capital) / initial_capital
        
        # 연간 수익률 계산
        if start_date and end_date:
            days = (end_date - start_date).days
            annual_return = ((final_capital / initial_capital) ** (365 / days)) - 1
        else:
            annual_return = total_return
        
        # 최대 낙폭 계산
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        # 샤프 비율 계산
        if daily_returns:
            returns_array = np.array(daily_returns)
            sharpe_ratio = np.mean(returns_array) / np.std(returns_array) * np.sqrt(252) if np.std(returns_array) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 승률 계산
        if trade_history:
            profitable_trades = len([t for t in trade_history if t['action'] == 'SELL' and t['amount'] > 0])
            total_trades = len([t for t in trade_history if t['action'] == 'SELL'])
            win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        else:
            profitable_trades = 0
            total_trades = 0
            win_rate = 0
        
        return BacktestResult(
            strategy_name="백테스트",
            start_date=start_date or datetime.now(),
            end_date=end_date or datetime.now(),
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            total_trades=total_trades,
            profitable_trades=profitable_trades,
            trade_history=trade_history,
            daily_returns=daily_returns,
            equity_curve=equity_curve
        )
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """
        최대 낙폭을 계산합니다.
        
        Args:
            equity_curve: 자본금 곡선
            
        Returns:
            float: 최대 낙폭
        """
        peak = equity_curve[0]
        max_drawdown = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def compare_strategies(self, 
                          historical_data: pd.DataFrame,
                          strategies: List[BaseStrategy],
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict[str, BacktestResult]:
        """
        여러 전략을 비교합니다.
        
        Args:
            historical_data: 과거 데이터
            strategies: 비교할 전략들
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            Dict[str, BacktestResult]: 전략별 백테스트 결과
        """
        results = {}
        
        for strategy in strategies:
            # 전략 엔진 초기화
            self.strategy_engine = StrategyEngine()
            self.strategy_engine.add_strategy(strategy)
            
            # 백테스트 실행
            result = self.run_backtest(historical_data, start_date, end_date)
            result.strategy_name = strategy.name
            results[strategy.name] = result
            
            self.logger.info(f"전략 '{strategy.name}' 백테스트 완료: 수익률 {result.total_return:.2%}")
        
        return results
