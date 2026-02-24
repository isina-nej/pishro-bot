#!/bin/bash
################################################################################
# Start Pishro Architecture: API Backend + Telegram Bot
# شروع معماری Pishro: Backend API + ربات تلگرام
################################################################################

PROJECT_DIR="/home/sina/Documents/project/pishro-bot"
cd "$PROJECT_DIR"

# فعال کردن venv
source venv/bin/activate

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🚀 Pishro Investment System - Modern Architecture"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Select startup mode:"
echo ""
echo "  [1] 🔌 Backend API Only (main_api.py)"
echo "  [2] 🤖 Bot Only (run_bot.py)"
echo "  [3] 🔄 API + Bot Together (Recommended)"
echo "  [4] 📊 API + Bot + Dashboard"
echo "  [5] 📚 View Documentation"
echo ""

read -p "Select option: " choice

case $choice in
    1)
        echo ""
        echo "🔌 Starting Backend API..."
        echo "📍 URL: http://localhost:8000"
        echo "📚 Docs: http://localhost:8000/docs"
        echo ""
        python3 main_api.py
        ;;
    
    2)
        echo ""
        echo "🤖 Starting Telegram Bot..."
        echo "📝 Logs: logs/bot.log"
        echo ""
        python3 run_bot.py
        ;;
    
    3)
        echo ""
        echo "🔄 Starting API + Bot (Two terminals needed)..."
        echo ""
        echo "Terminal 1️⃣  - Backend API..."
        echo "Terminal 2️⃣  - Telegram Bot..."
        echo ""
        echo "Starting API in background..."
        
        # Start API in background
        python3 main_api.py > logs/api.log 2>&1 &
        API_PID=$!
        echo "✅ API started (PID: $API_PID)"
        echo "$API_PID" > logs/api.pid
        
        sleep 3
        
        echo ""
        echo "🌍 API is running at: http://localhost:8000"
        echo "📚 Docs at: http://localhost:8000/docs"
        echo ""
        
        # Start Bot in foreground
        echo "Starting Bot in foreground..."
        python3 run_bot.py
        
        # Cleanup on exit
        echo ""
        echo "Cleaning up..."
        kill $API_PID 2>/dev/null || true
        rm -f logs/api.pid
        echo "✅ Stopped"
        ;;
    
    4)
        echo ""
        echo "📊 Starting API + Bot + Dashboard..."
        echo ""
        
        # Start API
        python3 main_api.py > logs/api.log 2>&1 &
        API_PID=$!
        echo "✅ API started (PID: $API_PID)"
        echo "$API_PID" > logs/api.pid
        
        sleep 2
        
        # Start Bot
        python3 run_bot.py > logs/bot.log 2>&1 &
        BOT_PID=$!
        echo "✅ Bot started (PID: $BOT_PID)"
        
        sleep 2
        
        # Start Dashboard/Webhook
        python3 webhook_server.py > logs/webhook.log 2>&1 &
        WEBHOOK_PID=$!
        echo "✅ Dashboard started (PID: $WEBHOOK_PID)"
        
        echo ""
        echo "════════════════════════════════════════════════════════════════"
        echo "🎉 All Services Running!"
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        echo "📍 Services:"
        echo "  • API:       http://localhost:8000"
        echo "  • Docs:      http://localhost:8000/docs"
        echo "  • Dashboard: http://localhost:8000 (web UI)"
        echo "  • Bot:       Running in polling mode"
        echo ""
        echo "📝 Logs:"
        echo "  • API:       logs/api.log"
        echo "  • Bot:       logs/bot.log"
        echo "  • Dashboard: logs/webhook.log"
        echo ""
        echo "💡 Commands:"
        echo "  tail -f logs/api.log       # Watch API logs"
        echo "  tail -f logs/bot.log       # Watch Bot logs"
        echo "  pkill -f main_api.py       # Stop API"
        echo "  pkill -f run_bot.py        # Stop Bot"
        echo "  pkill -f webhook_server.py # Stop Dashboard"
        echo ""
        echo "Press CTRL+C to stop monitoring..."
        echo ""
        
        # Monitor logs
        tail -f logs/api.log & 
        TAIL_PID=$!
        
        wait
        
        # Cleanup
        kill $API_PID $BOT_PID $WEBHOOK_PID $TAIL_PID 2>/dev/null || true
        rm -f logs/api.pid
        ;;
    
    5)
        echo ""
        echo "📚 Documentation:"
        echo ""
        cat API_ARCHITECTURE.md
        echo ""
        ;;
    
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac
