# 📈 Morning

이 프로젝트는 한국투자증권(KIS; Korea Investment Securities) Open API를 Tool/Agent화하여 ChatGPT 기반 자동 주식 매매 애플리케이션.
---

## 📌 주요 기능
- ✅ KIS Open API를 통한 실시간 주식 정보 조회 및 거래 실행
- 🧠 LLM 기반 프롬프트 시스템을 활용한 에이전트 의사결정
- 📊 포트폴리오 평가 및 리포트 생성 기능
- 🛠️ 모듈화된 구조로 확장성과 유지보수 용이

<app.py>
- KIS API를 통한 특정 종목 정보 조회
- KIS Access Token 캐싱 기능
- 샘플 Agent Graph 

---


### 1. 실행 환경 설정

#### 1-1. Python 3.11.4

#### 1-2. 의존성 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. Package Structure

```plaintext
morning-root/
├── agent/
│   ├── core/
│   │   └── workflows.py          # Graph Node Wrapper
│   ├── prompts/
│   │   ├── assets.py             # (TBD) Optimized Prompts/Context
│   │   ├── description.py        # Tool Description
│   │   └── system.py             # System Instructions
│   ├── anaytics.py               # Create Report for Super-Agent
│   ├── decision.py               # Super-Agent
│   ├── evaluation.py             # Evaluate action and portfolio
│   └── tools.py                  # Tools for agent
├── api/
│   ├── ki/
│   │   ├── sample/               # KIS Samples 
│   │   ├── kis_auth.py           # KIS Auth
│   │   └── kis_domstk.py         # KIS API Wrapper
│   ├── api_client.py             # API Client for Agent
│   ├── portfolio.py              # (TBD) Manage portfolio
│   └── trader.py                 # (TBD) Action for trading
├── config/
│   └── setting.py                # Configurations
├── log/
├── utils/
│   └── logger.py
├── app.py                        # Agentic Trader
├── README.md
├── requirements.txt 
└── restapi.py                    # Practice




### 2. config.py 설정
config/setting.py 파일을 열어 `AUTH_CONFIG`, `API_CONFIG`의 'your~' 값을 입력합니다.

```python
AUTH_CONFIG = {
    "APP_KEY" : os.getenv("APP_KEY", "your app key"),
    "APP_SECRET" : os.getenv("APP_SECRET", "your secret key"),
    "ACCOUNT_NO" : os.getenv("ACCOUNT_NO", "your account no"),
    "OPTION_ACCOUNT_NO" : os.getenv("OPTION_ACCOUNT_NO", "option_account_no"),
    ...
}
```

```python
API_CONFIG = {
    ...
    "OPENAI" : {
        "ACCESS_KEY" : os.getenv("ACCESS_KEY","your openai accesskey"),
        "MODEL_NAME" : "gpt-4o",
        "TEMPERATURE" : 0
    },
    ...
}
```

### 3. 실행
python app.py

### 4. 개선 예정 사항
	•	portfolio.py를 통한 포트폴리오 관리 기능 구현
	•	trader.py를 통한 거래 액션 로직 개발
	•	assets.py를 활용한 프롬프트 최적화
	•	멀티 에이전트 오케스트레이션 기능 추가
	•	백테스팅 및 성능 추적 기능 통합
