# monitor.py 服务器硬件监控插件
import psutil
import time
import json

def get_system_info():
    """获取服务器CPU、内存、磁盘、运行时间"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存
        mem = psutil.virtual_memory()
        mem_total = round(mem.total / 1024 / 1024 / 1024, 2)
        mem_used = round(mem.used / 1024 / 1024 / 1024, 2)
        mem_percent = mem.percent

        # 磁盘
        disk = psutil.disk_usage("C:\\")
        disk_total = round(disk.total / 1024 / 1024 / 1024, 2)
        disk_used = round(disk.used / 1024 / 1024 / 1024, 2)
        disk_percent = disk.percent

        # 运行时间
        boot_time = psutil.boot_time()
        now = time.time()
        uptime_seconds = now - boot_time
        uptime = round(uptime_seconds / 3600, 2)

        return {
            "cpu": cpu_percent,
            "mem_total": mem_total,
            "mem_used": mem_used,
            "mem_percent": mem_percent,
            "disk_total": disk_total,
            "disk_used": disk_used,
            "disk_percent": disk_percent,
            "uptime_hours": uptime
        }
    except:
        return {}

def save_log(data):
    """保存监控记录"""
    try:
        with open("log.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass