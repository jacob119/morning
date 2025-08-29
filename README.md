# 🌅 Morning - AI 기반 주식 분석 및 트레이딩 시스템

## 📋 프로젝트 개요

Morning은 AI 기술을 활용한 지능형 주식 분석 및 자동 트레이딩 시스템입니다. 실시간 시장 데이터 분석, AI 기반 투자 의견 생성, 그리고 다양한 트레이딩 전략을 제공합니다.

## ⚠️ 중요: 가상환경 사용 필수

**이 프로젝트는 반드시 가상환경(venv)에서 실행해야 합니다.** 시스템 Python을 직접 사용하면 의존성 충돌이나 권한 문제가 발생할 수 있습니다.

## ✨ 주요 기능

### 🤖 AI 기반 분석
- **실시간 주식 분석**: OpenAI를 활용한 지능형 주식 리포트 생성
- **투자 의견 생성**: Buy/Sell/Hold 추천 및 목표가 설정
- **뉴스 감정 분석**: 관련 뉴스 기반 시장 심리 분석

### 📊 전략 엔진
- **모듈화된 전략**: 모멘텀, Mean Reversion, Breakout 전략
- **백테스팅**: 과거 데이터 기반 전략 성능 검증
- **리스크 관리**: 포지션 제한, 손절/익절 규칙

### 🔗 API 통합
- **KIS API**: 한국투자증권 실시간 데이터 연동
- **Slack Bot**: 포트폴리오 상태 실시간 알림
- **웹 대시보드**: Streamlit 기반 시각화

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/morning.git
cd morning

# 가상환경 생성 및 활성화 (필수!)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구 설치
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# KIS API
KIS_APP_KEY=your_kis_app_key
KIS_APP_SECRET=your_kis_app_secret
KIS_ACCESS_TOKEN=your_kis_access_token

# Slack Bot
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_APP_TOKEN=xapp-your-slack-app-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
```

### 3. 애플리케이션 실행

```bash
# 가상환경이 활성화되어 있는지 확인
which python  # venv/bin/python이 출력되어야 함

# 대시보드 실행
streamlit run dashboard.py

# Slack Bot 실행
python slack_bot.py

# 전략 엔진 테스트
python test/strategy/test_strategy_engine.py
```

## 🏗️ 프로젝트 구조

```
morning/
├── agent/                 # AI 에이전트
│   ├── analytics.py      # 주식 분석 로직
│   ├── tools.py          # 분석 도구
│   └── prompts/          # AI 프롬프트
├── api/                  # API 클라이언트
│   ├── api_client.py     # 공통 API 클라이언트
│   ├── ki/              # KIS API
│   └── trader.py        # 트레이딩 API
├── strategy/             # 전략 엔진
│   ├── engines/         # 전략 실행 엔진
│   ├── strategies/      # 트레이딩 전략
│   ├── backtest/        # 백테스팅
│   └── risk_management/ # 리스크 관리
├── core/                 # 핵심 시스템
│   ├── dependency_injection.py  # 의존성 주입
│   ├── error_handling.py        # 에러 처리
│   └── performance_monitoring.py # 성능 모니터링
├── test/                 # 테스트
│   ├── unit/            # 단위 테스트
│   ├── integration/     # 통합 테스트
│   └── conftest.py      # 테스트 설정
├── scripts/             # 유틸리티 스크립트
├── ui/                  # 사용자 인터페이스
└── config/              # 설정 파일
```

## 🧪 테스팅

### 테스트 실행

```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 전체 테스트 실행
pytest

# 단위 테스트만 실행
pytest test/unit/

# 통합 테스트만 실행
pytest test/integration/

# 커버리지 확인
pytest --cov=. --cov-report=html
```

### 테스트 구조

- **단위 테스트**: 개별 함수/클래스 테스트
- **통합 테스트**: 모듈 간 상호작용 테스트
- **성능 테스트**: 성능 지표 측정
- **E2E 테스트**: 전체 워크플로우 테스트

## 📋 코딩 룰

이 프로젝트는 엄격한 코딩 룰을 따릅니다. 자세한 내용은 [CODING_RULES.md](CODING_RULES.md)를 참조하세요.

### 주요 원칙

1. **의존성 주입**: 모든 외부 의존성은 DI 컨테이너로 관리
2. **타입 힌트**: 모든 함수에 타입 힌트 필수
3. **에러 처리**: 커스텀 예외와 일관된 에러 핸들링
4. **테스트 커버리지**: 최소 80% 테스트 커버리지 유지
5. **문서화**: 모든 공개 API에 docstring 필수

## 🔄 개발 워크플로우

### 1. 코드 작성

```bash
# 가상환경 활성화 (매번 확인!)
source venv/bin/activate

# 브랜치 생성
git checkout -b feature/new-feature

# 코드 작성 후 스테이징
git add .

# 검증을 포함한 commit
./scripts/commit_with_validation.sh "feat(api): 새로운 API 추가"
```

### 2. 자동 검증

Commit 전 자동으로 다음 검증이 실행됩니다:

- ✅ 코드 포맷팅 (black, isort)
- ✅ 타입 힌트 검사 (mypy)
- ✅ 보안 검사 (API 키 노출 등)
- ✅ 테스트 실행 (pytest)
- ✅ 테스트 커버리지 확인 (80% 이상)
- ✅ 문서화 검사

### 3. Pull Request

```bash
# 브랜치 푸시
git push origin feature/new-feature

# GitHub에서 Pull Request 생성
# 리뷰어 승인 후 main 브랜치로 머지
```

## 🛠️ 개발 도구

### 필수 도구

- **Python 3.8+**
- **Black**: 코드 포맷터
- **isort**: import 순서 정렬
- **mypy**: 타입 체커
- **pytest**: 테스트 프레임워크
- **pre-commit**: Git hook

### 개발 환경 설정

```bash
# 가상환경 활성화 (필수!)
source venv/bin/activate

# 개발 도구 설치
pip install -r requirements-dev.txt

# pre-commit hook 설정
pre-commit install

# 코드 포맷팅
black .
isort .

# 타입 체크
mypy .

# 테스트 실행
pytest
```

## 📊 성능 모니터링

### 성능 지표

- **API 응답 시간**: 1초 이내
- **메모리 사용량**: 프로세스당 512MB 이내
- **CPU 사용률**: 평균 70% 이하
- **테스트 실행 시간**: 5분 이내

### 모니터링 도구

```python
from core.performance_monitoring import monitor_performance

@monitor_performance("api_call")
def get_stock_data(stock_code: str):
    # API 호출 로직
    pass
```

## 🔒 보안

### 보안 정책

1. **민감 정보**: 모든 API 키는 환경변수로 관리
2. **입력 검증**: 모든 외부 입력에 대한 검증 수행
3. **SQL Injection 방지**: 파라미터화된 쿼리 사용
4. **접근 제어**: 적절한 권한 설정

### 보안 검사

```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 보안 취약점 검사
./scripts/pre_commit_check.py
```

## 🤝 기여하기

### 기여 가이드

1. **이슈 생성**: 버그 리포트 또는 기능 요청
2. **브랜치 생성**: `feature/기능명` 또는 `fix/버그명`
3. **코드 작성**: 코딩 룰 준수
4. **테스트 작성**: 새로운 기능에 대한 테스트 추가
5. **Pull Request**: 상세한 설명과 함께 PR 생성

### 코드 리뷰 체크리스트

- [ ] 코딩 룰 준수
- [ ] 테스트 커버리지 충족
- [ ] 성능 영향 검토
- [ ] 보안 취약점 확인
- [ ] 문서화 완료

## 📈 로드맵

### v1.1 (예정)
- [ ] 실시간 알림 시스템
- [ ] 고급 차트 분석
- [ ] 포트폴리오 최적화

### v1.2 (예정)
- [ ] 머신러닝 모델 통합
- [ ] 다중 거래소 지원
- [ ] 모바일 앱

## 📞 지원

### 문의 및 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/your-username/morning/issues)
- **문서**: [Wiki](https://github.com/your-username/morning/wiki)
- **이메일**: team@morning.com

### 커뮤니티

- **Discord**: [Morning Community](https://discord.gg/morning)
- **Slack**: [Morning Workspace](https://morning.slack.com)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- **OpenAI**: GPT 모델 제공
- **KIS**: 한국투자증권 API 제공
- **Streamlit**: 웹 대시보드 프레임워크
- **커뮤니티**: 모든 기여자들

## 💡 가상환경 사용 팁

### 일상적인 작업

```bash
# 프로젝트 시작 시
cd morning
source venv/bin/activate

# 작업 완료 후
deactivate
```

### 문제 해결

```bash
# 가상환경 재생성 (문제 발생 시)
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 자동 활성화 (선택사항)

```bash
# .bashrc 또는 .zshrc에 추가
alias morning='cd /path/to/morning && source venv/bin/activate'
```

---

**⚠️ 주의**: 이 시스템은 교육 및 연구 목적으로 제작되었습니다. 실제 투자에 사용하기 전에 충분한 테스트와 검증이 필요합니다.

**🔧 중요**: 항상 가상환경을 사용하세요. 시스템 Python을 직접 사용하면 의존성 충돌이 발생할 수 있습니다.
