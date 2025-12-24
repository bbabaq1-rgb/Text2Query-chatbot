/**
 * Frontend App
 */

const BACKEND_URL = "http://127.0.0.1:8000";

const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const chatMessages = document.getElementById("chatMessages");

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const question = questionInput.value.trim();
    if (!question) return;

    addMessage(question, "user");
    questionInput.value = "";

    const loadingMessage = addMessage("생각 중...", "bot");

    try {
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
        loadingMessage.remove();
        addMessage(data.answer, "bot");

    } catch (error) {
        loadingMessage.remove();
        addMessage(
            `❌ 오류: ${error.message}\n\n` +
            `BACKEND_URL: ${BACKEND_URL}`,
            "bot"
        );
        console.error("Chat error:", error);
    }
});

function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    const p = document.createElement("p");
    p.textContent = text;

    messageDiv.appendChild(p);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}

window.addEventListener("load", async () => {
    try {
        const response = await fetch(`${BACKEND_URL}/health`);
        if (response.ok) {
            console.log("✅ 백엔드 연결 성공");
        }
    } catch (error) {
        console.warn("⚠️ 백엔드 연결 실패:", error.message);
    }
});
