# 🧪 Morning 프로젝트 테스트 가이드

## 📋 개요

이 디렉토리는 Morning 프로젝트의 모든 테스트를 포함합니다. 체계적인 테스트 구조를 통해 코드 품질과 안정성을 보장합니다.

## 🏗️ 테스트 구조

```
test/
├── unit/                    # 단위 테스트
│   ├── test_analytics.py   # 분석 모듈 테스트
│   ├── test_api.py         # API 모듈 테스트
│   └── test_strategy.py    # 전략 모듈 테스트
├── integration/            # 통합 테스트
│   ├── test_slack_bot.py   # Slack Bot 통합 테스트
│   └── test_workflow.py    # 전체 워크플로우 테스트
├── e2e/                   # 엔드투엔드 테스트
├── performance/           # 성능 테스트
├── conftest.py           # 공통 설정 및 fixtures
└── README.md             # 이 파일
```

## 🚀 테스트 실행

### 기본 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 카테고리 테스트 실행
pytest test/unit/          # 단위 테스트만
pytest test/integration/   # 통합 테스트만
pytest test/ui/           # UI 테스트만 (필수!)
pytest test/e2e/          # E2E 테스트만

# 특정 파일 테스트 실행
pytest test/unit/test_analytics.py

# 특정 함수 테스트 실행
pytest test/unit/test_analytics.py::test_stock_analyzer
```

### 커버리지 확인

```bash
# 커버리지 리포트 생성
pytest --cov=. --cov-report=html

# 터미널에서 커버리지 확인
pytest --cov=. --cov-report=term-missing

# 커버리지 기준 확인 (80% 이상)
pytest --cov=. --cov-report=term-missing --cov-fail-under=80

# UI 테스트 커버리지 확인
pytest test/ui/ --cov=ui --cov-report=html
```

### 성능 테스트

```bash
# 성능 테스트 실행
pytest test/performance/ -v

# 느린 테스트만 실행
pytest -m slow
```

## 📊 테스트 마커

### 사용 가능한 마커

- `@pytest.mark.unit`: 단위 테스트
- `@pytest.mark.integration`: 통합 테스트
- `@pytest.mark.e2e`: 엔드투엔드 테스트
- `@pytest.mark.ui`: UI 테스트 (필수!)
- `@pytest.mark.performance`: 성능 테스트
- `@pytest.mark.slow`: 느린 테스트

### 마커 사용 예시

```bash
# 단위 테스트만 실행
pytest -m unit

# UI 테스트만 실행 (필수!)
pytest -m ui

# 느린 테스트 제외하고 실행
pytest -m "not slow"

# API 테스트만 실행
pytest -m api
```

## 🎨 UI 테스팅 (필수!)

### UI 테스트 중요성

**UI 테스트는 Morning 프로젝트에서 필수입니다.** 웹 사용자 인터페이스의 품질과 사용자 경험을 보장하기 위해 모든 UI 컴포넌트에 대한 테스트가 필요합니다.

### UI 테스트 범위

1. **대시보드 컴포넌트**: 메인 대시보드, 차트, 테이블
2. **입력 폼**: 주식 코드 입력, 분석 옵션 선택
3. **결과 표시**: 분석 결과, 포트폴리오 정보
4. **에러 처리**: 에러 메시지, 로딩 상태
5. **반응형 디자인**: 모바일, 태블릿, 데스크톱 레이아웃
6. **접근성**: 키보드 네비게이션, 스크린 리더 호환성

### UI 테스트 실행

```bash
# UI 테스트만 실행
pytest test/ui/ -m ui -v

# UI 테스트 커버리지 확인
pytest test/ui/ --cov=ui --cov-report=html

# 특정 UI 컴포넌트 테스트
pytest test/ui/test_dashboard.py -v
pytest test/ui/test_web_components.py -v
```

### UI 테스트 예시

```python
@pytest.mark.ui
def test_dashboard_title_display(dashboard, mock_streamlit):
    """대시보드 제목 표시 테스트"""
    dashboard.display_title()
    
    mock_streamlit['title'].assert_called_once()
    call_args = mock_streamlit['title'].call_args[0][0]
    assert "Morning" in call_args

@pytest.mark.ui
def test_stock_input_validation(dashboard, mock_streamlit):
    """주식 입력 검증 테스트"""
    mock_streamlit['text_input'].return_value = "invalid"
    mock_streamlit['button'].return_value = True
    
    result = dashboard.get_stock_input()
    
    if result is None:
        mock_streamlit['error'].assert_called()
    else:
        assert len(result) == 6  # 한국 주식 코드는 6자리
```

### UI 테스트 베스트 프랙티스

1. **Mock 활용**: 실제 Streamlit 서버 없이 테스트
2. **사용자 시나리오**: 실제 사용자 워크플로우 기반 테스트
3. **에러 케이스**: 잘못된 입력, 네트워크 오류 등 예외 상황 테스트
4. **접근성 준수**: WCAG 가이드라인 준수 확인
5. **성능 기준**: 렌더링 시간, 메모리 사용량 기준 설정

### UI 테스트 필수 요구사항

- ✅ 모든 UI 컴포넌트에 대한 테스트 코드 작성
- ✅ 사용자 입력 검증 테스트
- ✅ 에러 처리 및 메시지 표시 테스트
- ✅ 반응형 디자인 테스트
- ✅ 접근성 테스트
- ✅ 성능 테스트
- ✅ 테스트 커버리지 80% 이상 유지

## 🛠️ 테스트 작성 가이드

### 1. 테스트 파일 명명 규칙

- 파일명: `test_*.py`
- 클래스명: `Test*`
- 함수명: `test_*`

### 2. 테스트 구조 (Given-When-Then)

```python
def test_function_name():
    """테스트 설명"""
    # Given - 테스트 준비
    input_data = "test_input"
    expected_result = "expected_output"
    
    # When - 테스트 실행
    result = function_to_test(input_data)
    
    # Then - 결과 검증
    assert result == expected_result
```

### 3. Mock 사용 예시

```python
@patch('module.function_to_mock')
def test_with_mock(mock_function):
    """Mock을 사용한 테스트"""
    # Mock 설정
    mock_function.return_value = "mocked_result"
    
    # 테스트 실행
    result = function_under_test()
    
    # 검증
    assert result == "mocked_result"
    mock_function.assert_called_once()
```

### 4. Fixture 사용 예시

```python
def test_with_fixture(sample_stock_data):
    """Fixture를 사용한 테스트"""
    # sample_stock_data fixture 사용
    assert len(sample_stock_data) > 0
    assert "stock_code" in sample_stock_data[0]
```

## 🔧 테스트 설정

### conftest.py

공통 설정과 fixtures는 `conftest.py`에 정의됩니다:

- 공통 fixtures
- 테스트 데이터
- Mock 설정
- 로깅 설정

### 환경 설정

테스트 실행을 위한 환경 설정:

```bash
# 가상환경 활성화
source venv/bin/activate

# 테스트 의존성 설치
pip install -r requirements-dev.txt

# 환경변수 설정 (테스트용)
export TESTING=true
export MOCK_EXTERNAL_APIS=true
```

## 📈 테스트 커버리지 목표

### 커버리지 기준

- **전체 커버리지**: 80% 이상
- **핵심 모듈**: 90% 이상
- **API 모듈**: 95% 이상

### 커버리지 제외 항목

- 테스트 코드 자체
- 설정 파일
- 로깅 설정
- 외부 라이브러리 코드

## 🚨 테스트 실패 시 대응

### 1. 테스트 실패 원인 분석

```bash
# 상세한 오류 정보 확인
pytest -v --tb=long

# 디버그 모드로 실행
pytest --pdb

# 특정 테스트만 디버그
pytest test_file.py::test_function --pdb
```

### 2. 일반적인 문제 해결

#### Import 오류
```bash
# PYTHONPATH 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 또는 pytest 실행 시 경로 추가
PYTHONPATH=. pytest
```

#### Mock 관련 오류
```python
# 올바른 경로로 patch
@patch('module.submodule.function')  # 전체 경로 사용
def test_function(mock_func):
    pass
```

#### 환경변수 문제
```bash
# 테스트용 환경변수 설정
export TESTING=true
export MOCK_EXTERNAL_APIS=true
```

## 📝 테스트 작성 체크리스트

### 테스트 작성 시 확인사항

- [ ] 테스트 함수명이 명확한가?
- [ ] Given-When-Then 구조를 따르는가?
- [ ] 적절한 assertion을 사용하는가?
- [ ] Mock을 올바르게 사용하는가?
- [ ] Edge case를 고려했는가?
- [ ] 테스트가 독립적인가?
- [ ] 문서화가 되어 있는가?

### 테스트 실행 시 확인사항

- [ ] 모든 테스트가 통과하는가?
- [ ] 커버리지가 목표치를 달성하는가?
- [ ] 성능 테스트가 기준을 만족하는가?
- [ ] 테스트 실행 시간이 적절한가?

## 🔄 CI/CD 연동

### GitHub Actions

테스트는 GitHub Actions를 통해 자동으로 실행됩니다:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📞 문제 해결

### 자주 발생하는 문제

1. **Import 오류**: PYTHONPATH 설정 확인
2. **Mock 실패**: 올바른 경로로 patch 확인
3. **환경변수 문제**: .env 파일 또는 환경변수 설정 확인
4. **의존성 문제**: requirements-dev.txt 설치 확인

### 도움말

테스트 관련 문제가 발생하면 다음을 확인하세요:

1. 가상환경이 활성화되어 있는지
2. 모든 의존성이 설치되어 있는지
3. 환경변수가 올바르게 설정되어 있는지
4. 테스트 파일의 경로가 올바른지

---

**💡 팁**: 테스트를 작성할 때는 실제 사용 시나리오를 고려하여 작성하세요. 단순히 코드가 실행되는지 확인하는 것이 아니라, 비즈니스 로직이 올바르게 동작하는지 검증하는 것이 중요합니다.
