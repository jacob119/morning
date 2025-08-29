"""
AI 채팅 모듈

포트폴리오 분석과 투자 전망에 대한 AI 채팅 기능을 제공합니다.
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

# OpenAI API
import openai
from config.setting import API_CONFIG

# OpenAI API 키 설정
OPENAI_API_KEY = API_CONFIG["OPENAI"]["ACCESS_KEY"]

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """채팅 메시지 데이터 클래스"""
    role: str  # 'user' 또는 'assistant'
    content: str
    timestamp: datetime
    message_id: str

@dataclass
class ChatSession:
    """채팅 세션 데이터 클래스"""
    session_id: str
    messages: List[ChatMessage]
    portfolio_context: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

class AIChatBot:
    """AI 채팅봇"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.sessions: Dict[str, ChatSession] = {}
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        return """당신은 전문적인 주식 투자 분석가입니다. 

주요 역할:
1. 포트폴리오 분석 및 전망 제공
2. 투자 전략 제안
3. 리스크 관리 조언
4. 시장 동향 해석

답변 스타일:
- 전문적이면서도 이해하기 쉽게 설명
- 구체적인 데이터와 근거 제시
- 투자자 관점에서 실용적인 조언
- 리스크와 기회를 균형있게 분석

주의사항:
- 투자 조언이 아닌 정보 제공 목적
- 개인 투자 결정은 투자자 본인의 책임
- 시장 변동성과 불확실성 언급
- 분산 투자와 리스크 관리 강조"""

    def create_session(self, portfolio_data: Dict[str, Any]) -> str:
        """새로운 채팅 세션 생성"""
        import uuid
        session_id = str(uuid.uuid4())
        
        session = ChatSession(
            session_id=session_id,
            messages=[],
            portfolio_context=portfolio_data,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """세션 가져오기"""
        return self.sessions.get(session_id)
    
    async def send_message(self, session_id: str, user_message: str) -> str:
        """사용자 메시지 전송 및 AI 응답"""
        try:
            session = self.get_session(session_id)
            if not session:
                return "세션을 찾을 수 없습니다. 새로운 세션을 시작해주세요."
            
            # 사용자 메시지 추가
            user_msg = ChatMessage(
                role="user",
                content=user_message,
                timestamp=datetime.now(),
                message_id=f"user_{len(session.messages)}"
            )
            session.messages.append(user_msg)
            
            # AI 응답 생성
            ai_response = await self._generate_ai_response(session, user_message)
            
            # AI 응답 추가
            ai_msg = ChatMessage(
                role="assistant",
                content=ai_response,
                timestamp=datetime.now(),
                message_id=f"assistant_{len(session.messages)}"
            )
            session.messages.append(ai_msg)
            
            # 세션 업데이트
            session.last_updated = datetime.now()
            
            return ai_response
            
        except Exception as e:
            logger.error(f"메시지 전송 실패: {e}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
    async def _generate_ai_response(self, session: ChatSession, user_message: str) -> str:
        """AI 응답 생성"""
        try:
            # 컨텍스트 정보 생성
            context = self._create_context(session.portfolio_context)
            
            # OpenAI API 키 확인 - 더 엄격한 검증
            api_key = self.openai_client.api_key
            logger.info(f"🔑 OpenAI API 키 상태 확인:")
            logger.info(f"   - API 키 존재: {bool(api_key)}")
            logger.info(f"   - API 키 길이: {len(api_key) if api_key else 0}")
            logger.info(f"   - API 키 시작: {api_key[:10] + '...' if api_key and len(api_key) > 10 else api_key}")
            
            if (not api_key or 
                api_key == "your openai accesskey" or 
                "your" in api_key.lower()):
                logger.info("❌ OpenAI API 키가 유효하지 않아 오프라인 모드로 전환합니다.")
                return self._generate_offline_response(user_message, context)
            
            logger.info("✅ OpenAI API 키가 유효합니다. 온라인 모드로 진행합니다.")
            
            # 메시지 히스토리 생성
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # 이전 대화 히스토리 추가 (최근 10개 메시지)
            recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
            for msg in recent_messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # OpenAI API 호출 로깅
            logger.info(f"🤖 OpenAI API 호출 시작:")
            logger.info(f"   - 모델: gpt-4o")
            logger.info(f"   - 최대 토큰: 1000")
            logger.info(f"   - 온도: 0.7")
            logger.info(f"   - 메시지 수: {len(messages)}")
            logger.info(f"   - 사용자 메시지: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
            
            # OpenAI API 호출
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            logger.info(f"✅ OpenAI API 응답 성공 (온라인 모드):")
            logger.info(f"   - 응답 길이: {len(response.choices[0].message.content)}")
            logger.info(f"   - 사용된 토큰: {response.usage.total_tokens if response.usage else 'N/A'}")
            logger.info(f"   - 응답 내용: {response.choices[0].message.content[:200]}{'...' if len(response.choices[0].message.content) > 200 else ''}")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI 응답 생성 실패: {e}")
            # 오류 발생 시 오프라인 모드로 전환
            try:
                context = self._create_context(session.portfolio_context)
                return self._generate_offline_response(user_message, context)
            except Exception as offline_error:
                logger.error(f"오프라인 응답 생성도 실패: {offline_error}")
                return "죄송합니다. 현재 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요."
    
    def _generate_offline_response(self, user_message: str, context: str) -> str:
        """오프라인 모드 응답 생성"""
        try:
            logger.info(f"🔄 오프라인 모드 응답 생성 시작")
            logger.info(f"   - 사용자 메시지: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
            logger.info(f"   - 컨텍스트: {context[:200]}{'...' if len(context) > 200 else ''}")
            
            # 간단한 키워드 기반 응답
            user_message_lower = user_message.lower()
            
            if any(keyword in user_message_lower for keyword in ['포트폴리오', '분석', '현재']):
                response = f"""📊 포트폴리오 분석 결과

현재 포트폴리오 상황:
{context}

💡 주요 인사이트:
• 포트폴리오 상태를 정기적으로 모니터링하세요
• 분산 투자를 통해 리스크를 관리하세요
• 시장 변동성에 대비한 여유 자금을 확보하세요

⚠️ 주의사항:
• 이는 참고용 정보이며, 실제 투자 결정은 신중히 하세요
• 전문 투자 상담을 받으시는 것을 권장합니다"""

            elif any(keyword in user_message_lower for keyword in ['전망', '미래', '앞으로']):
                response = f"""🔮 시장 전망 분석

현재 포트폴리오 기반 전망:
{context}

📈 단기 전망 (1-3개월):
• 시장 변동성 증가 예상
• 포트폴리오 리밸런싱 고려

📊 중기 전망 (3-6개월):
• 경제 회복세 지속 전망
• 분산 투자 전략 유지 권장

💡 투자 전략:
• 정기적인 포트폴리오 점검
• 리스크 관리 강화
• 장기 투자 관점 유지"""

            elif any(keyword in user_message_lower for keyword in ['리스크', '위험', '손실']):
                response = f"""⚠️ 리스크 분석

현재 포트폴리오 리스크 요인:
{context}

🚨 주요 리스크:
• 시장 변동성 리스크
• 개별 종목 리스크
• 환율 변동 리스크

🛡️ 리스크 관리 방안:
• 분산 투자 확대
• 정기적인 포트폴리오 점검
• 손절매 기준 설정
• 여유 자금 확보

📋 권장사항:
• 리스크 대비 수익률 균형 유지
• 전문가 상담 고려"""

            elif any(keyword in user_message_lower for keyword in ['전략', '투자', '방법']):
                response = f"""💡 투자 전략 제안

현재 상황 분석:
{context}

🎯 추천 전략:
• 정기적인 포트폴리오 리밸런싱
• 분산 투자로 리스크 분산
• 장기 투자 관점 유지
• 정기적인 시장 모니터링

📊 실행 방안:
• 월 1회 포트폴리오 점검
• 분기별 리밸런싱 검토
• 연 1회 전체 전략 재검토

⚠️ 주의사항:
• 개인 상황에 맞는 전략 수립 필요
• 전문 투자 상담 권장"""

            else:
                response = f"""안녕하세요! 포트폴리오 상담사입니다.

현재 포트폴리오 상황:
{context}

💬 도움이 필요한 내용을 말씀해주세요:
• 포트폴리오 분석
• 시장 전망
• 리스크 분석
• 투자 전략

⚠️ 참고사항:
• 이는 참고용 정보입니다
• 실제 투자 결정은 신중히 하세요
• OpenAI API 키 설정 시 더 정확한 분석을 제공합니다"""
                
            logger.info(f"✅ 오프라인 모드 응답 생성 완료:")
            logger.info(f"   - 응답 길이: {len(response)}")
            logger.info(f"   - 응답 내용: {response[:200]}{'...' if len(response) > 200 else ''}")
            
            return response

        except Exception as e:
            logger.error(f"오프라인 응답 생성 실패: {e}")
            return "죄송합니다. 현재 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요."
    
    def _create_context(self, portfolio_data: Dict[str, Any]) -> str:
        """포트폴리오 컨텍스트 생성"""
        try:
            context_parts = []
            
            # 보유 종목 정보
            if 'stocks' in portfolio_data:
                # 선택된 종목만 표시
                selected_stock_name = portfolio_data.get('selected_stock_name', '')
                if selected_stock_name:
                    # 선택된 종목만 찾아서 표시
                    selected_stock = None
                    for stock in portfolio_data['stocks']:
                        if stock.get('name') == selected_stock_name:
                            selected_stock = stock
                            break
                    
                    if selected_stock:
                        stock_info = f"{selected_stock.get('name', 'Unknown')}({selected_stock.get('code', 'Unknown')})"
                        
                        # 실시간 가격 정보 우선 사용
                        real_time_price = portfolio_data.get('selected_stock_price')
                        logger.info(f"🔍 실시간 가격 정보 확인:")
                        logger.info(f"   - 실시간 가격: {real_time_price}")
                        logger.info(f"   - 포트폴리오 가격: {selected_stock.get('current_price', 'N/A')}")
                        
                        if real_time_price:
                            stock_info += f" - 현재가: {int(real_time_price):,}원 (실시간)"
                            logger.info(f"✅ 실시간 가격 사용: {int(real_time_price):,}원")
                        elif 'current_price' in selected_stock:
                            current_price = selected_stock['current_price']
                            if isinstance(current_price, (int, float)):
                                stock_info += f" - 현재가: {current_price:,}원"
                            else:
                                stock_info += f" - 현재가: {current_price}원"
                        
                        if 'profit_rate' in selected_stock:
                            profit_rate = selected_stock['profit_rate']
                            if isinstance(profit_rate, (int, float)):
                                stock_info += f" - 수익률: {profit_rate:.2f}%"
                            else:
                                stock_info += f" - 수익률: {profit_rate}%"
                        
                        context_parts.append(f"분석 종목: {stock_info}")
                    else:
                        # 포트폴리오에 없으면 실시간 가격 조회 시도
                        try:
                            from agent.tools import get_real_stock_price
                            stock_code = portfolio_data.get('selected_stock_code')
                            if stock_code:
                                logger.info(f"🔍 실시간 가격 조회 시도: {selected_stock_name}({stock_code})")
                                price_info = get_real_stock_price(stock_code)
                                if price_info:
                                    import re
                                    price_match = re.search(r"'([0-9,]+)원'", price_info)
                                    if price_match:
                                        real_time_price = price_match.group(1).replace(',', '')
                                        stock_info = f"{selected_stock_name}({stock_code}) - 현재가: {int(real_time_price):,}원 (실시간)"
                                        context_parts.append(f"분석 종목: {stock_info}")
                                        logger.info(f"✅ 실시간 가격 조회 성공: {int(real_time_price):,}원")
                                    else:
                                        context_parts.append(f"분석 종목: {selected_stock_name} (가격 정보 추출 실패)")
                                else:
                                    context_parts.append(f"분석 종목: {selected_stock_name} (가격 조회 실패)")
                            else:
                                context_parts.append(f"분석 종목: {selected_stock_name} (종목 코드 없음)")
                        except Exception as e:
                            logger.error(f"❌ 실시간 가격 조회 중 오류: {e}")
                            context_parts.append(f"분석 종목: {selected_stock_name} (오류 발생)")
                else:
                    # 선택된 종목이 없으면 첫 번째 종목만 표시
                    if portfolio_data['stocks']:
                        stock = portfolio_data['stocks'][0]
                        stock_info = f"{stock.get('name', 'Unknown')}({stock.get('code', 'Unknown')})"
                        
                        # 실시간 가격 정보 우선 사용
                        real_time_price = portfolio_data.get('selected_stock_price')
                        if real_time_price:
                            stock_info += f" - 현재가: {int(real_time_price):,}원 (실시간)"
                        elif 'current_price' in stock:
                            current_price = stock['current_price']
                            if isinstance(current_price, (int, float)):
                                stock_info += f" - 현재가: {current_price:,}원"
                            else:
                                stock_info += f" - 현재가: {current_price}원"
                        
                        if 'profit_rate' in stock:
                            profit_rate = stock['profit_rate']
                            if isinstance(profit_rate, (int, float)):
                                stock_info += f" - 수익률: {profit_rate:.2f}%"
                            else:
                                stock_info += f" - 수익률: {profit_rate}%"
                        
                        context_parts.append(f"분석 종목: {stock_info}")
            
            # 실시간 가격 정보 추가
            selected_stock_price = portfolio_data.get('selected_stock_price')
            selected_stock_name = portfolio_data.get('selected_stock_name')
            if selected_stock_price and selected_stock_name:
                context_parts.append(f"실시간 가격 정보: {selected_stock_name} 현재가 {int(selected_stock_price):,}원")
                logger.info(f"📊 컨텍스트에 실시간 가격 추가: {selected_stock_name} {int(selected_stock_price):,}원")
            
            # 포트폴리오 성과
            if 'total_value' in portfolio_data:
                total_value = portfolio_data['total_value']
                if isinstance(total_value, (int, float)):
                    context_parts.append(f"총 평가금액: {total_value:,}원")
                else:
                    context_parts.append(f"총 평가금액: {total_value}원")
            
            if 'total_profit' in portfolio_data:
                total_profit = portfolio_data['total_profit']
                if isinstance(total_profit, (int, float)):
                    context_parts.append(f"총 평가손익: {total_profit:,}원")
                else:
                    context_parts.append(f"총 평가손익: {total_profit}원")
            
            if 'profit_rate' in portfolio_data:
                profit_rate = portfolio_data['profit_rate']
                if isinstance(profit_rate, (int, float)):
                    context_parts.append(f"총 수익률: {profit_rate:.2f}%")
                else:
                    context_parts.append(f"총 수익률: {profit_rate}%")
            
            # 뉴스 분석 결과 (선택된 종목만 표시)
            if 'news_analysis' in portfolio_data and portfolio_data['news_analysis']:
                # 현재 선택된 종목의 뉴스 분석만 표시
                selected_stock_news = None
                for analysis in portfolio_data['news_analysis']:
                    if analysis.get('stock_name') == portfolio_data.get('selected_stock_name'):
                        selected_stock_news = analysis
                        break
                
                if selected_stock_news:
                    context_parts.append(f"뉴스 분석: {selected_stock_news.get('stock_name', 'Unknown')}: {selected_stock_news.get('overall_sentiment', 'neutral')} ({selected_stock_news.get('news_count', 0)}건)")
                else:
                    context_parts.append("뉴스 분석: 해당 종목의 뉴스 데이터가 없습니다.")
            
            return " | ".join(context_parts)
            
        except Exception as e:
            logger.error(f"컨텍스트 생성 실패: {e}")
            return "포트폴리오 정보를 불러올 수 없습니다."
    
    async def get_portfolio_insights(self, session_id: str) -> str:
        """포트폴리오 인사이트 생성"""
        try:
            session = self.get_session(session_id)
            if not session:
                return "세션을 찾을 수 없습니다."
            
            # 포트폴리오 분석 요청
            analysis_request = """
포트폴리오를 분석하여 다음 사항에 대해 인사이트를 제공해주세요:

1. 현재 포트폴리오 상태 평가
2. 주요 투자 기회와 리스크 요인
3. 단기/중기 전망
4. 포트폴리오 최적화 제안
5. 주의해야 할 시장 동향

구체적이고 실용적인 조언을 부탁드립니다.
"""
            
            return await self.send_message(session_id, analysis_request)
            
        except Exception as e:
            logger.error(f"포트폴리오 인사이트 생성 실패: {e}")
            return "포트폴리오 분석을 수행할 수 없습니다."
    
    async def get_market_outlook(self, session_id: str) -> str:
        """시장 전망 분석"""
        try:
            session = self.get_session(session_id)
            if not session:
                return "세션을 찾을 수 없습니다."
            
            # 시장 전망 요청
            outlook_request = """
현재 시장 상황과 포트폴리오를 고려하여 다음에 대해 분석해주세요:

1. 전반적인 시장 동향
2. 포트폴리오 종목들의 전망
3. 시장 변동성과 리스크 요인
4. 투자 전략 조정 필요성
5. 향후 3-6개월 전망

투자자 관점에서 실용적인 분석을 부탁드립니다.
"""
            
            return await self.send_message(session_id, outlook_request)
            
        except Exception as e:
            logger.error(f"시장 전망 분석 실패: {e}")
            return "시장 전망 분석을 수행할 수 없습니다."
    
    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """채팅 히스토리 가져오기"""
        session = self.get_session(session_id)
        if session:
            return session.messages
        return []
    
    def clear_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 정보 가져오기"""
        session = self.get_session(session_id)
        if session:
            return {
                'session_id': session.session_id,
                'message_count': len(session.messages),
                'created_at': session.created_at,
                'last_updated': session.last_updated,
                'portfolio_summary': self._create_context(session.portfolio_context)
            }
        return None

# 싱글톤 인스턴스
ai_chat_bot = AIChatBot()
