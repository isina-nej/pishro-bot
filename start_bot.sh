#!/bin/bash
################################################################################
# Pishro Investment Bot - Start Script
# اسکریپت شروع بات سرمایه‌گذاری پیشرو
################################################################################

set -e

PROJECT_DIR="/home/sina/Documents/project/pishro-bot"
cd "$PROJECT_DIR"

# فعال کردن virtual environment
source venv/bin/activate

# ایجاد لاگ دایرکتوری
mkdir -p logs

# کشتن فرآیندهای قدیمی
pkill -f "run_bot.py" || true
sleep 2

# اجرای بات
echo ""
echo "🚀 شروع بات سرمایه‌گذاری پیشرو..."
echo "📝 لاگ‌ها: $PROJECT_DIR/logs/bot.log"
echo ""

python3 -u run_bot.py > logs/bot.log 2>&1 &
BOT_PID=$!

echo "$BOT_PID" > logs/bot.pid

echo "✅ بات شروع شد! (PID: $BOT_PID)"
echo ""
sleep 2

# نمایش لاگ های اولیه
echo "📋 لاگ‌های اولیه:"
tail -15 logs/bot.log
echo ""
echo "📊 نگاه کردن به لاگ‌های مستقیم:"
echo "   tail -f logs/bot.log"
