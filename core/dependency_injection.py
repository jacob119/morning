"""
의존성 주입 컨테이너

IoC (Inversion of Control) 패턴을 구현하여 의존성을 관리합니다.
"""

from typing import Dict, Any, Type, Optional, Callable
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class ServiceProvider(ABC):
    """서비스 제공자 인터페이스"""
    
    @abstractmethod
    def get_service(self, service_type: Type) -> Any:
        """서비스를 가져옵니다."""
        pass


class DependencyContainer:
    """의존성 주입 컨테이너"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, service_type: Type, implementation: Any) -> None:
        """싱글톤 서비스를 등록합니다."""
        self._services[service_type] = implementation
        logger.info(f"싱글톤 서비스 등록: {service_type.__name__}")
    
    def register_factory(self, service_type: Type, factory: Callable) -> None:
        """팩토리 서비스를 등록합니다."""
        self._factories[service_type] = factory
        logger.info(f"팩토리 서비스 등록: {service_type.__name__}")
    
    def register_transient(self, service_type: Type, implementation_type: Type) -> None:
        """트랜지언트 서비스를 등록합니다."""
        self._factories[service_type] = lambda: implementation_type()
        logger.info(f"트랜지언트 서비스 등록: {service_type.__name__}")
    
    def resolve(self, service_type: Type) -> Any:
        """서비스를 해결합니다."""
        # 싱글톤 인스턴스 확인
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # 싱글톤 서비스 확인
        if service_type in self._services:
            instance = self._services[service_type]
            self._singletons[service_type] = instance
            return instance
        
        # 팩토리 서비스 확인
        if service_type in self._factories:
            instance = self._factories[service_type]()
            return instance
        
        # 직접 인스턴스화 시도
        try:
            instance = service_type()
            return instance
        except Exception as e:
            raise ValueError(f"서비스를 해결할 수 없습니다: {service_type.__name__} - {e}")
    
    def resolve_with_dependencies(self, service_type: Type, **kwargs) -> Any:
        """의존성을 포함하여 서비스를 해결합니다."""
        # 생성자 의존성 주입
        constructor_params = {}
        
        # 타입 힌트를 기반으로 의존성 주입
        import inspect
        sig = inspect.signature(service_type.__init__)
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                try:
                    constructor_params[param_name] = self.resolve(param.annotation)
                except ValueError:
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(f"필수 의존성을 해결할 수 없습니다: {param.annotation}")
        
        # 추가 파라미터 병합
        constructor_params.update(kwargs)
        
        return service_type(**constructor_params)


class ServiceLocator:
    """서비스 로케이터 패턴"""
    
    _container: Optional[DependencyContainer] = None
    
    @classmethod
    def set_container(cls, container: DependencyContainer) -> None:
        """컨테이너를 설정합니다."""
        cls._container = container
    
    @classmethod
    def get_service(cls, service_type: Type) -> Any:
        """서비스를 가져옵니다."""
        if cls._container is None:
            raise RuntimeError("컨테이너가 설정되지 않았습니다.")
        return cls._container.resolve(service_type)


# 데코레이터를 사용한 의존성 주입
def inject(*dependencies: Type) -> Callable:
    """의존성 주입 데코레이터"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # 의존성 해결
            resolved_deps = [ServiceLocator.get_service(dep) for dep in dependencies]
            return func(*resolved_deps, *args, **kwargs)
        return wrapper
    return decorator


# 설정 관리자
class ConfigurationManager:
    """설정 관리자"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """설정을 로드합니다."""
        try:
            import yaml
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"설정 파일을 찾을 수 없습니다: {self.config_file}")
            self._config = {}
        except Exception as e:
            logger.error(f"설정 로드 중 오류: {e}")
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정값을 가져옵니다."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_required(self, key: str) -> Any:
        """필수 설정값을 가져옵니다."""
        value = self.get(key)
        if value is None:
            raise ValueError(f"필수 설정이 없습니다: {key}")
        return value


# 로깅 설정
class LoggingConfigurator:
    """로깅 설정자"""
    
    @staticmethod
    def configure(config: ConfigurationManager) -> None:
        """로깅을 설정합니다."""
        log_level = config.get('logging.level', 'INFO')
        log_format = config.get('logging.format', 
                               '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/app.log', encoding='utf-8')
            ]
        )


# 기본 서비스 등록
def register_default_services(container: DependencyContainer) -> None:
    """기본 서비스들을 등록합니다."""
    # 설정 관리자
    config_manager = ConfigurationManager()
    container.register_singleton(ConfigurationManager, config_manager)
    
    # 로깅 설정
    LoggingConfigurator.configure(config_manager)
    
    # API 클라이언트들
    from api.api_client import APIClient
    from api.ki.kis_auth import KISAuth
    
    container.register_singleton(APIClient, APIClient(config_manager))
    container.register_singleton(KISAuth, KISAuth(config_manager))
    
    # 전략 엔진
    from strategy.engines.strategy_engine import StrategyEngine
    from strategy.risk_management.risk_manager import RiskManager
    
    risk_manager = RiskManager()
    container.register_singleton(RiskManager, risk_manager)
    container.register_singleton(StrategyEngine, StrategyEngine(risk_manager))
    
    logger.info("기본 서비스 등록 완료")


# 사용 예시
if __name__ == "__main__":
    # 컨테이너 생성
    container = DependencyContainer()
    
    # 기본 서비스 등록
    register_default_services(container)
    
    # 서비스 로케이터 설정
    ServiceLocator.set_container(container)
    
    # 서비스 사용
    config = ServiceLocator.get_service(ConfigurationManager)
    strategy_engine = ServiceLocator.get_service(StrategyEngine)
    
    print(f"설정 로드됨: {config.get('app.name', 'Unknown')}")
    print(f"전략 엔진 상태: {strategy_engine.get_engine_status()}")
