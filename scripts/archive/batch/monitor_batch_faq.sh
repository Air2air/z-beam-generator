#!/bin/bash
# Monitor batch FAQ topic enhancement progress

LOG_FILE="batch_faq_enhancement.log"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FAQ TOPIC ENHANCEMENT - BATCH PROGRESS MONITOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  Log file not found: $LOG_FILE"
    echo "Batch processing may not have started yet."
    exit 1
fi

# Count processed materials
PROCESSED=$(grep -c "✅ Exported successfully" "$LOG_FILE" 2>/dev/null || echo "0")

# Count total FAQs generated
TOTAL_FAQS=$(grep -o "Generated [0-9]* FAQs" "$LOG_FILE" | awk '{sum+=$2} END {print sum+0}')

# Count enhanced FAQs
ENHANCED=$(grep -o "([0-9]* enhanced)" "$LOG_FILE" | grep -o "[0-9]*" | awk '{sum+=$1} END {print sum+0}')

# Get current material being processed
CURRENT=$(tail -20 "$LOG_FILE" | grep "Processing:" | tail -1 | sed 's/.*Processing: //')

# Get last error (if any)
LAST_ERROR=$(tail -50 "$LOG_FILE" | grep "❌ Error:" | tail -1)

# Calculate progress
TOTAL_MATERIALS=132
PERCENT=$((PROCESSED * 100 / TOTAL_MATERIALS))

echo "📊 PROGRESS SUMMARY"
echo "─────────────────────────────────────────────────────────────────────────"
echo "  Materials Processed:     $PROCESSED / $TOTAL_MATERIALS ($PERCENT%)"
echo "  Current Material:        ${CURRENT:-Initializing...}"
echo "  Total FAQs Generated:    $TOTAL_FAQS"
echo "  Enhanced FAQs:           $ENHANCED"
if [ $TOTAL_FAQS -gt 0 ]; then
    ENHANCE_PERCENT=$((ENHANCED * 100 / TOTAL_FAQS))
    echo "  Enhancement Rate:        ${ENHANCE_PERCENT}%"
fi
echo "─────────────────────────────────────────────────────────────────────────"
echo

if [ -n "$LAST_ERROR" ]; then
    echo "⚠️  LAST ERROR:"
    echo "  $LAST_ERROR"
    echo
fi

echo "📝 RECENT ACTIVITY (last 10 lines):"
echo "─────────────────────────────────────────────────────────────────────────"
tail -10 "$LOG_FILE" | grep -v "INFO -"
echo "─────────────────────────────────────────────────────────────────────────"
echo

if [ $PROCESSED -eq $TOTAL_MATERIALS ]; then
    echo "✅ BATCH PROCESSING COMPLETE!"
    echo
    echo "View full statistics:"
    echo "  tail -100 $LOG_FILE"
else
    echo "⏳ BATCH STILL RUNNING..."
    echo
    echo "Monitor live progress:"
    echo "  tail -f $LOG_FILE"
    echo
    echo "Or run this script again:"
    echo "  bash scripts/monitor_batch_faq.sh"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
