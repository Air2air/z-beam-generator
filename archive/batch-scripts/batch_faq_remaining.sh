#!/bin/bash
# Generate FAQ for remaining 3 materials

echo "=========================================="
echo "FAQ Generation for 3 Materials"
echo "=========================================="

for material in "Alabaster" "Ash" "Carbon Fiber Reinforced Polymer"; do
    echo ""
    echo "=========================================="
    echo "Generating: $material"
    echo "=========================================="
    python3 run.py --faq "$material" 2>&1 | tail -30
    echo ""
done

echo "=========================================="
echo "All FAQ generations complete!"
echo "=========================================="
