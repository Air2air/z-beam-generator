#!/bin/bash

# Batch Regeneration Script for All 132 Materials
# November 22, 2025

cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator

materials=(
"Alabaster" "Alumina" "Aluminum" "Ash" "Bamboo" "Basalt" "Beech" "Beryllium" 
"Birch" "Bluestone" "Borosilicate Glass" "Brass" "Breccia" "Brick" "Bronze" 
"Calcite" "Carbon Fiber Reinforced Polymer" "Cast Iron" "Cedar" "Cement" 
"Ceramic Matrix Composites CMCs" "Cerium" "Cherry" "Chromium" "Cobalt" 
"Concrete" "Copper" "Crown Glass" "Dysprosium" "Epoxy Resin Composites" 
"Europium" "Fiber Reinforced Polyurethane FRPU" "Fiberglass" "Fir" 
"Float Glass" "Fused Silica" "Gallium" "Gallium Arsenide" 
"Glass Fiber Reinforced Polymers GFRP" "Gold" "Gorilla Glass" "Granite" 
"Hafnium" "Hastelloy" "Hickory" "Inconel" "Indium" "Iridium" "Iron" 
"Kevlar-Reinforced Polymer" "Lanthanum" "Lead" "Lead Crystal" "Limestone" 
"MDF" "Magnesium" "Mahogany" "Manganese" "Maple" "Marble" 
"Metal Matrix Composites MMCs" "Molybdenum" "Mortar" "Neodymium" "Nickel" 
"Niobium" "Oak" "Onyx" "Palladium" "Phenolic Resin Composites" "Pine" 
"Plaster" "Platinum" "Plywood" "Polycarbonate" "Polyester Resin Composites" 
"Polyethylene" "Polypropylene" "Polystyrene" "Polytetrafluoroethylene" 
"Polyvinyl Chloride" "Poplar" "Porcelain" "Porphyry" "Praseodymium" "Pyrex" 
"Quartz Glass" "Quartzite" "Redwood" "Rhenium" "Rhodium" "Rosewood" "Rubber" 
"Ruthenium" "Sandstone" "Sapphire Glass" "Schist" "Serpentine" "Shale" 
"Silicon" "Silicon Carbide" "Silicon Germanium" "Silicon Nitride" "Silver" 
"Slate" "Soapstone" "Soda-Lime Glass" "Stainless Steel" "Steel" "Stoneware" 
"Stucco" "Tantalum" "Teak" "Tempered Glass" "Terbium" "Terracotta" 
"Thermoplastic Elastomer" "Tin" "Titanium" "Titanium Carbide" "Tool Steel" 
"Travertine" "Tungsten" "Tungsten Carbide" "Urethane Composites" "Vanadium" 
"Walnut" "Willow" "Yttrium" "Zinc" "Zirconia" "Zirconium"
)

total=${#materials[@]}
success=0
failed=0
start_time=$(date +%s)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 BATCH REGENERATION: All 132 Materials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏰ Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📊 Total: $total materials"
echo ""

for i in "${!materials[@]}"; do
    material="${materials[$i]}"
    num=$((i + 1))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[$num/$total] 🔄 $material"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if python3 run.py --description "$material" --skip-integrity-check 2>&1 | grep -q "Description generated and saved"; then
        success=$((success + 1))
        echo "✅ SUCCESS ($success/$total)"
    else
        failed=$((failed + 1))
        echo "❌ FAILED ($failed failures)"
    fi
    
    echo ""
    
    # Progress summary every 10 materials
    if [ $((num % 10)) -eq 0 ]; then
        elapsed=$(($(date +%s) - start_time))
        rate=$(echo "scale=2; $num / $elapsed" | bc)
        remaining=$((total - num))
        eta=$(echo "scale=0; $remaining / $rate" | bc)
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📊 PROGRESS CHECKPOINT"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "   Completed: $num/$total ($((num * 100 / total))%)"
        echo "   Success: $success | Failed: $failed"
        echo "   Rate: $rate materials/sec"
        echo "   ETA: $eta seconds (~$((eta / 60)) minutes)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
done

end_time=$(date +%s)
duration=$((end_time - start_time))
minutes=$((duration / 60))
seconds=$((duration % 60))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 BATCH REGENERATION COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏰ Completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo "⏱️  Duration: ${minutes}m ${seconds}s"
echo "📊 Results:"
echo "   ✅ Success: $success/$total"
echo "   ❌ Failed: $failed/$total"
echo "   📈 Success Rate: $((success * 100 / total))%"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
