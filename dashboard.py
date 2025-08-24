#!/usr/bin/env python3
"""
Morning - 주식 분석 대시보드 실행 파일
UI 폴더의 대시보드를 실행합니다.
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# UI 패키지의 대시보드 실행
if __name__ == "__main__":
    from ui.dashboard import main
    main()
else:
    # Streamlit에서 직접 실행할 때
    from ui.dashboard import *
