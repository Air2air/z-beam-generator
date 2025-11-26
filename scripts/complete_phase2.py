#!/usr/bin/env python3
"""
Complete Phase 2: Add final 22 patterns to reach exactly 100
"""

import yaml
from pathlib import Path
from datetime import datetime

# Final 22 patterns to complete Phase 2 (100 total)
FINAL_22_PATTERNS = {
    "ceramic-coating": {
        "name": "Ceramic Heat Barrier Coating",
        "description": "Thermal barrier ceramic coatings on engine and exhaust components",
        "composition": ["ZrO₂", "Y₂O₃", "Al₂O₃"],
        "valid_materials": ["Steel", "Stainless Steel", "Titanium"],
        "prohibited_materials": ["Aluminum", "Plastics"]
    },
    "pvd-coating": {
        "name": "PVD Coating Defects",
        "description": "Physical vapor deposition coating irregularities and delamination",
        "composition": ["TiN", "CrN", "AlTiN"],
        "valid_materials": ["Tool Steel", "Carbide", "HSS"],
        "prohibited_materials": ["Soft Metals", "Plastics"]
    },
    "diamond-coating": {
        "name": "Diamond-Like Carbon Removal",
        "description": "DLC coating removal for re-coating or repair operations",
        "composition": ["Amorphous Carbon", "Diamond"],
        "valid_materials": ["Steel", "Titanium", "Tungsten Carbide"],
        "prohibited_materials": ["Soft Metals", "Ceramics"]
    },
    "teflon-residue": {
        "name": "PTFE Coating Residue",
        "description": "Fluoropolymer coating deposits and degradation products",
        "composition": ["PTFE", "Fluorocarbons"],
        "valid_materials": ["Steel", "Aluminum", "Stainless Steel"],
        "prohibited_materials": ["Thin Metals", "Plastics"]
    },
    "nickel-plating": {
        "name": "Electroless Nickel Plating",
        "description": "Nickel-phosphorus coating for selective removal or repair",
        "composition": ["Ni", "P", "NiP Alloy"],
        "valid_materials": ["Steel", "Aluminum", "Copper"],
        "prohibited_materials": ["Thin Substrates", "Plastics"]
    },
    "cadmium-plating": {
        "name": "Cadmium Plating Removal",
        "description": "Hazardous cadmium coating removal from aerospace components",
        "composition": ["Cd", "Cd Alloys"],
        "valid_materials": ["Steel", "Stainless Steel"],
        "prohibited_materials": ["Aluminum", "Thin Metals"]
    },
    "zinc-plating": {
        "name": "Zinc Electroplating",
        "description": "Decorative and corrosion-resistant zinc coating removal",
        "composition": ["Zn", "Zn Alloys"],
        "valid_materials": ["Steel", "Iron"],
        "prohibited_materials": ["Aluminum", "Stainless Steel"]
    },
    "tin-plating": {
        "name": "Tin Plating Residue",
        "description": "Tin coating on electronic components and food containers",
        "composition": ["Sn", "Sn-Pb Alloy"],
        "valid_materials": ["Steel", "Copper", "Brass"],
        "prohibited_materials": ["Aluminum", "Thin Substrates"]
    },
    "gold-plating": {
        "name": "Gold Electroplating",
        "description": "Precious metal gold coating on electronics and jewelry",
        "composition": ["Au", "Au Alloys"],
        "valid_materials": ["Copper", "Brass", "Nickel"],
        "prohibited_materials": ["Steel", "Aluminum"]
    },
    "silver-plating": {
        "name": "Silver Plating Residue",
        "description": "Silver coating and tarnish on electrical contacts and tableware",
        "composition": ["Ag", "Ag₂S (Tarnish)"],
        "valid_materials": ["Copper", "Brass", "Bronze"],
        "prohibited_materials": ["Steel", "Aluminum"]
    },
    "copper-plating": {
        "name": "Copper Electroplating",
        "description": "Decorative and functional copper coating on various substrates",
        "composition": ["Cu", "Cu Compounds"],
        "valid_materials": ["Steel", "Brass", "Plastics (ABS)"],
        "prohibited_materials": ["Aluminum", "Zinc"]
    },
    "brass-plating": {
        "name": "Brass Coating Removal",
        "description": "Copper-zinc alloy decorative plating on hardware and fixtures",
        "composition": ["Cu-Zn Alloy", "Brass"],
        "valid_materials": ["Steel", "Zinc Alloy"],
        "prohibited_materials": ["Aluminum", "Soft Substrates"]
    },
    "bronze-patina": {
        "name": "Bronze Patina and Corrosion",
        "description": "Copper-tin alloy oxidation producing green-brown patinas",
        "composition": ["Cu₂O", "CuO", "Copper Salts"],
        "valid_materials": ["Bronze", "Brass", "Copper"],
        "prohibited_materials": ["Steel", "Aluminum"]
    },
    "lead-paint": {
        "name": "Lead-Based Paint Removal",
        "description": "Hazardous lead paint from historic buildings and structures",
        "composition": ["Pb₃O₄", "PbCO₃", "Oil Binder"],
        "valid_materials": ["Steel", "Wood", "Concrete"],
        "prohibited_materials": ["Thin Metals", "Delicate Substrates"]
    },
    "asbestos-coating": {
        "name": "Asbestos-Containing Material",
        "description": "Fibrous silicate insulation and coating (requires containment)",
        "composition": ["Mg₃Si₂O₅(OH)₄", "Fibers"],
        "valid_materials": ["Steel Pipes", "Boilers", "Concrete"],
        "prohibited_materials": ["Open Environments", "Uncontained Areas"]
    },
    "pcb-contamination": {
        "name": "PCB Oil Contamination",
        "description": "Polychlorinated biphenyl contamination on electrical equipment",
        "composition": ["C₁₂H₁₀₋ₓClₓ", "Chlorinated Compounds"],
        "valid_materials": ["Steel", "Concrete", "Transformer Housings"],
        "prohibited_materials": ["Porous Materials", "Food Areas"]
    },
    "radioactive-contamination": {
        "name": "Surface Radioactive Contamination",
        "description": "Low-level radioactive particle deposits (specialized protocols)",
        "composition": ["Isotopes", "Activation Products"],
        "valid_materials": ["Stainless Steel", "Concrete", "Metal"],
        "prohibited_materials": ["Porous Materials", "Unsealed Areas"]
    },
    "uranium-oxide": {
        "name": "Depleted Uranium Oxide",
        "description": "Uranium oxide contamination from manufacturing and military applications",
        "composition": ["U₃O₈", "UO₂"],
        "valid_materials": ["Steel", "Concrete"],
        "prohibited_materials": ["Porous Materials", "Uncontrolled Environments"]
    },
    "mercury-contamination": {
        "name": "Mercury Spill Residue",
        "description": "Elemental mercury and amalgam contamination",
        "composition": ["Hg", "Metal Amalgams"],
        "valid_materials": ["Concrete", "Tile", "Metal"],
        "prohibited_materials": ["Porous Materials", "Heated Surfaces"]
    },
    "beryllium-oxide": {
        "name": "Beryllium Oxide Contamination",
        "description": "Toxic beryllium oxide from aerospace and nuclear applications",
        "composition": ["BeO", "Be Compounds"],
        "valid_materials": ["Copper-Beryllium Alloy", "Steel"],
        "prohibited_materials": ["Open Environments", "Uncontained Areas"]
    },
    "semiconductor-residue": {
        "name": "Semiconductor Processing Residue",
        "description": "Chemical vapor deposition and etching residues from chip manufacturing",
        "composition": ["SiO₂", "Si₃N₄", "Photoresist", "Metal Films"],
        "valid_materials": ["Silicon Wafers", "Quartz", "Ceramic"],
        "prohibited_materials": ["Flexible Substrates", "Soft Materials"]
    },
    "plasma-spray": {
        "name": "Thermal Spray Coating",
        "description": "Plasma-sprayed ceramic and metal coatings for repair or removal",
        "composition": ["Al₂O₃", "ZrO₂", "MCrAlY", "WC-Co"],
        "valid_materials": ["Steel", "Titanium", "Turbine Blades"],
        "prohibited_materials": ["Thin Substrates", "Soft Metals"]
    }
}

def add_final_patterns(yaml_path: Path):
    """Add final 22 patterns to complete Phase 2 (100 total)"""
    
    print("🎯 Completing Phase 2: Final 22 Patterns")
    print("=" * 70)
    
    # Load existing data
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    patterns = data.get('contamination_patterns', {})
    current_count = len(patterns)
    
    print(f"📊 Current patterns: {current_count}")
    print(f"🎯 Target: 100 patterns")
    print(f"📝 Adding: {len(FINAL_22_PATTERNS)} patterns\n")
    
    # Add new patterns
    added_count = 0
    for pattern_id, pattern_data in FINAL_22_PATTERNS.items():
        if pattern_id not in patterns:
            patterns[pattern_id] = pattern_data
            added_count += 1
            print(f"  ✓ Added: {pattern_id}")
        else:
            print(f"  ⚠ Skipped (exists): {pattern_id}")
    
    # Update metadata
    data['contamination_patterns'] = patterns
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Save
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Final summary
    total = len(patterns)
    with_laser = sum(1 for p in patterns.values() if 'laser_properties' in p)
    need_research = total - with_laser
    
    print("\n" + "=" * 70)
    print("🎉 PHASE 2 COMPLETION SUMMARY")
    print("=" * 70)
    print(f"✅ Patterns added: {added_count}")
    print(f"📈 Total patterns: {total}")
    print(f"🔬 With laser properties: {with_laser} ({with_laser/total*100:.1f}%)")
    print(f"📋 Need research: {need_research}")
    
    if total >= 100:
        print(f"\n🎉🎉🎉 PHASE 2 COMPLETE! 🎉🎉🎉")
        print(f"✨ Achieved: {total}/100 patterns ({total}%)")
    else:
        print(f"\n📝 Gap: {100 - total} patterns remaining")
    
    print(f"\n📊 Research Progress:")
    print(f"   Researched: {with_laser}/{total} ({with_laser/total*100:.1f}%)")
    print(f"   Remaining: {need_research}/{total} ({need_research/total*100:.1f}%)")
    
    return added_count, total

if __name__ == "__main__":
    yaml_path = Path("data/contaminants/Contaminants.yaml")
    
    if not yaml_path.exists():
        print(f"❌ Error: {yaml_path} not found")
        exit(1)
    
    added, total = add_final_patterns(yaml_path)
    
    if added > 0:
        print(f"\n✅ SUCCESS! Added {added} patterns")
        print(f"\n🔬 Next Step: Research laser properties for {total - 11} patterns")
        print(f"   python3 scripts/research_laser_properties.py --all-patterns --type complete_profile --save")
    else:
        print("\n⚠️ No patterns added")
