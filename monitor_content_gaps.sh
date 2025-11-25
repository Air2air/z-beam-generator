#!/bin/bash

# Monitor script for batch content gap completion

PROGRESS_FILE="batch_content_gaps_progress.txt"
LOG_FILE="batch_content_gaps.log"
TOTAL_ITEMS=138  # 24 FAQs + 114 captions

while true; do
    clear
    echo "================================================"
    echo "CONTENT GAP COMPLETION - LIVE MONITOR"
    echo "================================================"
    echo ""
    
    if [ -f "$PROGRESS_FILE" ]; then
        CURRENT=$(cat "$PROGRESS_FILE")
        PERCENT=$(echo "scale=1; $CURRENT * 100 / $TOTAL_ITEMS" | bc)
        echo "Progress: $CURRENT / $TOTAL_ITEMS items ($PERCENT%)"
        
        # Visual progress bar
        FILLED=$(echo "$CURRENT * 50 / $TOTAL_ITEMS" | bc)
        BAR=$(printf '%*s' "$FILLED" | tr ' ' '█')
        EMPTY=$(printf '%*s' $((50 - FILLED)) | tr ' ' '░')
        echo "[$BAR$EMPTY]"
        echo ""
        
        # Phase status
        if [ "$CURRENT" -le 24 ]; then
            echo "Phase: 1/2 - Generating FAQs"
            echo "Current: FAQ $CURRENT/24"
        else
            CAPTION_NUM=$((CURRENT - 24))
            echo "Phase: 2/2 - Generating Captions"
            echo "Current: Caption $CAPTION_NUM/114"
        fi
    else
        echo "Status: Not started"
    fi
    
    echo ""
    echo "================================================"
    echo "Recent activity (last 10 lines):"
    echo "================================================"
    if [ -f "$LOG_FILE" ]; then
        tail -n 10 "$LOG_FILE"
    else
        echo "(No log file yet)"
    fi
    
    echo ""
    echo "Press Ctrl+C to exit monitor (batch will continue)"
    sleep 5
done
