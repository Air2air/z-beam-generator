#!/bin/bash

# Batch Settings Generation for 21 New Materials
# November 23, 2025
# Runs in background with full logging

LOG_FILE="batch_settings_generation.log"
PROGRESS_FILE="batch_settings_progress.txt"

# Initialize progress tracking
echo "0/21" > "$PROGRESS_FILE"
echo "🚀 BATCH SETTINGS GENERATION STARTED: $(date)" | tee "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# All 21 materials needing settings files (ordered by priority)
materials=(
    # Tier 1 - High Priority (already started)
    "Stainless Steel 316"
    "Stainless Steel 304"
    "PTFE"
    "Gallium Nitride"
    
    # Tier 2 - Medium Priority
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
    
    # Tier 3 - Lower Priority
    "PET"
    "Scandium"
    "Bismuth"
    "Ebony"
    "Dolomite"
    "Gneiss"
)

total=${#materials[@]}
completed=0

for material in "${materials[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "⚙️  [$((completed + 1))/$total] Generating settings: $material" | tee -a "$LOG_FILE"
    echo "   ⏰ Started: $(date)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # Run generation (no timeout on macOS)
    python3 run.py --settings-description "$material" --skip-integrity-check >> "$LOG_FILE" 2>&1
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        completed=$((completed + 1))
        echo "   ✅ SUCCESS: $material" | tee -a "$LOG_FILE"
    else
        echo "   ❌ FAILED: $material (exit code: $exit_code)" | tee -a "$LOG_FILE"
    fi
    
    echo "   ⏰ Finished: $(date)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # Update progress
    echo "$completed/$total" > "$PROGRESS_FILE"
    
    # Small delay between generations to avoid API rate limiting
    sleep 2
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "✨ BATCH SETTINGS GENERATION COMPLETE: $(date)" | tee -a "$LOG_FILE"
echo "📊 Results: $completed/$total materials successful" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📄 Full log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "📊 Progress: $PROGRESS_FILE" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
