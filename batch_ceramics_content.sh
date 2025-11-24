#!/bin/bash

# Batch generate content for 3 ceramic materials
MATERIALS=("Boron Nitride" "Titanium Nitride" "Yttria-Stabilized Zirconia")

echo "========================================"
echo "🔬 CERAMIC MATERIALS CONTENT GENERATION"
echo "========================================"
echo ""

for material in "${MATERIALS[@]}"; do
    echo "📝 Processing: $material"
    echo "   ├─ Material Description..."
    python3 run.py --material-description "$material" --skip-integrity-check 2>&1 | grep -E "(✅|❌|Generated|Saved)" | tail -5
    
    echo "   ├─ Caption..."
    python3 run.py --caption "$material" --skip-integrity-check 2>&1 | grep -E "(✅|❌|Generated|Saved)" | tail -5
    
    echo "   └─ FAQ..."
    python3 run.py --faq "$material" --skip-integrity-check 2>&1 | grep -E "(✅|❌|Generated|Saved)" | tail -5
    
    echo "   ✅ $material complete"
    echo ""
done

echo "========================================"
echo "✅ ALL CERAMICS COMPLETE"
echo "========================================"
