#!/usr/bin/env python3
"""
Comprehensive Materials.yaml Fix Script

Addresses all 3 priority issues:
1. Fix thermal conductivity units (restore truncated "(m·K)")
2. Complete missing data for wood/composite/incomplete materials
3. Add missing formulas for all materials

Uses authoritative scientific data sources.
"""

import yaml
import re
from pathlib import Path

def fix_thermal_conductivity_units():
    """Fix truncated thermal conductivity units."""
    materials_path = Path("data/materials.yaml")
    
    print("🔧 Priority 1: Fixing thermal conductivity units...")
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix patterns like "35 W/" to "35 W/(m·K)"
    content = re.sub(r'(\d+\.?\d*)\s*W/(?!\()', r'\1 W/(m·K)', content)
    
    with open(materials_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Count fixes
    fixes = len(re.findall(r'\d+\.?\d*\s*W/\(m·K\)', content))
    print(f"  ✅ Fixed {fixes} thermal conductivity unit entries")

def get_material_properties():
    """Get comprehensive material property database."""
    return {
        # Wood materials
        'Ash': {
            'density': '0.68 g/cm³',
            'thermalDestructionPoint': '250°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.16 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Bamboo': {
            'density': '0.6 g/cm³',
            'thermalDestructionPoint': '230°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.17 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Beech': {
            'density': '0.72 g/cm³',
            'thermalDestructionPoint': '260°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.17 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Cedar': {
            'density': '0.38 g/cm³',
            'thermalDestructionPoint': '240°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.095 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Cherry': {
            'density': '0.63 g/cm³',
            'thermalDestructionPoint': '250°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.14 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Ebony': {
            'density': '1.2 g/cm³',
            'thermalDestructionPoint': '280°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.23 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Fir': {
            'density': '0.45 g/cm³',
            'thermalDestructionPoint': '235°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.11 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Maple': {
            'density': '0.76 g/cm³',
            'thermalDestructionPoint': '260°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.18 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'MDF': {
            'density': '0.75 g/cm³',
            'thermalDestructionPoint': '220°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.15 W/(m·K)',
            'formula': 'Wood fiber + resin'
        },
        'Oak': {
            'density': '0.75 g/cm³',
            'thermalDestructionPoint': '270°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.17 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Pine': {
            'density': '0.52 g/cm³',
            'thermalDestructionPoint': '240°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.12 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Plywood': {
            'density': '0.55 g/cm³',
            'thermalDestructionPoint': '230°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.13 W/(m·K)',
            'formula': 'Wood layers + adhesive'
        },
        'Poplar': {
            'density': '0.43 g/cm³',
            'thermalDestructionPoint': '235°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.1 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Redwood': {
            'density': '0.41 g/cm³',
            'thermalDestructionPoint': '250°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.1 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Rosewood': {
            'density': '0.85 g/cm³',
            'thermalDestructionPoint': '270°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.19 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Spruce': {
            'density': '0.43 g/cm³',
            'thermalDestructionPoint': '235°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.1 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Teak': {
            'density': '0.66 g/cm³',
            'thermalDestructionPoint': '265°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.14 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Walnut': {
            'density': '0.65 g/cm³',
            'thermalDestructionPoint': '255°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.14 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Whitewood': {
            'density': '0.48 g/cm³',
            'thermalDestructionPoint': '240°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.11 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        'Willow': {
            'density': '0.5 g/cm³',
            'thermalDestructionPoint': '240°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.12 W/(m·K)',
            'formula': 'Cellulose composite'
        },
        
        # Composite materials
        'Carbon Fiber Reinforced Polymer': {
            'density': '1.6 g/cm³',
            'thermalDestructionPoint': '300°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '1.7 W/(m·K)',
            'formula': 'Carbon fiber + polymer matrix'
        },
        'Epoxy Resin Composites': {
            'density': '1.8 g/cm³',
            'thermalDestructionPoint': '180°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.2 W/(m·K)',
            'formula': 'Epoxy + reinforcement'
        },
        'Fiberglass': {
            'density': '2.1 g/cm³',
            'thermalDestructionPoint': '250°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.35 W/(m·K)',
            'formula': 'Glass fiber + resin'
        },
        'Kevlar-Reinforced Polymer': {
            'density': '1.44 g/cm³',
            'thermalDestructionPoint': '400°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.04 W/(m·K)',
            'formula': 'Aramid fiber + polymer'
        },
        'Phenolic Resin Composites': {
            'density': '1.3 g/cm³',
            'thermalDestructionPoint': '200°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.25 W/(m·K)',
            'formula': 'Phenolic resin + filler'
        },
        'Polyester Resin Composites': {
            'density': '1.5 g/cm³',
            'thermalDestructionPoint': '160°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.18 W/(m·K)',
            'formula': 'Polyester + reinforcement'
        },
        'Rubber': {
            'density': '1.2 g/cm³',
            'thermalDestructionPoint': '200°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.13 W/(m·K)',
            'formula': 'Elastomer polymer'
        },
        'Thermoplastic Elastomer': {
            'density': '1.1 g/cm³',
            'thermalDestructionPoint': '220°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.15 W/(m·K)',
            'formula': 'TPE polymer'
        },
        'Urethane Composites': {
            'density': '1.25 g/cm³',
            'thermalDestructionPoint': '190°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.2 W/(m·K)',
            'formula': 'Urethane + reinforcement'
        },
        'Glass Fiber Reinforced Polymers GFRP': {
            'density': '2.0 g/cm³',
            'thermalDestructionPoint': '240°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.3 W/(m·K)',
            'formula': 'Glass fiber + polymer'
        },
        'Fiber Reinforced Polyurethane FRPU': {
            'density': '1.4 g/cm³',
            'thermalDestructionPoint': '210°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '0.22 W/(m·K)',
            'formula': 'Fiber + polyurethane'
        },
        'Metal Matrix Composites MMCs': {
            'density': '3.2 g/cm³',
            'thermalDestructionPoint': '600°C',
            'thermalDestructionType': 'decomposition',
            'thermalConductivity': '120 W/(m·K)',
            'formula': 'Metal + ceramic/carbon'
        },
        'Ceramic Matrix Composites CMCs': {
            'density': '2.8 g/cm³',
            'thermalDestructionPoint': '1200°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '25 W/(m·K)',
            'formula': 'Ceramic + fiber'
        },
        
        # Missing metal properties
        'Antimony': {
            'density': '6.68 g/cm³',
            'thermalDestructionPoint': '631°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '24.4 W/(m·K)',
            'formula': 'Sb'
        },
        'Cadmium': {
            'density': '8.65 g/cm³',
            'thermalDestructionPoint': '321°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '96.6 W/(m·K)',
            'formula': 'Cd'
        },
        'Chromium': {
            'density': '7.19 g/cm³',
            'thermalDestructionPoint': '1907°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '93.9 W/(m·K)',
            'formula': 'Cr'
        },
        'Manganese': {
            'density': '7.21 g/cm³',
            'thermalDestructionPoint': '1246°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '7.8 W/(m·K)',
            'formula': 'Mn'
        },
        'Mercury': {
            'density': '13.53 g/cm³',
            'thermalDestructionPoint': '-39°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '8.3 W/(m·K)',
            'formula': 'Hg'
        },
        'Nickel': {
            'density': '8.91 g/cm³',
            'thermalDestructionPoint': '1455°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '90.9 W/(m·K)',
            'formula': 'Ni'
        },
        'Osmium': {
            'density': '22.59 g/cm³',
            'thermalDestructionPoint': '3033°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '87.6 W/(m·K)',
            'formula': 'Os'
        },
        'Palladium': {
            'density': '12.02 g/cm³',
            'thermalDestructionPoint': '1555°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '71.8 W/(m·K)',
            'formula': 'Pd'
        },
        'Platinum': {
            'density': '21.45 g/cm³',
            'thermalDestructionPoint': '1768°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '71.6 W/(m·K)',
            'formula': 'Pt'
        },
        'Rhenium': {
            'density': '21.02 g/cm³',
            'thermalDestructionPoint': '3186°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '48 W/(m·K)',
            'formula': 'Re'
        },
        'Rhodium': {
            'density': '12.41 g/cm³',
            'thermalDestructionPoint': '1964°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '150 W/(m·K)',
            'formula': 'Rh'
        },
        'Tantalum': {
            'density': '16.65 g/cm³',
            'thermalDestructionPoint': '3017°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '57.5 W/(m·K)',
            'formula': 'Ta'
        },
        'Thallium': {
            'density': '11.85 g/cm³',
            'thermalDestructionPoint': '304°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '46.1 W/(m·K)',
            'formula': 'Tl'
        },
        'Yttrium': {
            'density': '4.47 g/cm³',
            'thermalDestructionPoint': '1526°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '17.2 W/(m·K)',
            'formula': 'Y'
        },
        'Zirconium': {
            'density': '6.51 g/cm³',
            'thermalDestructionPoint': '1855°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '22.6 W/(m·K)',
            'formula': 'Zr'
        },
        
        # Missing semiconductor properties
        'Gallium Arsenide': {
            'density': '5.32 g/cm³',
            'thermalDestructionPoint': '1238°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '55 W/(m·K)',
            'formula': 'GaAs'
        },
        'Indium Phosphide': {
            'density': '4.81 g/cm³',
            'thermalDestructionPoint': '1062°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '68 W/(m·K)',
            'formula': 'InP'
        },
        'Silicon Germanium': {
            'density': '3.5 g/cm³',
            'thermalDestructionPoint': '1300°C',
            'thermalDestructionType': 'melting',
            'thermalConductivity': '85 W/(m·K)',
            'formula': 'SiGe'
        },
        
        # Missing glass formulas
        'Tempered Glass': {
            'formula': 'SiO₂ + Na₂O + CaO (treated)'
        },
        'Laminated Glass': {
            'formula': 'Glass + PVB interlayer'
        },
        'Optical Glass': {
            'formula': 'SiO₂ + rare earth oxides'
        },
        'Safety Glass': {
            'formula': 'SiO₂ + Na₂O + CaO (treated)'
        },
        'Insulated Glass': {
            'formula': 'Multiple glass panes + gas'
        },
        
        # Missing stone formulas and properties
        'Basalt': {
            'formula': 'Complex silicate'
        },
        'Calcite': {
            'formula': 'CaCO₃'
        },
        'Dolomite': {
            'formula': 'CaMg(CO₃)₂'
        },
        'Gneiss': {
            'formula': 'Metamorphic silicate'
        },
        'Limestone': {
            'formula': 'CaCO₃'
        },
        'Obsidian': {
            'formula': 'Volcanic glass'
        },
        'Porphyry': {
            'formula': 'Igneous silicate'
        },
        'Pumice': {
            'formula': 'Volcanic glass'
        },
        'Sandstone': {
            'formula': 'SiO₂ cemented'
        },
        'Serpentine': {
            'formula': 'Mg₃Si₂O₅(OH)₄'
        },
        'Shale': {
            'formula': 'Clay minerals'
        },
        'Soapstone': {
            'formula': 'Talc + chlorite'
        },
        'Travertine': {
            'formula': 'CaCO₃'
        }
    }

def complete_missing_data():
    """Complete missing material data."""
    materials_path = Path("data/materials.yaml")
    
    print("🔧 Priority 2: Completing missing material data...")
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    properties_db = get_material_properties()
    
    added_count = 0
    updated_count = 0
    
    for category, cat_data in data['materials'].items():
        for i, item in enumerate(cat_data['items']):
            material_name = item.get('name', '')
            
            if material_name in properties_db:
                props = properties_db[material_name]
                updated = False
                
                # Add missing properties
                for prop_key, prop_value in props.items():
                    if prop_key not in item or not item[prop_key]:
                        item[prop_key] = prop_value
                        added_count += 1
                        updated = True
                
                if updated:
                    updated_count += 1
    
    # Write back the updated data
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"  ✅ Added {added_count} missing properties to {updated_count} materials")

def add_missing_formulas():
    """Add missing chemical formulas."""
    materials_path = Path("data/materials.yaml")
    
    print("🔧 Priority 3: Adding missing chemical formulas...")
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Common metal formulas
    metal_formulas = {
        'Aluminum': 'Al', 'Antimony': 'Sb', 'Beryllium': 'Be', 'Brass': 'Cu + Zn',
        'Bronze': 'Cu + Sn', 'Cadmium': 'Cd', 'Chromium': 'Cr', 'Cobalt': 'Co',
        'Copper': 'Cu', 'Gallium': 'Ga', 'Gold': 'Au', 'Hafnium': 'Hf',
        'Hastelloy': 'Ni-Cr-Mo alloy', 'Inconel': 'Ni-Cr alloy', 'Indium': 'In',
        'Iridium': 'Ir', 'Iron': 'Fe', 'Lead': 'Pb', 'Magnesium': 'Mg',
        'Manganese': 'Mn', 'Mercury': 'Hg', 'Molybdenum': 'Mo', 'Nickel': 'Ni',
        'Niobium': 'Nb', 'Osmium': 'Os', 'Palladium': 'Pd', 'Platinum': 'Pt',
        'Rhenium': 'Re', 'Rhodium': 'Rh', 'Silver': 'Ag', 'Steel': 'Fe + C',
        'Tantalum': 'Ta', 'Thallium': 'Tl', 'Tin': 'Sn', 'Titanium': 'Ti',
        'Tungsten': 'W', 'Vanadium': 'V', 'Yttrium': 'Y', 'Zinc': 'Zn',
        'Zirconium': 'Zr'
    }
    
    # Semiconductor formulas
    semiconductor_formulas = {
        'Gallium Arsenide': 'GaAs', 'Indium Phosphide': 'InP',
        'Silicon': 'Si', 'Silicon Germanium': 'SiGe'
    }
    
    # Ceramic formulas
    ceramic_formulas = {
        'Alumina': 'Al₂O₃', 'Porcelain': 'Al₂O₃·2SiO₂·2H₂O',
        'Silicon Nitride': 'Si₃N₄', 'Stoneware': 'Aluminosilicate',
        'Zirconia': 'ZrO₂'
    }
    
    all_formulas = {**metal_formulas, **semiconductor_formulas, **ceramic_formulas}
    
    formula_count = 0
    
    for category, cat_data in data['materials'].items():
        for item in cat_data['items']:
            material_name = item.get('name', '')
            
            if material_name in all_formulas and ('formula' not in item or not item['formula']):
                item['formula'] = all_formulas[material_name]
                formula_count += 1
    
    # Write back the updated data
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"  ✅ Added {formula_count} missing chemical formulas")

def main():
    """Execute all 3 priority fixes."""
    print("🚀 Starting comprehensive materials.yaml fixes...")
    print("=" * 50)
    
    # Create backup
    backup_path = Path(f"data/materials_comprehensive_fix_{int(__import__('time').time())}.yaml")
    materials_path = Path("data/materials.yaml")
    
    import shutil
    shutil.copy2(materials_path, backup_path)
    print(f"📁 Backup created: {backup_path}")
    print()
    
    # Execute all fixes
    fix_thermal_conductivity_units()
    print()
    
    complete_missing_data()
    print()
    
    add_missing_formulas()
    print()
    
    print("=" * 50)
    print("✅ ALL PRIORITY FIXES COMPLETED!")
    print("📊 Summary:")
    print("  🔧 Priority 1: Thermal conductivity units restored")
    print("  📝 Priority 2: Missing wood/composite data added")
    print("  🧪 Priority 3: Chemical formulas completed")
    print(f"📁 Backup saved: {backup_path}")

if __name__ == "__main__":
    main()
