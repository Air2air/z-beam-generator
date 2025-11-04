#!/bin/bash
# Monitor the research progress in real-time

LOG_FILE="/tmp/full_research_incremental.log"

echo "=== Research Process Monitor ==="
echo ""

# Check if process is running
PROCESS=$(ps aux | grep "run.py --research-missing-properties" | grep -v grep)
if [ -z "$PROCESS" ]; then
    echo "❌ Research process NOT running"
    echo ""
    echo "To start it again:"
    echo "  nohup python3 run.py --research-missing-properties >> /tmp/full_research_incremental.log 2>&1 &"
else
    echo "✅ Research process running"
    PID=$(echo "$PROCESS" | awk '{print $2}')
    echo "   PID: $PID"
    UPTIME=$(ps -p $PID -o etime= | tr -d ' ')
    echo "   Runtime: $UPTIME"
fi

echo ""
echo "=== Materials Processed ==="
MATERIALS=$(grep "🔬 Researching" "$LOG_FILE" 2>/dev/null | sed 's/.*for \([A-Za-z ]*\) in.*/\1/' | sort -u)
COUNT=$(echo "$MATERIALS" | wc -l | tr -d ' ')
echo "   Total: $COUNT materials"
echo ""
echo "$MATERIALS" | sed 's/^/   ✓ /'

echo ""
echo "=== Current Activity (last 10 research operations) ==="
grep "🔬 Researching" "$LOG_FILE" 2>/dev/null | tail -10 | sed 's/^/   /'

echo ""
echo "=== Recent Completions (last 5) ==="
grep "✅ Successfully researched" "$LOG_FILE" 2>/dev/null | tail -5 | sed 's/^/   /'

echo ""
echo "=== API Activity ==="
CACHE_HITS=$(grep "Cache HIT" "$LOG_FILE" 2>/dev/null | wc -l | tr -d ' ')
API_CALLS=$(grep "Making API request" "$LOG_FILE" 2>/dev/null | wc -l | tr -d ' ')
echo "   Cache hits: $CACHE_HITS"
echo "   API calls: $API_CALLS"
if [ "$API_CALLS" -gt 0 ]; then
    CACHE_RATE=$(echo "scale=1; $CACHE_HITS * 100 / ($CACHE_HITS + $API_CALLS)" | bc)
    echo "   Cache rate: ${CACHE_RATE}%"
fi

echo ""
echo "=== Log File ==="
echo "   Location: $LOG_FILE"
LOG_SIZE=$(ls -lh "$LOG_FILE" 2>/dev/null | awk '{print $5}')
echo "   Size: $LOG_SIZE"

echo ""
echo "To watch live updates:"
echo "  tail -f $LOG_FILE | grep -E '🔬|✅|💾'"
