"""
Agent 용 KIS Tool 
"""

# 한국투자증권 API 일반 구현 로직 (4/26)
# Github : https://github.com/koreainvestment/open-trading-api.git
import api.ki.kis_auth as ka
import api.ki.kis_domstk as kb

# Tool
from langchain.tools import Tool

# Utilities
import pandas as pd
import sys

ka.auth()

# Sample Tool
def get_current_price(stock_code="071050"):
    # [국내주식] 기본시세 > 주식현재가 시세 (종목번호 6자리)
    rt_data = kb.get_inquire_price(itm_no=stock_code)
    print(rt_data.stck_prpr+ " " + rt_data.prdy_vrss)    # 현재가, 전일대비
    return f'{stock_code}의 현재가는 {rt_data.stck_prpr}원 입니다.'

price_tool = Tool.from_function(
    name="fetch_price",
    func=get_current_price,
    description="주식 종목 코드를 입력받아 현재가를 반환합니다. 예: '005930' (삼성전자)"
)