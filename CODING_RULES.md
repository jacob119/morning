# 📋 Morning 프로젝트 코딩 룰

## 🎯 목적
이 문서는 Morning 프로젝트의 코드 품질, 일관성, 유지보수성을 보장하기 위한 코딩 룰을 정의합니다.

## 📚 목차
1. [아키텍처 원칙](#아키텍처-원칙)
2. [코드 스타일](#코드-스타일)
3. [에러 처리](#에러-처리)
4. [성능 최적화](#성능-최적화)
5. [보안](#보안)
6. [테스팅](#테스팅)
7. [UI 테스팅](#ui-테스팅)
8. [문서화](#문서화)
9. [Git 워크플로우](#git-워크플로우)
10. [Commit 전 검증](#commit-전-검증)

---

## 🏗️ 아키텍처 원칙

### 1. 의존성 주입 (Dependency Injection)
- **필수**: 모든 외부 의존성은 의존성 주입 컨테이너를 통해 관리
- **금지**: 하드코딩된 의존성 생성
- **예시**:
```python
# ❌ 잘못된 예시
class StockAnalyzer:
    def __init__(self):
        self.api_client = APIClient()  # 하드코딩

# ✅ 올바른 예시
class StockAnalyzer:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
```

### 2. 단일 책임 원칙 (Single Responsibility Principle)
- **필수**: 각 클래스/함수는 하나의 명확한 책임만 가져야 함
- **금지**: 하나의 클래스가 여러 책임을 가지는 것
- **예시**:
```python
# ❌ 잘못된 예시 - 여러 책임
class StockManager:
    def analyze_stock(self): pass
    def trade_stock(self): pass
    def save_to_database(self): pass

# ✅ 올바른 예시 - 단일 책임
class StockAnalyzer:
    def analyze_stock(self): pass

class StockTrader:
    def trade_stock(self): pass

class StockRepository:
    def save_to_database(self): pass
```

### 3. 인터페이스 분리 원칙 (Interface Segregation Principle)
- **필수**: 클라이언트는 사용하지 않는 인터페이스에 의존하지 않아야 함
- **예시**:
```python
# ✅ 올바른 예시
class DataProvider(ABC):
    @abstractmethod
    def get_data(self): pass

class DataProcessor(ABC):
    @abstractmethod
    def process_data(self): pass

class StockDataProvider(DataProvider):
    def get_data(self): pass

class StockDataProcessor(DataProcessor):
    def process_data(self): pass
```

---

## 🎨 코드 스타일

### 1. 타입 힌트 (Type Hints)
- **필수**: 모든 함수와 메서드에 타입 힌트 사용
- **예시**:
```python
# ✅ 올바른 예시
def get_stock_price(stock_code: str) -> Optional[float]:
    """주식 가격을 가져옵니다."""
    pass

def calculate_portfolio_value(stocks: List[Dict[str, Any]]) -> float:
    """포트폴리오 가치를 계산합니다."""
    pass
```

### 2. 함수 길이
- **제한**: 함수는 최대 50줄, 메서드는 최대 30줄
- **권장**: 함수는 20줄 이하, 메서드는 15줄 이하
- **예시**:
```python
# ❌ 잘못된 예시 - 너무 긴 함수
def analyze_stock_comprehensive(stock_code: str) -> Dict[str, Any]:
    # 100줄 이상의 복잡한 로직
    pass

# ✅ 올바른 예시 - 작은 함수들로 분리
def analyze_stock(stock_code: str) -> Dict[str, Any]:
    price_data = get_price_data(stock_code)
    technical_indicators = calculate_technical_indicators(price_data)
    fundamental_analysis = analyze_fundamentals(stock_code)
    return combine_analysis(price_data, technical_indicators, fundamental_analysis)
```

### 3. 변수명과 함수명
- **필수**: 명확하고 의미있는 이름 사용
- **규칙**: 
  - 변수/함수: snake_case
  - 클래스: PascalCase
  - 상수: UPPER_SNAKE_CASE
- **예시**:
```python
# ✅ 올바른 예시
class StockAnalyzer:
    def calculate_moving_average(self, prices: List[float], period: int) -> float:
        pass

    def get_stock_recommendation(self, stock_code: str) -> str:
        pass

# 상수
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
```

### 4. Import 순서
- **필수**: isort를 사용한 표준 import 순서
- **순서**:
  1. 표준 라이브러리
  2. 서드파티 라이브러리
  3. 로컬 애플리케이션
- **예시**:
```python
# ✅ 올바른 예시
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

import pandas as pd
import numpy as np
from requests import Session

from core.error_handling import ValidationError
from api.stock_api import StockAPI
```

---

## 🚨 에러 처리

### 1. 커스텀 예외 사용
- **필수**: 일반 Exception 대신 커스텀 예외 사용
- **예시**:
```python
# ❌ 잘못된 예시
try:
    price = get_stock_price(stock_code)
except Exception as e:
    print(f"Error: {e}")

# ✅ 올바른 예시
try:
    price = get_stock_price(stock_code)
except ValidationError as e:
    logger.error(f"검증 오류: {e}")
except APIError as e:
    logger.error(f"API 오류: {e}")
```

### 2. 로깅 사용
- **필수**: print() 대신 logging 모듈 사용
- **금지**: print() 사용 (테스트 코드 제외)
- **예시**:
```python
# ❌ 잘못된 예시
print("주식 가격 조회 중...")

# ✅ 올바른 예시
logger.info("주식 가격 조회 중...")
logger.error(f"API 호출 실패: {error}")
logger.debug(f"디버그 정보: {debug_data}")
```

### 3. 에러 핸들링 패턴
- **필수**: @handle_errors 데코레이터 사용
- **예시**:
```python
# ✅ 올바른 예시
@handle_errors
def get_stock_data(stock_code: str) -> Dict[str, Any]:
    """주식 데이터를 가져옵니다."""
    Validator.validate_stock_code(stock_code)
    return api_client.get_stock_data(stock_code)
```

---

## ⚡ 성능 최적화

### 1. 성능 모니터링
- **필수**: API 호출 함수에 @monitor_performance 데코레이터 적용
- **예시**:
```python
# ✅ 올바른 예시
@monitor_performance("stock_price_fetch")
def get_stock_price(stock_code: str) -> Optional[float]:
    """주식 가격을 가져옵니다."""
    pass
```

### 2. 캐싱 사용
- **권장**: 자주 호출되는 데이터는 캐시 사용
- **예시**:
```python
# ✅ 올바른 예시
@cache_result(ttl=300)  # 5분 캐시
def get_stock_info(stock_code: str) -> Dict[str, Any]:
    """주식 정보를 가져옵니다."""
    pass
```

### 3. 비동기 처리
- **권장**: I/O 작업은 비동기로 처리
- **예시**:
```python
# ✅ 올바른 예시
async def fetch_multiple_stock_prices(stock_codes: List[str]) -> Dict[str, float]:
    """여러 주식 가격을 비동기로 가져옵니다."""
    tasks = [get_stock_price_async(code) for code in stock_codes]
    results = await asyncio.gather(*tasks)
    return dict(zip(stock_codes, results))
```

---

## 🔒 보안

### 1. 민감 정보 관리
- **필수**: API 키, 토큰 등은 환경변수로 관리
- **금지**: 소스코드에 하드코딩
- **예시**:
```python
# ❌ 잘못된 예시
API_KEY = "sk-1234567890abcdef"

# ✅ 올바른 예시
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ConfigurationError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다")
```

### 2. 입력 검증
- **필수**: 모든 외부 입력에 대한 검증 수행
- **예시**:
```python
# ✅ 올바른 예시
def process_stock_order(stock_code: str, quantity: int, price: float) -> bool:
    """주식 주문을 처리합니다."""
    Validator.validate_stock_code(stock_code)
    Validator.validate_quantity(quantity)
    Validator.validate_price(price)
    # 주문 처리 로직
```

### 3. SQL Injection 방지
- **필수**: 파라미터화된 쿼리 사용
- **금지**: 문자열 포맷팅으로 SQL 쿼리 생성
- **예시**:
```python
# ❌ 잘못된 예시
query = f"SELECT * FROM stocks WHERE code = '{stock_code}'"

# ✅ 올바른 예시
query = "SELECT * FROM stocks WHERE code = %s"
cursor.execute(query, (stock_code,))
```

---

## 🧪 테스팅

### 1. 테스트 구조
- **필수**: 모든 코드 레이어에 대한 테스트 작성
- **구조**:
```
test/
├── unit/           # 단위 테스트
├── integration/    # 통합 테스트
├── e2e/           # 엔드투엔드 테스트
├── performance/   # 성능 테스트
└── conftest.py    # 공통 설정
```

### 2. 테스트 커버리지
- **필수**: 최소 80% 테스트 커버리지 유지
- **권장**: 90% 이상 테스트 커버리지
- **실행**:
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=80
```

### 3. 테스트 작성 규칙
- **필수**: 각 테스트는 독립적이어야 함
- **권장**: Given-When-Then 패턴 사용
- **예시**:
```python
# ✅ 올바른 예시
def test_get_stock_price_success():
    """주식 가격 조회 성공 테스트"""
    # Given
    stock_code = "000660"
    expected_price = 150000
    
    # When
    with patch('api.stock_api.get_price') as mock_get_price:
        mock_get_price.return_value = expected_price
        result = get_stock_price(stock_code)
    
    # Then
    assert result == expected_price
    mock_get_price.assert_called_once_with(stock_code)
```

### 4. Mock 사용
- **필수**: 외부 의존성은 Mock으로 격리
- **예시**:
```python
# ✅ 올바른 예시
@patch('api.openai_client.OpenAIClient.generate_report')
def test_generate_stock_report(mock_generate):
    """주식 리포트 생성 테스트"""
    mock_generate.return_value = "Buy, 목표가 150,000원"
    result = generate_stock_report("000660")
    assert "Buy" in result
```

---

## 📖 문서화

### 1. Docstring
- **필수**: 모든 클래스, 함수, 메서드에 docstring 작성
- **형식**: Google 스타일 사용
- **예시**:
```python
# ✅ 올바른 예시
def calculate_portfolio_return(portfolio: List[Dict[str, Any]]) -> float:
    """포트폴리오 수익률을 계산합니다.
    
    Args:
        portfolio: 포트폴리오 정보 리스트
            - stock_code: 주식 코드
            - quantity: 보유 수량
            - purchase_price: 매수 가격
            - current_price: 현재 가격
    
    Returns:
        float: 포트폴리오 수익률 (퍼센트)
    
    Raises:
        ValidationError: 포트폴리오 데이터가 유효하지 않은 경우
        ValueError: 수익률 계산 중 오류가 발생한 경우
    
    Example:
        >>> portfolio = [
        ...     {"stock_code": "000660", "quantity": 10, "purchase_price": 100000, "current_price": 110000}
        ... ]
        >>> calculate_portfolio_return(portfolio)
        10.0
    """
    pass
```

### 2. README 파일
- **필수**: 프로젝트 루트에 README.md 파일 존재
- **내용**:
  - 프로젝트 개요
  - 설치 방법
  - 사용법
  - API 문서
  - 기여 가이드

### 3. API 문서
- **필수**: 모든 공개 API에 대한 문서 작성
- **형식**: OpenAPI/Swagger 스펙 사용

---

## 🔄 Git 워크플로우

### 1. 브랜치 전략
- **main**: 프로덕션 코드
- **develop**: 개발 브랜치
- **feature/기능명**: 새로운 기능 개발
- **hotfix/버그명**: 긴급 버그 수정

### 2. Commit 메시지 규칙
- **형식**: `type(scope): description`
- **타입**:
  - feat: 새로운 기능
  - fix: 버그 수정
  - docs: 문서 수정
  - style: 코드 스타일 수정
  - refactor: 코드 리팩토링
  - test: 테스트 추가/수정
  - chore: 빌드 프로세스 수정

- **예시**:
```
feat(api): 주식 가격 조회 API 추가
fix(analytics): 목표가 계산 로직 수정
docs(readme): 설치 가이드 업데이트
test(strategy): 모멘텀 전략 테스트 추가
```

### 3. Pull Request 규칙
- **필수**: 모든 변경사항은 PR을 통해 검토
- **템플릿**:
  - 변경사항 요약
  - 테스트 결과
  - 관련 이슈 번호
  - 체크리스트

---

## ✅ Commit 전 검증

### 1. 자동 검증 스크립트
- **실행**: `python scripts/pre_commit_check.py`
- **검증 항목**:
  - 코드 포맷팅 (black, isort)
  - 타입 힌트 검사 (mypy)
  - 에러 처리 검사
  - 보안 검사
  - 테스트 실행
  - 테스트 커버리지 확인
  - 성능 검사
  - 문서화 검사

### 2. Git Hook 설정
```bash
# .git/hooks/pre-commit 파일 생성
#!/bin/sh
python scripts/pre_commit_check.py
```

### 3. 검증 실패 시 처리
- **차단**: 검증 실패 시 commit 차단
- **수정**: 오류 수정 후 재검증
- **예외**: 긴급 상황 시 `--no-verify` 플래그 사용 (최소한)

---

## 🛠️ 개발 도구

### 1. 필수 도구
- **Python**: 3.8+
- **포맷터**: black, isort
- **린터**: flake8, mypy
- **테스터**: pytest, pytest-cov
- **IDE**: VS Code, PyCharm

### 2. 설정 파일
- **pyproject.toml**: 프로젝트 설정
- **.flake8**: flake8 설정
- **.mypy.ini**: mypy 설정
- **pytest.ini**: pytest 설정

### 3. 개발 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 개발 도구 설치
pip install black isort flake8 mypy pytest pytest-cov
```

---

## 📊 품질 지표

### 1. 코드 품질
- **복잡도**: 함수당 최대 10 (McCabe 복잡도)
- **길이**: 함수당 최대 50줄
- **중복**: 최대 5% 코드 중복

### 2. 테스트 품질
- **커버리지**: 최소 80%
- **실행 시간**: 전체 테스트 5분 이내
- **안정성**: 테스트 실패율 1% 미만

### 3. 성능 지표
- **응답 시간**: API 호출 1초 이내
- **메모리 사용**: 프로세스당 512MB 이내
- **CPU 사용**: 평균 70% 이하

---

## 🔄 리뷰 프로세스

### 1. 코드 리뷰 체크리스트
- [ ] 코딩 룰 준수
- [ ] 테스트 커버리지 충족
- [ ] 성능 영향 검토
- [ ] 보안 취약점 확인
- [ ] 문서화 완료

### 2. 리뷰어 역할
- **기술적 검토**: 코드 품질, 아키텍처
- **비즈니스 검토**: 요구사항 충족
- **보안 검토**: 보안 취약점

### 3. 승인 조건
- **최소 2명**의 리뷰어 승인
- **모든 체크리스트** 완료
- **CI/CD 파이프라인** 통과

---

## 📝 변경 이력

| 버전 | 날짜 | 변경사항 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2025-01-27 | 초기 버전 작성 | AI Assistant |

---

## 📞 문의

코딩 룰에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.

**⚠️ 주의**: 이 룰을 위반하는 코드는 리뷰에서 거부될 수 있습니다.
