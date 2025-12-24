"""LLM 클라이언트 - OpenAI/Anthropic 지원"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generate_sql(prompt: str) -> str:
    """
    LLM을 호출하여 자연어 질문을 SQL로 변환
    
    Args:
        prompt: SQL 생성 프롬프트 (스키마 정보 + 사용자 질문)
        
    Returns:
        생성된 SQL 쿼리문
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    api_key = os.getenv("LLM_API_KEY")
    
    if not api_key:
        logger.warning("LLM_API_KEY가 설정되지 않음 - 샘플 SQL 반환")
        return "SELECT COUNT(*) as total FROM fact_loan_sales;"
    
    if provider == "openai":
        return _generate_with_openai(prompt, api_key)
    elif provider == "anthropic":
        return _generate_with_anthropic(prompt, api_key)
    else:
        raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")


def _generate_with_openai(prompt: str, api_key: str) -> str:
    """OpenAI API를 사용한 SQL 생성"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a SQL expert. Generate ONLY the SQL query without any explanation, markdown formatting, or additional text. Return pure SQL only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql = response.choices[0].message.content.strip()
        
        # 마크다운 코드 블록 제거
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        logger.info(f"OpenAI로 생성된 SQL: {sql[:100]}...")
        return sql
        
    except ImportError:
        logger.error("openai 패키지가 설치되지 않음")
        raise
    except Exception as e:
        logger.error(f"OpenAI API 호출 실패: {e}")
        raise


def _generate_with_anthropic(prompt: str, api_key: str) -> str:
    """Anthropic Claude API를 사용한 SQL 생성"""
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
        
        response = client.messages.create(
            model=model,
            max_tokens=500,
            temperature=0.1,
            system="You are a SQL expert. Generate ONLY the SQL query without any explanation, markdown formatting, or additional text. Return pure SQL only.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        sql = response.content[0].text.strip()
        
        # 마크다운 코드 블록 제거
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        logger.info(f"Anthropic로 생성된 SQL: {sql[:100]}...")
        return sql
        
    except ImportError:
        logger.error("anthropic 패키지가 설치되지 않음")
        raise
    except Exception as e:
        logger.error(f"Anthropic API 호출 실패: {e}")
        raise
