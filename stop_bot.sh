#!/bin/bash
################################################################################
# Pishro Investment Bot - Stop Script
# اسکریپت متوقف کردن بات
################################################################################

PROJECT_DIR="/home/sina/Documents/project/pishro-bot"
PID_FILE="$PROJECT_DIR/logs/bot.pid"

echo "🛑 درحال متوقف کردن بات..."

# تلاش برای بسته کردن با استفاده از فایل PID
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "   از PID استفاده: $PID"
        kill "$PID"
        sleep 2
        
        # اگر هنوز زنده بود، force kill کن
        if kill -0 "$PID" 2>/dev/null; then
            echo "   ⚠️  فرآیند همچنان فعال است. Force kill..."
            kill -9 "$PID"
        fi
        echo "✅ بات متوقف شد"
    else
        echo "⚠️  فرآیند با PID $PID یافت نشد"
    fi
    rm -f "$PID_FILE"
else
    echo "   فایل PID یافت نشد. تمام نمونه‌ها را می‌کشم..."
    pkill -f "run_bot.py" || true
    echo "✅ تمام فرآیندهای bot بسته شدند"
fi

echo ""
echo "📊 وضعیت:"
ps aux | grep "run_bot.py" | grep -v grep || echo "   هیچ فرآیند bot فعالی یافت نشد"
