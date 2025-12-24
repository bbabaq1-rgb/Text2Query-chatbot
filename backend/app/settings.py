import os
from functools import lru_cache
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    """애플리케이션 설정"""

    def __init__(self):
        """환경 변수로부터 설정 로드"""
        # 데이터베이스
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")
        
        # LLM API
        self.LLM_API_KEY = os.getenv("LLM_API_KEY", "")
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
        # CORS
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:8080")
        self.CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",")]

@lru_cache()
def get_settings():
    """Settings 인스턴스 반환"""
    return Settings()
