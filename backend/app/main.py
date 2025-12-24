"""FastAPI 메인 애플리케이션"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.settings import get_settings

# 조건부 import (파일 존재 여부에 따라)
try:
    from app.db import test_db_connection, run_query
    from app.llm_client import generate_sql
    from app.sql_prompt import build_prompt
    from app.guardrails import validate_and_rewrite
    LLM_ENABLED = True
except ImportError as e:
    logging.warning(f"일부 모듈 로드 실패: {e}")
    LLM_ENABLED = False
    def test_db_connection(): return False
    def run_query(sql): return [], []
    def generate_sql(prompt): return "SELECT 1;"
    def build_prompt(q): return q
    def validate_and_rewrite(sql): return sql

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 애플리케이션
app = FastAPI(
    title="Loan Sales AI Chat API",
    description="영업 데이터 조회 챗봇 API",
    version="0.1.0",
)

# CORS 설정
settings = get_settings()
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 모델
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    columns: Optional[List[str]] = None
    rows: Optional[List[Dict[str, Any]]] = None
    chart_data: Optional[Dict[str, Any]] = None

# 라우트

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 데이터베이스 연결 테스트"""
    logger.info("🚀 애플리케이션 시작...")
    settings = get_settings()
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")

    # DB 연결 테스트(무시해도 됨 - 오류가 있어도 계속 시작됨)
    try:
        db_ok = test_db_connection()
        if db_ok:
            logger.info("✅ 데이터베이스 연결 성공")
        else:
            logger.warning("⚠️ 데이터베이스 연결 실패 - LLM SQL 생성만 사용 가능")
    except Exception as e:
        logger.warning(f"⚠️ 데이터베이스 연결 실패 - LLM SQL 생성만 사용 가능: {str(e)[:100]}")

@app.get("/health")
async def health_check():
    """상태 체크 엔드포인트"""
    return {"ok": True}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    채팅 엔드포인트 - Text-to-SQL 기반 질의응답
    
    Flow:
    1. 사용자 질문 → SQL 프롬프트 생성
    2. LLM 호출 → SQL 생성
    3. Guardrails 검증 → 안전한 SQL
    4. DB 실행 → 결과 반환
    5. 자연어 답변 생성
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question이 필수입니다")

    question = request.question.strip()
    
    # LLM이 비활성화된 경우 샘플 응답
    if not LLM_ENABLED:
        logger.warning("LLM 비활성화 상태 - 샘플 응답 반환")
        return ChatResponse(
            answer="LLM이 설정되지 않았습니다. LLM_API_KEY 환경 변수를 설정해주세요.",
            sql=None,
            columns=[],
            rows=[]
        )
    
    try:
        # 1. SQL 프롬프트 생성
        logger.info(f"사용자 질문: {question}")
        prompt = build_prompt(question)
        
        # 2. LLM으로 SQL 생성
        logger.info("LLM 호출 중...")
        raw_sql = generate_sql(prompt)
        logger.info(f"생성된 SQL: {raw_sql}")
        
        # 3. Guardrails 검증
        try:
            safe_sql = validate_and_rewrite(raw_sql)
            logger.info(f"검증된 SQL: {safe_sql}")
        except ValueError as e:
            logger.error(f"SQL 검증 실패: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"생성된 SQL이 안전하지 않습니다: {str(e)}"
            )
        
        # 4. DB에서 쿼리 실행
        try:
            logger.info("쿼리 실행 중...")
            columns, rows = run_query(safe_sql)
            logger.info(f"결과: {len(rows)}개 행")
        except TimeoutError as e:
            # DB 타임아웃 - SQL은 보여주되 에러 메시지 표시
            return ChatResponse(
                answer="⚠️ 쿼리 실행 시간이 초과되었습니다. 생성된 SQL을 확인해주세요.",
                sql=safe_sql,
                columns=[],
                rows=[]
            )
        except Exception as e:
            logger.error(f"쿼리 실행 오류: {e}")
            # DB 연결 실패 - SQL은 보여주되 에러 메시지 표시
            return ChatResponse(
                answer=f"⚠️ 데이터베이스 연결 오류가 발생했습니다.\n생성된 SQL은 확인할 수 있습니다.\n\n오류: {str(e)[:100]}",
                sql=safe_sql,
                columns=[],
                rows=[]
            )
        
        # 5. 답변 생성
        row_count = len(rows)
        col_count = len(columns)
        
        if row_count == 0:
            answer = "조회된 데이터가 없습니다."
        elif row_count == 1 and col_count == 1:
            # 단일 값 결과 (예: COUNT)
            value = list(rows[0].values())[0]
            answer = f"결과: {value}"
        else:
            answer = f"총 {row_count}개의 데이터를 조회했습니다.\n컬럼: {', '.join(columns)}"
        
        # 6. 응답 반환
        return ChatResponse(
            answer=answer,
            sql=safe_sql,
            columns=columns,
            rows=rows,
            chart_data=None  # TODO: 차트 데이터 생성 로직 추가
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"서버 오류가 발생했습니다: {str(e)}"
        )

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Loan Sales AI Chat API",
        "docs": "/docs",
        "health": "/health",
        "chat": "/chat",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
