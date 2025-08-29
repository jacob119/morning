"""
에러 처리 및 예외 관리 시스템

일관된 에러 처리 패턴과 커스텀 예외들을 정의합니다.
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """에러 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """에러 카테고리"""
    VALIDATION = "validation"
    API = "api"
    DATABASE = "database"
    NETWORK = "network"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"


@dataclass
class ErrorContext:
    """에러 컨텍스트"""
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class BaseApplicationError(Exception):
    """애플리케이션 기본 예외"""
    
    def __init__(self, 
                 message: str,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """예외를 딕셔너리로 변환"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class ValidationError(BaseApplicationError):
    """검증 에러"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(
            message=message,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            details={"field": field, "value": value}
        )


class APIError(BaseApplicationError):
    """API 에러"""
    
    def __init__(self, 
                 message: str, 
                 status_code: Optional[int] = None,
                 endpoint: Optional[str] = None):
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.API,
            details={"status_code": status_code, "endpoint": endpoint}
        )


class NetworkError(BaseApplicationError):
    """네트워크 에러"""
    
    def __init__(self, message: str, url: Optional[str] = None):
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.NETWORK,
            details={"url": url}
        )


class BusinessLogicError(BaseApplicationError):
    """비즈니스 로직 에러"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"operation": operation}
        )


class ConfigurationError(BaseApplicationError):
    """설정 에러"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            details={"config_key": config_key}
        )


class ErrorHandler:
    """에러 핸들러"""
    
    def __init__(self):
        self.error_callbacks: Dict[ErrorCategory, Callable] = {}
        self.severity_callbacks: Dict[ErrorSeverity, Callable] = {}
    
    def register_category_handler(self, 
                                 category: ErrorCategory, 
                                 handler: Callable[[ErrorContext], None]) -> None:
        """카테고리별 에러 핸들러 등록"""
        self.error_callbacks[category] = handler
    
    def register_severity_handler(self, 
                                 severity: ErrorSeverity, 
                                 handler: Callable[[ErrorContext], None]) -> None:
        """심각도별 에러 핸들러 등록"""
        self.severity_callbacks[severity] = handler
    
    def handle_error(self, error: BaseApplicationError, **context) -> None:
        """에러 처리"""
        error_context = ErrorContext(
            timestamp=error.timestamp,
            severity=error.severity,
            category=error.category,
            message=error.message,
            details=error.details,
            stack_trace=traceback.format_exc(),
            user_id=context.get('user_id'),
            session_id=context.get('session_id')
        )
        
        # 로깅
        self._log_error(error_context)
        
        # 카테고리별 핸들러 호출
        if error.category in self.error_callbacks:
            try:
                self.error_callbacks[error.category](error_context)
            except Exception as e:
                logger.error(f"카테고리 핸들러 실행 중 오류: {e}")
        
        # 심각도별 핸들러 호출
        if error.severity in self.severity_callbacks:
            try:
                self.severity_callbacks[error.severity](error_context)
            except Exception as e:
                logger.error(f"심각도 핸들러 실행 중 오류: {e}")
    
    def _log_error(self, error_context: ErrorContext) -> None:
        """에러 로깅"""
        log_message = f"[{error_context.severity.value.upper()}] {error_context.message}"
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra=error_context.details)
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra=error_context.details)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra=error_context.details)
        else:
            logger.info(log_message, extra=error_context.details)


# 전역 에러 핸들러
error_handler = ErrorHandler()


def handle_errors(func: Callable) -> Callable:
    """에러 처리 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseApplicationError as e:
            error_handler.handle_error(e)
            raise
        except Exception as e:
            # 일반 예외를 애플리케이션 예외로 변환
            app_error = BaseApplicationError(
                message=str(e),
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.SYSTEM,
                details={"original_error": e.__class__.__name__}
            )
            error_handler.handle_error(app_error)
            raise app_error
    return wrapper


def safe_execute(func: Callable, 
                default_return: Any = None,
                error_message: str = "함수 실행 중 오류가 발생했습니다") -> Any:
    """안전한 함수 실행"""
    try:
        return func()
    except Exception as e:
        logger.error(f"{error_message}: {e}")
        return default_return


class ErrorReporter:
    """에러 리포터"""
    
    def __init__(self):
        self.error_history: list[ErrorContext] = []
    
    def report_error(self, error_context: ErrorContext) -> None:
        """에러 보고"""
        self.error_history.append(error_context)
        
        # 에러 통계 업데이트
        self._update_error_statistics(error_context)
        
        # 심각한 에러는 즉시 알림
        if error_context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._send_alert(error_context)
    
    def _update_error_statistics(self, error_context: ErrorContext) -> None:
        """에러 통계 업데이트"""
        # 에러 통계를 업데이트하는 로직
        pass
    
    def _send_alert(self, error_context: ErrorContext) -> None:
        """알림 전송"""
        # Slack, 이메일 등으로 알림 전송
        alert_message = f"""
🚨 심각한 에러 발생
- 시간: {error_context.timestamp}
- 심각도: {error_context.severity.value}
- 카테고리: {error_context.category.value}
- 메시지: {error_context.message}
        """
        logger.critical(alert_message)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """에러 요약 반환"""
        if not self.error_history:
            return {"total_errors": 0}
        
        severity_counts = {}
        category_counts = {}
        
        for error in self.error_history:
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "latest_error": self.error_history[-1].timestamp.isoformat()
        }


# 검증 유틸리티
class Validator:
    """검증 유틸리티"""
    
    @staticmethod
    def validate_stock_code(stock_code: str) -> None:
        """주식 코드 검증"""
        if not stock_code or not isinstance(stock_code, str):
            raise ValidationError("주식 코드는 비어있을 수 없습니다", "stock_code", stock_code)
        
        if len(stock_code) != 6 or not stock_code.isdigit():
            raise ValidationError("주식 코드는 6자리 숫자여야 합니다", "stock_code", stock_code)
    
    @staticmethod
    def validate_price(price: float) -> None:
        """가격 검증"""
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValidationError("가격은 양수여야 합니다", "price", price)
    
    @staticmethod
    def validate_quantity(quantity: int) -> None:
        """수량 검증"""
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValidationError("수량은 양의 정수여야 합니다", "quantity", quantity)
    
    @staticmethod
    def validate_percentage(percentage: float, field_name: str = "percentage") -> None:
        """퍼센트 검증"""
        if not isinstance(percentage, (int, float)) or percentage < -100 or percentage > 100:
            raise ValidationError(f"{field_name}는 -100에서 100 사이의 값이어야 합니다", field_name, percentage)


# 사용 예시
if __name__ == "__main__":
    # 에러 핸들러 설정
    def api_error_handler(error_context: ErrorContext):
        print(f"API 에러 처리: {error_context.message}")
    
    def critical_error_handler(error_context: ErrorContext):
        print(f"심각한 에러 발생: {error_context.message}")
    
    error_handler.register_category_handler(ErrorCategory.API, api_error_handler)
    error_handler.register_severity_handler(ErrorSeverity.CRITICAL, critical_error_handler)
    
    # 에러 리포터
    error_reporter = ErrorReporter()
    
    # 테스트
    try:
        Validator.validate_stock_code("12345")  # 잘못된 주식 코드
    except ValidationError as e:
        error_handler.handle_error(e)
        error_reporter.report_error(ErrorContext(
            timestamp=datetime.now(),
            severity=e.severity,
            category=e.category,
            message=e.message,
            details=e.details
        ))
    
    # 에러 요약 출력
    print("에러 요약:", error_reporter.get_error_summary())
