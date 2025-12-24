"""데이터베이스 연결 및 쿼리 실행"""

import os
import logging
from typing import List, Dict, Tuple, Any
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# 커넥션 풀
_connection_pool = None


def get_connection_pool():
    \"\"\"데이터베이스 커넥션 풀 가져오기\"\"\"
    global _connection_pool
    
    if _connection_pool is None:
        database_url = os.getenv(\"DATABASE_URL\")
        if not database_url:
            raise ValueError(\"DATABASE_URL 환경 변수가 설정되지 않았습니다\")
        
        try:
            _connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=database_url
            )
            logger.info(\"데이터베이스 커넥션 풀 생성 완료\")
        except Exception as e:
            logger.error(f\"커넥션 풀 생성 실패: {e}\")
            raise
    
    return _connection_pool


def test_db_connection() -> bool:
    \"\"\"데이터베이스 연결 테스트\"\"\"
    try:
        pool_instance = get_connection_pool()
        conn = pool_instance.getconn()
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(\"SELECT 1;\")
                result = cursor.fetchone()
                logger.info(f\" DB 연결 성공: {result}\")
                return True
        finally:
            pool_instance.putconn(conn)
            
    except Exception as e:
        logger.error(f\" DB 연결 실패: {e}\")
        return False


def run_query(sql: str, timeout: int = 10) -> Tuple[List[str], List[Dict[str, Any]]]:
    \"\"\"
    SQL 쿼리 실행 및 결과 반환
    
    Args:
        sql: 실행할 SQL 쿼리
        timeout: 쿼리 타임아웃 (초)
        
    Returns:
        (컬럼명 리스트, 행 데이터 리스트) 튜플
        - columns: ['col1', 'col2', ...]
        - rows: [{'col1': val1, 'col2': val2}, ...]
        
    Raises:
        Exception: 쿼리 실행 중 오류 발생 시
    \"\"\"
    pool_instance = get_connection_pool()
    conn = pool_instance.getconn()
    
    try:
        # 타임아웃 설정
        conn.set_session(readonly=True)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Statement timeout 설정
            cursor.execute(f\"SET statement_timeout TO {timeout * 1000};\")
            
            # 쿼리 실행
            logger.info(f\"SQL 실행: {sql[:200]}...\")
            cursor.execute(sql)
            
            # 결과 가져오기
            rows = cursor.fetchall()
            
            # 최대 1000개 제한
            if len(rows) > 1000:
                logger.warning(f\"결과 {len(rows)}개 중 1000개만 반환\")
                rows = rows[:1000]
            
            # 컬럼명 추출
            columns = [desc.name for desc in cursor.description] if cursor.description else []
            
            # RealDict를 일반 dict로 변환
            rows_dict = [dict(row) for row in rows]
            
            logger.info(f\"쿼리 성공: {len(rows_dict)}개 행, {len(columns)}개 컬럼\")
            return columns, rows_dict
            
    except psycopg2.errors.QueryCanceled:
        logger.error(f\"쿼리 타임아웃 ({timeout}초 초과)\")
        raise TimeoutError(f\"쿼리 실행 시간이 {timeout}초를 초과했습니다\")
        
    except psycopg2.Error as e:
        logger.error(f\"SQL 실행 오류: {e}\")
        raise
        
    except Exception as e:
        logger.error(f\"예상치 못한 오류: {e}\")
        raise
        
    finally:
        conn.rollback()  # 읽기 전용이므로 롤백
        pool_instance.putconn(conn)


def close_pool():
    \"\"\"커넥션 풀 종료\"\"\"
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info(\"커넥션 풀 종료됨\")
