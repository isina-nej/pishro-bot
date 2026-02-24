#!/bin/bash
PROJECT_DIR="/home/sina/Documents/project/pishro-bot"
cd "$PROJECT_DIR"

source venv/bin/activate
mkdir -p logs

# فایل PID
PID_FILE="logs/bot.pid"

# تابع cleanup
cleanup() {
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
    fi
    exit 0
}

trap cleanup SIGTERM SIGINT

# اجرای بات با تکرار خودکار
while true; do
    # اگر فرآیند قدیمی بود پاکش کن
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        kill "$OLD_PID" 2>/dev/null || true
    fi
    
    # اجرای بات
    python3 -u run_bot.py > logs/bot.log 2>&1 &
    BOT_PID=$!
    echo "$BOT_PID" > "$PID_FILE"
    
    # منتظر فرآیند
    wait $BOT_PID
    EXIT_CODE=$?
    
    # اگر exit code 0 بود (درخواست خروج معقول) بیرون بکش
    if [ $EXIT_CODE -eq 0 ]; then
        break
    fi
    
    # در غیر این صورت 5 ثانیه صبر کن و دوباره شروع کن
    echo "$(date) - بات سقوط کرد (exit code: $EXIT_CODE). 5 ثانیه بعد دوباره شروع می‌شود..."
    sleep 5
done
