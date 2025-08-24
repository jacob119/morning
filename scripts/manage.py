#!/usr/bin/env python3
"""
Morning - 주식 분석 시스템 관리 스크립트
사용법: python manage.py [start|stop|status|restart|logs]
"""

import os
import sys
import time
import signal
import subprocess
import psutil
from pathlib import Path

class AppManager:
    def __init__(self):
        self.app_name = "morning"
        # 프로젝트 루트 디렉토리로 경로 설정
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pid_file = os.path.join(self.root_dir, "logs/morning.pid")
        self.log_file = os.path.join(self.root_dir, "logs/morning.log")
        self.dashboard_port = 8501
        
        # 로그 디렉토리 생성
        os.makedirs(os.path.join(self.root_dir, "logs"), exist_ok=True)
    
    def get_pid(self):
        """PID 파일에서 프로세스 ID를 읽습니다."""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
        except (ValueError, IOError):
            pass
        return None
    
    def save_pid(self, pid):
        """PID를 파일에 저장합니다."""
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))
    
    def remove_pid(self):
        """PID 파일을 삭제합니다."""
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
    
    def is_running(self, pid=None):
        """프로세스가 실행 중인지 확인합니다."""
        if pid is None:
            pid = self.get_pid()
        
        if pid is None:
            return False
        
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.name().lower() in ['python', 'python3']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def start(self):
        """애플리케이션을 시작합니다."""
        print(f"🚀 {self.app_name} 애플리케이션 시작 중...")
        
        # 이미 실행 중인지 확인
        if self.is_running():
            print(f"❌ {self.app_name}이 이미 실행 중입니다. (PID: {self.get_pid()})")
            return False
        
        try:
            # Streamlit 대시보드 시작
            cmd = [
                sys.executable, "-m", "streamlit", "run", os.path.join(self.root_dir, "dashboard.py"),
                "--server.port", str(self.dashboard_port),
                "--server.headless", "true"
            ]
            
            # 백그라운드에서 실행
            process = subprocess.Popen(
                cmd,
                stdout=open(self.log_file, 'a'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid
            )
            
            # PID 저장
            self.save_pid(process.pid)
            
            # 시작 확인
            time.sleep(2)
            if self.is_running(process.pid):
                print(f"✅ {self.app_name} 시작 완료!")
                print(f"📊 대시보드: http://localhost:{self.dashboard_port}")
                print(f"📝 로그 파일: {self.log_file}")
                print(f"🆔 프로세스 ID: {process.pid}")
                return True
            else:
                print(f"❌ {self.app_name} 시작 실패")
                self.remove_pid()
                return False
                
        except Exception as e:
            print(f"❌ 시작 중 오류 발생: {e}")
            self.remove_pid()
            return False
    
    def stop(self):
        """애플리케이션을 중지합니다."""
        print(f"🛑 {self.app_name} 애플리케이션 중지 중...")
        
        pid = self.get_pid()
        if pid is None:
            print(f"❌ 실행 중인 {self.app_name} 프로세스를 찾을 수 없습니다.")
            return False
        
        if not self.is_running(pid):
            print(f"❌ {self.app_name}이 실행 중이지 않습니다.")
            self.remove_pid()
            return False
        
        try:
            # 프로세스 종료
            process = psutil.Process(pid)
            process.terminate()
            
            # 5초 대기 후 강제 종료
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                process.kill()
                process.wait()
            
            self.remove_pid()
            print(f"✅ {self.app_name} 중지 완료!")
            return True
            
        except psutil.NoSuchProcess:
            print(f"✅ {self.app_name}이 이미 종료되었습니다.")
            self.remove_pid()
            return True
        except Exception as e:
            print(f"❌ 중지 중 오류 발생: {e}")
            return False
    
    def restart(self):
        """애플리케이션을 재시작합니다."""
        print(f"🔄 {self.app_name} 애플리케이션 재시작 중...")
        
        # 현재 상태와 관계없이 중지 시도
        self.stop()
        time.sleep(2)
        return self.start()
    
    def status(self):
        """애플리케이션 상태를 확인합니다."""
        print(f"📊 {self.app_name} 상태 확인 중...")
        
        pid = self.get_pid()
        if pid is None:
            print("❌ 실행 중이지 않음")
            return False
        
        if self.is_running(pid):
            try:
                process = psutil.Process(pid)
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()
                
                print("✅ 실행 중")
                print(f"🆔 프로세스 ID: {pid}")
                print(f"💾 메모리 사용량: {memory_info.rss / 1024 / 1024:.1f} MB")
                print(f"🖥️  CPU 사용률: {cpu_percent:.1f}%")
                print(f"📊 대시보드: http://localhost:{self.dashboard_port}")
                print(f"📝 로그 파일: {self.log_file}")
                return True
            except psutil.NoSuchProcess:
                print("❌ 프로세스가 존재하지 않음")
                self.remove_pid()
                return False
        else:
            print("❌ 실행 중이지 않음")
            self.remove_pid()
            return False
    
    def logs(self, lines=50):
        """로그를 확인합니다."""
        if not os.path.exists(self.log_file):
            print(f"❌ 로그 파일이 존재하지 않습니다: {self.log_file}")
            return
        
        print(f"📝 최근 {lines}줄의 로그:")
        print("-" * 50)
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
                for line in recent_lines:
                    print(line.rstrip())
        except Exception as e:
            print(f"❌ 로그 읽기 오류: {e}")
    
    def clean(self):
        """로그 파일을 정리합니다."""
        print(f"🧹 {self.app_name} 로그 정리 중...")
        
        try:
            if os.path.exists(self.log_file):
                # 로그 파일 백업
                backup_file = f"{self.log_file}.backup"
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(self.log_file, backup_file)
                print(f"✅ 로그 파일이 {backup_file}로 백업되었습니다.")
            
            self.remove_pid()
            print("✅ 정리 완료!")
            return True
        except Exception as e:
            print(f"❌ 정리 중 오류 발생: {e}")
            return False

def print_usage():
    """사용법을 출력합니다."""
    print("""
🌅 Morning - 주식 분석 시스템 관리 스크립트

사용법:
  python manage.py start     - 애플리케이션 시작
  python manage.py stop      - 애플리케이션 중지
  python manage.py restart   - 애플리케이션 재시작
  python manage.py status    - 애플리케이션 상태 확인
  python manage.py logs      - 로그 확인 (최근 50줄)
  python manage.py logs 100  - 로그 확인 (최근 100줄)
  python manage.py clean     - 로그 파일 정리

예시:
  python manage.py start
  python manage.py status
  python manage.py logs 20
  python manage.py stop
""")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    manager = AppManager()
    command = sys.argv[1].lower()
    
    try:
        if command == "start":
            manager.start()
        elif command == "stop":
            manager.stop()
        elif command == "restart":
            manager.restart()
        elif command == "status":
            manager.status()
        elif command == "logs":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            manager.logs(lines)
        elif command == "clean":
            manager.clean()
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print_usage()
    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
