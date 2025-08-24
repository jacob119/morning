from config.setting import API_CONFIG
from pydantic import BaseModel
from agent.tools import TOOLS
from utils.logger import get_logger

logger = get_logger(__name__)


# OpenAI API 키가 설정되지 않은 경우를 위한 더미 LLM
class DummyLLM:
    def __init__(self):
        self.call_count = 0
        self.actions = ["fetch_price", "fetch_news", "fetch_report", "end"]
    
    def invoke(self, prompt):
        """더미 LLM 응답"""
        class DummyResponse:
            def __init__(self, content):
                self.content = content
        
        # 호출 횟수에 따라 다른 응답 반환
        action_index = min(self.call_count, len(self.actions) - 1)
        action = self.actions[action_index]
        self.call_count += 1
        
        logger.info(f"DummyLLM decision: {action} (call #{self.call_count})")
        return DummyResponse(action)

def get_llm():
    """LLM 인스턴스를 반환합니다."""
    try:
        if API_CONFIG['OPENAI']['ACCESS_KEY'] == "your openai accesskey":
            logger.info("Using DummyLLM (no API key configured)")
            return DummyLLM()
        else:
            logger.info("Using OpenAI ChatGPT")
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=API_CONFIG['OPENAI']['MODEL_NAME'],
                temperature=API_CONFIG['OPENAI']['TEMPERATURE'],
                openai_api_key=API_CONFIG['OPENAI']['ACCESS_KEY']
            )
            # 간단한 테스트로 API 키 유효성 확인
            try:
                test_response = llm.invoke("Hello")
                logger.info("OpenAI API test successful")
                return llm
            except Exception as api_error:
                logger.error(f"OpenAI API test failed: {api_error}")
                logger.info("Falling back to DummyLLM due to API error")
                return DummyLLM()
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        logger.info("Falling back to DummyLLM")
        return DummyLLM()

class StockState(BaseModel):
    stock_code: str 
    stock_name: str = ""  # 주식명 추가
    info_log: list[str] = []
    next_action: str = ""

class StockAnalyzer:
    """주식 분석 에이전트"""
    
    def __init__(self):
        self.llm = get_llm()
        self.max_iterations = 10  # 무한 루프 방지
        
    def decide_next_action(self, state: StockState) -> str:
        """다음 액션을 결정합니다."""
        try:
            context = "\n".join(state.info_log[-5:])  # 최근 5개만 사용
            iteration_count = len([log for log in state.info_log if log.startswith("LLM 결정:")])
            
            # 최소 2번의 액션을 실행하도록 강제
            if iteration_count < 2:
                # 아직 2번 미만이면 가격 조회 후 뉴스나 리포트 중 하나 선택
                if iteration_count == 0:
                    return "fetch_price"
                elif iteration_count == 1:
                    # 가격 조회 후에는 뉴스나 리포트 중 선택
                    prompt = f"""
                    현재 주식 코드: {state.stock_code}
                    지금까지 수집한 정보:
                    {context}

                    가격 정보를 확인했습니다. 이제 다음 중 무엇을 더 조회하시겠습니까?
                    1. 뉴스 조회 (fetch_news) - 최신 기업 뉴스
                    2. 리포트 조회 (fetch_report) - 증권사 투자의견
                    3. 종료 (end) - 충분한 정보 수집 완료

                    'fetch_news', 'fetch_report', 'end' 중 하나만 선택해서 답변하세요.
                    """
                else:
                    # 2번째 이후에는 모든 옵션 제공
                    prompt = f"""
                    현재 주식 코드: {state.stock_code}
                    지금까지 수집한 정보:
                    {context}

                    다음 중 무엇을 하시겠습니까? 
                    1. 뉴스 조회 (fetch_news) - 최신 기업 뉴스
                    2. 리포트 조회 (fetch_report) - 증권사 투자의견
                    3. 현재 가격 재조회 (fetch_price) - 최신 가격 정보
                    4. 충분하니 종료 (end) - 분석 완료

                    'fetch_news', 'fetch_report', 'fetch_price', 'end' 중 하나만 선택해서 답변하세요.
                    """
            else:
                # 2번 이상 실행 후에는 모든 옵션 제공
                prompt = f"""
                현재 주식 코드: {state.stock_code}
                지금까지 수집한 정보:
                {context}

                다음 중 무엇을 하시겠습니까? 
                1. 뉴스 조회 (fetch_news) - 최신 기업 뉴스
                2. 리포트 조회 (fetch_report) - 증권사 투자의견
                3. 현재 가격 재조회 (fetch_price) - 최신 가격 정보
                4. 충분하니 종료 (end) - 분석 완료

                'fetch_news', 'fetch_report', 'fetch_price', 'end' 중 하나만 선택해서 답변하세요.
                """
            
            logger.debug(f"Sending prompt to LLM for stock {state.stock_code} (iteration {iteration_count})")
            response = self.llm.invoke(prompt)
            decision = response.content.strip().lower()
            
            # 유효하지 않은 응답 처리
            if decision not in ["fetch_news", "fetch_report", "fetch_price", "end"]:
                logger.warning(f"Invalid decision: {decision}, defaulting to 'fetch_news'")
                decision = "fetch_news"
                
            logger.info(f"LLM decision: {decision}")
            return decision
            
        except Exception as e:
            logger.error(f"Error in decide_next_action: {e}")
            return "fetch_news"  # 오류 시 뉴스 조회로 기본 설정
    
    def execute_action(self, action: str, stock_code: str) -> str:
        """액션을 실행합니다."""
        try:
            if action in TOOLS:
                logger.info(f"Executing action: {action} for stock: {stock_code}")
                result = TOOLS[action](stock_code)
                return result
            else:
                error_msg = f"알 수 없는 액션: {action}"
                logger.error(error_msg)
                return error_msg
        except Exception as e:
            error_msg = f"액션 실행 중 오류: {e}"
            logger.error(error_msg)
            return error_msg
    
    def analyze(self, stock_code: str) -> StockState:
        """주식을 분석합니다."""
        logger.info(f"Starting analysis for stock: {stock_code}")
        
        # 주식명 조회
        stock_name = ""
        try:
            if 'get_stock_name' in TOOLS:
                stock_name = TOOLS['get_stock_name'](stock_code)
                if stock_name:
                    logger.info(f"주식명 조회 성공: {stock_code} -> {stock_name}")
                else:
                    logger.warning(f"주식명을 찾을 수 없음: {stock_code}")
        except Exception as e:
            logger.error(f"주식명 조회 중 오류: {e}")
        
        state = StockState(stock_code=stock_code, stock_name=stock_name or "")
        iteration = 0
        
        try:
            while iteration < self.max_iterations:
                iteration += 1
                logger.debug(f"Analysis iteration {iteration}/{self.max_iterations}")
                
                # 다음 액션 결정
                action = self.decide_next_action(state)
                state.next_action = action
                state.info_log.append(f"LLM 결정: {action}")
                
                # 종료 조건
                if action == "end":
                    logger.info("Analysis completed by LLM decision")
                    break
                
                # 액션 실행
                result = self.execute_action(action, stock_code)
                state.info_log.append(result)
                
            # 최종 결과 출력
            logger.info("=== Analysis Results ===")
            for log in state.info_log:
                print(log)
                logger.info(log)
                
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            state.info_log.append(f"분석 중 오류 발생: {e}")
        
        logger.info(f"Analysis completed for stock: {stock_code}")
        return state

def run(stock_code: str) -> StockState:
    """주식 분석을 실행합니다."""
    analyzer = StockAnalyzer()
    return analyzer.analyze(stock_code)
