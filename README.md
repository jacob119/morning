# 📈 Morning

이 프로젝트는 한국투자증권(KIS; Korea Investment Securities) Open API를 Tool/Agent화하여 ChatGPT 기반 자동 주식 매매 애플리케이션입니다.
---

## 📌 주요 기능

<restapi.py>
- KIS API를 통한 실시간 주식 정보 조회
- KIS Access Token 캐싱 기능
- 주식 현재가, 전일 대비 가격/등락률, 거래량/거래대금 출력
- 5일/20일 이동 평균 돌파 기반 AI 매수 신호 감지
- 콘솔에 컬러 출력 및 로그 파일 저장

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

morning-root/
├── agent/
│   ├── core
│   │   └── workflows.py # Graph Node Wrapper
│   ├── prompts
│   │   ├── assets.py # (TBD) 
│   │   ├── description.py # Tool Description
│   │   └── system.py # System Instructions
│   ├── anaytics.py
│   ├── decision.py
│   ├── evaluation.py
│   └── tools.py
├── api/
│   ├── ki/
│   │   ├── clean.py
│   │   └── transform.py
│   ├── api_client.py
│   ├── portfolio.py
│   └── trader.py
└── config/
│   └── setting.txt
└── log/
└── utils/
│   └── logger.py
└── app.py
└── README.md
└── requirements.txt
└── restapi.py



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
