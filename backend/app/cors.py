from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.settings import get_settings

def setup_cors(app: FastAPI) -> None:
    """CORS 미들웨어 설정"""
    settings = get_settings()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
