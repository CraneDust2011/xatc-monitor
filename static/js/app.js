// 渲染服务器状态
function renderServerStatus(statusData) {
    const cardList = document.getElementById("cardList");
    let html = "";

    servers.forEach(item => {
        const isOnline = statusData[item.ip] || false;
        const dotClass = isOnline ? "dot online" : "dot offline";
        const stateText = isOnline ? "✅ 在线" : "❌ 离线";

        html += `
        <div class="card">
            <div class="${dotClass}"></div>
            <div class="info">
                <div class="name">
                    ${item.name}
                    <span class="type">${item.type}</span>
                </div>
                <div class="ip">
                    IP：${item.ip} | 端口：${item.port} | 状态：${stateText}
                </div>
            </div>
        </div>
        `;
    });

    cardList.innerHTML = html;
}

// 刷新状态
async function refreshStatus() {
    try {
        const res = await fetch("/api/status");
        const data = await res.json();
        renderServerStatus(data.data);
    } catch (err) {
        console.error("刷新失败", err);
    }
}

// 初始化
window.onload = function () {
    refreshStatus();
    setInterval(refreshStatus, 8000);
};