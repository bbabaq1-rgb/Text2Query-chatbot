"""SQL 검증 및 가드레일 함수"""

import re

# 금지된 키워드
FORBIDDEN_KEYWORDS = [
    "DROP",
    "DELETE",
    "INSERT",
    "UPDATE",
    "TRUNCATE",
    "ALTER",
    "CREATE",
    "GRANT",
    "REVOKE",
]

def validate_sql_query(query: str) -> tuple[bool, str]:
    """
    SQL 쿼리 검증
    
    Args:
        query: 검증할 SQL 쿼리
        
    Returns:
        (is_valid, message) 튜플
    """
    query_upper = query.upper().strip()
    
    # 1. SELECT만 허용
    if not query_upper.startswith("SELECT"):
        return False, "SELECT 쿼리만 허용됩니다"
    
    # 2. 금지 키워드 확인
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf'\b{keyword}\b', query_upper):
            return False, f"'{keyword}' 키워드는 사용할 수 없습니다"
    
    # 3. LIMIT 강제 (추후 쿼리 자동 추가 가능)
    # 현재는 경고만 반환
    if "LIMIT" not in query_upper:
        return True, "LIMIT 절을 추가하는 것을 권장합니다"
    
    return True, "쿼리가 유효합니다"


def sanitize_sql_query(query: str) -> str:
    """
    SQL 쿼리에 LIMIT을 자동 추가 (미구현 상태)
    
    Args:
        query: SQL 쿼리
        
    Returns:
        정제된 SQL 쿼리
    """
    # TODO: 실제 구현 필요
    return query
