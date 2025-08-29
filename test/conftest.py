"""
pytest 설정 파일

공통 테스트 설정과 fixture들을 정의합니다.
"""

import sys
import os
import pytest
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 테스트용 로깅 설정
logging.basicConfig(
    level=logging.WARNING,  # 테스트 중에는 WARNING 레벨만 출력
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture(scope="session")
def test_data_dir():
    """테스트 데이터 디렉토리 경로"""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture(scope="session")
def sample_stock_data():
    """샘플 주식 데이터"""
    return {
        "005930": {
            "name": "삼성전자",
            "current_price": 70000,
            "open_price": 69500,
            "high_price": 70500,
            "low_price": 69000,
            "volume": 5000000
        },
        "000660": {
            "name": "SK하이닉스", 
            "current_price": 250000,
            "open_price": 248000,
            "high_price": 252000,
            "low_price": 246000,
            "volume": 2000000
        },
        "035420": {
            "name": "NAVER",
            "current_price": 220000,
            "open_price": 218000,
            "high_price": 222000,
            "low_price": 216000,
            "volume": 1000000
        }
    }

@pytest.fixture(scope="session")
def sample_portfolio_data():
    """샘플 포트폴리오 데이터"""
    return {
        "005930": {"name": "삼성전자", "quantity": 10, "avg_price": 70000},
        "000660": {"name": "SK하이닉스", "quantity": 5, "avg_price": 250000},
        "035420": {"name": "NAVER", "quantity": 3, "avg_price": 220000}
    }

@pytest.fixture(scope="function")
def mock_openai_response():
    """OpenAI API 응답 모킹"""
    return {
        "choices": [{
            "message": {
                "content": "Buy, 목표가 75000원 (메모리 반도체 수요 증가 기대)"
            }
        }]
    }

@pytest.fixture(scope="function")
def mock_kis_api_response():
    """KIS API 응답 모킹"""
    return {
        "rt_cd": "0",
        "msg1": "정상처리 되었습니다.",
        "output": {
            "hts_kor_isnm": "삼성전자",
            "stck_prpr": "70000",
            "stck_oprc": "69500",
            "stck_hgpr": "70500",
            "stck_lwpr": "69000",
            "acml_vol": "5000000"
        }
    }

@pytest.fixture(scope="function")
def mock_slack_event():
    """Slack 이벤트 모킹"""
    return {
        "type": "message",
        "user": "U1234567890",
        "text": "내 보유 주식",
        "channel": "C1234567890",
        "ts": "1234567890.123456"
    }

@pytest.fixture(scope="function")
def sample_market_data():
    """샘플 시장 데이터"""
    from strategy.strategies import MarketData
    
    return MarketData(
        stock_code="005930",
        current_price=70000,
        open_price=69500,
        high_price=70500,
        low_price=69000,
        volume=5000000,
        timestamp=datetime.now()
    )

@pytest.fixture(scope="function")
def sample_signal():
    """샘플 매매 신호"""
    from strategy.strategies import Signal
    
    return Signal(
        stock_code="005930",
        action="BUY",
        confidence=0.8,
        price=70000,
        quantity=10,
        reason="모멘텀 상승 신호"
    )

@pytest.fixture(scope="function")
def mock_env_vars():
    """환경 변수 모킹"""
    env_vars = {
        'OPENAI_API_KEY': 'test-openai-key',
        'SLACK_BOT_TOKEN': 'xoxb-test-token',
        'SLACK_APP_TOKEN': 'xapp-test-token',
        'SLACK_SIGNING_SECRET': 'test-signing-secret',
        'KIS_APP_KEY': 'test-kis-app-key',
        'KIS_APP_SECRET': 'test-kis-app-secret',
        'KIS_ACCESS_TOKEN': 'test-kis-access-token'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture(scope="function")
def temp_log_file(tmp_path):
    """임시 로그 파일"""
    log_file = tmp_path / "test.log"
    return str(log_file)

@pytest.fixture(scope="function")
def mock_file_system(tmp_path):
    """모킹된 파일 시스템"""
    # 테스트용 디렉토리 구조 생성
    config_dir = tmp_path / "config"
    logs_dir = tmp_path / "logs"
    data_dir = tmp_path / "data"
    
    config_dir.mkdir()
    logs_dir.mkdir()
    data_dir.mkdir()
    
    return {
        "root": str(tmp_path),
        "config": str(config_dir),
        "logs": str(logs_dir),
        "data": str(data_dir)
    }

# 테스트 마커 정의
def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers", "unit: 단위 테스트"
    )
    config.addinivalue_line(
        "markers", "integration: 통합 테스트"
    )
    config.addinivalue_line(
        "markers", "e2e: 엔드투엔드 테스트"
    )
    config.addinivalue_line(
        "markers", "performance: 성능 테스트"
    )
    config.addinivalue_line(
        "markers", "slow: 느린 테스트"
    )
    config.addinivalue_line(
        "markers", "api: API 테스트"
    )

# 테스트 수집 시 경고 무시
def pytest_collection_modifyitems(config, items):
    """테스트 수집 시 설정"""
    for item in items:
        # 모든 테스트에 기본 마커 추가
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)
