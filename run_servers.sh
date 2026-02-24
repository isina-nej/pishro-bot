#!/bin/bash
################################################################################
# Webhook + Polling Server Manager
# مدیر سرور Webhook و Polling
################################################################################

PROJECT_DIR="/home/sina/Documents/project/pishro-bot"
cd "$PROJECT_DIR"

# باز کردن Virtual Environment
source venv/bin/activate

# صفحات PID
BOT_PID_FILE="logs/bot.pid"
WEBHOOK_PID_FILE="logs/webhook.pid"

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "🚀 Pishro Bot - مدیر سرور Webhook و Polling"
echo "══════════════════════════════════════════════════════════════"
echo ""

# ایجاد دایرکتوری لاگ
mkdir -p logs

# خریدن FastAPI اگر نصب نشده باشد
echo "📦 بررسی وابستگی‌ها..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "⚠️  FastAPI نصب نشده است. درحال نصب..."
    pip install fastapi uvicorn --quiet
}

# نمایش گزینه‌ها
echo "👇 لطفا انتخاب کنید:"
echo ""
echo "  [1] شروع Webhook Server (پورت 8000)"
echo "  [2] شروع Bot + Webhook با هم"
echo "  [3] مشاهدهٔ Dashboard (http://localhost:8000)"
echo "  [4] نمایش لاگ‌ها"
echo "  [5] متوقف کردن همه"
echo ""

read -p "انتخاب شما: " choice

case $choice in
    1)
        echo ""
        echo "🌐 درحال شروع Webhook Server..."
        python3 webhook_server.py > logs/webhook.log 2>&1 &
        WEBHOOK_PID=$!
        echo "$WEBHOOK_PID" > "$WEBHOOK_PID_FILE"
        echo "✅ Webhook Server شروع شد (PID: $WEBHOOK_PID)"
        echo "🌍 بروند: http://localhost:8000"
        echo ""
        ;;
    
    2)
        echo ""
        echo "🤖 درحال شروع Bot..."
        bash start_bot.sh
        
        sleep 3
        
        echo ""
        echo "🌐 درحال شروع Webhook Server..."
        python3 webhook_server.py > logs/webhook.log 2>&1 &
        WEBHOOK_PID=$!
        echo "$WEBHOOK_PID" > "$WEBHOOK_PID_FILE"
        echo "✅ Webhook Server شروع شد (PID: $WEBHOOK_PID)"
        echo ""
        echo "🎉 هر دو سرور در حال اجرا هستند!"
        echo "   • Bot: Polling Mode"
        echo "   • Dashboard: http://localhost:8000"
        echo ""
        ;;
    
    3)
        echo "🌍 Dashboard را در مرورگر خود باز کنید:"
        echo "   👉 http://localhost:8000"
        echo ""
        ;;
    
    4)
        echo ""
        echo "📋 آخرین 50 لاگ:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        tail -50 logs/bot.log
        echo ""
        ;;
    
    5)
        echo ""
        echo "⏹️  درحال متوقف کردن تمام سرور‌ها..."
        
        # متوقف کردن Bot
        bash stop_bot.sh 2>/dev/null || true
        
        # متوقف کردن Webhook
        if [ -f "$WEBHOOK_PID_FILE" ]; then
            WEBHOOK_PID=$(cat "$WEBHOOK_PID_FILE")
            kill $WEBHOOK_PID 2>/dev/null || true
            rm -f "$WEBHOOK_PID_FILE"
            echo "✅ Webhook Server متوقف شد"
        fi
        
        pkill -f "uvicorn" || true
        pkill -f "webhook_server.py" || true
        
        echo "✅ تمام سرور‌ها متوقف شدند"
        echo ""
        ;;
    
    *)
        echo "❌ انتخاب نامعتبر است"
        ;;
esac

echo ""
