"""SQL Guardrails - SQL 쿼리 검증 및 안전성 확보"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# 금지된 키워드 (대소문자 구분 없음)
FORBIDDEN_KEYWORDS = [
    "DROP", "TRUNCATE", "INSERT", "UPDATE", "DELETE", 
    "MERGE", "ALTER", "CREATE", "GRANT", "REVOKE",
    "EXEC", "EXECUTE", "IMPORT", "EXPORT", "BACKUP",
    "RESTORE", "SHUTDOWN", "KILL"
]

# 허용되는 SELECT 패턴
ALLOWED_PATTERN = re.compile(r'^\s*SELECT\s+', re.IGNORECASE | re.MULTILINE)


def validate_and_rewrite(sql: str) -> str:
    """
    SQL 쿼리를 검증하고 필요시 재작성
    
    Args:
        sql: 검증할 SQL 쿼리
        
    Returns:
        검증 및 안전 처리된 SQL 쿼리
        
    Raises:
        ValueError: SQL이 안전하지 않은 경우
    """
    if not sql or not sql.strip():
        raise ValueError("SQL 쿼리가 비어있습니다")
    
    sql = sql.strip()
    
    # 1. SELECT 문인지 확인
    if not ALLOWED_PATTERN.match(sql):
        raise ValueError("SELECT 문만 허용됩니다")
    
    # 2. 세미콜론 검사 (여러 statement 방지)
    semicolon_count = sql.count(';')
    if semicolon_count > 1:
        raise ValueError("여러 개의 SQL 문은 허용되지 않습니다")
    
    # 끝의 세미콜론 제거 (하나만 허용)
    sql = sql.rstrip(';').strip()
    
    # 3. 금지 키워드 검사
    sql_upper = sql.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        # 단어 경계를 고려한 검사
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            raise ValueError(f"금지된 키워드가 포함되어 있습니다: {keyword}")
    
    # 4. LIMIT 절 확인 및 추가
    if not re.search(r'\bLIMIT\s+\d+', sql, re.IGNORECASE):
        logger.info("LIMIT 절이 없어 LIMIT 1000 추가")
        sql = sql + " LIMIT 1000"
    
    # 5. 날짜 조건 확인 (경고만, 실행은 허용)
    if 'sale_date' not in sql.lower():
        logger.warning("날짜 조건(sale_date)이 없습니다 - 전체 데이터 조회 주의")
    
    # 6. 주석 제거 (-- 및 /* */)
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    sql = sql.strip()
    
    # 7. 최종 세미콜론 추가
    sql = sql + ";"
    
    logger.info(f"SQL 검증 완료: {sql[:100]}...")
    return sql


# 레거시 함수들 (하위 호환성 유지)
def validate_sql_query(query: str) -> tuple[bool, str]:
    """
    SQL 쿼리 검증 (레거시)
    
    Args:
        query: 검증할 SQL 쿼리
        
    Returns:
        (is_valid, message) 튜플
    """
    try:
        validate_and_rewrite(query)
        return True, "쿼리가 유효합니다"
    except ValueError as e:
        return False, str(e)


def sanitize_sql_query(query: str) -> str:
    """
    SQL 쿼리 정제 (레거시)
    
    Args:
        query: SQL 쿼리
        
    Returns:
        정제된 SQL 쿼리
    """
    try:
        return validate_and_rewrite(query)
    except ValueError:
        return query

