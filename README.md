# 📈 Morning

이 프로젝트는 한국투자증권(KIS; Korea Investment Securities) Open API를 Tool/Agent화하여 ChatGPT 기반 자동 주식 매매 애플리케이션입니다.

## 📌 주요 기능
- ✅ KIS Open API를 통한 실시간 주식 정보 조회 및 거래 실행
- 🧠 LLM 기반 프롬프트 시스템을 활용한 에이전트 의사결정
- 📊 포트폴리오 평가 및 리포트 생성 기능
- 🛠️ 모듈화된 구조로 확장성과 유지보수 용이
- 🔧 환경변수 기반 설정 관리
- 📝 구조화된 로깅 시스템

## 🚀 최근 개선사항
- ✅ 의존성 패키지 단순화 및 호환성 개선
- ✅ 에러 핸들링 및 로깅 시스템 강화
- ✅ 클래스 기반 분석 에이전트 구조
- ✅ 환경변수 기반 설정 관리
- ✅ 무한 루프 방지 및 안정성 향상


### 1. 실행 환경 설정

#### 1-1. Python 3.9+ (권장: 3.11.4)

#### 1-2. 가상환경 생성 및 의존성 설치

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치 (핵심 패키지만)
pip install -r requirements_simple.txt

# 또는 전체 패키지 설치 (LangChain 포함)
pip install -r requirements.txt
```

### 2. 프로젝트 구조

```plaintext
morning/
├── agent/
│   ├── analytics.py              # 🧠 주식 분석 에이전트 (StockAnalyzer)
│   ├── tools.py                  # 🛠️ 분석 도구들 (가격, 뉴스, 리포트)
│   ├── core/
│   │   └── workflows.py          # Graph Node Wrapper (레거시)
│   ├── prompts/
│   │   ├── description.py        # Tool Description
│   │   ├── system.py             # System Instructions
│   │   └── assets.py             # (TBD) Optimized Prompts
│   ├── decision.py               # (TBD) Super-Agent
│   └── evaluation.py             # (TBD) Portfolio Evaluation
├── api/
│   ├── ki/
│   │   ├── kis_auth.py           # 🔐 KIS 인증
│   │   ├── kis_domstk.py         # 📊 KIS 주식 API
│   │   └── sample/               # 📝 KIS API 샘플들
│   ├── api_client.py             # 🌐 API 클라이언트
│   ├── portfolio.py              # (TBD) 포트폴리오 관리
│   └── trader.py                 # (TBD) 거래 실행
├── config/
│   └── setting.py                # ⚙️ 환경변수 기반 설정
├── utils/
│   └── logger.py                 # 📝 로깅 시스템
├── app.py                        # 🚀 메인 실행 파일
├── .env.example                  # 📋 환경변수 템플릿
├── requirements.txt              # 📦 전체 의존성
├── requirements_simple.txt       # 📦 핵심 의존성만
└── README.md                     # 📖 프로젝트 문서
```




### 3. 환경 설정
.env.example 파일을 .env로 복사하고 실제 API 키를 입력합니다.

```bash
cp .env.example .env
```

.env 파일에서 다음 항목들을 설정하세요:
```bash
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# KIS API 설정 (한국투자증권)
KIS_APP_KEY=your_kis_app_key_here
KIS_APP_SECRET=your_kis_app_secret_here
KIS_ACCOUNT_NO=your_account_number_here
```

### 4. 실행

```bash
# 기본 실행 (삼성전자 분석)
python app.py

# 다른 종목 분석 (예: SK하이닉스)
python -c "from agent.analytics import run; run('000660')"
```

### 5. 실행 예시

```bash
$ python app.py

2025-08-24 11:48:28 - agent.analytics - INFO - Starting analysis for stock: 005930
2025-08-24 11:48:28 - agent.tools - INFO - Fetching price for stock: 005930
005930 현재 주가는 : '71,782원' 입니다.
005930 관련 최신 뉴스: '신제품 출시 발표' 입니다.
005930 관련 증권사 리포트: 'Hold, 목표가 75,000원' 입니다.
2025-08-24 11:48:28 - agent.analytics - INFO - Analysis completed for stock: 005930
```

### 6. 주요 기능 설명

#### 🧠 StockAnalyzer 클래스
- **무한 루프 방지**: 최대 10회 반복으로 안정성 보장
- **에러 핸들링**: 각 단계별 예외 처리
- **구조화된 로깅**: 상세한 실행 과정 추적
- **LLM 폴백**: API 키 없어도 더미 LLM으로 동작

#### 🛠️ 분석 도구들
- **fetch_price**: 현재 주식 가격 조회 (랜덤 변동)
- **fetch_news**: 관련 뉴스 조회 (다양한 뉴스 제공)
- **fetch_report**: 증권사 리포트 조회 (Buy/Hold/Strong Buy)

#### ⚙️ 설정 관리
- **환경변수**: `.env` 파일로 API 키 관리
- **로깅**: 파일 로테이션 및 콘솔 출력
- **의존성**: 핵심 패키지만 사용 가능

### 7. 향후 개선 계획
- 🔄 **portfolio.py**: 포트폴리오 관리 기능 구현
- 💰 **trader.py**: 실제 거래 실행 로직 개발
- 🎯 **assets.py**: 프롬프트 최적화 및 컨텍스트 관리
- 🤖 **멀티 에이전트**: 여러 종목 동시 분석
- 📈 **백테스팅**: 과거 데이터 기반 성능 분석
- 🔍 **실시간 모니터링**: 웹 대시보드 구축

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

- **프로젝트 링크**: [https://github.com/jacob119/morning](https://github.com/jacob119/morning)
- **이슈 리포트**: [GitHub Issues](https://github.com/jacob119/morning/issues)

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!
