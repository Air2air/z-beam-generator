#!/bin/bash

# Batch Property Research Script
# Researches numeric property values for 24 newly imported materials

MATERIALS=(
    "Stainless Steel 316"
    "Stainless Steel 304"
    "PTFE"
    "Gallium Nitride"
    "PEEK"
    "Polyimide"
    "Aluminum Bronze"
    "Aluminum Nitride"
    "Boron Carbide"
    "Titanium Alloy"
    "Nitinol"
    "Germanium"
    "Indium Phosphide"
    "Nylon"
    "ABS"
    "PET"
    "Scandium"
    "Bismuth"
    "Ebony"
    "Dolomite"
    "Gneiss"
)

LOG_FILE="batch_property_research.log"
PROGRESS_FILE="batch_property_research_progress.txt"

echo "0/${#MATERIALS[@]}" > "$PROGRESS_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" > "$LOG_FILE"
echo "🔬 BATCH PROPERTY RESEARCH STARTED: $(date)" >> "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$LOG_FILE"

SUCCESS_COUNT=0
FAIL_COUNT=0

for i in "${!MATERIALS[@]}"; do
    MATERIAL="${MATERIALS[$i]}"
    INDEX=$((i + 1))
    
    echo "" >> "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$LOG_FILE"
    echo "⚙️  [$INDEX/${#MATERIALS[@]}] Researching properties: $MATERIAL" >> "$LOG_FILE"
    echo "   ⏰ Started: $(date)" >> "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$LOG_FILE"
    
    python3 -m export.research.property_value_researcher --material "$MATERIAL" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "   ✅ SUCCESS: $MATERIAL" >> "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "   ❌ FAILED: $MATERIAL" >> "$LOG_FILE"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    
    echo "   ⏰ Finished: $(date)" >> "$LOG_FILE"
    echo "$INDEX/${#MATERIALS[@]}" > "$PROGRESS_FILE"
    
    # Small delay between materials
    sleep 2
done

echo "" >> "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$LOG_FILE"
echo "✨ BATCH PROPERTY RESEARCH COMPLETE: $(date)" >> "$LOG_FILE"
echo "📊 Results: $SUCCESS_COUNT/${#MATERIALS[@]} materials successful" >> "$LOG_FILE"
if [ $FAIL_COUNT -gt 0 ]; then
    echo "⚠️  Failures: $FAIL_COUNT materials" >> "$LOG_FILE"
fi
echo "" >> "$LOG_FILE"
echo "📄 Full log: $LOG_FILE" >> "$LOG_FILE"
echo "📊 Progress: $PROGRESS_FILE" >> "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$LOG_FILE"
