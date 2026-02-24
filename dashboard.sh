#!/bin/bash
################################################################################
# Dashboard - View Bot Logs & Status in Terminal
# نمایش لاگ‌ها و وضعیت در ترمینال
################################################################################

PROJECT_DIR="/home/sina/Documents/project/pishro-bot"
cd "$PROJECT_DIR"

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                   🤖 Pishro Bot - Terminal Dashboard                    ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# نمایش وضعیت فرآیندها
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📊 وضعیت فرآیندها:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# بررسی Bot
if pgrep -f "run_bot.py" > /dev/null; then
    BOT_PID=$(pgrep -f "run_bot.py")
    echo -e "${GREEN}✓ Bot:${NC} فعال (PID: $BOT_PID)"
else
    echo -e "${RED}✗ Bot:${NC} غیرفعال"
fi

# بررسی Webhook
if pgrep -f "webhook_server.py" > /dev/null; then
    WEBHOOK_PID=$(pgrep -f "webhook_server.py")
    echo -e "${GREEN}✓ Webhook:${NC} فعال (PID: $WEBHOOK_PID)"
else
    echo -e "${RED}✗ Webhook:${NC} غیرفعال"
fi

# بررسی Ngrok
if pgrep -f "ngrok" > /dev/null; then
    NGROK_PID=$(pgrep -f "ngrok")
    echo -e "${GREEN}✓ Ngrok:${NC} فعال (PID: $NGROK_PID)"
else
    echo -e "${YELLOW}○ Ngrok:${NC} غیرفعال"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📋 آخرین 30 لاگ:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "logs/bot.log" ]; then
    # خط‌های لاگ را رنگی کنید
    tail -30 logs/bot.log | while read line; do
        if [[ $line == *"ERROR"* ]] || [[ $line == *"CRITICAL"* ]]; then
            echo -e "${RED}$line${NC}"
        elif [[ $line == *"WARNING"* ]]; then
            echo -e "${YELLOW}$line${NC}"
        elif [[ $line == *"INFO"* ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ $line == *"DEBUG"* ]]; then
            echo -e "${PURPLE}$line${NC}"
        else
            echo "$line"
        fi
    done
else
    echo "لاگی موجود نیست"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⌨️  دستورات موجود:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cat << 'EOF'

  📝 مشاهدهٔ لاگ‌ها:
    tail -f logs/bot.log          - پیوسته
    tail -100 logs/bot.log        - آخرین 100 خط

  ▶️ شروع/متوقف:
    bash start_bot.sh             - شروع بات
    bash stop_bot.sh              - متوقف کردن بات
    bash run_servers.sh           - مدیر سرور‌ها

  🌐 Webhook:
    bash setup_webhook_ngrok.sh   - شروع Webhook + Ngrok
    python3 webhook_server.py     - Webhook مستقیم

  🎯 دیگر:
    ./venv/bin/python3 test_bot.py    - تست سیستم
    ps aux | grep run_bot             - فرآیند‌ها

EOF

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "💡 تلگرام: https://t.me/PishroSarmayehBot"
echo ""
