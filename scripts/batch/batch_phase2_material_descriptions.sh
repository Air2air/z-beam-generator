#!/bin/bash

# Phase 2: Material Descriptions - 13 Complete Materials
# Generated: November 23, 2025
# Purpose: Generate comprehensive material descriptions for Phase 3 complete materials

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

MATERIALS=(
    "Stainless Steel 316"
    "Stainless Steel 304"
    "PTFE"
    "Gallium Nitride"
    "PEEK"
    "Polyimide"
    "Zirconia"
    "Titanium Carbide"
    "Tungsten Carbide"
    "Boron Carbide"
    "Silicon Carbide"
    "Aluminum Nitride"
    "Silicon Nitride"
)

TOTAL=${#MATERIALS[@]}
SUCCESS_COUNT=0
FAILED_COUNT=0
LOG_FILE="batch_phase2_descriptions.log"
PROGRESS_FILE="batch_phase2_progress.txt"

> "$LOG_FILE"
> "$PROGRESS_FILE"

echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📝 PHASE 2: Material Description Generation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "📋 Materials: ${TOTAL}"
echo -e "📝 Log: ${LOG_FILE}"
echo -e "📊 Progress: ${PROGRESS_FILE}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

for INDEX in "${!MATERIALS[@]}"; do
    MATERIAL="${MATERIALS[$INDEX]}"
    ACTUAL_INDEX=$((INDEX + 1))
    
    echo -e "${BLUE}📝 [$ACTUAL_INDEX/$TOTAL] Generating description: ${MATERIAL}${NC}" | tee -a "$LOG_FILE"
    echo -e "⏰ Started: $(date)" | tee -a "$LOG_FILE"
    
    if python3 run.py --material-description "$MATERIAL" --skip-integrity-check >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✅ SUCCESS: ${MATERIAL}${NC}" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}❌ FAILED: ${MATERIAL}${NC}" | tee -a "$LOG_FILE"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
    
    echo -e "⏰ Finished: $(date)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    echo "$ACTUAL_INDEX/$TOTAL" > "$PROGRESS_FILE"
    
    if [ $ACTUAL_INDEX -lt $TOTAL ]; then
        sleep 3
    fi
done

echo "" | tee -a "$LOG_FILE"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}📊 PHASE 2 COMPLETE${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}✅ Successful: ${SUCCESS_COUNT}/${TOTAL}${NC}" | tee -a "$LOG_FILE"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Failed: ${FAILED_COUNT}/${TOTAL}${NC}" | tee -a "$LOG_FILE"
fi
echo -e "📝 Full log: ${LOG_FILE}" | tee -a "$LOG_FILE"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"

exit 0
