with open(r'C:\workspace\monorepo\frontend\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# BACKEND_URL 변경
content = content.replace(
    'const BACKEND_URL = "http://localhost:8000";',
    'const BACKEND_URL = "http://127.0.0.1:8000";'
)

with open(r'C:\workspace\monorepo\frontend\app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ app.js 수정 완료: BACKEND_URL = http://127.0.0.1:8000')
