import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config.slack_config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, PORTFOLIO_STOCKS, MESSAGE_TEMPLATES
from agent.tools import get_real_stock_price
import asyncio
import threading
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack 앱 초기화
app = App(token=SLACK_BOT_TOKEN)

def get_portfolio_status():
    """보유 주식 현황을 조회하고 계산합니다."""
    try:
        stock_list = []
        total_investment = 0
        current_total = 0
        
        for code, stock_info in PORTFOLIO_STOCKS.items():
            try:
                # 실시간 주가 조회
                price_result = get_real_stock_price(code)
                
                # 가격 정보 파싱 (예: "70,300원" -> 70300)
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
                
                # 주식 정보 포맷팅
                stock_item = MESSAGE_TEMPLATES["stock_item"].format(
                    name=stock_info["name"],
                    code=code,
                    current_price=current_price,
                    quantity=quantity,
                    avg_price=avg_price,
                    profit_rate=profit_rate,
                    profit_loss=profit_loss
                )
                stock_list.append(stock_item)
                
                logger.info(f"주식 {stock_info['name']} 정보 조회 완료")
                
            except Exception as e:
                logger.error(f"주식 {code} 조회 실패: {e}")
                # 에러 시 기본 정보만 표시
                stock_item = f"• *{stock_info['name']}* ({code}) - 조회 실패"
                stock_list.append(stock_item)
        
        # 전체 수익률 계산
        total_profit_loss = current_total - total_investment
        total_profit_rate = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
        
        # 최종 메시지 생성
        final_message = MESSAGE_TEMPLATES["portfolio_response"].format(
            stock_list="\n".join(stock_list),
            total_investment=total_investment,
            current_total=current_total,
            profit_rate=total_profit_rate,
            profit_loss=total_profit_loss
        )
        
        return final_message
        
    except Exception as e:
        logger.error(f"포트폴리오 조회 중 오류: {e}")
        return "❌ 포트폴리오 조회 중 오류가 발생했습니다."

@app.message("내 보유 주식")
def handle_portfolio_request(message, say):
    """'내 보유 주식' 메시지에 대한 응답"""
    try:
        logger.info(f"포트폴리오 요청 받음: {message['user']}")
        
        # 로딩 메시지 전송
        say("📊 보유 주식 정보를 조회하고 있습니다...")
        
        # 포트폴리오 정보 조회
        portfolio_message = get_portfolio_status()
        
        # 결과 전송
        say(portfolio_message)
        
        logger.info(f"포트폴리오 응답 완료: {message['user']}")
        
    except Exception as e:
        logger.error(f"포트폴리오 요청 처리 중 오류: {e}")
        say("❌ 요청 처리 중 오류가 발생했습니다.")

@app.message("도움말")
def handle_help_request(message, say):
    """도움말 메시지"""
    help_message = """
🤖 *Morning Stock Bot 도움말*

사용 가능한 명령어:
• `내 보유 주식` - 현재 보유 주식 현황 조회
• `도움말` - 이 도움말 메시지 표시

📊 제공 정보:
- 실시간 주가
- 보유 수량 및 평균단가
- 수익률 및 평가손익
- 전체 포트폴리오 현황
    """
    say(help_message)

@app.event("app_mention")
def handle_app_mention(event, say):
    """봇이 멘션되었을 때의 처리"""
    text = event.get("text", "").lower()
    
    if "보유 주식" in text or "포트폴리오" in text:
        handle_portfolio_request(event, say)
    elif "도움말" in text or "help" in text:
        handle_help_request(event, say)
    else:
        say("안녕하세요! `내 보유 주식` 또는 `도움말`을 입력해보세요.")

def start_slack_bot():
    """슬랙 봇을 시작합니다."""
    try:
        logger.info("🚀 Slack Bot 시작 중...")
        
        if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
            logger.error("❌ Slack 토큰이 설정되지 않았습니다.")
            logger.info("💡 .env 파일에 SLACK_BOT_TOKEN과 SLACK_APP_TOKEN을 설정해주세요.")
            return
        
        # Socket Mode 핸들러로 봇 시작
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        logger.info("✅ Slack Bot 시작 완료!")
        handler.start()
        
    except Exception as e:
        logger.error(f"❌ Slack Bot 시작 실패: {e}")

if __name__ == "__main__":
    start_slack_bot()
