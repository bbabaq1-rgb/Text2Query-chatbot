import urllib.request

try:
    with urllib.request.urlopen('http://localhost:3000/') as response:
        content = response.read().decode('utf-8')
        print(f'Status: {response.status}')
        print(f'Content length: {len(content)} bytes')
        if len(content) > 0:
            print('\n✓ 서버가 응답함!')
            print(f'\n처음 300글자:\n{content[:300]}\n...')
        else:
            print('✗ 빈 응답')
except Exception as e:
    print(f'✗ 오류: {type(e).__name__}: {e}')
