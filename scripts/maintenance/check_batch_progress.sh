#!/bin/bash
# Quick batch generation progress checker

LOG_FILE="/tmp/batch_all_132_force.log"

echo "🔍 BATCH GENERATION PROGRESS"
echo "================================"
echo ""

# Current material
echo "📍 Current:"
tail -500 "$LOG_FILE" | grep "🔄 MATERIAL" | tail -1

echo ""

# Success/fail counts
echo "📊 Statistics:"
SUCCESS=$(grep -c "✅ SUCCESS" "$LOG_FILE" 2>/dev/null || echo "0")
FAILED=$(grep -c "❌ FAILED" "$LOG_FILE" 2>/dev/null || echo "0")
TIMEOUT=$(grep -c "⏱️  TIMEOUT" "$LOG_FILE" 2>/dev/null || echo "0")

echo "  ✅ Success: $SUCCESS"
echo "  ❌ Failed: $FAILED"
echo "  ⏱️  Timeout: $TIMEOUT"

echo ""
echo "📈 Progress: $SUCCESS/132 ($((SUCCESS * 100 / 132))%)"

# Recent activity
echo ""
echo "🕐 Recent activity:"
tail -50 "$LOG_FILE" | grep -E "🔄 MATERIAL|✅ SUCCESS|❌ FAILED" | tail -5

echo ""
echo "💡 Full log: tail -f $LOG_FILE"
