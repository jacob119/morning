#!/usr/bin/env python3
"""
주식 도구 기본 기능 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools import get_stock_name, get_real_stock_price, get_stock_news
from utils.logger import get_logger

logger = get_logger(__name__)

def test_stock_name():
    """주식명 조회 기능을 테스트합니다."""
    print("🧪 주식명 조회 테스트")
    print("-" * 30)
    
    test_codes = ["005930", "000660", "035420", "035720"]
    
    for code in test_codes:
        try:
            name = get_stock_name(code)
            print(f"   {code}: {name}")
        except Exception as e:
            print(f"   {code}: ❌ 오류 - {e}")
    
    print("-" * 30)

def test_stock_price():
    """주식 가격 조회 기능을 테스트합니다."""
    print("🧪 주식 가격 조회 테스트")
    print("-" * 30)
    
    test_codes = ["005930", "000660"]
    
    for code in test_codes:
        try:
            price_info = get_real_stock_price(code)
            print(f"   {code}: {price_info}")
        except Exception as e:
            print(f"   {code}: ❌ 오류 - {e}")
    
    print("-" * 30)

def test_stock_news():
    """주식 뉴스 조회 기능을 테스트합니다."""
    print("🧪 주식 뉴스 조회 테스트")
    print("-" * 30)
    
    test_codes = ["005930", "000660"]
    
    for code in test_codes:
        try:
            news = get_stock_news(code)
            print(f"   {code}: {news}")
        except Exception as e:
            print(f"   {code}: ❌ 오류 - {e}")
    
    print("-" * 30)

def run_all_tests():
    """모든 기본 기능 테스트를 실행합니다."""
    print("🚀 주식 도구 기본 기능 테스트 시작")
    print("=" * 50)
    
    test_stock_name()
    test_stock_price()
    test_stock_news()
    
    print("\n🎉 모든 기본 기능 테스트 완료")

if __name__ == "__main__":
    run_all_tests()



