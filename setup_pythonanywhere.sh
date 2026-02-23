#!/bin/bash

# 🤖 Pishro Investment Bot - PythonAnywhere Setup Script
# This script prepares the bot for deployment on PythonAnywhere

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Pishro Investment Bot - Setup for PythonAnywhere"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create virtual environment
echo ""
echo "📦 Step 1: Creating virtual environment..."
python3 -m venv venv --without-pip || python3 -m venv venv
source venv/bin/activate

# Bootstrap pip
if ! command -v pip &> /dev/null; then
    echo "📥 Installing pip..."
    python3 << 'PYEOF'
import urllib.request
import subprocess
import sys
urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')
subprocess.run([sys.executable, 'get-pip.py'], check=True)
PYEOF
    rm -f get-pip.py
fi

# Install requirements
echo "📦 Step 2: Installing dependencies..."
pip install -q aiogram sqlalchemy jdatetime pydantic python-dotenv pydantic-settings aiosqlite aiohttp python-multipart alembic cryptography

# Initialize database
echo "💾 Step 3: Initializing database..."
python3 init_db.py

# Create startup script for PythonAnywhere
echo "📝 Step 4: Creating PythonAnywhere startup scripts..."

cat > start_bot.sh << 'BASHEOF'
#!/bin/bash
cd /home/sina/Documents/project/pishro-bot
source venv/bin/activate
python3 run_bot.py >> logs/bot.log 2>&1 &
echo $! > bot.pid
echo "✅ Bot started (PID: $(cat bot.pid))"
BASHEOF

cat > stop_bot.sh << 'BASHEOF'
#!/bin/bash
if [ -f /home/sina/Documents/project/pishro-bot/bot.pid ]; then
    kill $(cat /home/sina/Documents/project/pishro-bot/bot.pid) 2>/dev/null || true
    rm /home/sina/Documents/project/pishro-bot/bot.pid
    echo "✅ Bot stopped"
else
    echo "⚠️  Bot is not running"
fi
BASHEOF

chmod +x start_bot.sh stop_bot.sh

# Create logs directory
mkdir -p logs

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 Next Steps:"
echo ""
echo "1. Verify .env file has BOT_TOKEN set:"
echo "   grep BOT_TOKEN .env"
echo ""
echo "2. Start the bot:"
echo "   ./start_bot.sh"
echo ""
echo "3. Check logs:"
echo "   tail -f logs/bot.log"
echo ""
echo "4. Stop the bot:"
echo "   ./stop_bot.sh"
echo ""
echo "📱 Test Credentials:"
echo "   Admin: Telegram ID 123456789, Phone 09121234567"
echo "   Investor: Telegram ID 111111111, Phone 09121111111"
echo "   Accountant: Telegram ID 987654321, Phone 09129876543"
echo ""
