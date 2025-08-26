#!/usr/bin/env python3
"""
Slack Bot 기능 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.slack_config import PORTFOLIO_STOCKS, MESSAGE_TEMPLATES
from agent.tools import get_real_stock_price

def test_portfolio_calculation():
    """포트폴리오 계산 기능 테스트"""
    print("🧪 포트폴리오 계산 테스트 시작")
    print("=" * 50)
    
    stock_list = []
    total_investment = 0
    current_total = 0
    
    for code, stock_info in PORTFOLIO_STOCKS.items():
        try:
            print(f"📊 {stock_info['name']} ({code}) 조회 중...")
            
            # 실시간 주가 조회
            price_result = get_real_stock_price(code)
            
            # 가격 정보 파싱
            price_text = price_result.split("'")[1] if "'" in price_result else "0"
            current_price = int(price_text.replace(",", "").replace("원", ""))
            
            # 수익률 계산
            avg_price = stock_info["avg_price"]
            quantity = stock_info["quantity"]
            investment = avg_price * quantity
            current_value = current_price * quantity
            profit_loss = current_value - investment
            profit_rate = (profit_loss / investment) * 100 if investment > 0 else 0
            
            # 총액 누적
            total_investment += investment
            current_total += current_value
            
            print(f"   💰 현재가: {current_price:,}원")
            print(f"   📊 보유수량: {quantity}주")
            print(f"   💵 평균단가: {avg_price:,}원")
            print(f"   📈 수익률: {profit_rate:+.2f}%")
            print(f"   💸 평가손익: {profit_loss:+,}원")
            print()
            
        except Exception as e:
            print(f"   ❌ 조회 실패: {e}")
            print()
    
    # 전체 수익률 계산
    total_profit_loss = current_total - total_investment
    total_profit_rate = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
    
    print("📊 전체 포트폴리오 현황")
    print("=" * 50)
    print(f"💰 총 투자금액: {total_investment:,}원")
    print(f"📈 현재 총액: {current_total:,}원")
    print(f"📊 전체 수익률: {total_profit_rate:+.2f}%")
    print(f"💵 전체 평가손익: {total_profit_loss:+,}원")
    
    return True

def test_message_templates():
    """메시지 템플릿 테스트"""
    print("\n🧪 메시지 템플릿 테스트")
    print("=" * 50)
    
    # 샘플 데이터로 메시지 생성 테스트
    sample_stock = {
        "name": "삼성전자",
        "code": "005930",
        "current_price": 70300,
        "quantity": 10,
        "avg_price": 70000,
        "profit_rate": 0.43,
        "profit_loss": 3000
    }
    
    stock_item = MESSAGE_TEMPLATES["stock_item"].format(**sample_stock)
    print("📝 주식 정보 메시지:")
    print(stock_item)
    
    return True

def main():
    """메인 테스트 함수"""
    print("🚀 Slack Bot 기능 테스트 시작")
    print("=" * 60)
    
    try:
        # 포트폴리오 계산 테스트
        test_portfolio_calculation()
        
        # 메시지 템플릿 테스트
        test_message_templates()
        
        print("\n✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
