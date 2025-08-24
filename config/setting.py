import os
from pathlib import Path

# .env 파일 로드
def load_env():
    """환경변수 파일을 로드합니다."""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

# 환경변수 로드
load_env()

# KIS API 설정
AUTH_CONFIG = {
    "APP_KEY": os.getenv("KIS_APP_KEY", "your_kis_app_key"),
    "APP_SECRET": os.getenv("KIS_APP_SECRET", "your_kis_app_secret"),
    "ACCOUNT_NO": os.getenv("KIS_ACCOUNT_NO", "your_account_no"),
    "OPTION_ACCOUNT_NO": os.getenv("KIS_OPTION_ACCOUNT_NO", "your_option_account_no"),
}

# API 설정
API_CONFIG = {
    "KIS": {
        "BASE_URL": os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443"),
        "WS_URL": os.getenv("KIS_WS_URL", "ws://ops.koreainvestment.com:31000"),
        "APP_KEY": AUTH_CONFIG["APP_KEY"],
        "APP_SECRET": AUTH_CONFIG["APP_SECRET"],
        "ACCOUNT_NO": AUTH_CONFIG["ACCOUNT_NO"],
        "OPTION_ACCOUNT_NO": AUTH_CONFIG["OPTION_ACCOUNT_NO"],
    },
    "OPENAI": {
        "ACCESS_KEY": os.getenv("OPENAI_API_KEY", "your openai accesskey"),
        "MODEL_NAME": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "TEMPERATURE": int(os.getenv("OPENAI_TEMPERATURE", "0"))
    },
}

# 로깅 설정
LOGGING_CONFIG = {
    "LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "FILE": os.getenv("LOG_FILE", "logs/morning.log"),
}

# 애플리케이션 설정
APP_CONFIG = {
    "MAX_ITERATIONS": int(os.getenv("MAX_ITERATIONS", "10")),
    "ENABLE_CACHE": os.getenv("ENABLE_CACHE", "true").lower() == "true",
}
