#!/bin/bash
# Monitor Deep Research Background Jobs

echo "=============================================================="
echo "DEEP RESEARCH BATCH JOBS - STATUS MONITOR"
echo "=============================================================="
echo ""

# Count running jobs
RUNNING=$(ps aux | grep "populate_deep_research" | grep -v grep | wc -l | tr -d ' ')
echo "📊 Running jobs: $RUNNING"
echo ""

# Check log files
echo "📋 Log Files Status:"
echo "-----------------------------------------------------------"
for log in research_*.log; do
    if [ -f "$log" ]; then
        SIZE=$(ls -lh "$log" | awk '{print $5}')
        LINES=$(wc -l < "$log")
        COMPLETE=$(grep -c "RESEARCH POPULATION COMPLETE" "$log" 2>/dev/null || echo "0")
        ERROR=$(grep -c "Error\|Failed\|Exception" "$log" 2>/dev/null || echo "0")
        
        STATUS="⏳ IN PROGRESS"
        if [ "$COMPLETE" -gt 0 ]; then
            STATUS="✅ COMPLETE"
        elif [ "$ERROR" -gt 0 ]; then
            STATUS="❌ ERROR"
        fi
        
        printf "%-40s %s (Size: %s, Lines: %d)\n" "$log" "$STATUS" "$SIZE" "$LINES"
    fi
done

echo ""
echo "-----------------------------------------------------------"
echo "📁 Generated Files:"
echo "-----------------------------------------------------------"

# Check variation research files
VARIATION_FILES=$(ls materials/data/*_variations_research.txt 2>/dev/null | wc -l | tr -d ' ')
echo "Variation research files: $VARIATION_FILES"

# Check PropertyResearch.yaml updates
if [ -f "materials/data/PropertyResearch.yaml" ]; then
    PROP_SIZE=$(ls -lh materials/data/PropertyResearch.yaml | awk '{print $5}')
    PROP_MATERIALS=$(grep -c "^[A-Z]" materials/data/PropertyResearch.yaml 2>/dev/null || echo "0")
    echo "PropertyResearch.yaml: $PROP_SIZE ($PROP_MATERIALS materials)"
fi

# Check SettingResearch.yaml updates
if [ -f "materials/data/SettingResearch.yaml" ]; then
    SET_SIZE=$(ls -lh materials/data/SettingResearch.yaml | awk '{print $5}')
    SET_MATERIALS=$(grep -c "^[A-Z]" materials/data/SettingResearch.yaml 2>/dev/null || echo "0")
    echo "SettingResearch.yaml: $SET_SIZE ($SET_MATERIALS materials)"
fi

echo ""
echo "-----------------------------------------------------------"
echo "💾 Backup Files Created:"
echo "-----------------------------------------------------------"
BACKUPS=$(ls materials/data/*_backup_*.yaml 2>/dev/null | wc -l | tr -d ' ')
echo "Total backups: $BACKUPS"

echo ""
echo "-----------------------------------------------------------"
echo "⏰ Last Updated: $(date)"
echo "=============================================================="

# Show recent errors if any
TOTAL_ERRORS=0
for log in research_*.log; do
    if [ -f "$log" ]; then
        ERRORS=$(grep -c "Error\|Failed\|Exception" "$log" 2>/dev/null || echo "0")
        TOTAL_ERRORS=$((TOTAL_ERRORS + ERRORS))
    fi
done

if [ "$TOTAL_ERRORS" -gt 0 ]; then
    echo ""
    echo "⚠️  WARNING: $TOTAL_ERRORS errors detected in logs"
    echo "Run: grep -n 'Error\|Failed\|Exception' research_*.log | head -20"
fi

echo ""
