#!/bin/bash
cd /home/sina/Documents/project/pishro-bot
source venv/bin/activate
python3 run_bot.py >> logs/bot.log 2>&1 &
echo $! > bot.pid
echo "✅ Bot started (PID: $(cat bot.pid))"
