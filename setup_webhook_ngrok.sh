#!/bin/bash
################################################################################
# Quick Start Webhook with Ngrok
# شروع سریع Webhook با Ngrok برای expose کردن آدرس
################################################################################

PROJECT_DIR="/home/sina/Documents/project/pishro-bot"
cd "$PROJECT_DIR"

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "🌐 Webhook + Ngrok Setup"
echo "══════════════════════════════════════════════════════════════"
echo ""

# بررسی ngrok
if ! command -v ngrok &> /dev/null; then
    echo "⚠️  Ngrok نصب نشده است"
    echo ""
    echo "برای نصب Ngrok:"
    echo "  Ubuntu/Debian: sudo apt install ngrok"
    echo "  MacOS: brew install ngrok"
    echo "  یا دانلود از: https://ngrok.com/download"
    echo ""
    read -p "آیا می‌خواهید ادامه دهید؟ (y/n): " ans
    if [ "$ans" != "y" ]; then
        exit 1
    fi
fi

# فعال کردن Virtual Environment
source venv/bin/activate

# بررسی FastAPI
python3 -c "import fastapi" 2>/dev/null || {
    echo "📦 نصب FastAPI..."
    pip install fastapi uvicorn --quiet
}

# ایجاد دایرکتوری لاگ
mkdir -p logs

echo "🚀 درحال شروع سرور‌ها..."
echo ""

# شروع Webhook Server
echo "🌐 شروع Webhook Server (پورت 8000)..."
python3 webhook_server.py > logs/webhook.log 2>&1 &
WEBHOOK_PID=$!
echo "$WEBHOOK_PID" > logs/webhook.pid
echo "✅ Webhook Server شروع شد (PID: $WEBHOOK_PID)"

sleep 2

# بررسی اینکه سرور آماده است
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Webhook Server پاسخ دهنده است"
else
    echo "⚠️  Webhook Server ممکن است آماده نباشد"
fi

echo ""
echo "🌐 شروع Ngrok خوشایند..."
echo ""
echo "لطفا منتظر بمانید. آدرس عمومی‌تر شما نمایش داده خواهد شد."
echo ""

# شروع Ngrok
ngrok http 8000 --log=stdout > logs/ngrok.log 2>&1
