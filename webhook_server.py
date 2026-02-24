"""
Webhook Server for Pishro Bot
سرور Webhook برای بات پیشرو با Dashboard لاگ‌ها
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncio
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pishro Bot Webhook Server")

# Store logs in memory
logs_buffer: List[Dict] = []
MAX_LOGS = 500


class LogManager:
    """Manage logs for web dashboard."""
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.last_size = 0
    
    def read_logs(self, limit: int = 100) -> List[str]:
        """Read logs from file."""
        if not self.log_file.exists():
            return []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return lines[-limit:]
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            return []
    
    def get_formatted_logs(self, limit: int = 100) -> List[Dict]:
        """Get formatted logs for API."""
        logs = self.read_logs(limit)
        formatted = []
        
        for line in logs:
            try:
                # Parse log line
                if " - " in line:
                    parts = line.strip().split(" - ", 3)
                    if len(parts) >= 4:
                        timestamp, logger_name, level, message = parts[0], parts[1], parts[2], parts[3]
                        
                        # Determine log level color
                        level_color = {
                            'DEBUG': '#666',
                            'INFO': '#0088cc',
                            'WARNING': '#ff9800',
                            'ERROR': '#f44336',
                            'CRITICAL': '#d32f2f'
                        }.get(level, '#000')
                        
                        formatted.append({
                            'timestamp': timestamp,
                            'logger': logger_name,
                            'level': level,
                            'message': message,
                            'color': level_color
                        })
            except Exception as e:
                formatted.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
                    'logger': 'Parser',
                    'level': 'ERROR',
                    'message': f"Parse error: {line}",
                    'color': '#f44336'
                })
        
        return formatted


log_manager = LogManager("/home/sina/Documents/project/pishro-bot/logs/bot.log")


# ==================== Web Routes ====================

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Dashboard for logs and bot management."""
    return """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pishro Bot Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .status {
            display: flex;
            gap: 30px;
            margin-top: 20px;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.active {
            background: #4caf50;
        }
        
        .status-indicator.inactive {
            background: #f44336;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
        }
        
        .btn-danger {
            background: #f44336;
            color: white;
        }
        
        .btn-danger:hover {
            background: #d32f2f;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(244, 67, 54, 0.4);
        }
        
        .btn-refresh {
            background: #4caf50;
            color: white;
        }
        
        .btn-refresh:hover {
            background: #45a049;
            transform: translateY(-2px);
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 30px;
        }
        
        .logs-panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .logs-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logs-container {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        
        .log-line {
            padding: 8px 12px;
            margin-bottom: 4px;
            border-radius: 4px;
            background: white;
            border-left: 4px solid;
            display: flex;
            gap: 10px;
        }
        
        .log-timestamp {
            color: #999;
            flex-shrink: 0;
            min-width: 150px;
        }
        
        .log-level {
            font-weight: bold;
            flex-shrink: 0;
            min-width: 70px;
        }
        
        .log-message {
            flex: 1;
            word-break: break-all;
        }
        
        .sidebar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            height: fit-content;
        }
        
        .sidebar-section {
            margin-bottom: 25px;
        }
        
        .sidebar-title {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .stat-label {
            color: #666;
            font-size: 13px;
        }
        
        .stat-value {
            color: #667eea;
            font-weight: bold;
            font-size: 14px;
        }
        
        .quick-actions {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .quick-actions button {
            width: 100%;
            padding: 10px;
            font-size: 12px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .status {
                flex-direction: column;
            }
        }
        
        .refresh-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 18px;
        }
        
        .logs-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .logs-container::-webkit-scrollbar-track {
            background: #e0e0e0;
        }
        
        .logs-container::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        
        .logs-container::-webkit-scrollbar-thumb:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Pishro Bot Dashboard</h1>
            <p style="color: #999; margin-top: 5px;">سیستم مدیریت و نظارت بات سرمایه‌گذاری</p>
            
            <div class="status">
                <div class="status-item">
                    <div class="status-indicator active" id="botStatus"></div>
                    <span id="statusText">وضعیت: <strong>فعال</strong></span>
                </div>
                <div class="status-item">
                    <span>⏰ <span id="currentTime"></span></span>
                </div>
            </div>
            
            <div class="controls">
                <button class="btn-primary" onclick="startBot()">▶️ شروع</button>
                <button class="btn-danger" onclick="stopBot()">⏹️ متوقف</button>
                <button class="btn-refresh" onclick="refreshLogs()">🔄 تازه‌کردن</button>
            </div>
        </header>
        
        <div class="main-content">
            <div class="logs-panel">
                <div class="logs-header">
                    <span>📋 لاگ‌های بات</span>
                    <button class="refresh-btn" onclick="refreshLogs()" title="تازه‌کردن">🔄</button>
                </div>
                <div class="logs-container" id="logsContainer">
                    <div style="text-align: center; color: #999; padding: 20px;">
                        در حال بارگذاری لاگ‌ها...
                    </div>
                </div>
            </div>
            
            <aside class="sidebar">
                <div class="sidebar-section">
                    <div class="sidebar-title">📊 آمار</div>
                    <div class="stat">
                        <span class="stat-label">کل لاگ‌ها:</span>
                        <span class="stat-value" id="totalLogs">0</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Errors:</span>
                        <span class="stat-value" id="errorCount">0</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Warnings:</span>
                        <span class="stat-value" id="warningCount">0</span>
                    </div>
                </div>
                
                <div class="sidebar-section">
                    <div class="sidebar-title">🎮 کنترل</div>
                    <div class="quick-actions">
                        <button class="btn-primary" onclick="clearLogs()" style="font-size: 11px;">🗑️ حذف لاگ‌ها</button>
                        <button class="btn-primary" onclick="downloadLogs()" style="font-size: 11px;">⬇️ دانلود لاگ‌ها</button>
                        <button class="btn-primary" onclick="toggleAutoRefresh()" style="font-size: 11px;" id="autoRefreshBtn">🔄 خودکار بـه OFF</button>
                    </div>
                </div>
                
                <div class="sidebar-section">
                    <div class="sidebar-title">ℹ️ اطلاعات</div>
                    <p style="font-size: 12px; color: #666; line-height: 1.6;">
                        این داشبورد برای نظارت بر عملیات بات در زمان واقعی استفاده می‌شود.
                    </p>
                </div>
            </aside>
        </div>
    </div>
    
    <script>
        let autoRefresh = true;
        let autoRefreshInterval = null;
        
        function updateClock() {
            const now = new Date();
            document.getElementById('currentTime').textContent = now.toLocaleTimeString('fa-IR');
        }
        
        function refreshLogs() {
            fetch('/api/logs')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('logsContainer');
                    container.innerHTML = '';
                    
                    if (data.logs.length === 0) {
                        container.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">لاگی موجود نیست</div>';
                        return;
                    }
                    
                    let errorCount = 0, warningCount = 0;
                    
                    data.logs.forEach(log => {
                        const line = document.createElement('div');
                        line.className = 'log-line';
                        line.style.borderColor = log.color;
                        
                        line.innerHTML = `
                            <span class="log-timestamp">${log.timestamp}</span>
                            <span class="log-level" style="color: ${log.color}">${log.level}</span>
                            <span class="log-message">${log.message}</span>
                        `;
                        
                        container.appendChild(line);
                        
                        if (log.level === 'ERROR') errorCount++;
                        if (log.level === 'WARNING') warningCount++;
                    });
                    
                    document.getElementById('totalLogs').textContent = data.logs.length;
                    document.getElementById('errorCount').textContent = errorCount;
                    document.getElementById('warningCount').textContent = warningCount;
                    
                    // Scroll to bottom
                    container.scrollTop = container.scrollHeight;
                })
                .catch(e => console.error('Error:', e));
        }
        
        function startBot() {
            fetch('/api/bot/start', {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    alert('✅ ' + (d.message || 'بات شروع شد'));
                    document.getElementById('botStatus').className = 'status-indicator active';
                    refreshLogs();
                });
        }
        
        function stopBot() {
            if (confirm('آیا مطمئن هستید؟')) {
                fetch('/api/bot/stop', {method: 'POST'})
                    .then(r => r.json())
                    .then(d => {
                        alert('⏹️ ' + (d.message || 'بات متوقف شد'));
                        document.getElementById('botStatus').className = 'status-indicator inactive';
                    });
            }
        }
        
        function clearLogs() {
            if (confirm('آیا مطمئن هستید؟')) {
                fetch('/api/logs/clear', {method: 'POST'})
                    .then(r => r.json())
                    .then(d => {
                        alert('✅ لاگ‌ها حذف شدند');
                        refreshLogs();
                    });
            }
        }
        
        function downloadLogs() {
            window.location.href = '/api/logs/download';
        }
        
        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            const btn = document.getElementById('autoRefreshBtn');
            
            if (autoRefresh) {
                btn.textContent = '🔄 خودکار ON';
                autoRefreshInterval = setInterval(refreshLogs, 3000);
            } else {
                btn.textContent = '🔄 خودکار OFF';
                clearInterval(autoRefreshInterval);
            }
        }
        
        // Initialize
        updateClock();
        setInterval(updateClock, 1000);
        refreshLogs();
        autoRefreshInterval = setInterval(refreshLogs, 3000);
    </script>
</body>
</html>
    """


@app.get("/api/logs")
async def get_logs():
    """Get formatted logs as JSON."""
    logs = log_manager.get_formatted_logs(200)
    return JSONResponse({"logs": logs})


@app.get("/api/logs/download")
async def download_logs():
    """Download logs as text file."""
    logs = log_manager.read_logs(1000)
    content = "".join(logs)
    
    from fastapi.responses import Response
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=bot_logs.txt"}
    )


@app.post("/api/logs/clear")
async def clear_logs():
    """Clear logs (truncate file)."""
    try:
        with open(log_manager.log_file, 'w') as f:
            f.write("")
        return {"message": "لاگ‌ها پاک شدند"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bot/start")
async def start_bot():
    """Start bot."""
    import subprocess
    try:
        subprocess.Popen(["bash", "/home/sina/Documents/project/pishro-bot/start_bot.sh"])
        return {"message": "بات شروع شد ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bot/stop")
async def stop_bot():
    """Stop bot."""
    import subprocess
    try:
        subprocess.run(["bash", "/home/sina/Documents/project/pishro-bot/stop_bot.sh"])
        return {"message": "بات متوقف شد ⏹️"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Telegram webhook endpoint."""
    try:
        data = await request.json()
        logger.info(f"Received update: {data}")
        
        # Process update here
        # This would be handled by the main bot
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Pishro Bot Webhook Server"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
