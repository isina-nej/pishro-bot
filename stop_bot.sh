#!/bin/bash
if [ -f /home/sina/Documents/project/pishro-bot/bot.pid ]; then
    kill $(cat /home/sina/Documents/project/pishro-bot/bot.pid) 2>/dev/null || true
    rm /home/sina/Documents/project/pishro-bot/bot.pid
    echo "✅ Bot stopped"
else
    echo "⚠️  Bot is not running"
fi
