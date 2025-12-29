"""Vanna AI - Text-to-SQL 프레임워크"""

import os
import logging
from typing import Optional

try:
    import vanna
    from vanna.remote import VannaDefault
    VANNA_AVAILABLE = True
except ImportError:
    VANNA_AVAILABLE = False

logger = logging.getLogger(__name__)

# Vanna 클라이언트 인스턴스
_vanna_instance = None


def get_vanna_client():
    """Vanna 클라이언트 가져오기 (싱글톤)"""
    global _vanna_instance
    
    if _vanna_instance is None:
        _vanna_instance = initialize_vanna()
    
    return _vanna_instance


def initialize_vanna():
    """Vanna 초기화 및 스키마 학습"""
    
    if not VANNA_AVAILABLE:
        logger.warning("Vanna 패키지가 설치되지 않음")
        return None
    
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    if not api_key:
        logger.warning("LLM_API_KEY가 설정되지 않음")
        return None
    
    try:
        # VannaDefault 사용 (OpenAI 기본)
        vn = VannaDefault(api_key=api_key, model=model)
        logger.info(f"Vanna 초기화 완료 (모델: {model})")
        
        # 스키마 학습
        train_vanna(vn)
        
        return vn
        
    except Exception as e:
        logger.error(f"Vanna 초기화 실패: {e}")
        return None


def train_vanna(vn):
    """데이터베이스 스키마 및 KPI 정의 학습"""
    
    # 1. DDL 학습 - 테이블 스키마
    ddl_statements = [
        """
        CREATE TABLE dim_branch (
            branch_id INT PRIMARY KEY,
            branch_name VARCHAR(100) NOT NULL,
            region VARCHAR(50),
            manager_name VARCHAR(100)
        );
        """,
        """
        CREATE TABLE dim_product (
            product_id INT PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            product_category VARCHAR(50),
            description TEXT
        );
        """,
        """
        CREATE TABLE fact_loan_sales (
            contract_id VARCHAR(50) PRIMARY KEY,
            branch_id INT,
            product_id INT,
            sale_date DATE NOT NULL,
            disbursed_amount BIGINT NOT NULL,
            quantity INT DEFAULT 1,
            FOREIGN KEY (branch_id) REFERENCES dim_branch(branch_id),
            FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
        );
        """
    ]
    
    for ddl in ddl_statements:
        vn.train(ddl=ddl)
    
    logger.info("DDL 학습 완료")
    
    # 2. Documentation 학습 - 비즈니스 용어 및 KPI 정의
    documentations = [
        """
        판매량(계약 건수)은 fact_loan_sales 테이블의 contract_id를 카운트하여 계산합니다.
        예: SELECT COUNT(*) FROM fact_loan_sales 또는 COUNT(DISTINCT contract_id)
        """,
        """
        판매액(대출 실행액)은 fact_loan_sales 테이블의 disbursed_amount를 합산하여 계산합니다.
        예: SELECT SUM(disbursed_amount) FROM fact_loan_sales
        단위는 원(KRW)이며, 억원으로 표시할 경우 100000000으로 나눕니다.
        """,
        """
        지점별 실적을 조회할 때는 dim_branch 테이블과 조인하여 branch_name을 사용합니다.
        예: SELECT b.branch_name, SUM(f.disbursed_amount)
            FROM fact_loan_sales f
            JOIN dim_branch b ON f.branch_id = b.branch_id
            GROUP BY b.branch_name
        """,
        """
        상품별 실적을 조회할 때는 dim_product 테이블과 조인하여 product_name을 사용합니다.
        예: SELECT p.product_name, COUNT(*)
            FROM fact_loan_sales f
            JOIN dim_product p ON f.product_id = p.product_id
            GROUP BY p.product_name
        """,
        """
        기간별 조회 시 sale_date 컬럼을 사용합니다.
        '지난 달', '이번 달'과 같은 상대적 기간은 현재 날짜 기준으로 계산합니다.
        예: WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
            AND sale_date < DATE_TRUNC('month', CURRENT_DATE)
        """,
        """
        '서울본점', '부산지점'과 같은 지점명은 dim_branch.branch_name에 저장되어 있습니다.
        지점명으로 검색할 때는 LIKE 연산자를 사용할 수 있습니다.
        예: WHERE branch_name LIKE '%서울%'
        """,
        """
        대출 상품은 product_category로 분류됩니다 (신차, 중고차, 담보대출, 리스, 보증 등).
        상품 카테고리별 조회 시: WHERE product_category = '신차'
        """
    ]
    
    for doc in documentations:
        vn.train(documentation=doc)
    
    logger.info("Documentation 학습 완료")
    
    # 3. SQL 예제 학습 (선택사항)
    sql_examples = [
        {
            "question": "지난 달 전체 판매액은?",
            "sql": """
                SELECT SUM(disbursed_amount) AS total_sales_amount
                FROM fact_loan_sales
                WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
                  AND sale_date < DATE_TRUNC('month', CURRENT_DATE)
            """
        },
        {
            "question": "서울본점의 이번 달 계약 건수는?",
            "sql": """
                SELECT COUNT(*) AS contract_count
                FROM fact_loan_sales f
                JOIN dim_branch b ON f.branch_id = b.branch_id
                WHERE b.branch_name LIKE '%서울본점%'
                  AND sale_date >= DATE_TRUNC('month', CURRENT_DATE)
            """
        },
        {
            "question": "상위 5개 지점의 판매액은?",
            "sql": """
                SELECT b.branch_name, SUM(f.disbursed_amount) AS total_sales
                FROM fact_loan_sales f
                JOIN dim_branch b ON f.branch_id = b.branch_id
                GROUP BY b.branch_name
                ORDER BY total_sales DESC
                LIMIT 5
            """
        }
    ]
    
    for example in sql_examples:
        vn.train(question=example["question"], sql=example["sql"])
    
    logger.info("SQL 예제 학습 완료")


def generate_sql_with_vanna(question: str) -> Optional[str]:
    """Vanna를 사용하여 자연어 질문을 SQL로 변환"""
    vn = get_vanna_client()
    
    if vn is None:
        logger.error("Vanna 클라이언트가 초기화되지 않음")
        return None
    
    try:
        # Vanna로 SQL 생성
        sql = vn.generate_sql(question=question)
        
        if sql:
            logger.info(f"Vanna로 생성된 SQL: {sql[:200]}...")
            return sql.strip()
        else:
            logger.warning("Vanna가 SQL을 생성하지 못했습니다")
            return None
            
    except Exception as e:
        logger.error(f"Vanna SQL 생성 실패: {e}")
        return None
