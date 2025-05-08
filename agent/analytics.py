from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from config.setting import API_CONFIG
from pydantic import BaseModel
from agent.core.workflows import TOOLS


llm = ChatOpenAI(
    model=API_CONFIG['OPENAI']['MODEL_NAME'],
    temperature=API_CONFIG['OPENAI']['TEMPERATURE'],
    openai_api_key=API_CONFIG['OPENAI']['ACCESS_KEY']
)

class StockState(BaseModel):
    stock_code: str 
    info_log: list[str] = []
    next_action: str = ""

# Dispatcher
def decide_next_action(state: StockState) -> StockState:
    context = "\n".join(state.info_log)
    prompt = f"""
        현재 주식 코드: {state.stock_code}
        지금까지 수집한 정보:
        {context}

        다음 중 무엇을 하시겠습니까? 
        1. 뉴스 조회 (fetch_news)
        2. 리포트 조회 (fetch_report)
        3. 충분하니 종료 (end)

        'fetch_news', 'fetch_report', 'end' 중 하나만 선택해서 답변하세요
    """
    print(f"prompt : {prompt}")
    response = llm.invoke(prompt)
    print(f"GPT 결정: {response}")
    decision = response.content.strip().lower()
    if decision not in ["fetch_news", "fetch_report", "end"]:
        decision = "end"
    state.next_action = decision
    state.info_log.append(f"LLM 결정: {decision}")
    return state

def tool_wrapper(tool_func, state: StockState) -> StockState:
    result = tool_func(state.stock_code)
    state.info_log.append(result)
    return state

def end_node(state: StockState) -> StockState:
    return state


# Analytics workflow 
# TODO Refactoring
builder = StateGraph(StockState)
builder.add_node("fetch_news", lambda s : tool_wrapper(TOOLS["fetch_news"], s))
builder.add_node("fetch_report", lambda s : tool_wrapper(TOOLS["fetch_report"], s))
builder.add_node("decide", decide_next_action)
builder.add_node("end", end_node)

builder.add_conditional_edges(
    "decide", 
    lambda state: state.next_action or "end", 
    {
        "fetch_news" : "fetch_news",
        "fetch_report": "fetch_report",
        "end" : "end"
    })

builder.add_edge("fetch_news", "decide")
builder.add_edge("fetch_report", "decide")
builder.set_entry_point("decide")

graph = builder.compile()

def run(stock_code):
    initial_state = StockState(stock_code=stock_code)
    result_state = graph.invoke(initial_state)
    print(result_state)
