# Database Schema & Seed Data

판매 데이터 PostgreSQL 스키마 및 샘플 데이터

## 테이블 구조

### dim_branch (지점 마스터)
- `branch_id` (PK): 지점 ID
- `branch_name`: 지점명 (고유)
- `region`: 지역
- `manager_name`: 지점장명
- `created_at`: 생성일시

### dim_product (상품 마스터)
- `product_id` (PK): 상품 ID
- `product_name`: 상품명 (고유)
- `product_category`: 상품 카테고리
- `description`: 상품 설명
- `created_at`: 생성일시

### fact_loan_sales (판매 팩트)
- `sale_id` (PK): 판매 ID
- `contract_id`: 계약 ID (고유)
- `branch_id` (FK): 지점 ID
- `product_id` (FK): 상품 ID
- `sale_date`: 판매일
- `disbursed_amount`: 판매액 (NUMERIC)
- `quantity`: 판매량 (기본값 1)
- `created_at`: 생성일시

## 샘플 데이터

### 지점 (5개)
- 서울본점, 부산지점, 대구지점, 대전지점, 광주지점

### 상품 (5개)
- 신차구매금융, **중고차금융**, 차량담보대출, 리스금융, 보증금융

### 판매 기록 (약 200건)
- 기간: 2024년 1월 ~ 9월
- 판매액: 900만 ~ 4,300만원
- 지점별 분포: 서울 50건, 부산 40건, 대구 45건, 대전 35건, 광주 30건

## 주요 쿼리

### 판매량 계산
```sql
SELECT dim_branch.branch_name, COUNT(DISTINCT contract_id) as sales_count
FROM fact_loan_sales
JOIN dim_branch ON fact_loan_sales.branch_id = dim_branch.branch_id
GROUP BY dim_branch.branch_id, dim_branch.branch_name
ORDER BY sales_count DESC;
```

### 판매액 계산
```sql
SELECT dim_branch.branch_name, SUM(disbursed_amount) as total_sales
FROM fact_loan_sales
JOIN dim_branch ON fact_loan_sales.branch_id = dim_branch.branch_id
GROUP BY dim_branch.branch_id, dim_branch.branch_name
ORDER BY total_sales DESC;
```

### 상품별 판매현황
```sql
SELECT dim_product.product_name, 
       COUNT(DISTINCT contract_id) as sales_count,
       SUM(disbursed_amount) as total_sales
FROM fact_loan_sales
JOIN dim_product ON fact_loan_sales.product_id = dim_product.product_id
GROUP BY dim_product.product_id, dim_product.product_name
ORDER BY total_sales DESC;
```

## Supabase 배포

### 1. SQL 실행 방법
1. Supabase 대시보드 → SQL Editor
2. `schema.sql` 복사 후 실행
3. `seed.sql` 복사 후 실행

### 2. 데이터 확인
```sql
SELECT COUNT(*) FROM dim_branch;   -- 5
SELECT COUNT(*) FROM dim_product;  -- 5
SELECT COUNT(*) FROM fact_loan_sales;  -- ~200
```

## 백엔드 연결

### 환경 변수
```
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]
```

### 데이터베이스 테스트
- 백엔드 시작 시 `db.test_db_connection()` 자동 실행
- `/health` 엔드포인트로 연결 확인 가능
