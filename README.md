# 📈 Realtime Stock Monitoring with Korea Investment API

이 프로젝트는 한국투자증권 Open API를 이용하여 실시간으로 국내 주식의 시세를 모니터링하고, 간단한 이동 평균 기반 AI 매수 신호를 출력하는 CLI 애플리케이션입니다.

---

## 📌 주요 기능

- 한국투자증권 API를 통한 실시간 주식 정보 조회
- 1시간 단위의 Access Token 캐싱 기능
- 주식 현재가, 전일 대비 가격/등락률, 거래량/거래대금 출력
- 5일/20일 이동 평균 돌파 기반 AI 매수 신호 감지
- 콘솔에 컬러 출력 및 로그 파일 저장

---

## 🛠️ 설치 및 실행

### 1. 의존 라이브러리 설치

```bash
pip install requests

2. config.py 설정
config.py 파일을 생성하고, 다음과 같이 앱 키와 시크릿을 입력합니다.
APP_KEY = "YOUR_APP_KEY"
APP_SECRET = "YOUR_APP_SECRET"


3. 실행
python restapi.py
