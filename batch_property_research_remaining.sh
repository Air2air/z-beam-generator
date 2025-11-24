#!/bin/bash

# Batch Property Research - Remaining 8 Materials (Phase 3 Completion)
# Generated: November 23, 2025
# Purpose: Research numeric properties for materials missing from Phase 3

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Materials needing property research
MATERIALS=(
    "Yttria-Stabilized Zirconia"
    "Boron Nitride"
    "Titanium Nitride"
    "Magnesium Oxide"
    "Hafnium Oxide"
    "Tantalum Oxide"
    "Niobium Oxide"
    "Indium Tin Oxide"
)

TOTAL=${#MATERIALS[@]}
SUCCESS_COUNT=0
FAILED_COUNT=0
LOG_FILE="batch_property_research_remaining.log"
PROGRESS_FILE="batch_property_research_remaining_progress.txt"

# Clear previous logs
> "$LOG_FILE"
> "$PROGRESS_FILE"

echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🔬 PHASE 3 COMPLETION: Property Research for Remaining 8 Materials${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "📋 Materials to research: ${TOTAL}"
echo -e "📝 Log file: ${LOG_FILE}"
echo -e "📊 Progress: ${PROGRESS_FILE}"
echo ""
echo -e "${YELLOW}⚠️  GROK Compliance: NO fallbacks, NO defaults, FAIL FAST on missing data${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Process each material
for INDEX in "${!MATERIALS[@]}"; do
    MATERIAL="${MATERIALS[$INDEX]}"
    ACTUAL_INDEX=$((INDEX + 1))
    
    echo -e "${BLUE}⚙️  [$ACTUAL_INDEX/$TOTAL] Researching properties: ${MATERIAL}${NC}" | tee -a "$LOG_FILE"
    echo -e "⏰ Started: $(date)" | tee -a "$LOG_FILE"
    
    # Run property research
    if python3 -m export.research.property_value_researcher --material "$MATERIAL" >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✅ SUCCESS: ${MATERIAL}${NC}" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}❌ FAILED: ${MATERIAL}${NC}" | tee -a "$LOG_FILE"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
    
    echo -e "⏰ Finished: $(date)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # Update progress
    echo "$ACTUAL_INDEX/$TOTAL" > "$PROGRESS_FILE"
    
    # Rate limiting (2 seconds between materials)
    if [ $ACTUAL_INDEX -lt $TOTAL ]; then
        sleep 2
    fi
done

# Final summary
echo "" | tee -a "$LOG_FILE"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}📊 BATCH PROPERTY RESEARCH COMPLETE${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}✅ Successful: ${SUCCESS_COUNT}/${TOTAL}${NC}" | tee -a "$LOG_FILE"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Failed: ${FAILED_COUNT}/${TOTAL}${NC}" | tee -a "$LOG_FILE"
fi
echo -e "📝 Full log: ${LOG_FILE}" | tee -a "$LOG_FILE"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"

exit 0
