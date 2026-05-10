from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import time
import threading
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# =====================核心代码=====================
app = FastAPI(title="多服务器集中监控站 ")
server_records = {}
OFFLINE_TIME = 600
FAIL_MAX = 3

def monitor_loop():
    while True:
        now = time.time()
        for ip, info in server_records.items():
            if now - info["last_time"] > 30:
                info["fail_count"] += 1
            if info["fail_count"] >= FAIL_MAX or (now - info["last_time"] > OFFLINE_TIME):
                info["status"] = "offline"
            else:
                info["status"] = "online"
        time.sleep(10)

threading.Thread(target=monitor_loop, daemon=True).start()

@app.post("/api/report")
async def report_data(request: Request):
    data = await request.json()
    ip = data.get("ip", "unknown")
    now = time.time()
    if ip not in server_records:
        server_records[ip] = {
            "info": data,
            "last_time": now,
            "fail_count": 0,
            "status": "online"
        }
    else:
        server_records[ip]["info"] = data
        server_records[ip]["last_time"] = now
        server_records[ip]["fail_count"] = 0
        server_records[ip]["status"] = "online"
    return {"code": 200, "msg": "ok"}

@app.get("/api/servers")
def get_servers():
    return {"data": server_records}

@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>信航多服务器集中监控站 </title>
    <style>
        body{background:#f5f7fa;font-family:"微软雅黑";padding:20px;}
        .container{max-width:1200px;margin:0 auto;}
        h1{text-align:center;color:#333;margin-bottom:30px;}
        .card{background:#fff;padding:20px;margin:12px 0;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.08);}
        .online{color:#27ae60;font-weight:bold;}
        .offline{color:#e74c3c;font-weight:bold;}
    </style>
</head>
<body>
    <div class="container">
        <h1>信阳航空技师学院·多服务器集中监控</h1>
        <div id="serverList"></div>
    </div>

    <script>
        async function load(){
            let res = await fetch("/api/servers");
            let json = await res.json();
            let html = "";
            for(let ip in json.data){
                let item = json.data[ip];
                let d = item.info;
                let state = item.status;
                let fail = item.fail_count;
                let stateText = state === "online" 
                    ? `<span class="online">✅ 在线</span>` 
                    : `<span class="offline">❌ 离线</span>`;
                html += `
                <div class="card">
                    <h3>${d.name} ｜ ${ip} ${stateText}</h3>
                    <p>CPU 占用：${d.cpu} %</p>
                    <p>内存占用：${d.mem_percent} %</p>
                    <p>磁盘占用：${d.disk_percent} %</p>
                    <p>运行时长：${d.uptime_hours} 小时</p>
                    <p>连续失败次数：${fail} / 3</p>
                </div>
                `;
            }
            document.getElementById("serverList").innerHTML = html;
        }
        load();
        setInterval(load, 5000);
    </script>
</body>
</html>
    """
# ==============================================================

# ===================== 主控UI =====================
import uvicorn
class ServerThread(QThread):
    log = pyqtSignal(str)
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
    def run(self):
        self.log.emit(f"✅ 服务启动成功 {self.host}:{self.port}")
        uvicorn.run(app, host=self.host, port=self.port)

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多服务器监控 · 主控服务端")
        self.setFixedSize(720,460)
        self.server = None
        self.running = False
        self.init_ui()

    def init_ui(self):
        w = QWidget()
        self.setCentralWidget(w)
        self.setStyleSheet("background-color:#12141d;")
        layout = QVBoxLayout(w)

        # 全局字体
        font = QFont("Microsoft YaHei",10)
        self.setFont(font)

        # 标题
        title = QLabel("🚀 信航监控服务端 | 主控面板")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color:#eeeeee;font-size:18px;font-weight:bold;padding:12px;")
        layout.addWidget(title)

        # IP端口
        bar1 = QHBoxLayout()
        self.ip_edit = QLineEdit("0.0.0.0")
        self.port_edit = QLineEdit("8000")
        for edit in [self.ip_edit,self.port_edit]:
            edit.setStyleSheet("background:#1e2230;color:#fff;padding:6px;border-radius:6px;border:1px solid #333a4a;")
        bar1.addWidget(QLabel("<font color='#cccccc'>监听IP：</font>"))
        bar1.addWidget(self.ip_edit)
        bar1.addWidget(QLabel("<font color='#cccccc'>端口：</font>"))
        bar1.addWidget(self.port_edit)
        layout.addLayout(bar1)

        # 按钮
        bar2 = QHBoxLayout()
        self.start_btn = QPushButton("▶ 启动服务")
        self.stop_btn = QPushButton("■ 关闭服务")
        self.open_web = QPushButton("🌐 打开监控面板")
        for btn in [self.start_btn,self.stop_btn,self.open_web]:
            btn.setStyleSheet("""
            QPushButton{
                background:#252b3b;color:#48a0ff;border-radius:6px;padding:8px;
                border:1px solid #36415e;
            }
            QPushButton:hover{background:#30394f;}
            """)
        bar2.addWidget(self.start_btn)
        bar2.addWidget(self.stop_btn)
        bar2.addWidget(self.open_web)
        layout.addLayout(bar2)

        # 状态
        self.status = QLabel("● 未运行")
        self.status.setStyleSheet("color:#ff5555;font-size:13px;margin:10px;")
        layout.addWidget(self.status)

        # 日志
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background:#0e1016;color:#bbbbbb;border-radius:8px;padding:8px;")
        layout.addWidget(self.log_box)

        # 绑定
        self.start_btn.clicked.connect(self.start_server)
        self.stop_btn.clicked.connect(self.stop_server)
        self.open_web.clicked.connect(self.open_browser)

    def start_server(self):
        if self.running:return
        h = self.ip_edit.text().strip()
        p = int(self.port_edit.text().strip())
        self.server = ServerThread(h,p)
        self.server.log.connect(self.append_log)
        self.server.start()
        self.running = True
        self.status.setText("● 运行中")
        self.status.setStyleSheet("color:#29d088;font-size:13px;margin:10px;")

    def stop_server(self):
        if self.running:
            self.append_log("⚠️ 关闭服务需要重启程序生效")
        self.running = False
        self.status.setText("● 已停止")
        self.status.setStyleSheet("color:#ff5555;font-size:13px;margin:10px;")

    def append_log(self,txt):
        self.log_box.append(f"[ {time.strftime('%H:%M:%S')} ] {txt}")

    def open_browser(self):
        import webbrowser
        ip = self.ip_edit.text().strip()
        port = self.port_edit.text().strip()
        webbrowser.open(f"http://{ip}:{port}")

if __name__ == "__main__":
    app_ui = QApplication(sys.argv)
    win = MainUI()
    win.show()
    sys.exit(app_ui.exec_())