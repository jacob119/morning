import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging():
    """로깅 시스템을 설정합니다."""
    try:
        # config를 import하기 전에 순환참조 방지
        from config.setting import LOGGING_CONFIG
        
        # 로그 디렉토리 생성
        log_file = Path(LOGGING_CONFIG["FILE"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 로그 레벨 설정
        log_level = getattr(logging, LOGGING_CONFIG["LEVEL"].upper(), logging.INFO)
        
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # 기존 핸들러 제거
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 파일 핸들러 (로테이션)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        return True
    except Exception as e:
        print(f"로깅 설정 실패: {e}")
        # 기본 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return False

def get_logger(name):
    """로거를 반환합니다."""
    # 로깅 시스템이 설정되지 않았다면 설정
    if not logging.getLogger().handlers:
        setup_logging()
    
    logger = logging.getLogger(name)
    return logger