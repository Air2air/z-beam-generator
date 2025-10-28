#!/bin/bash
# Generate FAQ for 4 diverse materials

materials=("Beryllium" "Alabaster" "Ash" "Carbon Fiber Reinforced Polymer")

for material in "${materials[@]}"; do
    echo "=========================================="
    echo "Generating FAQ for: $material"
    echo "=========================================="
    python3 run.py --faq "$material" 2>&1 | grep -E "(✅|❌|📊|📝|💾|Error)" | tail -20
    echo ""
done

echo "=========================================="
echo "All FAQ generations complete!"
echo "=========================================="
