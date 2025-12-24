import os
os.chdir(r'C:\workspace\monorepo\frontend')

# index.html
html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>판매 데이터 조회 챗봇</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <div class="chat-box">
            <div class="chat-header">
                <h1>💬 판매 데이터 조회 챗봇</h1>
                <p class="subtitle">자연어로 판매 정보를 조회하세요</p>
            </div>

            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    <p>안녕하세요! 판매 데이터에 대해 물어보세요.</p>
                </div>
            </div>

            <div class="chat-input-area">
                <form id="chatForm">
                    <input 
                        type="text" 
                        id="questionInput" 
                        placeholder="질문을 입력하세요... 예: 지난 월 판매액은?"
                        autocomplete="off"
                    >
                    <button type="submit" class="send-btn">전송</button>
                </form>
            </div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ index.html 생성")

# app.js
js = '''/**
 * Frontend App
 * 
 * 배포 후 BACKEND_URL을 실제 백엔드 URL로 변경하세요
 * 예: https://your-backend.onrender.com
 */

// ============ 설정 ============
// TODO: 배포 후 이 URL을 실제 백엔드 URL로 변경하세요
const BACKEND_URL = "http://localhost:8000";

// ============ DOM 요소 ============
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const chatMessages = document.getElementById("chatMessages");

// ============ 이벤트 리스너 ============
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const question = questionInput.value.trim();
    if (!question) return;
    
    // 사용자 메시지 추가
    addMessage(question, "user");
    questionInput.value = "";
    
    // 로딩 상태 표시
    const loadingMessage = addMessage("생각 중...", "bot");
    
    try {
        // 백엔드에 요청
        const response = await fetch(`${BACKEND_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // 로딩 메시지 제거
        loadingMessage.remove();
        
        // 봇 응답 추가
        addMessage(data.answer, "bot");
        
    } catch (error) {
        // 로딩 메시지 제거
        loadingMessage.remove();
        
        // 에러 메시지 표시
        addMessage(
            `❌ 오류 발생: ${error.message}\\n\\n` +
            `백엔드 URL: ${BACKEND_URL}\\n` +
            `index.html 또는 app.js에서 BACKEND_URL을 확인하세요.`,
            "bot"
        );
        console.error("Chat error:", error);
    }
});

// ============ 함수 ============
/**
 * 메시지를 채팅창에 추가
 * @param {string} text - 메시지 텍스트
 * @param {string} sender - "user" 또는 "bot"
 * @returns {HTMLElement} 추가된 메시지 요소
 */
function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;
    
    const p = document.createElement("p");
    p.textContent = text;
    
    messageDiv.appendChild(p);
    chatMessages.appendChild(messageDiv);
    
    // 자동 스크롤
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// ============ 초기화 ============
// 페이지 로드 시 백엔드 연결 확인
window.addEventListener("load", async () => {
    try {
        const response = await fetch(`${BACKEND_URL}/health`);
        if (response.ok) {
            console.log("✓ 백엔드 연결 성공");
        }
    } catch (error) {
        console.warn("⚠️ 백엔드 연결 실패:", error.message);
    }
});
'''

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("✓ app.js 생성")

# styles.css
css = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.container {
    width: 100%;
    max-width: 600px;
}

.chat-box {
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    height: 600px;
    overflow: hidden;
}

.chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    text-align: center;
}

.chat-header h1 {
    font-size: 24px;
    margin-bottom: 8px;
}

.chat-header .subtitle {
    font-size: 14px;
    opacity: 0.9;
}

.chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    background: #f9f9f9;
}

.message {
    margin-bottom: 15px;
    display: flex;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.user-message {
    justify-content: flex-end;
}

.user-message p {
    background: #667eea;
    color: white;
    padding: 10px 15px;
    border-radius: 18px;
    max-width: 70%;
    word-wrap: break-word;
    font-size: 14px;
}

.bot-message {
    justify-content: flex-start;
}

.bot-message p {
    background: #e8e8e8;
    color: #333;
    padding: 10px 15px;
    border-radius: 18px;
    max-width: 70%;
    word-wrap: break-word;
    font-size: 14px;
    line-height: 1.4;
}

.chat-input-area {
    padding: 15px;
    background: white;
    border-top: 1px solid #e0e0e0;
}

#chatForm {
    display: flex;
    gap: 10px;
}

#questionInput {
    flex: 1;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 24px;
    font-size: 14px;
    outline: none;
    transition: border-color 0.3s;
}

#questionInput:focus {
    border-color: #667eea;
}

#questionInput::placeholder {
    color: #999;
}

.send-btn {
    padding: 12px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 24px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: transform 0.2s, box-shadow 0.2s;
}

.send-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.send-btn:active {
    transform: translateY(0);
}

/* 반응형 디자인 */
@media (max-width: 480px) {
    .chat-box {
        height: 100vh;
        max-height: 100vh;
        border-radius: 0;
    }
    
    .user-message p,
    .bot-message p {
        max-width: 85%;
    }
}
'''

with open('styles.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("✓ styles.css 생성")

print("\\n✓ 모든 파일 생성 완료!")
