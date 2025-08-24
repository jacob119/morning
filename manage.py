#!/usr/bin/env python3
"""
Morning - 주식 분석 시스템 관리 스크립트 (루트 디렉토리)
scripts 폴더의 관리 스크립트를 실행합니다.
"""

import sys
import os
import subprocess

def main():
    """메인 함수"""
    # 현재 디렉토리
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(current_dir, "scripts")
    manage_script = os.path.join(scripts_dir, "manage.py")
    
    # scripts 폴더의 manage.py 실행
    if os.path.exists(manage_script):
        # 현재 작업 디렉토리를 scripts 폴더로 변경
        os.chdir(scripts_dir)
        
        # manage.py 실행
        cmd = [sys.executable, "manage.py"] + sys.argv[1:]
        subprocess.run(cmd)
    else:
        print(f"❌ 스크립트 파일을 찾을 수 없습니다: {manage_script}")
        sys.exit(1)

if __name__ == "__main__":
    main()
