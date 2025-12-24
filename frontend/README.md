# Frontend (Static HTML)

판매 데이터 조회 챗봇 프론트엔드

## 시작하기

### 로컬 실행

간단한 HTTP 서버를 실행하면 됩니다.

#### 방법 1: Python 내장 웹 서버
```bash
cd frontend
python -m http.server 3000
```

#### 방법 2: Node.js (http-server)
```bash
npm install -g http-server
cd frontend
http-server -p 3000
```

#### 방법 3: VS Code Live Server 확장
- VS Code에 "Live Server" 확장 설치
- `index.html` 우클릭 → "Open with Live Server"

서버는 `http://localhost:3000`에서 실행됩니다.

### 파일 구조
```
frontend/
├── index.html      # HTML 마크업
├── app.js          # JavaScript 로직
├── styles.css      # CSS 스타일
└── README.md       # 이 파일
```

### 백엔드 URL 설정

**개발 환경**
- `app.js`의 `BACKEND_URL`이 `http://localhost:8000`으로 설정되어 있습니다.
- 백엔드 서버를 `localhost:8000`에서 실행하면 자동으로 연결됩니다.

**배포 환경**
- 배포 후 `app.js`의 `BACKEND_URL`을 실제 백엔드 URL로 변경하세요:
  ```javascript
  // 변경 전
  const BACKEND_URL = "http://localhost:8000";
  
  // 변경 후 (예: Render 배포)
  const BACKEND_URL = "https://your-backend.onrender.com";
  ```

### 사용 방법

1. 페이지 로드 후 채팅 입력창에 질문을 입력합니다.
2. "전송" 버튼을 클릭하거나 Enter 키를 누릅니다.
3. 백엔드에서 응답을 받으면 챗창에 표시됩니다.

### 트러블슈팅

#### CORS 오류
- 브라우저 콘솔에 "CORS 오류" 메시지가 나타나면:
  1. 백엔드의 `.env` 파일에서 `CORS_ORIGINS` 확인
  2. 프론트엔드 도메인이 포함되어 있는지 확인
  3. 개발 중: `http://localhost:3000` 추가 필수

#### 백엔드 연결 안됨
- `app.js`에서 `BACKEND_URL` 확인
- 백엔드 서버 실행 여부 확인
- 브라우저 개발자 도구 → Network 탭에서 요청 확인

## 배포 (Render)

`render.yaml`에 배포 설정이 포함되어 있습니다. 정적 파일 호스팅으로 배포됩니다.
