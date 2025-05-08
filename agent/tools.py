from langchain.tools import Tool
from agent.core.workflows import tool
import requests

# 증권사 리포트 조회 Tool
@tool(name='fetch_report')
def get_stock_reports(stock_code):
    # Dummy Code : X-API 
    return f"{stock_code} 관련 증권사 리포트: 'Buy, 목표가 80,000원' 입니다."

# 뉴스 조회 Tool
@tool(name='fetch_news')
def get_stock_news(stock_code):
    # Dummy Code : Crawling
    return f"{stock_code} 관련 최신 뉴스: '시장 점유율 확대 중' 입니다."