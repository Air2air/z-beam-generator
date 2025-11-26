#!/usr/bin/env python3
"""
Phase 2 Expansion: Add patterns to reach 100 total + rename with hyphens
"""

import yaml
from pathlib import Path
from datetime import datetime

# Additional 45 patterns to reach Phase 2 (100 total from current 33 + 22 = 55)
PHASE2_PATTERNS = {
    "steel-corrosion": {
        "name": "Steel Surface Corrosion",
        "description": "General oxidation and corrosion products on carbon steel and alloy steel surfaces",
        "composition": ["Fe₃O₄", "FeO", "Fe₂O₃"],
        "valid_materials": ["Steel", "Carbon Steel", "Alloy Steel"],
        "prohibited_materials": ["Stainless Steel", "Aluminum", "Copper"]
    },
    "salt-residue": {
        "name": "Salt and Chloride Deposits",
        "description": "Marine salt deposits and road salt residues causing chloride contamination",
        "composition": ["NaCl", "MgCl₂", "CaCl₂"],
        "valid_materials": ["Metal", "Concrete", "Stone"],
        "prohibited_materials": ["Electronics", "Painted Surfaces"]
    },
    "hydraulic-fluid": {
        "name": "Hydraulic Fluid Contamination",
        "description": "Petroleum-based hydraulic oil deposits from heavy machinery leaks",
        "composition": ["Mineral Oil", "Additives", "Zinc Compounds"],
        "valid_materials": ["Steel", "Aluminum", "Concrete"],
        "prohibited_materials": ["Plastics", "Rubber", "Electronics"]
    },
    "cutting-fluid": {
        "name": "Machining Coolant Residue",
        "description": "Water-soluble and oil-based cutting fluid residues from metal machining",
        "composition": ["Emulsified Oil", "Biocides", "Surfactants"],
        "valid_materials": ["Steel", "Aluminum", "Brass", "Titanium"],
        "prohibited_materials": ["Plastics", "Wood"]
    },
    "welding-spatter": {
        "name": "Welding Spatter and Slag",
        "description": "Molten metal droplets and slag deposits from welding operations",
        "composition": ["Fe", "SiO₂", "CaO", "MnO"],
        "valid_materials": ["Steel", "Stainless Steel", "Aluminum"],
        "prohibited_materials": ["Plastics", "Glass", "Thin Metals"]
    },
    "primer-coating": {
        "name": "Paint Primer Layers",
        "description": "Zinc-rich and epoxy-based primer coatings on metal surfaces",
        "composition": ["Zinc Dust", "Epoxy Resin", "Pigments"],
        "valid_materials": ["Steel", "Aluminum", "Galvanized Metal"],
        "prohibited_materials": ["Plastics", "Wood"]
    },
    "metal-polish": {
        "name": "Metal Polish Residue",
        "description": "Abrasive compound deposits from metal polishing operations",
        "composition": ["Al₂O₃", "CeO₂", "Wax", "Surfactants"],
        "valid_materials": ["Steel", "Aluminum", "Brass", "Copper"],
        "prohibited_materials": ["Plastics", "Glass", "Ceramics"]
    },
    "laser-marking": {
        "name": "Laser Marking Discoloration",
        "description": "Oxidized surface layer from laser engraving and marking processes",
        "composition": ["Metal Oxides", "Carbon", "Nitrides"],
        "valid_materials": ["Steel", "Aluminum", "Titanium", "Brass"],
        "prohibited_materials": ["Plastics", "Ceramics"]
    },
    "annealing-scale": {
        "name": "Heat Treatment Scale",
        "description": "Thick oxide layer from annealing and heat treatment processes",
        "composition": ["Fe₃O₄", "FeO", "Cr₂O₃"],
        "valid_materials": ["Steel", "Stainless Steel", "Titanium"],
        "prohibited_materials": ["Aluminum", "Copper", "Plastics"]
    },
    "forging-scale": {
        "name": "Forging Mill Scale",
        "description": "Black oxide scale formed during hot forging and rolling operations",
        "composition": ["Fe₃O₄", "FeO"],
        "valid_materials": ["Steel", "Iron", "Carbon Steel"],
        "prohibited_materials": ["Stainless Steel", "Aluminum", "Copper"]
    },
    "quench-oil": {
        "name": "Quenching Oil Residue",
        "description": "Carbonized oil deposits from metal heat treatment quenching",
        "composition": ["Carbonized Oil", "PAH", "Additives"],
        "valid_materials": ["Steel", "Tool Steel", "Alloy Steel"],
        "prohibited_materials": ["Aluminum", "Plastics"]
    },
    "pickling-residue": {
        "name": "Acid Pickling Stains",
        "description": "Residual acid and iron salt deposits from chemical pickling processes",
        "composition": ["FeCl₂", "H₂SO₄", "Iron Salts"],
        "valid_materials": ["Stainless Steel", "Steel"],
        "prohibited_materials": ["Aluminum", "Copper", "Plastics"]
    },
    "passivation-defect": {
        "name": "Passivation Layer Irregularities",
        "description": "Uneven chromium oxide layer from stainless steel passivation",
        "composition": ["Cr₂O₃", "Fe₂O₃"],
        "valid_materials": ["Stainless Steel", "Chrome-Plated Steel"],
        "prohibited_materials": ["Carbon Steel", "Aluminum"]
    },
    "electroplating-residue": {
        "name": "Electroplating Solution Residue",
        "description": "Chemical deposits from electroplating bath solutions",
        "composition": ["Cyanides", "Metal Salts", "Brighteners"],
        "valid_materials": ["Steel", "Brass", "Copper"],
        "prohibited_materials": ["Aluminum", "Plastics"]
    },
    "conversion-coating": {
        "name": "Chemical Conversion Coating",
        "description": "Phosphate and chromate conversion coatings on metal surfaces",
        "composition": ["Zn₃(PO₄)₂", "Fe₃(PO₄)₂", "Chromates"],
        "valid_materials": ["Steel", "Aluminum", "Zinc"],
        "prohibited_materials": ["Stainless Steel", "Plastics"]
    },
    "anti-seize": {
        "name": "Anti-Seize Compound",
        "description": "Metallic and graphite-based thread lubricant deposits",
        "composition": ["Copper", "Graphite", "Aluminum", "Grease"],
        "valid_materials": ["Steel", "Stainless Steel", "Aluminum"],
        "prohibited_materials": ["Plastics", "Electronics"]
    },
    "thread-locker": {
        "name": "Threadlocker Adhesive",
        "description": "Anaerobic adhesive residue from mechanical fasteners",
        "composition": ["Dimethacrylate", "Peroxides", "Dyes"],
        "valid_materials": ["Steel", "Stainless Steel", "Aluminum"],
        "prohibited_materials": ["Plastics", "Soft Metals"]
    },
    "gasket-material": {
        "name": "Gasket Material Residue",
        "description": "Compressed fiber, rubber, and silicone gasket remnants",
        "composition": ["Cellulose", "Rubber", "Silicone", "Graphite"],
        "valid_materials": ["Steel", "Aluminum", "Cast Iron"],
        "prohibited_materials": ["Thin Metals", "Plastics"]
    },
    "carbon-buildup": {
        "name": "Carbon Deposit Buildup",
        "description": "Hard carbon deposits from combustion and pyrolysis",
        "composition": ["C", "PAH", "Soot"],
        "valid_materials": ["Steel", "Stainless Steel", "Ceramic"],
        "prohibited_materials": ["Aluminum", "Plastics"]
    },
    "fuel-varnish": {
        "name": "Fuel System Varnish",
        "description": "Polymerized fuel deposits in engines and fuel systems",
        "composition": ["Gum", "Varnish", "Carbon"],
        "valid_materials": ["Steel", "Aluminum", "Brass"],
        "prohibited_materials": ["Plastics", "Rubber"]
    },
    "exhaust-residue": {
        "name": "Exhaust System Deposits",
        "description": "Carbonaceous and metallic deposits from engine exhaust",
        "composition": ["C", "Pb", "V₂O₅", "Sulfates"],
        "valid_materials": ["Steel", "Stainless Steel", "Titanium"],
        "prohibited_materials": ["Aluminum", "Plastics"]
    },
    "coolant-scale": {
        "name": "Engine Coolant Scale",
        "description": "Silicate and phosphate deposits from engine cooling systems",
        "composition": ["SiO₂", "CaCO₃", "Phosphates"],
        "valid_materials": ["Aluminum", "Cast Iron", "Brass"],
        "prohibited_materials": ["Plastics", "Rubber"]
    },
    "brake-dust": {
        "name": "Brake Pad Dust Deposits",
        "description": "Metallic and ceramic brake pad wear particles",
        "composition": ["Fe", "Cu", "Ceramic Fibers", "Graphite"],
        "valid_materials": ["Steel", "Aluminum", "Cast Iron"],
        "prohibited_materials": ["Plastics", "Glass"]
    },
    "road-grime": {
        "name": "Automotive Road Grime",
        "description": "Mixed contamination from road use including dirt, oil, and salt",
        "composition": ["Soil", "Oil", "NaCl", "Rubber"],
        "valid_materials": ["Steel", "Aluminum", "Painted Surfaces"],
        "prohibited_materials": ["Electronics", "Optics"]
    },
    "undercoating": {
        "name": "Automotive Undercoating",
        "description": "Rubberized or tar-based protective coating on vehicle underbodies",
        "composition": ["Asphalt", "Rubber", "Solvents"],
        "valid_materials": ["Steel", "Painted Metal"],
        "prohibited_materials": ["Plastics", "Aluminum"]
    },
    "aviation-sealant": {
        "name": "Aerospace Sealant Residue",
        "description": "Polysulfide and silicone sealants from aircraft assembly",
        "composition": ["Polysulfide", "Silicone", "Additives"],
        "valid_materials": ["Aluminum", "Titanium", "Composite"],
        "prohibited_materials": ["Plastics", "Glass"]
    },
    "corrosion-inhibitor": {
        "name": "Corrosion Inhibitor Coating",
        "description": "Chemical protective coatings applied for storage and shipping",
        "composition": ["Amines", "Oil", "Wax", "VCI"],
        "valid_materials": ["Steel", "Aluminum", "Copper"],
        "prohibited_materials": ["Plastics", "Electronics"]
    },
    "fire-damage": {
        "name": "Fire and Smoke Damage",
        "description": "Char, soot, and thermal degradation products from fire exposure",
        "composition": ["C", "Ash", "Tar", "Metal Oxides"],
        "valid_materials": ["Steel", "Concrete", "Stone", "Ceramic"],
        "prohibited_materials": ["Wood", "Plastics", "Fabrics"]
    },
    "water-stain": {
        "name": "Water Staining and Marks",
        "description": "Mineral deposits and discoloration from water exposure",
        "composition": ["CaCO₃", "Fe₂O₃", "Organic Matter"],
        "valid_materials": ["Stone", "Concrete", "Metal", "Glass"],
        "prohibited_materials": ["Electronics", "Wood"]
    },
    "algae-growth": {
        "name": "Algae and Lichen Growth",
        "description": "Photosynthetic organism colonization on outdoor surfaces",
        "composition": ["Chlorophyll", "Polysaccharides", "Minerals"],
        "valid_materials": ["Stone", "Concrete", "Wood", "Metal"],
        "prohibited_materials": ["Food Surfaces", "Medical Equipment"]
    },
    "efflorescence": {
        "name": "Concrete Efflorescence",
        "description": "White crystalline salt deposits on concrete and masonry",
        "composition": ["CaCO₃", "CaSO₄", "Na₂CO₃"],
        "valid_materials": ["Concrete", "Brick", "Stone"],
        "prohibited_materials": ["Metal", "Glass"]
    },
    "graffiti-paint": {
        "name": "Graffiti and Spray Paint",
        "description": "Aerosol paint and marker deposits on public surfaces",
        "composition": ["Acrylic", "Enamel", "Solvents", "Pigments"],
        "valid_materials": ["Concrete", "Stone", "Metal", "Brick"],
        "prohibited_materials": ["Porous Surfaces", "Plastics"]
    },
    "bird-droppings": {
        "name": "Bird Waste Deposits",
        "description": "Avian fecal matter containing uric acid and calcium",
        "composition": ["Uric Acid", "CaCO₃", "Organic Matter"],
        "valid_materials": ["Stone", "Metal", "Glass", "Concrete"],
        "prohibited_materials": ["Food Surfaces", "Porous Materials"]
    },
    "tree-sap": {
        "name": "Tree Sap and Resin",
        "description": "Sticky organic plant exudates on surfaces",
        "composition": ["Terpenes", "Resin Acids", "Sugars"],
        "valid_materials": ["Metal", "Glass", "Painted Surfaces"],
        "prohibited_materials": ["Fabrics", "Porous Materials"]
    },
    "pollen-deposit": {
        "name": "Pollen Accumulation",
        "description": "Fine powdery plant pollen deposits on outdoor surfaces",
        "composition": ["Proteins", "Lipids", "Cellulose"],
        "valid_materials": ["Glass", "Metal", "Painted Surfaces"],
        "prohibited_materials": ["Electronics", "Optics"]
    },
    "insect-residue": {
        "name": "Insect Impact Residue",
        "description": "Protein-rich insect body deposits on vehicles and structures",
        "composition": ["Proteins", "Chitin", "Fats"],
        "valid_materials": ["Glass", "Metal", "Painted Surfaces"],
        "prohibited_materials": ["Food Surfaces", "Medical Equipment"]
    },
    "lime-scale": {
        "name": "Limescale Deposits",
        "description": "Hard calcium carbonate buildup from hard water evaporation",
        "composition": ["CaCO₃", "MgCO₃"],
        "valid_materials": ["Glass", "Metal", "Ceramic", "Tile"],
        "prohibited_materials": ["Electronics", "Painted Surfaces"]
    },
    "soap-scum": {
        "name": "Soap Scum Buildup",
        "description": "Fatty acid salt deposits from soap and hard water interaction",
        "composition": ["Calcium Stearate", "Mg Stearate", "Surfactants"],
        "valid_materials": ["Glass", "Ceramic", "Tile", "Fiberglass"],
        "prohibited_materials": ["Electronics", "Porous Stone"]
    },
    "mineral-stain": {
        "name": "Mineral Staining",
        "description": "Iron, manganese, and copper staining from water sources",
        "composition": ["Fe₂O₃", "MnO₂", "CuO"],
        "valid_materials": ["Concrete", "Stone", "Tile", "Grout"],
        "prohibited_materials": ["Metal", "Electronics"]
    },
    "fertilizer-residue": {
        "name": "Fertilizer Salt Deposits",
        "description": "Nitrate and phosphate deposits from agricultural chemicals",
        "composition": ["KNO₃", "NH₄NO₃", "Phosphates"],
        "valid_materials": ["Concrete", "Stone", "Metal"],
        "prohibited_materials": ["Electronics", "Food Surfaces"]
    },
    "pesticide-residue": {
        "name": "Pesticide Chemical Residue",
        "description": "Organic and inorganic pesticide deposits on surfaces",
        "composition": ["Organophosphates", "Pyrethroids", "Copper Compounds"],
        "valid_materials": ["Metal", "Glass", "Concrete"],
        "prohibited_materials": ["Food Surfaces", "Wood"]
    },
    "medical-disinfectant": {
        "name": "Medical Disinfectant Residue",
        "description": "Chlorine and quaternary ammonium compound deposits",
        "composition": ["NaOCl", "Quats", "Phenolics"],
        "valid_materials": ["Stainless Steel", "Glass", "Ceramic"],
        "prohibited_materials": ["Aluminum", "Soft Plastics"]
    },
    "surgical-marking": {
        "name": "Surgical Ink Markings",
        "description": "Gentian violet and skin marker residues on medical instruments",
        "composition": ["Gentian Violet", "Dyes", "Alcohol"],
        "valid_materials": ["Stainless Steel", "Titanium"],
        "prohibited_materials": ["Plastics", "Rubber"]
    },
    "blood-residue": {
        "name": "Biological Blood Residue",
        "description": "Protein and hemoglobin deposits from biological contamination",
        "composition": ["Hemoglobin", "Proteins", "Lipids"],
        "valid_materials": ["Stainless Steel", "Glass", "Ceramic"],
        "prohibited_materials": ["Porous Materials", "Fabrics"]
    },
    "pharmaceutical-residue": {
        "name": "Pharmaceutical Drug Residue",
        "description": "Active pharmaceutical ingredient deposits on processing equipment",
        "composition": ["APIs", "Excipients", "Coatings"],
        "valid_materials": ["Stainless Steel", "Glass", "Teflon"],
        "prohibited_materials": ["Porous Materials", "Soft Plastics"]
    }
}

def rename_patterns_to_hyphens(data: dict) -> dict:
    """Convert all pattern IDs from underscore to hyphen format"""
    patterns = data.get('contamination_patterns', {})
    
    # Create new dict with hyphenated keys
    new_patterns = {}
    rename_count = 0
    
    for old_key, pattern_data in patterns.items():
        new_key = old_key.replace('_', '-')
        new_patterns[new_key] = pattern_data
        if old_key != new_key:
            rename_count += 1
            print(f"  ✓ {old_key} → {new_key}")
    
    data['contamination_patterns'] = new_patterns
    return data, rename_count

def add_phase2_patterns(yaml_path: Path):
    """Add Phase 2 patterns and rename to hyphen format"""
    
    print("🔧 Phase 2 Expansion + Hyphen Renaming")
    print("=" * 70)
    
    # Load existing data
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Step 1: Rename existing patterns
    print("\n📝 Step 1: Renaming patterns (underscore → hyphen)")
    data, rename_count = rename_patterns_to_hyphens(data)
    print(f"   Renamed: {rename_count} patterns")
    
    # Step 2: Add new patterns
    print("\n📝 Step 2: Adding Phase 2 patterns")
    patterns = data['contamination_patterns']
    
    added_count = 0
    for pattern_id, pattern_data in PHASE2_PATTERNS.items():
        if pattern_id not in patterns:
            patterns[pattern_id] = pattern_data
            added_count += 1
            print(f"  ✓ Added: {pattern_id}")
        else:
            print(f"  ⚠ Skipped (exists): {pattern_id}")
    
    # Update metadata
    data['contamination_patterns'] = patterns
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Save back to file
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Summary
    total = len(patterns)
    with_laser = sum(1 for p in patterns.values() if 'laser_properties' in p)
    need_research = total - with_laser
    
    print("\n" + "=" * 70)
    print("📊 PHASE 2 SUMMARY")
    print("=" * 70)
    print(f"✅ Patterns renamed: {rename_count}")
    print(f"✅ Patterns added: {added_count}")
    print(f"📈 Total patterns: {total}")
    print(f"🔬 With laser properties: {with_laser}")
    print(f"📋 Need research: {need_research}")
    print(f"\n🎯 Phase 2 Target: 100 patterns")
    print(f"📊 Current: {total}/100 ({total}%)")
    
    if total >= 100:
        print("🎉 PHASE 2 COMPLETE!")
    else:
        print(f"📝 Gap: {100 - total} patterns to Phase 2 target")
    
    return added_count, rename_count

if __name__ == "__main__":
    yaml_path = Path("data/contaminants/Contaminants.yaml")
    
    if not yaml_path.exists():
        print(f"❌ Error: {yaml_path} not found")
        exit(1)
    
    added, renamed = add_phase2_patterns(yaml_path)
    
    if added > 0 or renamed > 0:
        print(f"\n✅ SUCCESS!")
        print(f"\nNext step: Research laser properties")
        print(f"  python3 scripts/research_laser_properties.py --all-patterns --type complete_profile --save")
    else:
        print("\n⚠️ No changes made")
