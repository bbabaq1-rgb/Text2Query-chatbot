#!/usr/bin/env python
"""설정 및 환경 테스트 스크립트"""

import sys
from pathlib import Path

print("=" * 60)
print("모노레포 설정 테스트")
print("=" * 60)

# 1. Python 버전 확인
print(f"\n✓ Python 버전: {sys.version}")
print(f"✓ Python 경로: {sys.executable}")

# 2. 필수 파일 확인
backend_dir = Path(__file__).parent
required_files = [
    "app/main.py",
    "app/settings.py",
    "app/cors.py",
    "app/guardrails.py",
    "app/db.py",
    "requirements.txt",
    ".env.example",
    ".env",
]

print("\n[백엔드 파일 확인]")
for file in required_files:
    path = backend_dir / file
    status = "✓" if path.exists() else "✗"
    print(f"{status} {file}")

# 3. .env 파일 내용 확인
print("\n[환경 변수 설정]")
env_file = backend_dir / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key = line.split("=")[0]
                print(f"  ✓ {key}")
else:
    print("  ✗ .env 파일 없음")

# 4. 패키지 의존성 확인
print("\n[필수 패키지 확인]")
packages = ["fastapi", "uvicorn", "sqlalchemy", "psycopg2"]
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} (설치 필요)")

print("\n" + "=" * 60)
print("설정 테스트 완료")
print("=" * 60)
