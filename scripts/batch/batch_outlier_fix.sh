#!/bin/bash

# Batch subtitle regeneration for outliers
# 8 materials with abbreviations + 1 too long

echo "=========================================="
echo "BATCH OUTLIER SUBTITLE REGENERATION"
echo "=========================================="
echo ""

MATERIALS=(
    "Carbon Fiber Reinforced Polymer"
    "Ceramic Matrix Composites"
    "Fiber Reinforced Polyurethane"
    "Polytetrafluoroethylene"
    "Polyvinyl Chloride"
    "Glass Fiber Reinforced Polymer"
    "Metal Matrix Composites"
    "Cerium"
    "Quartz Glass"
)

SUCCESS=0
FAILED=0
TOTAL=${#MATERIALS[@]}

for MATERIAL in "${MATERIALS[@]}"; do
    echo "----------------------------------------"
    echo "Processing: $MATERIAL"
    echo "----------------------------------------"
    
    OUTPUT=$(python3 run.py --subtitle "$MATERIAL" --skip-integrity-check 2>&1)
    
    if echo "$OUTPUT" | grep -q "✅ Subtitle generated"; then
        SUCCESS=$((SUCCESS + 1))
        WORD_COUNT=$(echo "$OUTPUT" | grep -o '[0-9]\+ words' | head -1 | grep -o '[0-9]\+')
        echo "✅ SUCCESS - Generated: $WORD_COUNT words"
    else
        FAILED=$((FAILED + 1))
        echo "❌ FAILED"
    fi
    
    echo ""
done

echo "=========================================="
echo "BATCH COMPLETE"
echo "=========================================="
echo "Total: $TOTAL materials"
echo "Success: $SUCCESS"
echo "Failed: $FAILED"
echo "=========================================="
