import sys
from agent.analytics import run

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
    else:
        stock_code = "005930"  # 기본값
    
    print(f"🔍 주식 분석 시작: {stock_code}")
    run(stock_code=stock_code)

if __name__ == "__main__":
    main()
