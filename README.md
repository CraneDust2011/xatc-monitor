# 多服务器状态监控系统

> 一套轻量、美观、可跨平台部署的服务器状态监控工具，支持 Windows 一键运行。

## ✨ 功能亮点
- 🏠 **服务端主控面板**：黑色商务风 UI，支持自定义 IP/端口、热启动/热停止、一键打开监控网页。
- 📊 **客户端实时上报**：自动采集服务器 CPU、内存、磁盘使用率，稳定可靠。
- 🌐 **网页监控面板**：自动刷新，实时查看所有客户端状态，支持在线/离线高亮显示。
- 📦 **一键打包**：支持用 PyInstaller 打包成单文件 EXE，无需 Python 环境。

## 🚀 快速开始

### 方式一：直接下载发行版（推荐）
1. 前往 [Releases 页面](https://github.com/CraneDust2011/xatc-monitor/releases/tag/monitor)
2. 下载最新版本的 `server.exe` 和 `client.exe`
3. 先运行 `monitor_Server_Service_Windows_x86.exe`，启动服务端
4. 再运行 `client_windows_x86.exe`，修改服务端地址即可连接

### 方式二：源码运行
#### 1. 安装依赖
```bash
pip install fastapi uvicorn pyqt5 psutil requests
