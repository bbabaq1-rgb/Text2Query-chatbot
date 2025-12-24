-- 판매 데이터 스키마
-- Supabase PostgreSQL

-- 1. 지점 마스터 (dim_branch)
CREATE TABLE IF NOT EXISTS dim_branch (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL UNIQUE,
    region VARCHAR(50),
    manager_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 상품 마스터 (dim_product)
CREATE TABLE IF NOT EXISTS dim_product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL UNIQUE,
    product_category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 판매 팩트 (fact_loan_sales)
CREATE TABLE IF NOT EXISTS fact_loan_sales (
    sale_id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) NOT NULL UNIQUE,
    branch_id INTEGER NOT NULL REFERENCES dim_branch(branch_id),
    product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
    sale_date DATE NOT NULL,
    disbursed_amount NUMERIC(15, 2) NOT NULL,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (쿼리 성능 개선)
CREATE INDEX IF NOT EXISTS idx_fact_sales_branch ON fact_loan_sales(branch_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON fact_loan_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON fact_loan_sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_fact_sales_contract ON fact_loan_sales(contract_id);
