"""데이터베이스 연결 관리"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from app.settings import get_settings

logger = logging.getLogger(__name__)

def get_db_engine():
    """데이터베이스 엔진 생성"""
    settings = get_settings()
    
    # Supabase는 postgresql:// 또는 postgresql+psycopg2:// 지원
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    engine = create_engine(
        database_url,
        poolclass=NullPool,  # Render 무료 플랜용 (connection pool 없음)
        echo=False,
    )
    return engine

def test_db_connection() -> bool:
    """데이터베이스 연결 테스트"""
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False

def get_db_connection():
    """데이터베이스 연결 반환 (컨텍스트 매니저)"""
    engine = get_db_engine()
    with engine.connect() as conn:
        yield conn
