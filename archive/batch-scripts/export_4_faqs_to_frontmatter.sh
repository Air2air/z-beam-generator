#!/bin/bash
# Export 4 materials with FAQ to frontmatter using data-only mode

echo "=========================================="
echo "Exporting 4 Materials to Frontmatter"
echo "=========================================="

for material in "Beryllium" "Alabaster" "Ash" "Carbon Fiber Reinforced Polymer"; do
    echo ""
    echo "Exporting: $material"
    python3 run.py --material "$material" --data-only 2>&1 | grep -E "(✅|❌|Exported|Error|content/frontmatter)" | head -5
done

echo ""
echo "=========================================="
echo "Export Complete!"
echo "=========================================="
