#!/usr/bin/env python3
"""
Exa MCP 통합 기능 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools import get_stock_reports, get_company_info_from_exa, calculate_target_price_based_on_company_info
from utils.logger import get_logger

logger = get_logger(__name__)

def test_exa_integration():
    """Exa MCP 통합 기능을 테스트합니다."""
    print("🧪 Exa MCP 통합 기능 테스트 시작")
    print("=" * 50)
    
    # 테스트할 주식 코드들
    test_stocks = [
        "005930",  # 삼성전자
        "000660",  # SK하이닉스
        "035420",  # 네이버
        "035720",  # 카카오
    ]
    
    for stock_code in test_stocks:
        print(f"\n📊 테스트 주식: {stock_code}")
        print("-" * 30)
        
        try:
            # 1. 회사 정보 조회 테스트
            print("1️⃣ 회사 정보 조회 테스트")
            company_info = get_company_info_from_exa(f"주식{stock_code}")
            if company_info:
                print(f"   ✅ 회사 정보: {company_info}")
            else:
                print("   ❌ 회사 정보 조회 실패")
            
            # 2. 목표가 계산 테스트
            print("2️⃣ 목표가 계산 테스트")
            current_price = 70000  # 테스트용 현재가
            if company_info:
                target_analysis = calculate_target_price_based_on_company_info(
                    current_price, company_info, f"주식{stock_code}"
                )
                print(f"   ✅ 목표가 분석: {target_analysis}")
            else:
                print("   ⚠️ 회사 정보 없음으로 인한 테스트 생략")
            
            # 3. 전체 리포트 생성 테스트
            print("3️⃣ 전체 리포트 생성 테스트")
            report = get_stock_reports(stock_code)
            print(f"   ✅ 리포트: {report}")
            
        except Exception as e:
            print(f"   ❌ 테스트 실패: {e}")
        
        print("-" * 30)
    
    print("\n🎉 Exa MCP 통합 기능 테스트 완료")

if __name__ == "__main__":
    test_exa_integration()
