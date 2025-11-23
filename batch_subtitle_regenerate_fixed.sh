#!/bin/bash

# Batch Subtitle Regeneration Script (Fixed - single generation per material)
# Regenerates subtitles for all 132 materials

MATERIALS=(
    "Aluminum" "Copper" "Steel" "Titanium" "Bronze" "Brass" "Iron" "Zinc" "Nickel" "Lead"
    "Tin" "Chromium" "Cobalt" "Tungsten" "Molybdenum" "Magnesium" "Silver" "Gold" "Platinum" "Palladium"
    "Stainless Steel" "Carbon Steel" "Tool Steel" "Cast Iron" "Wrought Iron" "Galvanized Steel" "Zirconium" "Beryllium" "Vanadium" "Niobium"
    "Tantalum" "Rhenium" "Osmium" "Iridium" "Ruthenium" "Rhodium" "Indium" "Gallium" "Germanium" "Antimony"
    "Bismuth" "Cadmium" "Mercury" "Thallium" "Arsenic" "Selenium" "Tellurium" "Polonium" "Astatine" "Francium"
    "Radium" "Actinium" "Thorium" "Protactinium" "Uranium" "Neptunium" "Plutonium" "Americium" "Curium" "Berkelium"
    "Californium" "Einsteinium" "Fermium" "Mendelevium" "Nobelium" "Lawrencium" "Silicon" "Glass" "Quartz" "Ceramic"
    "Porcelain" "Concrete" "Brick" "Stone" "Marble" "Granite" "Limestone" "Sandstone" "Slate" "Basalt"
    "Obsidian" "Plastic" "Polypropylene" "Polyethylene" "PVC" "Polystyrene" "Nylon" "Acrylic" "Polycarbonate" "ABS"
    "Teflon" "Rubber" "Silicone" "Wood" "Oak" "Pine" "Maple" "Cherry" "Walnut" "Bamboo"
    "Plywood" "MDF" "Particleboard" "Composite" "Carbon Fiber" "Fiberglass" "Kevlar" "Graphite" "Diamond" "Sapphire"
    "Ruby" "Emerald" "Topaz" "Amethyst" "Jade" "Lapis Lazuli" "Turquoise" "Opal" "Pearl" "Coral"
    "Amber" "Jet" "Ivory" "Bone" "Shell" "Leather" "Fabric" "Cotton" "Silk" "Wool"
    "Linen" "Paper"
)

# Skip already completed materials (Aluminum through Lead = first 10)
START_INDEX=11
TOTAL=${#MATERIALS[@]}
SUCCESS=0
FAILED=0

echo "=================================================="
echo "📝 BATCH SUBTITLE REGENERATION (RESUMED)"
echo "=================================================="
echo "Total materials: $TOTAL"
echo "Resuming from: ${MATERIALS[$START_INDEX]} (index $START_INDEX)"
echo ""

for i in $(seq $START_INDEX $((TOTAL - 1))); do
    MATERIAL="${MATERIALS[$i]}"
    NUM=$((i + 1))
    
    echo "[$NUM/$TOTAL] Generating subtitle for: $MATERIAL"
    
    OUTPUT=$(python3 run.py --subtitle "$MATERIAL" --skip-integrity-check 2>&1)
    
    if echo "$OUTPUT" | grep -q "✅ Subtitle generated"; then
        echo "   ✅ SUCCESS"
        ((SUCCESS++))
    else
        echo "   ❌ FAILED"
        ((FAILED++))
    fi
    echo ""
done

echo "=================================================="
echo "📊 BATCH COMPLETE"
echo "=================================================="
echo "✅ Success: $SUCCESS"
echo "❌ Failed: $FAILED"
echo "📈 Success rate: $(echo "scale=1; $SUCCESS * 100 / ($SUCCESS + $FAILED)" | bc)%"
