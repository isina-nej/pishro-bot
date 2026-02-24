#!/bin/bash
################################################################################
# Kill all bot instances and clean properly
################################################################################

echo "🛑 Killing all bot instances..."

# Kill all run_bot.py processes
for pid in $(pgrep -f "run_bot.py"); do
    echo "Killing PID: $pid"
    if [ "$(whoami)" = "root" ]; then
        kill -9 $pid 2>/dev/null || true
    else
        kill $pid 2>/dev/null || true
    fi
done

sleep 2

# Verify all killed
if pgrep -f "run_bot.py" > /dev/null; then
    echo "⚠️  Some instances still running, trying harder..."
    for pid in $(pgrep -f "run_bot.py"); do
        kill -9 $pid 2>/dev/null || true
    done
    sleep 1
fi

# Final check
if pgrep -f "run_bot.py" > /dev/null; then
    ps aux | grep "run_bot" || echo "Still processes exist, but pkill failed"
else
    echo "✅ All instances killed"
fi

# Remove PID file
rm -f logs/bot.pid

# Clean logs
> logs/bot.log

echo "✅ Cleanup complete"

