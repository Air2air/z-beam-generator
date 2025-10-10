#!/bin/bash
# Monitor subtitle generation progress

LOG_FILE="subtitle_batch_generation.log"

echo "📊 Subtitle Generation Progress Monitor"
echo "========================================"
echo ""

# Check if process is running
if ps aux | grep -v grep | grep "generate_subtitles_batch.py" > /dev/null; then
    echo "✅ Generation process is RUNNING"
    PID=$(ps aux | grep -v grep | grep "generate_subtitles_batch.py" | awk '{print $2}')
    echo "   PID: $PID"
else
    echo "❌ Generation process is NOT running"
fi

echo ""
echo "📈 Progress:"
echo "------------"

# Count completed materials
if [ -f "$LOG_FILE" ]; then
    # Count successful generations
    SUCCESS_COUNT=$(grep -c "✅.*Success" "$LOG_FILE" 2>/dev/null || echo "0")
    ERROR_COUNT=$(grep -c "❌.*Error" "$LOG_FILE" 2>/dev/null || echo "0")
    
    echo "✅ Completed: $SUCCESS_COUNT/122"
    echo "❌ Errors: $ERROR_COUNT"
    
    # Calculate percentage
    if [ $SUCCESS_COUNT -gt 0 ]; then
        PERCENT=$((SUCCESS_COUNT * 100 / 122))
        echo "📊 Progress: ${PERCENT}%"
    fi
    
    echo ""
    echo "🔄 Last 10 lines of log:"
    echo "------------------------"
    tail -10 "$LOG_FILE"
else
    echo "⚠️  Log file not found"
fi

echo ""
echo "💡 To check full log: tail -f subtitle_batch_generation.log"
echo "💡 To stop generation: kill $PID"
