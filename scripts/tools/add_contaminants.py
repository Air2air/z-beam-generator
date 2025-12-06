#!/usr/bin/env python3
"""
Add 22 new contamination patterns to Contaminants.yaml
"""

import yaml
from pathlib import Path
from datetime import datetime

# New contamination patterns with basic metadata
NEW_PATTERNS = {
    "silicone_buildup": {
        "name": "Silicone Sealant Buildup",
        "description": "Polysiloxane-based sealant and coating residues commonly found in construction and automotive applications",
        "composition": ["(CH₃)₂SiO", "SiO₂"],
        "valid_materials": ["Metal", "Glass", "Ceramic", "Concrete"],
        "prohibited_materials": ["Plastics", "Wood"]
    },
    "grease_deposits": {
        "name": "Heavy Machinery Grease",
        "description": "Petroleum-based lubricant deposits with metallic additives from industrial machinery",
        "composition": ["Mineral Oil", "Lithium Soap", "PTFE"],
        "valid_materials": ["Steel", "Iron", "Aluminum", "Cast Iron"],
        "prohibited_materials": ["Plastics", "Wood", "Textiles"]
    },
    "carbon_soot": {
        "name": "Carbon Soot Deposits",
        "description": "Fine particulate carbon from incomplete combustion in engines, furnaces, and industrial processes",
        "composition": ["C", "PAH"],
        "valid_materials": ["Metal", "Ceramic", "Stone", "Concrete"],
        "prohibited_materials": ["Wood", "Plastics", "Textiles"]
    },
    "concrete_dust": {
        "name": "Concrete Dust Deposits",
        "description": "Portland cement and aggregate particulates from construction and grinding operations",
        "composition": ["CaCO₃", "SiO₂", "CaO"],
        "valid_materials": ["Steel", "Concrete", "Stone"],
        "prohibited_materials": ["Electronics", "Optical Glass"]
    },
    "rubber_residue": {
        "name": "Rubber Compound Residue",
        "description": "Vulcanized rubber deposits from tire marks, seals, and gaskets",
        "composition": ["C₅H₈", "Sulfur", "Carbon Black"],
        "valid_materials": ["Concrete", "Asphalt", "Metal"],
        "prohibited_materials": ["Plastics", "Glass"]
    },
    "bitumen_tar": {
        "name": "Bitumen and Tar Coatings",
        "description": "Heavy petroleum-based coatings from roofing, paving, and waterproofing applications",
        "composition": ["Asphaltene", "Resin", "Saturates"],
        "valid_materials": ["Concrete", "Steel", "Stone"],
        "prohibited_materials": ["Plastics", "Wood", "Electronics"]
    },
    "mineral_deposits": {
        "name": "Hard Water Mineral Scale",
        "description": "Calcium and magnesium carbonate deposits from evaporated hard water",
        "composition": ["CaCO₃", "MgCO₃", "CaSO₄"],
        "valid_materials": ["Metal", "Glass", "Ceramic", "Stone"],
        "prohibited_materials": ["Electronics", "Plastics"]
    },
    "mold_mildew": {
        "name": "Mold and Mildew Growth",
        "description": "Fungal colonization producing organic acids and pigmented spores on damp surfaces",
        "composition": ["Fungal Hyphae", "Melanin", "Organic Acids"],
        "valid_materials": ["Wood", "Concrete", "Drywall", "Ceramic"],
        "prohibited_materials": ["Food Surfaces", "Medical Equipment"]
    },
    "wax_buildup": {
        "name": "Wax Coating Buildup",
        "description": "Paraffin, carnauba, and synthetic wax deposits from protective coatings and polishes",
        "composition": ["C₂₅H₅₂", "Esters", "Fatty Acids"],
        "valid_materials": ["Metal", "Wood", "Painted Surfaces"],
        "prohibited_materials": ["Plastics", "Rubber"]
    },
    "epoxy_residue": {
        "name": "Epoxy Resin Deposits",
        "description": "Cured two-part epoxy adhesive and coating residues with high cross-link density",
        "composition": ["Bisphenol A", "Epichlorohydrin", "Amine Hardener"],
        "valid_materials": ["Metal", "Concrete", "Composite"],
        "prohibited_materials": ["Thin Plastics", "Glass"]
    },
    "ink_stains": {
        "name": "Printing Ink Residue",
        "description": "Pigmented ink deposits from industrial printing, markers, and spray paint",
        "composition": ["Pigments", "Binder Resin", "Solvents"],
        "valid_materials": ["Paper", "Cardboard", "Metal", "Concrete"],
        "prohibited_materials": ["Fabrics", "Porous Wood"]
    },
    "solder_flux": {
        "name": "Soldering Flux Residue",
        "description": "Rosin-based and no-clean flux residues from electronics soldering operations",
        "composition": ["Abietic Acid", "Activators", "Surfactants"],
        "valid_materials": ["PCB", "Copper", "Brass", "Electronics"],
        "prohibited_materials": ["Plastics", "Optical Components"]
    },
    "thermal_paste": {
        "name": "Thermal Compound Deposits",
        "description": "Silicone or metal-based thermal interface materials from CPU/GPU cooling systems",
        "composition": ["ZnO", "Ag", "Al₂O₃", "Silicone Oil"],
        "valid_materials": ["Copper", "Aluminum", "Nickel-Plated Surfaces"],
        "prohibited_materials": ["Plastics", "PCB"]
    },
    "battery_corrosion": {
        "name": "Battery Leakage Corrosion",
        "description": "Alkaline hydroxide or sulfuric acid corrosion products from battery leakage",
        "composition": ["KOH", "K₂CO₃", "PbSO₄"],
        "valid_materials": ["Copper", "Steel", "Brass"],
        "prohibited_materials": ["Aluminum", "Electronics"]
    },
    "chrome_pitting": {
        "name": "Chromium Oxide Pitting",
        "description": "Localized chromium oxide layer breakdown causing surface degradation on plated surfaces",
        "composition": ["Cr₂O₃", "CrO₃", "Cr(OH)₃"],
        "valid_materials": ["Chrome-Plated Steel", "Stainless Steel"],
        "prohibited_materials": ["Aluminum", "Copper"]
    },
    "graphite_marks": {
        "name": "Graphite Deposit Traces",
        "description": "Carbon-based marks from pencils, graphite lubricants, and electrical contacts",
        "composition": ["C (Graphite)", "Clay Binder"],
        "valid_materials": ["Paper", "Metal", "Concrete", "Ceramic"],
        "prohibited_materials": ["Porous Materials", "Fabrics"]
    },
    "ceramic_glaze": {
        "name": "Ceramic Glaze Deposits",
        "description": "Vitrified silicate coating residues from fired ceramic manufacturing processes",
        "composition": ["SiO₂", "Al₂O₃", "Fluxes"],
        "valid_materials": ["Ceramic", "Porcelain", "Stone"],
        "prohibited_materials": ["Metal", "Glass"]
    },
    "powder_coating": {
        "name": "Powder Coating Buildup",
        "description": "Electrostatically-applied thermosetting polymer coating used in industrial finishing",
        "composition": ["Polyester Resin", "Epoxy", "Pigments", "Additives"],
        "valid_materials": ["Steel", "Aluminum", "Galvanized Metal"],
        "prohibited_materials": ["Plastics", "Wood", "Thin Sheet Metal"]
    },
    "anodizing_defects": {
        "name": "Anodizing Layer Irregularities",
        "description": "Aluminum oxide surface layer defects including pitting, staining, and uneven thickness",
        "composition": ["Al₂O₃", "Dye Molecules", "Sealed Pores"],
        "valid_materials": ["Aluminum", "Aluminum Alloys"],
        "prohibited_materials": ["Steel", "Copper", "Magnesium"]
    },
    "galvanize_corrosion": {
        "name": "White Rust on Galvanized Steel",
        "description": "Zinc carbonate and hydroxide formation on galvanized coatings exposed to moisture",
        "composition": ["ZnO", "Zn(OH)₂", "ZnCO₃"],
        "valid_materials": ["Galvanized Steel", "Zinc-Coated Metal"],
        "prohibited_materials": ["Aluminum", "Stainless Steel", "Copper"]
    },
    "plastic_residue": {
        "name": "Degraded Polymer Deposits",
        "description": "Melted, degraded, or oxidized plastic residues from heat exposure or UV degradation",
        "composition": ["Polyethylene", "Polypropylene", "PVC", "Additives"],
        "valid_materials": ["Metal", "Concrete", "Glass"],
        "prohibited_materials": ["Plastics", "Rubber", "Wood"]
    },
    "biological_stains": {
        "name": "Organic Biofilm Deposits",
        "description": "Biological matter including algae, bacteria, and organic waste creating surface films",
        "composition": ["Proteins", "Polysaccharides", "Lipids", "Chlorophyll"],
        "valid_materials": ["Concrete", "Stone", "Metal", "Glass"],
        "prohibited_materials": ["Food Surfaces", "Medical Equipment", "Wood"]
    }
}

def add_patterns_to_yaml(yaml_path: Path):
    """Add new patterns to existing Contaminants.yaml"""
    
    # Load existing data
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    patterns = data.get('contamination_patterns', {})
    
    # Add new patterns
    added_count = 0
    for pattern_id, pattern_data in NEW_PATTERNS.items():
        if pattern_id not in patterns:
            patterns[pattern_id] = pattern_data
            added_count += 1
            print(f"✅ Added: {pattern_id}")
        else:
            print(f"⚠️  Skipped (already exists): {pattern_id}")
    
    # Update data
    data['contamination_patterns'] = patterns
    data['last_updated'] = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Save back to file
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    total_patterns = len(patterns)
    print(f"\n📊 Summary:")
    print(f"   Added: {added_count} new patterns")
    print(f"   Total: {total_patterns} contamination patterns")
    
    return added_count

if __name__ == "__main__":
    yaml_path = Path("data/contaminants/Contaminants.yaml")
    
    if not yaml_path.exists():
        print(f"❌ Error: {yaml_path} not found")
        exit(1)
    
    print("🔧 Adding new contamination patterns...")
    added = add_patterns_to_yaml(yaml_path)
    
    if added > 0:
        print(f"\n✅ SUCCESS: {added} patterns added to {yaml_path}")
        print(f"\nNext step: Research laser properties for new patterns:")
        print(f"  python3 scripts/research_laser_properties.py --all-patterns --type complete_profile --save")
    else:
        print("\n⚠️  No new patterns added (all already exist)")
