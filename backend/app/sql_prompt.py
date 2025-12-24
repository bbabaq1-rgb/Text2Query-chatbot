"""SQL 생성을 위한 프롬프트 템플릿"""

# 데이터베이스 스키마 정의
SCHEMA_INFO = """
## 데이터베이스 스키마

### 1. dim_branch (지점 테이블)
- branch_id (INT, PRIMARY KEY): 지점 ID
- branch_name (VARCHAR): 지점명 (예: '서울본점', '부산지점')
- region (VARCHAR): 지역 (예: '서울', '부산')
- manager_name (VARCHAR): 담당자명

### 2. dim_product (상품 테이블)
- product_id (INT, PRIMARY KEY): 상품 ID
- product_name (VARCHAR): 상품명 (예: '신차구매금융', '중고차금융')
- product_category (VARCHAR): 상품 카테고리 (예: '신차', '중고차', '담보대출', '리스', '보증')
- description (VARCHAR): 상품 설명

### 3. fact_loan_sales (대출 판매 실적 테이블)
- contract_id (VARCHAR, PRIMARY KEY): 계약 ID
- branch_id (INT, FOREIGN KEY): 지점 ID
- product_id (INT, FOREIGN KEY): 상품 ID
- sale_date (DATE): 판매일자
- disbursed_amount (BIGINT): 대출 실행금액 (원 단위)
- quantity (INT): 수량 (보통 1)

## 테이블 관계
- fact_loan_sales.branch_id → dim_branch.branch_id
- fact_loan_sales.product_id → dim_product.product_id
"""

# KPI 정의
KPI_DEFINITIONS = """
## 주요 KPI 정의

1. **판매량 (계약 건수)**
   - COUNT(DISTINCT contract_id) 또는 COUNT(*)
   - 모든 계약 건수 집계

2. **판매액 (대출 실행액)**
   - SUM(disbursed_amount)
   - 단위: 원 (억원으로 표시할 경우 /100000000)

3. **지점별 실적**
   - dim_branch.branch_name으로 그룹화
   - JOIN을 통해 지점명 표시

4. **상품별 실적**
   - dim_product.product_name으로 그룹화
   - JOIN을 통해 상품명 표시

5. **기간별 집계**
   - sale_date로 필터링 및 그룹화
   - 월별: DATE_TRUNC('month', sale_date)
   - 분기별: DATE_TRUNC('quarter', sale_date)
"""

# SQL 작성 규칙
SQL_RULES = """
## SQL 작성 규칙

1. **필수 사항**
   - SELECT 문만 사용
   - 세미콜론(;)은 쿼리 끝에 한 번만 사용
   - 테이블명은 정확히 명시 (dim_branch, dim_product, fact_loan_sales)
   - 컬럼명은 정확히 명시

2. **권장 사항**
   - 명확한 별칭(alias) 사용
   - JOIN 시 명시적 조인 조건 작성
   - 날짜 필터링 시 sale_date 컬럼 사용
   - 정렬이 필요한 경우 ORDER BY 추가
   - 결과 제한이 필요한 경우 LIMIT 사용

3. **금지 사항**
   - DROP, TRUNCATE, INSERT, UPDATE, DELETE 등 DML/DDL
   - 여러 개의 SQL 문 (;로 구분된 다중 쿼리)
   - 시스템 테이블이나 정보 스키마 접근

4. **날짜 처리**
   - PostgreSQL 날짜 함수 사용
   - 예: WHERE sale_date >= '2024-01-01' AND sale_date < '2024-02-01'
   - 예: DATE_TRUNC('month', sale_date) AS month
"""


def build_prompt(user_question: str) -> str:
    """
    사용자 질문을 기반으로 SQL 생성 프롬프트 구성
    
    Args:
        user_question: 사용자의 자연어 질문
        
    Returns:
        LLM에 전달할 완전한 프롬프트
    """
    prompt = f"""당신은 PostgreSQL SQL 전문가입니다. 다음 데이터베이스 스키마를 참고하여 사용자 질문에 대한 SQL 쿼리를 생성하세요.

{SCHEMA_INFO}

{KPI_DEFINITIONS}

{SQL_RULES}

## 사용자 질문
{user_question}

## 요구사항
- 위 질문에 답변할 수 있는 PostgreSQL SELECT 쿼리를 생성하세요
- 한국어 질문이므로 적절한 테이블과 컬럼을 매핑하세요
- 명확한 컬럼명과 별칭을 사용하세요
- 필요시 JOIN을 사용하여 지점명, 상품명을 포함하세요
- 결과가 많을 경우 LIMIT을 추가하세요
- SQL 쿼리만 반환하고 설명은 포함하지 마세요

SQL:"""
    
    return prompt
