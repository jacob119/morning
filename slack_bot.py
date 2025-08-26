import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config.slack_config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_SIGNING_SECRET, PORTFOLIO_STOCKS, MESSAGE_TEMPLATES
from agent.tools import get_real_stock_price
import asyncio
import threading
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack 앱 초기화
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

def get_portfolio_status():
    """보유 주식 현황을 조회하고 계산합니다."""
    try:
        logger.info("🔄 포트폴리오 상태 조회 시작")
        logger.info(f"📊 총 {len(PORTFOLIO_STOCKS)}개 주식 처리 예정")
        
        stock_list = []
        total_investment = 0
        current_total = 0
        
        for i, (code, stock_info) in enumerate(PORTFOLIO_STOCKS.items(), 1):
            try:
                logger.info(f"📈 [{i}/{len(PORTFOLIO_STOCKS)}] {stock_info['name']}({code}) 처리 시작")
                
                # 실시간 주가 조회
                logger.info(f"🔍 {code} 실시간 주가 조회 중...")
                price_result = get_real_stock_price(code)
                logger.info(f"💰 {code} 주가 조회 결과: {price_result}")
                
                # 가격 정보 파싱 (예: "70,300원" -> 70300)
                price_text = price_result.split("'")[1] if "'" in price_result else "0"
                current_price = int(price_text.replace(",", "").replace("원", ""))
                logger.info(f"💵 {code} 파싱된 현재가: {current_price:,}원")
                
                # 수익률 계산
                avg_price = stock_info["avg_price"]
                quantity = stock_info["quantity"]
                investment = avg_price * quantity
                current_value = current_price * quantity
                profit_loss = current_value - investment
                profit_rate = (profit_loss / investment) * 100 if investment > 0 else 0
                
                logger.info(f"📊 {code} 계산 결과:")
                logger.info(f"   - 평균단가: {avg_price:,}원")
                logger.info(f"   - 보유수량: {quantity}주")
                logger.info(f"   - 투자금액: {investment:,}원")
                logger.info(f"   - 현재가치: {current_value:,}원")
                logger.info(f"   - 평가손익: {profit_loss:+,}원")
                logger.info(f"   - 수익률: {profit_rate:+.2f}%")
                
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
                
                logger.info(f"✅ {stock_info['name']} 정보 조회 완료")
                
            except Exception as e:
                logger.error(f"❌ 주식 {code} 조회 실패: {e}")
                logger.error(f"🔍 오류 상세: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"📚 스택 트레이스: {traceback.format_exc()}")
                # 에러 시 기본 정보만 표시
                stock_item = f"• *{stock_info['name']}* ({code}) - 조회 실패"
                stock_list.append(stock_item)
        
        # 전체 수익률 계산
        total_profit_loss = current_total - total_investment
        total_profit_rate = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
        
        logger.info("📊 전체 포트폴리오 계산 결과:")
        logger.info(f"   - 총 투자금액: {total_investment:,}원")
        logger.info(f"   - 현재 총액: {current_total:,}원")
        logger.info(f"   - 총 평가손익: {total_profit_loss:+,}원")
        logger.info(f"   - 총 수익률: {total_profit_rate:+.2f}%")
        
        # 최종 메시지 생성
        logger.info("📝 최종 메시지 생성 시작...")
        final_message = MESSAGE_TEMPLATES["portfolio_response"].format(
            stock_list="\n".join(stock_list),
            total_investment=total_investment,
            current_total=current_total,
            profit_rate=total_profit_rate,
            profit_loss=total_profit_loss
        )
        
        logger.info(f"✅ 최종 메시지 생성 완료: {len(final_message)} 문자")
        return final_message
        
    except Exception as e:
        logger.error(f"❌ 포트폴리오 조회 중 오류: {e}")
        logger.error(f"🔍 오류 상세: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"📚 스택 트레이스: {traceback.format_exc()}")
        return "❌ 포트폴리오 조회 중 오류가 발생했습니다."

@app.message("내 보유 주식")
def handle_portfolio_request(message, say):
    """'내 보유 주식' 메시지에 대한 응답"""
    try:
        logger.info(f"📱 포트폴리오 요청 받음: {message.get('user', 'Unknown')}")
        logger.info(f"🔍 메시지 상세 정보: {message}")
        logger.info(f"👤 사용자: {message.get('user', 'Unknown')}")
        logger.info(f"📝 채널: {message.get('channel', 'Unknown')}")
        logger.info(f"📄 텍스트: {message.get('text', 'Unknown')}")
        
        # 로딩 메시지 전송
        logger.info("📤 로딩 메시지 전송 시작...")
        say("📊 보유 주식 정보를 조회하고 있습니다...")
        logger.info("✅ 로딩 메시지 전송 완료")
        
        # 포트폴리오 정보 조회
        logger.info("📊 포트폴리오 정보 조회 시작...")
        portfolio_message = get_portfolio_status()
        logger.info(f"📋 포트폴리오 메시지 생성 완료: {len(portfolio_message)} 문자")
        logger.info(f"📄 포트폴리오 내용 미리보기: {portfolio_message[:200]}...")
        
        # 결과 전송
        logger.info("📤 최종 응답 전송 시작...")
        say(portfolio_message)
        logger.info("✅ 최종 응답 전송 완료")
        
        logger.info(f"🎉 포트폴리오 응답 완료: {message.get('user', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"❌ 포트폴리오 요청 처리 중 오류: {e}")
        logger.error(f"🔍 오류 상세: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"📚 스택 트레이스: {traceback.format_exc()}")
        say("❌ 요청 처리 중 오류가 발생했습니다.")

@app.message("도움말")
def handle_help_request(message, say):
    """도움말 메시지"""
    try:
        logger.info(f"📚 도움말 요청 받음: {message.get('user', 'Unknown')}")
        logger.info(f"🔍 메시지 상세 정보: {message}")
        
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
        
        logger.info("📤 도움말 메시지 전송 중...")
        say(help_message)
        logger.info("✅ 도움말 메시지 전송 완료")
        
    except Exception as e:
        logger.error(f"❌ 도움말 요청 처리 중 오류: {e}")
        logger.error(f"🔍 오류 상세: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"📚 스택 트레이스: {traceback.format_exc()}")
        say("❌ 도움말 처리 중 오류가 발생했습니다.")

@app.event("app_mention")
def handle_app_mention(event, say):
    """봇이 멘션되었을 때의 처리"""
    try:
        logger.info(f"🔔 앱 멘션 이벤트 받음: {event.get('user', 'Unknown')}")
        logger.info(f"🔍 이벤트 상세 정보: {event}")
        
        text = event.get("text", "").lower()
        logger.info(f"📄 멘션 텍스트: {text}")
        
        if "보유 주식" in text or "포트폴리오" in text:
            logger.info("📊 포트폴리오 요청으로 인식")
            handle_portfolio_request(event, say)
        elif "도움말" in text or "help" in text:
            logger.info("📚 도움말 요청으로 인식")
            handle_help_request(event, say)
        else:
            logger.info("❓ 알 수 없는 요청으로 인식")
            say("안녕하세요! `내 보유 주식` 또는 `도움말`을 입력해보세요.")
            
    except Exception as e:
        logger.error(f"❌ 앱 멘션 처리 중 오류: {e}")
        logger.error(f"🔍 오류 상세: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"📚 스택 트레이스: {traceback.format_exc()}")
        say("❌ 요청 처리 중 오류가 발생했습니다.")

def start_slack_bot():
    """슬랙 봇을 시작합니다."""
    try:
        logger.info("🚀 Slack Bot 시작 중...")
        
        # 토큰 정보 출력
        print("=" * 60)
        print("🔑 Slack Bot 토큰 정보")
        print("=" * 60)
        print(f"SLACK_BOT_TOKEN: {SLACK_BOT_TOKEN}")
        print(f"SLACK_APP_TOKEN: {SLACK_APP_TOKEN}")
        print(f"SLACK_SIGNING_SECRET: {SLACK_SIGNING_SECRET}")
        print("=" * 60)
        
        # 토큰 유효성 검사
        logger.info("🔍 토큰 유효성 검사 중...")
        if not SLACK_BOT_TOKEN:
            logger.error("❌ SLACK_BOT_TOKEN이 설정되지 않았습니다.")
            return
        if not SLACK_APP_TOKEN:
            logger.error("❌ SLACK_APP_TOKEN이 설정되지 않았습니다.")
            return
        if not SLACK_SIGNING_SECRET:
            logger.error("❌ SLACK_SIGNING_SECRET이 설정되지 않았습니다.")
            return
        
        logger.info("✅ 모든 토큰이 설정되었습니다.")
        
        # 앱 초기화 확인
        logger.info("🔧 Slack 앱 초기화 확인 중...")
        logger.info(f"앱 토큰: {app.client.token}")
        logger.info(f"앱 signing_secret: {app.signing_secret}")
        
        # Socket Mode 핸들러로 봇 시작
        logger.info("🔌 Socket Mode 핸들러 생성 중...")
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        logger.info("✅ Socket Mode 핸들러 생성 완료!")
        
        logger.info("🚀 Slack Bot 시작 완료! 이벤트 대기 중...")
        handler.start()
        
    except Exception as e:
        logger.error(f"❌ Slack Bot 시작 실패: {e}")
        logger.error(f"🔍 오류 상세: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"📚 스택 트레이스: {traceback.format_exc()}")

if __name__ == "__main__":
    start_slack_bot()
