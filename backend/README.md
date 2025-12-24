# Backend API (FastAPI)

Text-to-SQL 기반 판매 데이터 조회 챗봇 백엔드 API

## 시작하기

### 필수 환경
- Python 3.11+
- PostgreSQL (Supabase)
- OpenAI API Key 또는 Anthropic API Key

### 로컬 실행

#### 1. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

#### 2. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일에 다음 변수 설정:
```env
# 필수
DATABASE_URL=postgresql://user:password@host:5432/dbname
LLM_API_KEY=sk-...  # OpenAI 또는 Anthropic API 키

# 선택 (기본값 사용 가능)
LLM_PROVIDER=openai  # openai 또는 anthropic
LLM_MODEL=gpt-4o-mini  # OpenAI 모델명 (또는 claude-3-5-sonnet-20241022)
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
PYTHON_VERSION=3.11.9
```

#### 3. 앱 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버는 `http://localhost:8000`에서 실행됩니다.

### API 엔드포인트

- `GET /health` - 헬스 체크
  ```bash
  curl http://localhost:8000/health
  # 응답: {"ok": true}
  ```

- `POST /chat` - Text-to-SQL 챗봇
  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"question": "서울본점의 1월 판매액은?"}'
  # 응답: {
  #   "answer": "결과: 1234567890",
  #   "sql": "SELECT ...",
  #   "columns": ["total"],
  #   "rows": [{"total": 1234567890}],
  #   "chart_data": null
  # }
  ```

### 프로젝트 구조
```
backend/
├── app/
│   ├── main.py          # FastAPI 메인 앱
│   ├── settings.py      # 환경 설정 로딩
│   ├── cors.py          # CORS 미들웨어
│   ├── guardrails.py    # SQL 검증 (미사용)
│   └── db.py            # DB 연결 관리
├── requirements.txt     # 의존성
├── .env.example         # 환경 변수 예시
└── README.md            # 이 파일
```

### 향후 작업

1. **Vanna 통합** - 자연어 -> SQL 변환
2. **SQL 검증** - `guardrails.validate_sql_query()` 활용
3. **DB 쿼리 실행** - `/chat`에서 실제 데이터 조회
4. **응답 변환** - SQL 결과를 자연어로 변환

### 문제 해결

#### DB 연결 실패
- Supabase 또는 PostgreSQL 서버 확인
- DATABASE_URL 형식: `postgresql://user:password@host:5432/database`
- psycopg2 설치 확인: `pip install psycopg2-binary`

#### CORS 오류
- CORS_ORIGINS에 프론트엔드 도메인이 포함되어 있는지 확인
- 개발 중: `http://localhost:3000` 또는 `http://localhost:5173`

## 배포 (Render)

`render.yaml`에 배포 설정이 포함되어 있습니다.
