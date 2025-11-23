#!/bin/bash

# Batch Subtitle Regeneration for 74 Out-of-Range Materials
# Target: 21-63 words (subtitle_length configuration)
# Date: November 22, 2025

echo "════════════════════════════════════════════════════════════════"
echo "📝 BATCH SUBTITLE REGENERATION - 74 Materials"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Target: 21-63 words (subtitle_length config)"
echo "Reason: Materials outside target range (too short <21 or too long >63)"
echo ""

# Read materials from file
MATERIALS_FILE="materials_needing_subtitle_regen.txt"

if [ ! -f "$MATERIALS_FILE" ]; then
    echo "❌ Error: $MATERIALS_FILE not found"
    exit 1
fi

# Count total materials
TOTAL=$(wc -l < "$MATERIALS_FILE" | xargs)
echo "Total materials to process: $TOTAL"
echo ""

# Counters
SUCCESS=0
FAILED=0
CURRENT=0

# Read materials line by line
while IFS= read -r MATERIAL; do
    CURRENT=$((CURRENT + 1))
    
    echo "────────────────────────────────────────────────────────────────"
    echo "[$CURRENT/$TOTAL] Generating subtitle for: $MATERIAL"
    echo "────────────────────────────────────────────────────────────────"
    
    # Run generation
    OUTPUT=$(python3 run.py --subtitle "$MATERIAL" --skip-integrity-check 2>&1)
    
    # Check for success
    if echo "$OUTPUT" | grep -q "✅ Subtitle generated"; then
        echo "   ✅ SUCCESS"
        SUCCESS=$((SUCCESS + 1))
        
        # Extract word count if available
        if echo "$OUTPUT" | grep -q "words"; then
            WORD_COUNT=$(echo "$OUTPUT" | grep -o '[0-9]\+ words' | head -1)
            echo "   📊 $WORD_COUNT"
        fi
    else
        echo "   ❌ FAILED"
        FAILED=$((FAILED + 1))
        
        # Show error if available
        if echo "$OUTPUT" | grep -q "Error"; then
            ERROR=$(echo "$OUTPUT" | grep "Error" | head -1)
            echo "   📋 $ERROR"
        fi
    fi
    
    echo ""
    
done < "$MATERIALS_FILE"

echo "════════════════════════════════════════════════════════════════"
echo "📊 BATCH REGENERATION COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Total processed: $CURRENT"
echo "✅ Successful: $SUCCESS"
echo "❌ Failed: $FAILED"
echo ""
echo "Success rate: $(awk "BEGIN {printf \"%.1f\", ($SUCCESS/$TOTAL)*100}")%"
echo ""
echo "════════════════════════════════════════════════════════════════"
