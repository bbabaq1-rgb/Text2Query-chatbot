# 프로젝트 사양서 (SPEC)

## 목표

**Render 배포 가능한 MVP: Front(Static) + Back(FastAPI) + Supabase(Postgres)**

- 판매 데이터 조회 챗봇
- 자연어로 판매 정보 조회 (현재 Echo, 향후 Vanna 연동 예정)
- CORS 적용으로 프론트 도메인 허용

---

## 기술 스택

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy (선택)
- **Python**: 3.8+

### Frontend
- **HTML5 + CSS3 + Vanilla JavaScript**
- **No Build Tool** (Static Hosting)
- **API Communication**: Fetch API

### Infrastructure
- **Deployment**: Render (PaaS)
- **Database**: Supabase (PostgreSQL managed service)

---

## API 명세

### 1. GET /health
**목적**: 헬스 체크

**요청**:
```http
GET /health HTTP/1.1
```

**응답** (200 OK):
```json
{
  "ok": true
}
```

---

### 2. POST /chat
**목적**: 판매 데이터 조회 (자연어 챗)

**요청**:
```http
POST /chat HTTP/1.1
Content-Type: application/json

{
  "question": "지난 월 판매액은?"
}
```

**응답** (200 OK):
```json
{
  "answer": "Echo: 지난 월 판매액은?"
}
```

**현재 상태**: Echo 모드 (입력값 그대로 반환)

**향후 구현**:
1. Vanna로 자연어 → SQL 변환
2. `guardrails.validate_sql_query()` 검증
3. PostgreSQL 쿼리 실행
4. 결과를 자연어로 변환

---

## 데이터베이스 스키마

### dim_branch (지점 마스터)
```
branch_id (PK, SERIAL)
branch_name (VARCHAR, UNIQUE)
region (VARCHAR)
manager_name (VARCHAR)
created_at (TIMESTAMP DEFAULT NOW)
```

**샘플 데이터**: 5개 지점
- 서울본점, 부산지점, 대구지점, 대전지점, 광주지점

---

### dim_product (상품 마스터)
```
product_id (PK, SERIAL)
product_name (VARCHAR, UNIQUE)
product_category (VARCHAR)
description (TEXT)
created_at (TIMESTAMP DEFAULT NOW)
```

**샘플 데이터**: 5개 상품
- 신차구매금융
- **중고차금융** (중요)
- 차량담보대출
- 리스금융
- 보증금융

---

### fact_loan_sales (판매 팩트)
```
sale_id (PK, SERIAL)
contract_id (VARCHAR, UNIQUE)
branch_id (FK → dim_branch)
product_id (FK → dim_product)
sale_date (DATE)
disbursed_amount (NUMERIC(15,2))
quantity (INTEGER DEFAULT 1)
created_at (TIMESTAMP DEFAULT NOW)
```

**인덱스**:
- `idx_fact_sales_branch` (branch_id)
- `idx_fact_sales_product` (product_id)
- `idx_fact_sales_date` (sale_date)
- `idx_fact_sales_contract` (contract_id)

**샘플 데이터**: ~200건
- 기간: 2024년 1월 ~ 9월
- 판매액: 900만 ~ 4,300만원
- 지점별 분포: 서울 50건, 부산 40건, 대구 45건, 대전 35건, 광주 30건

---

## 핵심 구현 사항

### Backend (FastAPI)

#### `settings.py` - 환경 설정
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `LLM_API_KEY`: (향후) LLM API 키
- `CORS_ORIGINS`: 콤마 구분 리스트 (개발: localhost:3000, localhost:5173)

#### `cors.py` - CORS 미들웨어
- CORSMiddleware 적용
- `CORS_ORIGINS`에서 허용 도메인 동적 로드

#### `guardrails.py` - SQL 검증 (미사용 상태)
- `validate_sql_query()`: SELECT-only, 금지 키워드 차단, LIMIT 강제 검증
- `sanitize_sql_query()`: 쿼리 정제 (미구현)

#### `db.py` - 데이터베이스 관리
- `get_db_engine()`: SQLAlchemy 엔진 생성
- `test_db_connection()`: 연결 테스트 (앱 시작 시 자동 실행)
- `get_db_connection()`: 컨텍스트 매니저

#### `main.py` - FastAPI 애플리케이션
- `/health`: 헬스 체크
- `/chat`: 챗 엔드포인트 (현재 Echo)
- CORS 설정 적용
- 로깅 설정

### Frontend (Static)

#### `index.html`
- 간단한 챗 UI
- 메시지 표시 영역 + 입력 폼
- CSS 클래스: `.chat-box`, `.chat-messages`, `.message`, etc.

#### `app.js`
- `BACKEND_URL` 상수 (상단에 주석 포함)
- `fetch()` API로 POST /chat 호출
- 메시지 추가 함수 (`addMessage()`)
- 페이지 로드 시 백엔드 연결 확인

#### `styles.css`
- 모던한 그래디언트 디자인
- 반응형 디자인 (모바일 대응)
- 애니메이션 효과

### Database

#### `schema.sql`
- 3개 테이블 정의 + 인덱스 생성

#### `seed.sql`
- ~200건의 판매 데이터 (2024년 1월~9월)

---

## 배포 (Render)

### `render.yaml` 구조

```yaml
services:
  - type: web
    name: loan-sales-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - DATABASE_URL (sync: false)
      - LLM_API_KEY (sync: false)
      - CORS_ORIGINS (sync: false)

  - type: web
    name: loan-sales-frontend
    runtime: static
    rootDir: frontend
    buildCommand: echo "no build"
    staticPublishPath: .
```

### 배포 절차

1. GitHub에 모노레포 푸시
2. Render 대시보드에서 Blueprint 연결
3. 환경 변수 설정:
   - `DATABASE_URL`: Supabase 연결 문자열
   - `LLM_API_KEY`: (나중에) API 키
   - `CORS_ORIGINS`: 프론트엔드 도메인 (Render에서 제공)
4. 배포 자동 실행

### 프론트엔드 URL 설정
- `app.js`의 `BACKEND_URL` 배포 후 실제 백엔드 URL로 수정
- 주석 표시로 대표님이 쉽게 찾을 수 있도록 안내

---

## 로컬 실행 (개발 환경)

### 1. 백엔드
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 환경 변수 설정
uvicorn app.main:app --reload
```
서버: `http://localhost:8000`

### 2. 프론트엔드
```bash
cd frontend
python -m http.server 3000  # 또는 다른 서버
```
페이지: `http://localhost:3000`

### 3. 데이터베이스
- Supabase 프로젝트 생성 후 CONNECTION STRING 복사
- `backend/.env`의 `DATABASE_URL`에 설정
- `schema.sql` + `seed.sql` 실행

---

## 파일 구조

```
monorepo/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI 앱
│   │   ├── settings.py      # 환경 설정
│   │   ├── cors.py          # CORS 미들웨어
│   │   ├── guardrails.py    # SQL 검증
│   │   └── db.py            # DB 관리
│   ├── requirements.txt      # 의존성
│   ├── .env.example          # 환경 변수 예시
│   └── README.md             # 백엔드 가이드
├── frontend/
│   ├── index.html           # HTML
│   ├── app.js               # JavaScript
│   ├── styles.css           # CSS
│   └── README.md            # 프론트 가이드
├── db/
│   ├── schema.sql           # 스키마
│   ├── seed.sql             # 샘플 데이터
│   └── README.md            # DB 가이드
├── render.yaml              # Render 배포 설정
├── SPEC.md                  # 이 파일
└── .gitignore               # Git 무시 파일
```

---

## 향후 개선 사항

### Phase 2: Vanna 연동
- 자연어 → SQL 변환
- SQL 검증 활성화
- 결과 변환

### Phase 3: 고급 기능
- 인증/인가 (JWT)
- 쿼리 캐싱
- 데이터 시각화
- 멀티-턴 챗 (이력 저장)

---

## 문제 해결

### CORS 오류
- `CORS_ORIGINS` 환경 변수 확인
- 프론트엔드 도메인이 포함되어 있는지 확인

### DB 연결 실패
- `DATABASE_URL` 형식 확인: `postgresql://user:password@host:5432/db`
- Supabase 인스턴스 상태 확인
- `psycopg2-binary` 설치 확인

### 프론트 백엔드 못 찾음
- `app.js`의 `BACKEND_URL` 확인
- 브라우저 콘솔에서 요청 확인 (F12 → Network 탭)

---

## 참고

- **FastAPI 공식 문서**: https://fastapi.tiangolo.com
- **Render 배포 가이드**: https://render.com/docs
- **Supabase 시작 가이드**: https://supabase.com/docs
- **Vanna 문서**: https://vanna.ai (향후 참고)
