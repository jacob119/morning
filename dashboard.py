#!/usr/bin/env python3
"""
Morning - 주식 분석 대시보드 실행 파일
UI 폴더의 대시보드를 실행합니다.
"""

import sys
import os
import subprocess

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """메인 실행 함수"""
    try:
        # ui/dashboard.py를 직접 실행
        dashboard_path = os.path.join(os.path.dirname(__file__), "ui", "dashboard.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])
    except Exception as e:
        print(f"대시보드 실행 중 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
