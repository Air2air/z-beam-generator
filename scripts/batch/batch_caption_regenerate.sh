#!/bin/bash

# Batch Caption Regeneration Script
# Regenerates captions for all 132 materials

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

TOTAL=${#MATERIALS[@]}
SUCCESS=0
FAILED=0

echo "=================================================="
echo "🎨 BATCH CAPTION REGENERATION"
echo "=================================================="
echo "Total materials: $TOTAL"
echo ""

for i in "${!MATERIALS[@]}"; do
    MATERIAL="${MATERIALS[$i]}"
    NUM=$((i + 1))
    
    echo "[$NUM/$TOTAL] Generating caption for: $MATERIAL"
    
    if python3 run.py --caption "$MATERIAL" --skip-integrity-check 2>&1 | grep -q "✅ Caption generated"; then
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
echo "📈 Success rate: $(echo "scale=1; $SUCCESS * 100 / $TOTAL" | bc)%"
