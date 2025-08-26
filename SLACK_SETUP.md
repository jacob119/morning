# Slack Bot 설정 가이드

## 1. Slack App 생성

### 1.1 Slack API 웹사이트에서 앱 생성
1. https://api.slack.com/apps 접속
2. "Create New App" 클릭
3. "From scratch" 선택
4. 앱 이름 입력 (예: "Morning Stock Bot")
5. 워크스페이스 선택

### 1.2 Bot Token 설정
1. 왼쪽 메뉴에서 "OAuth & Permissions" 클릭
2. "Scopes" 섹션에서 "Bot Token Scopes" 추가:
   - `app_mentions:read`
   - `channels:history`
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
3. "Install to Workspace" 클릭
4. "Bot User OAuth Token" 복사 (xoxb-로 시작)

### 1.3 App-Level Token 설정
1. 왼쪽 메뉴에서 "Basic Information" 클릭
2. "App-Level Tokens" 섹션에서 "Generate Token and Scopes" 클릭
3. 토큰 이름 입력 (예: "socket-token")
4. "connections:write" 스코프 추가
5. 토큰 생성 후 복사 (xapp-로 시작)

### 1.4 Signing Secret 복사
1. "Basic Information" 페이지에서 "Signing Secret" 복사

## 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
# Slack Bot 설정
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here

# KIS API 설정 (기존)
KIS_APP_KEY=your-kis-app-key
KIS_APP_SECRET=your-kis-app-secret
KIS_ACCOUNT_NO=your-account-number
KIS_ACCOUNT_CODE=your-account-code

# OpenAI API 설정 (기존)
OPENAI_API_KEY=your-openai-api-key
```

## 3. 봇을 채널에 초대

1. Slack 워크스페이스에서 봇을 사용할 채널 선택
2. `/invite @봇이름` 입력하여 봇 초대

## 4. 봇 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 봇 실행
python slack_bot.py
```

## 5. 사용 방법

### 5.1 기본 명령어
- `내 보유 주식` - 현재 보유 주식 현황 조회
- `도움말` - 도움말 메시지 표시

### 5.2 멘션 사용
- `@봇이름 보유 주식` - 멘션으로 포트폴리오 조회
- `@봇이름 도움말` - 멘션으로 도움말 요청

## 6. 보유 주식 정보 수정

`config/slack_config.py` 파일의 `PORTFOLIO_STOCKS` 딕셔너리를 수정하여 실제 보유 주식 정보를 입력:

```python
PORTFOLIO_STOCKS = {
    "005930": {"name": "삼성전자", "quantity": 10, "avg_price": 70000},
    "000660": {"name": "SK하이닉스", "quantity": 5, "avg_price": 250000},
    # 추가 주식 정보...
}
```

## 7. 제공 정보

- 실시간 주가 (KIS API 연동)
- 보유 수량 및 평균단가
- 개별 주식 수익률 및 평가손익
- 전체 포트폴리오 현황
- 총 투자금액 및 현재 총액

## 8. 문제 해결

### 8.1 토큰 오류
- 토큰이 올바르게 설정되었는지 확인
- `.env` 파일이 프로젝트 루트에 있는지 확인

### 8.2 권한 오류
- Bot Token Scopes가 올바르게 설정되었는지 확인
- 봇이 채널에 초대되었는지 확인

### 8.3 연결 오류
- 인터넷 연결 상태 확인
- Slack API 서버 상태 확인
