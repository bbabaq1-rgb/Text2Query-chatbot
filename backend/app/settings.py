import os
from functools import lru_cache

class Settings:
    """애플리케이션 설정"""

    # 데이터베이스
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/loan_db")

    # LLM API
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

    # CORS
    CORS_ORIGINS: list = []

    def __init__(self):
        """CORS_ORIGINS를 쉼표 구분 문자열에서 리스트로 변환"""
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:8080")
        self.CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",")]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    """Settings 인스턴스 반환"""
    return Settings()
