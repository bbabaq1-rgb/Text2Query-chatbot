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

    const loadingMessage = addLoadingMessage();

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

function addLoadingMessage() {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message";

    const p = document.createElement("p");
    p.innerHTML = '생각 중<span class="loading-dots"></span>';
    
    messageDiv.appendChild(p);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}

function addBotMessage(data) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message";

    // 메시지 내용을 담을 컨테이너 (세로 정렬을 위해)
    const contentWrapper = document.createElement("div");
    contentWrapper.style.display = "flex";
    contentWrapper.style.flexDirection = "column";
    contentWrapper.style.maxWidth = "80%"; // 전체 너비 제한
    contentWrapper.style.gap = "10px"; // 요소 간 간격

    // SQL이 있으면 먼저 표시 (상단)
    if (data.sql) {
        const sqlDetails = document.createElement("details");
        const sqlSummary = document.createElement("summary");
        sqlSummary.textContent = "생성된 SQL 쿼리 보기";
        sqlSummary.style.cursor = "pointer";
        sqlSummary.style.color = "#007bff";
        sqlSummary.style.marginBottom = "5px";
        sqlSummary.style.fontWeight = "500";
        
        const sqlPre = document.createElement("pre");
        sqlPre.style.background = "#f5f5f5";
        sqlPre.style.padding = "10px";
        sqlPre.style.borderRadius = "5px";
        sqlPre.style.overflowX = "auto";
        sqlPre.style.fontSize = "12px";
        sqlPre.style.marginTop = "5px";
        sqlPre.textContent = data.sql;
        
        sqlDetails.appendChild(sqlSummary);
        sqlDetails.appendChild(sqlPre);
        contentWrapper.appendChild(sqlDetails);
    }

    // 답변 텍스트 (하단)
    const answerP = document.createElement("p");
    answerP.textContent = data.answer;
    answerP.style.maxWidth = "100%"; // wrapper가 이미 너비를 제한하므로 100%로 변경
    contentWrapper.appendChild(answerP);

    // 테이블 데이터가 있으면 표시
    if (data.columns && data.columns.length > 0 && data.rows && data.rows.length > 0) {
        const tableContainer = document.createElement("div");
        tableContainer.style.marginTop = "5px";
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
                
                let displayValue = value;
                if (typeof value === 'number') {
                    // 소숫점 첫째 자리에서 반올림 (정수로 만듦) 및 3자리마다 콤마
                    displayValue = Math.round(value).toLocaleString();
                } else if (value === null || value === undefined) {
                    displayValue = "";
                }

                td.textContent = displayValue;
                td.style.border = "1px solid #ddd";
                td.style.padding = "8px";
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        tableContainer.appendChild(table);
        contentWrapper.appendChild(tableContainer);
    }

    messageDiv.appendChild(contentWrapper);
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
