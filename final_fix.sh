#!/bin/bash
################################################################################
# Final Bot Fix - Kill old instances and restart clean
################################################################################

echo "🔴 تمام ربات‌ها را کشتیم..."

# Hard kill everything
pkill -9 -f "python3.*run_bot" 2>/dev/null || true
pkill -9 -f "python3.*webhook_server" 2>/dev/null || true

sleep 3

# Verify
if pgrep -f "python3.*run_bot" > /dev/null 2>&1; then
    echo "⚠️ Still running! Using sudo..."
    sudo pkill -9 -f "python3.*run_bot" 2>/dev/null || true
fi

sleep 2

# Clean PID
rm -f logs/bot.pid logs/webhook.pid

echo "✅ تمام process‌ها کشته شدند!"

# Now reset Telegram connection
echo ""
echo "🔄 Resetting Telegram connection..."
cd /home/sina/Documents/project/pishro-bot
source venv/bin/activate 2>/dev/null

python3 << 'EOF'
import asyncio
from app.config import settings
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

async def reset():
    try:
        props = DefaultBotProperties(parse_mode=ParseMode.HTML)
        bot = Bot(token=settings.BOT_TOKEN, default=props)
        
        # Delete webhook
        await bot.delete_webhook()
        print("✅ Webhook deleted")
        
        # Close session
        await bot.session.close()
        print("✅ Session closed")
        
    except Exception as e:
        print(f"⚠️  Error: {e}")

asyncio.run(reset())
EOF

sleep 1

echo ""
echo "✅ Reset complete!"
echo ""
echo "🚀 Starting fresh bot..."
cd /home/sina/Documents/project/pishro-bot
source venv/bin/activate
python3 -u run_bot.py 2>&1 | tee -a logs/bot.log &

sleep 4

echo ""
echo "📊 Status:"
ps aux | grep "run_bot" | grep -v grep | awk '{print "PID: " $2 " - " $11}' || echo "Bot not running!"

echo ""
echo "📝 Recent logs:"
tail -10 logs/bot.log | grep -v "^$"

