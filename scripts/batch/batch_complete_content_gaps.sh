#!/bin/bash

# Batch Content Gap Completion Script
# Generates missing captions (114) and FAQs (24)

LOG_FILE="batch_content_gaps.log"
PROGRESS_FILE="batch_content_gaps_progress.txt"

echo "================================================" | tee -a "$LOG_FILE"
echo "CONTENT GAP COMPLETION - Started $(date)" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Initialize progress tracking
echo "0" > "$PROGRESS_FILE"

# Phase 1: Generate FAQs (24 materials - faster)
echo "🔧 PHASE 1: Generating FAQs (24 materials)" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

FAQ_COUNT=0
FAQ_SUCCESS=0
FAQ_FAILED=0

while IFS= read -r material; do
    FAQ_COUNT=$((FAQ_COUNT + 1))
    echo "" | tee -a "$LOG_FILE"
    echo "[$FAQ_COUNT/24] Generating FAQ: $material" | tee -a "$LOG_FILE"
    
    if python3 run.py --faq "$material" --skip-integrity-check >> "$LOG_FILE" 2>&1; then
        FAQ_SUCCESS=$((FAQ_SUCCESS + 1))
        echo "  ✅ SUCCESS" | tee -a "$LOG_FILE"
    else
        FAQ_FAILED=$((FAQ_FAILED + 1))
        echo "  ❌ FAILED" | tee -a "$LOG_FILE"
    fi
    
    echo "$FAQ_COUNT" > "$PROGRESS_FILE"
    sleep 2
done < materials_needing_faqs.txt

echo "" | tee -a "$LOG_FILE"
echo "Phase 1 Summary: $FAQ_SUCCESS success, $FAQ_FAILED failed" | tee -a "$LOG_FILE"

# Phase 2: Generate Captions (114 materials)
echo "" | tee -a "$LOG_FILE"
echo "🖼️  PHASE 2: Generating Captions (114 materials)" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"

CAPTION_COUNT=0
CAPTION_SUCCESS=0
CAPTION_FAILED=0

while IFS= read -r material; do
    CAPTION_COUNT=$((CAPTION_COUNT + 1))
    TOTAL_PROGRESS=$((FAQ_COUNT + CAPTION_COUNT))
    echo "" | tee -a "$LOG_FILE"
    echo "[$CAPTION_COUNT/114] Generating Caption: $material" | tee -a "$LOG_FILE"
    
    if python3 run.py --caption "$material" --skip-integrity-check >> "$LOG_FILE" 2>&1; then
        CAPTION_SUCCESS=$((CAPTION_SUCCESS + 1))
        echo "  ✅ SUCCESS" | tee -a "$LOG_FILE"
    else
        CAPTION_FAILED=$((CAPTION_FAILED + 1))
        echo "  ❌ FAILED" | tee -a "$LOG_FILE"
    fi
    
    echo "$TOTAL_PROGRESS" > "$PROGRESS_FILE"
    sleep 2
done < materials_needing_captions.txt

# Final summary
echo "" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "FINAL SUMMARY" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "FAQs: $FAQ_SUCCESS/$FAQ_COUNT successful" | tee -a "$LOG_FILE"
echo "Captions: $CAPTION_SUCCESS/$CAPTION_COUNT successful" | tee -a "$LOG_FILE"
echo "Total: $((FAQ_SUCCESS + CAPTION_SUCCESS))/$((FAQ_COUNT + CAPTION_COUNT)) successful" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Completed: $(date)" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE"
