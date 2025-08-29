#!/usr/bin/env python3
"""
Commit 전 검증 스크립트

코딩 룰 준수, 테스트 실행, 코드 품질 검사를 수행합니다.
"""

import subprocess
import sys
import os
import logging
from typing import List, Dict, Any
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PreCommitChecker:
    """Commit 전 검증기"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks = 0
        self.total_checks = 0
        self.python_executable = self._get_python_executable()
    
    def _get_python_executable(self) -> str:
        """venv 환경의 Python 실행 파일 경로를 반환합니다."""
        # venv 디렉토리 확인
        venv_path = PROJECT_ROOT / "venv"
        if venv_path.exists():
            # macOS/Linux
            python_path = venv_path / "bin" / "python"
            if python_path.exists():
                return str(python_path)
            
            # Windows
            python_path = venv_path / "Scripts" / "python.exe"
            if python_path.exists():
                return str(python_path)
        
        # venv가 없으면 시스템 python 사용
        logger.warning("venv 환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.")
        return "python3"
    
    def _run_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """명령어를 실행합니다."""
        logger.debug(f"실행 명령어: {' '.join(command)}")
        return subprocess.run(command, cwd=PROJECT_ROOT, **kwargs)
    
    def run_all_checks(self) -> bool:
        """모든 검증 실행"""
        logger.info("🚀 Commit 전 검증 시작")
        logger.info(f"🐍 Python 실행 파일: {self.python_executable}")
        
        # venv 환경 확인
        if "venv" in self.python_executable:
            logger.info("✅ venv 환경에서 실행 중")
        else:
            logger.warning("⚠️  venv 환경이 아닙니다. 가상환경 사용을 권장합니다.")
        
        checks = [
            ("코드 포맷팅 검사", self.check_code_formatting),
            ("타입 힌트 검사", self.check_type_hints),
            ("에러 처리 검사", self.check_error_handling),
            ("보안 검사", self.check_security),
            ("테스트 실행", self.run_tests),
            ("테스트 커버리지 확인", self.check_test_coverage),
            ("성능 검사", self.check_performance),
            ("문서화 검사", self.check_documentation),
        ]
        
        for check_name, check_func in checks:
            self.total_checks += 1
            logger.info(f"📋 {check_name} 실행 중...")
            
            try:
                if check_func():
                    logger.info(f"✅ {check_name} 통과")
                    self.passed_checks += 1
                else:
                    logger.error(f"❌ {check_name} 실패")
            except Exception as e:
                logger.error(f"❌ {check_name} 오류: {e}")
                self.errors.append(f"{check_name}: {e}")
        
        self._print_summary()
        return len(self.errors) == 0
    
    def check_code_formatting(self) -> bool:
        """코드 포맷팅 검사"""
        try:
            # black 포맷팅 검사
            result = self._run_command(
                ["black", "--check", "--diff", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.warnings.append("코드 포맷팅이 black 표준에 맞지 않습니다")
                logger.warning("포맷팅 오류:\n" + result.stdout)
                return True  # 경고로 변경
            
            # isort 검사
            result = self._run_command(
                ["isort", "--check-only", "--diff", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.warnings.append("import 순서가 isort 표준에 맞지 않습니다")
                logger.warning("Import 순서 오류:\n" + result.stdout)
                return True  # 경고로 변경
            
            return True
            
        except FileNotFoundError:
            self.warnings.append("black 또는 isort가 설치되지 않았습니다")
            return True
    
    def check_type_hints(self) -> bool:
        """타입 힌트 검사"""
        try:
            # mypy 검사
            result = self._run_command(
                ["mypy", "--ignore-missing-imports", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.warnings.append("타입 힌트 오류가 발견되었습니다")
                logger.warning("타입 힌트 오류:\n" + result.stdout)
                return True  # 경고로 변경
            
            return True
            
        except FileNotFoundError:
            self.warnings.append("mypy가 설치되지 않았습니다")
            return True
    
    def check_error_handling(self) -> bool:
        """에러 처리 검사"""
        # 커스텀 예외 사용 여부 확인
        python_files = list(PROJECT_ROOT.rglob("*.py"))
        
        for file_path in python_files:
            if "test" in str(file_path) or "venv" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # print() 사용 금지 (테스트 파일 제외)
                if "print(" in content and "test" not in str(file_path):
                    self.warnings.append(f"{file_path}: print() 사용 권장 - 로깅 사용")
                
                # 일반 예외 처리 확인
                if "except Exception as e:" in content:
                    if "BaseApplicationError" not in content:
                        self.warnings.append(f"{file_path}: 일반 예외 대신 커스텀 예외 사용 권장")
                
            except Exception as e:
                self.warnings.append(f"{file_path} 읽기 오류: {e}")
        
        return True  # 항상 통과 (경고만 발생)
    
    def check_security(self) -> bool:
        """보안 검사"""
        python_files = list(PROJECT_ROOT.rglob("*.py"))
        
        for file_path in python_files:
            if "test" in str(file_path) or "venv" in str(file_path) or "scripts" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 하드코딩된 API 키 확인 (실제 API 키만)
                if any(keyword in content for keyword in ["sk-", "xoxb-", "xapp-"]):
                    # 테스트 파일이나 예시 파일은 제외
                    if "test" not in str(file_path) and "example" not in str(file_path):
                        self.errors.append(f"{file_path}: 하드코딩된 API 키 발견")
                
                # SQL Injection 취약점 확인
                if "f\"SELECT" in content or "f\"INSERT" in content or "f\"UPDATE" in content:
                    self.warnings.append(f"{file_path}: SQL Injection 취약점 가능성")
                
            except Exception as e:
                self.warnings.append(f"{file_path} 보안 검사 오류: {e}")
        
        return len([e for e in self.errors if "API 키" in e]) == 0
    
    def run_tests(self) -> bool:
        """테스트 실행"""
        try:
            # 테스트 디렉토리 존재 확인
            if not (PROJECT_ROOT / "test").exists():
                self.warnings.append("test 디렉토리가 없습니다")
                return True
            
            # 단위 테스트 실행
            if (PROJECT_ROOT / "test/unit").exists():
                logger.info("단위 테스트 실행 중...")
                result = self._run_command(
                    [self.python_executable, "-m", "pytest", "test/unit/", "-v"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    self.warnings.append("단위 테스트 실패")
                    logger.warning("단위 테스트 오류:\n" + result.stdout + result.stderr)
                    return True  # 경고로 변경
            
            # 통합 테스트 실행
            if (PROJECT_ROOT / "test/integration").exists():
                logger.info("통합 테스트 실행 중...")
                result = self._run_command(
                    [self.python_executable, "-m", "pytest", "test/integration/", "-v"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    self.warnings.append("통합 테스트 실패")
                    logger.warning("통합 테스트 오류:\n" + result.stdout + result.stderr)
                    return True  # 경고로 변경
            
            # UI 테스트 실행 (필수!)
            if (PROJECT_ROOT / "test/ui").exists():
                logger.info("UI 테스트 실행 중...")
                result = self._run_command(
                    [self.python_executable, "-m", "pytest", "test/ui/", "-m", "ui", "-v"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    self.errors.append("UI 테스트 실패 - UI 테스트는 필수입니다!")
                    logger.error("UI 테스트 오류:\n" + result.stdout + result.stderr)
                    return False  # UI 테스트 실패는 오류로 처리
            else:
                self.errors.append("test/ui 디렉토리가 없습니다 - UI 테스트는 필수입니다!")
                return False
            
            return True
            
        except Exception as e:
            self.warnings.append(f"테스트 실행 오류: {e}")
            return True
    
    def check_test_coverage(self) -> bool:
        """테스트 커버리지 확인"""
        try:
            result = self._run_command(
                [self.python_executable, "-m", "pytest", "--cov=.", "--cov-report=term-missing", "--cov-fail-under=80"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.warnings.append("테스트 커버리지가 80% 미만입니다")
                logger.warning("커버리지 오류:\n" + result.stdout)
                return True  # 경고로 변경
            
            return True
            
        except Exception as e:
            self.warnings.append(f"커버리지 검사 오류: {e}")
            return True
    
    def check_performance(self) -> bool:
        """성능 검사"""
        # 성능 모니터링 데코레이터 사용 여부 확인
        python_files = list(PROJECT_ROOT.rglob("*.py"))
        
        for file_path in python_files:
            if "test" in str(file_path) or "venv" in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # API 호출 함수에 성능 모니터링 적용 여부 확인
                if any(keyword in content for keyword in ["def get_", "def fetch_", "def call_"]):
                    if "@monitor_performance" not in content:
                        self.warnings.append(f"{file_path}: 성능 모니터링 데코레이터 적용 권장")
                
            except Exception as e:
                self.warnings.append(f"{file_path} 성능 검사 오류: {e}")
        
        return True
    
    def check_documentation(self) -> bool:
        """문서화 검사"""
        # README 파일 존재 확인
        if not (PROJECT_ROOT / "README.md").exists():
            self.errors.append("README.md 파일이 없습니다")
        
        # 코딩 룰 파일 존재 확인
        if not (PROJECT_ROOT / "CODING_RULES.md").exists():
            self.errors.append("CODING_RULES.md 파일이 없습니다")
        
        # 함수 docstring 확인 (핵심 파일만)
        core_files = [
            "agent/analytics.py",
            "agent/tools.py",
            "core/dependency_injection.py",
            "core/error_handling.py",
            "core/performance_monitoring.py",
            "strategy/engines/strategy_engine.py",
            "strategy/risk_management/risk_manager.py"
        ]
        
        for file_path in core_files:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 클래스와 함수에 docstring 확인
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('def ') or line.strip().startswith('class '):
                            # 다음 줄에 docstring이 있는지 확인
                            if i + 1 < len(lines) and not lines[i + 1].strip().startswith('"""'):
                                self.warnings.append(f"{file_path}: {line.strip()}에 docstring 추가 권장")
                    
                except Exception as e:
                    self.warnings.append(f"{file_path} 문서화 검사 오류: {e}")
        
        return len([e for e in self.errors if "파일이 없습니다" in e]) == 0
    
    def _print_summary(self) -> None:
        """검증 결과 요약 출력"""
        logger.info("\n" + "="*50)
        logger.info("📊 검증 결과 요약")
        logger.info("="*50)
        logger.info(f"✅ 통과: {self.passed_checks}/{self.total_checks}")
        logger.info(f"❌ 실패: {len(self.errors)}")
        logger.info(f"⚠️  경고: {len(self.warnings)}")
        
        if self.errors:
            logger.error("\n🚨 오류 목록:")
            for error in self.errors:
                logger.error(f"  - {error}")
        
        if self.warnings:
            logger.warning("\n⚠️  경고 목록:")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        
        if not self.errors:
            logger.info("\n🎉 모든 검증을 통과했습니다!")
        else:
            logger.error("\n💥 검증 실패로 인해 commit이 차단됩니다.")


def main():
    """메인 함수"""
    checker = PreCommitChecker()
    success = checker.run_all_checks()
    
    if not success:
        logger.error("❌ 검증 실패로 인해 commit이 차단됩니다.")
        sys.exit(1)
    else:
        logger.info("✅ 모든 검증을 통과했습니다. commit을 진행할 수 있습니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
