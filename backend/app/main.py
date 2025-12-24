"""FastAPI 메인 애플리케이션"""

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.cors import setup_cors
from app.db import test_db_connection
from app.settings import get_settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 애플리케이션
app = FastAPI(
    title="Loan Sales AI Chat API",
    description="영업 데이터 조회 챗봇 API",
    version="0.1.0",
)

# CORS 설정
setup_cors(app)

# 요청/응답 모델
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

# 라우트

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 데이터베이스 연결 테스트"""
    logger.info("🚀 애플리케이션 시작...")
    settings = get_settings()
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")

    # DB 연결 테스트(무시해도 됨 - 오류가 있어도 계속 시작됨)
    test_db_connection()

@app.get("/health")
async def health_check():
    """상태 체크 엔드포인트"""
    return {"ok": True}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    채팅 엔드포인트
    
    현재: 샘플 응답 제공
    향후: Vanna + DB 연동으로 실제 SQL 쿼리 실행
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question이 필수입니다")

    question = request.question.strip().lower()

    # 샘플 응답 (실제로는 DB에서 조회)
    sample_responses = {
        "판매액": "지난 달 판매액은 총 1,250만원입니다.\n\n📊 상세내역:\n- 서울지점: 450만원\n- 부산지점: 380만원\n- 대구지점: 420만원",
        "판매": "지난 달 판매액은 총 1,250만원입니다.\n\n📊 상세내역:\n- 서울지점: 450만원\n- 부산지점: 380만원\n- 대구지점: 420만원",
        "상품": "현재 판매 중인 상품:\n\n1️⃣ 신차구매 - 월 이자율 2.5%\n2️⃣ 중고차구매 - 월 이자율 3.2%\n3️⃣ 담보대출 - 월 이자율 2.8%\n4️⃣ 리스 - 월 이자율 3.0%\n5️⃣ 보증부차용증권 - 월 이자율 2.3%",
        "지점": "전국 5개 지점:\n\n📍 서울 - 강남구 (담당자: 김영수)\n📍 부산 - 중앙로 (담당자: 이순신)\n📍 대구 - 중구 (담당자: 박민준)\n📍 대전 - 유성구 (담당자: 최대호)\n📍 광주 - 동구 (담당자: 정미영)",
    }

    # 키워드 매칭으로 샘플 응답 선택
    for key, response in sample_responses.items():
        if key in question:
            return ChatResponse(answer=response)

    # 기본 응답
    default_response = f"'{request.question}'에 대한 데이터를 조회했습니다.\n\n현재는 샘플 데이터만 제공 중입니다.\n\n💡 시도해볼 수 있는 질문:\n- 판매액은?\n- 어떤 상품이 있나?\n- 지점은 어디?"

    return ChatResponse(answer=default_response)

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
