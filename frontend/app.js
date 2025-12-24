/**
 * Frontend App
 */

const BACKEND_URL = "https://loan-sales-backend.onrender.com";

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
        
        // 답변 메시지 추가
        addBotMessage(data);

    } catch (error) {
        loadingMessage.remove();
        addMessage(
            `오류: ${error.message}\n\n` +
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

function addBotMessage(data) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message";

    // 답변 텍스트
    const answerP = document.createElement("p");
    answerP.textContent = data.answer;
    messageDiv.appendChild(answerP);

    // SQL이 있으면 표시 (접어서)
    if (data.sql) {
        const sqlDetails = document.createElement("details");
        const sqlSummary = document.createElement("summary");
        sqlSummary.textContent = "생성된 SQL 쿼리 보기";
        sqlSummary.style.cursor = "pointer";
        sqlSummary.style.color = "#007bff";
        sqlSummary.style.marginTop = "10px";
        
        const sqlPre = document.createElement("pre");
        sqlPre.style.background = "#f5f5f5";
        sqlPre.style.padding = "10px";
        sqlPre.style.borderRadius = "5px";
        sqlPre.style.overflowX = "auto";
        sqlPre.style.fontSize = "12px";
        sqlPre.textContent = data.sql;
        
        sqlDetails.appendChild(sqlSummary);
        sqlDetails.appendChild(sqlPre);
        messageDiv.appendChild(sqlDetails);
    }

    // 테이블 데이터가 있으면 표시
    if (data.columns && data.columns.length > 0 && data.rows && data.rows.length > 0) {
        const tableContainer = document.createElement("div");
        tableContainer.style.marginTop = "15px";
        tableContainer.style.overflowX = "auto";
        
        const table = document.createElement("table");
        table.style.width = "100%";
        table.style.borderCollapse = "collapse";
        table.style.fontSize = "13px";

        // 헤더
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        data.columns.forEach(col => {
            const th = document.createElement("th");
            th.textContent = col;
            th.style.border = "1px solid #ddd";
            th.style.padding = "8px";
            th.style.background = "#f0f0f0";
            th.style.textAlign = "left";
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // 바디
        const tbody = document.createElement("tbody");
        data.rows.forEach((row, idx) => {
            const tr = document.createElement("tr");
            if (idx % 2 === 0) {
                tr.style.background = "#f9f9f9";
            }
            data.columns.forEach(col => {
                const td = document.createElement("td");
                const value = row[col];
                td.textContent = value !== null && value !== undefined ? value : "";
                td.style.border = "1px solid #ddd";
                td.style.padding = "8px";
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        tableContainer.appendChild(table);
        messageDiv.appendChild(tableContainer);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}

window.addEventListener("load", async () => {
    try {
        const response = await fetch(`${BACKEND_URL}/health`);
        if (response.ok) {
            console.log("??백엔???�결 ?�공");
        }
    } catch (error) {
        console.warn("?�️ 백엔???�결 ?�패:", error.message);
    }
});
