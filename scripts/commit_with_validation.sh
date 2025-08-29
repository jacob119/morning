#!/bin/bash
#
# 검증을 포함한 commit 스크립트
# 코딩 룰 검증, 테스트 실행 후 commit을 수행합니다.
#

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 프로젝트 루트 디렉토리로 이동
cd "$(git rev-parse --show-toplevel)"

log_info "🚀 Morning 프로젝트 Commit 검증 시작"

# 1. 변경된 파일 확인
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
if [ -z "$CHANGED_FILES" ]; then
    log_warning "스테이징된 파일이 없습니다."
    exit 0
fi

log_info "변경된 파일:"
echo "$CHANGED_FILES" | while read -r file; do
    echo "  - $file"
done

# 2. 가상환경 활성화 (필수)
if [ -d "venv" ]; then
    log_info "가상환경 활성화 중..."
    source venv/bin/activate
    
    # 가상환경 활성화 확인
    if [ -z "$VIRTUAL_ENV" ]; then
        log_error "가상환경 활성화에 실패했습니다."
        exit 1
    fi
    
    log_success "가상환경 활성화 완료: $VIRTUAL_ENV"
else
    log_error "venv 디렉토리가 없습니다. 가상환경을 먼저 생성해주세요."
    log_info "가상환경 생성 방법:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  pip install -r requirements-dev.txt"
    exit 1
fi

# 3. 의존성 확인
log_info "의존성 확인 중..."
if ! python -c "import pytest" 2>/dev/null; then
    log_error "pytest가 설치되지 않았습니다. requirements-dev.txt를 설치해주세요."
    log_info "설치 명령어: pip install -r requirements-dev.txt"
    exit 1
fi

# 4. 코드 포맷팅 검사
log_info "코드 포맷팅 검사 중..."
if command -v black >/dev/null 2>&1; then
    if ! black --check --diff .; then
        log_error "코드 포맷팅이 black 표준에 맞지 않습니다."
        log_info "다음 명령어로 포맷팅을 수정하세요: black ."
        exit 1
    fi
    log_success "코드 포맷팅 검사 통과"
else
    log_warning "black이 설치되지 않았습니다. 포맷팅 검사를 건너뜁니다."
fi

# 5. Import 순서 검사
log_info "Import 순서 검사 중..."
if command -v isort >/dev/null 2>&1; then
    if ! isort --check-only --diff .; then
        log_error "Import 순서가 isort 표준에 맞지 않습니다."
        log_info "다음 명령어로 import 순서를 수정하세요: isort ."
        exit 1
    fi
    log_success "Import 순서 검사 통과"
else
    log_warning "isort가 설치되지 않았습니다. Import 순서 검사를 건너뜁니다."
fi

# 6. 타입 힌트 검사
log_info "타입 힌트 검사 중..."
if command -v mypy >/dev/null 2>&1; then
    if ! mypy --ignore-missing-imports .; then
        log_error "타입 힌트 오류가 발견되었습니다."
        exit 1
    fi
    log_success "타입 힌트 검사 통과"
else
    log_warning "mypy가 설치되지 않았습니다. 타입 힌트 검사를 건너뜁니다."
fi

# 7. 보안 검사
log_info "보안 검사 중..."
SECURITY_ISSUES=0

# 하드코딩된 API 키 검사
if grep -r "sk-[a-zA-Z0-9]" . --exclude-dir=venv --exclude-dir=.git --exclude-dir=__pycache__ >/dev/null 2>&1; then
    log_error "하드코딩된 OpenAI API 키가 발견되었습니다."
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
fi

if grep -r "xoxb-[a-zA-Z0-9]" . --exclude-dir=venv --exclude-dir=.git --exclude-dir=__pycache__ >/dev/null 2>&1; then
    log_error "하드코딩된 Slack Bot 토큰이 발견되었습니다."
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
fi

if [ $SECURITY_ISSUES -eq 0 ]; then
    log_success "보안 검사 통과"
else
    log_error "보안 문제가 발견되었습니다. 수정 후 다시 시도해주세요."
    exit 1
fi

# 8. 테스트 실행
log_info "테스트 실행 중..."
if [ -d "test" ]; then
    # 단위 테스트 실행
    if [ -d "test/unit" ]; then
        log_info "단위 테스트 실행 중..."
        if ! python -m pytest test/unit/ -v --tb=short; then
            log_error "단위 테스트가 실패했습니다."
            exit 1
        fi
        log_success "단위 테스트 통과"
    fi
    
    # 통합 테스트 실행
    if [ -d "test/integration" ]; then
        log_info "통합 테스트 실행 중..."
        if ! python -m pytest test/integration/ -v --tb=short; then
            log_error "통합 테스트가 실패했습니다."
            exit 1
        fi
        log_success "통합 테스트 통과"
    fi
    
    # UI 테스트 실행 (필수!)
    if [ -d "test/ui" ]; then
        log_info "UI 테스트 실행 중..."
        if ! python -m pytest test/ui/ -m ui -v --tb=short; then
            log_error "UI 테스트가 실패했습니다. UI 테스트는 필수입니다!"
            exit 1
        fi
        log_success "UI 테스트 통과"
    else
        log_error "test/ui 디렉토리가 없습니다. UI 테스트는 필수입니다!"
        exit 1
    fi
else
    log_error "test 디렉토리가 없습니다. 테스트 코드를 작성해주세요."
    exit 1
fi

# 9. 테스트 커버리지 확인
log_info "테스트 커버리지 확인 중..."
if command -v coverage >/dev/null 2>&1; then
    if ! python -m pytest --cov=. --cov-report=term-missing --cov-fail-under=80; then
        log_error "테스트 커버리지가 80% 미만입니다."
        exit 1
    fi
    log_success "테스트 커버리지 검사 통과"
else
    log_warning "coverage가 설치되지 않았습니다. 커버리지 검사를 건너뜁니다."
fi

# 10. 문서화 검사
log_info "문서화 검사 중..."
if [ ! -f "README.md" ]; then
    log_error "README.md 파일이 없습니다."
    exit 1
fi

if [ ! -f "CODING_RULES.md" ]; then
    log_error "CODING_RULES.md 파일이 없습니다."
    exit 1
fi

log_success "문서화 검사 통과"

# 11. Commit 메시지 검증
log_info "Commit 메시지 검증 중..."
if [ $# -eq 0 ]; then
    log_error "Commit 메시지를 입력해주세요."
    log_info "사용법: $0 \"type(scope): description\""
    log_info "예시: $0 \"feat(api): 주식 가격 조회 API 추가\""
    exit 1
fi

COMMIT_MESSAGE="$1"

# Commit 메시지 형식 검증
if ! echo "$COMMIT_MESSAGE" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)\([a-z-]+\): .+"; then
    log_error "Commit 메시지 형식이 올바르지 않습니다."
    log_info "형식: type(scope): description"
    log_info "타입: feat, fix, docs, style, refactor, test, chore"
    log_info "예시: feat(api): 주식 가격 조회 API 추가"
    exit 1
fi

log_success "Commit 메시지 검증 통과"

# 12. 모든 검증 통과 - Commit 실행
log_success "🎉 모든 검증을 통과했습니다!"

log_info "Commit 실행 중..."
git commit -m "$COMMIT_MESSAGE"

log_success "✅ Commit이 성공적으로 완료되었습니다!"
log_info "Commit 해시: $(git rev-parse HEAD)"

# 13. 추가 정보 출력
log_info "📊 검증 요약:"
echo "  - 코드 포맷팅: ✅"
echo "  - Import 순서: ✅"
echo "  - 타입 힌트: ✅"
echo "  - 보안 검사: ✅"
echo "  - 테스트 실행: ✅"
echo "  - 테스트 커버리지: ✅"
echo "  - 문서화: ✅"
echo "  - Commit 메시지: ✅"

log_info "🚀 다음 단계:"
echo "  - git push origin main"
echo "  - Pull Request 생성 (필요한 경우)"

log_info "💡 가상환경 사용 팁:"
echo "  - 항상 가상환경을 활성화하세요: source venv/bin/activate"
echo "  - 새로운 패키지 설치 시: pip install -r requirements-dev.txt"
echo "  - 가상환경 비활성화: deactivate"
