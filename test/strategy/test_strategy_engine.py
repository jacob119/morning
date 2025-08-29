"""
전략 엔진 테스트 스크립트

전략 엔진의 기능을 테스트합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from strategy import StrategyEngine, RiskManager
from strategy.strategies import (
    MomentumStrategy, 
    MeanReversionStrategy, 
    BreakoutStrategy,
    MarketData
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_sample_market_data():
    """샘플 시장 데이터를 생성합니다."""
    # 삼성전자 샘플 데이터
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # 가격 데이터 생성 (랜덤 워크)
    np.random.seed(42)
    base_price = 70000
    returns = np.random.normal(0, 0.02, len(dates))  # 일일 수익률 2% 표준편차
    prices = [base_price]
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(max(new_price, 1000))  # 최소 1000원
    
    # 거래량 데이터 생성
    volumes = np.random.randint(1000000, 10000000, len(dates))
    
    # OHLC 데이터 생성
    data = []
    for i, (date, price, volume) in enumerate(zip(dates, prices, volumes)):
        # 간단한 OHLC 생성
        open_price = price * (1 + np.random.normal(0, 0.005))
        high_price = max(open_price, price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(open_price, price) * (1 - abs(np.random.normal(0, 0.01)))
        close_price = price
        
        data.append({
            'stock_code': '005930',
            'date': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(data)

def test_strategy_engine():
    """전략 엔진을 테스트합니다."""
    print("=" * 60)
    print("🚀 전략 엔진 테스트 시작")
    print("=" * 60)
    
    # 전략 엔진 초기화
    risk_manager = RiskManager()
    engine = StrategyEngine(risk_manager)
    
    # 전략들 추가
    momentum_strategy = MomentumStrategy(
        lookback_period=10,
        momentum_threshold=0.03,
        volume_threshold=1.5
    )
    
    mean_reversion_strategy = MeanReversionStrategy(
        lookback_period=20,
        std_dev_threshold=1.5,
        reversion_strength=0.5
    )
    
    breakout_strategy = BreakoutStrategy(
        price_change_threshold=0.04,
        volume_surge_threshold=2.5,
        resistance_break_threshold=0.015,
        max_holding_days=3
    )
    
    engine.add_strategy(momentum_strategy)
    engine.add_strategy(mean_reversion_strategy)
    engine.add_strategy(breakout_strategy)
    
    print(f"✅ {len(engine.get_all_strategies())}개 전략 추가 완료")
    
    # 샘플 데이터 생성
    sample_data = create_sample_market_data()
    print(f"✅ 샘플 데이터 생성 완료: {len(sample_data)}개 데이터")
    
    # 전략 엔진 시작
    engine.start()
    
    # 신호 콜백 함수
    def signal_callback(signal):
        print(f"📡 신호 생성: {signal.stock_code} {signal.action} "
              f"(신뢰도: {signal.confidence:.2f}) - {signal.reason}")
    
    engine.add_signal_callback(signal_callback)
    
    # 샘플 데이터로 테스트
    print("\n🔍 전략 신호 테스트 중...")
    signals_generated = 0
    
    for _, row in sample_data.iterrows():
        market_data = MarketData(
            stock_code=row['stock_code'],
            current_price=row['close'],
            open_price=row['open'],
            high_price=row['high'],
            low_price=row['low'],
            volume=row['volume'],
            timestamp=row['date']
        )
        
        signals = engine.process_market_data(market_data)
        signals_generated += len(signals)
        
        # 처음 10개 신호만 출력
        if signals_generated <= 10:
            for signal in signals:
                print(f"  📊 {signal.stock_code}: {signal.action} "
                      f"@ {signal.price:,.0f}원 ({signal.quantity}주) "
                      f"- {signal.reason}")
    
    print(f"\n📈 총 {signals_generated}개 신호 생성됨")
    
    # 엔진 상태 확인
    status = engine.get_engine_status()
    print(f"\n🔧 엔진 상태:")
    print(f"  - 실행 중: {status['is_running']}")
    print(f"  - 총 전략 수: {status['total_strategies']}")
    print(f"  - 활성 전략 수: {status['active_strategies']}")
    print(f"  - 콜백 함수 수: {status['signal_callbacks']}")
    
    # 리스크 관리 상태 확인
    risk_status = risk_manager.get_risk_status()
    print(f"\n🛡️ 리스크 관리 상태:")
    print(f"  - 일일 매수 금액: {risk_status['daily_buy_amount']:,.0f}원")
    print(f"  - 총 포지션 수: {risk_status['total_positions']}")
    print(f"  - 활성 포지션 수: {risk_status['active_positions']}")
    print(f"  - 총 거래 수: {risk_status['total_trades']}")
    
    # 엔진 중지
    engine.stop()
    print("\n✅ 전략 엔진 테스트 완료")

def test_individual_strategies():
    """개별 전략들을 테스트합니다."""
    print("\n" + "=" * 60)
    print("🧪 개별 전략 테스트")
    print("=" * 60)
    
    # 샘플 데이터
    sample_data = create_sample_market_data()
    
    # 각 전략별 테스트
    strategies = [
        ("모멘텀 전략", MomentumStrategy()),
        ("Mean Reversion 전략", MeanReversionStrategy()),
        ("급등주 전략", BreakoutStrategy())
    ]
    
    for strategy_name, strategy in strategies:
        print(f"\n🔍 {strategy_name} 테스트 중...")
        
        buy_signals = 0
        sell_signals = 0
        hold_signals = 0
        
        for _, row in sample_data.iterrows():
            market_data = MarketData(
                stock_code=row['stock_code'],
                current_price=row['close'],
                open_price=row['open'],
                high_price=row['high'],
                low_price=row['low'],
                volume=row['volume'],
                timestamp=row['date']
            )
            
            signal = strategy.generate_signal(market_data)
            
            if signal.action == "BUY":
                buy_signals += 1
            elif signal.action == "SELL":
                sell_signals += 1
            else:
                hold_signals += 1
        
        total_signals = buy_signals + sell_signals + hold_signals
        print(f"  📊 매수 신호: {buy_signals} ({buy_signals/total_signals*100:.1f}%)")
        print(f"  📊 매도 신호: {sell_signals} ({sell_signals/total_signals*100:.1f}%)")
        print(f"  📊 보유 신호: {hold_signals} ({hold_signals/total_signals*100:.1f}%)")

if __name__ == "__main__":
    try:
        test_strategy_engine()
        test_individual_strategies()
        print("\n🎉 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
