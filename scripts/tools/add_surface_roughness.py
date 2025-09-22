#!/usr/bin/env python3
"""
Surface Roughness Automation Script

Adds research-based surface roughness values to frontmatter files based on material categories.
"""

import os
import yaml
from typing import Tuple

# Research-based surface roughness data by material category and specific materials
SURFACE_ROUGHNESS_DATA = {
    # Metals (70-80% improvement, tight tolerances)
    'aluminum': (6.3, 1.5),
    'beryllium': (2.5, 0.5),
    'brass': (4.0, 0.8),
    'bronze': (4.5, 0.9),
    'cobalt': (3.2, 0.6),
    'copper': (3.2, 0.6),
    'gallium': (2.0, 0.4),
    'gold': (1.6, 0.3),
    'hafnium': (3.5, 0.7),
    'hastelloy': (3.8, 0.8),
    'inconel': (4.0, 0.8),
    'indium': (2.5, 0.5),
    'iridium': (2.0, 0.4),
    'iron': (5.0, 1.0),
    'lead': (6.3, 1.3),
    'magnesium': (4.0, 0.8),
    'molybdenum': (2.5, 0.5),
    'nickel': (3.2, 0.6),
    'niobium': (3.0, 0.6),
    'palladium': (2.0, 0.4),
    'platinum': (1.8, 0.4),
    'rhenium': (2.2, 0.4),
    'rhodium': (1.8, 0.4),
    'ruthenium': (2.0, 0.4),
    'silver': (1.6, 0.3),
    'stainless steel': (3.2, 0.6),
    'steel': (4.0, 0.8),
    'tantalum': (2.8, 0.6),
    'tin': (4.5, 0.9),
    'titanium': (2.5, 0.5),
    'tungsten': (2.0, 0.4),
    'vanadium': (3.0, 0.6),
    'zinc': (4.2, 0.8),
    'zirconium': (3.0, 0.6),
    
    # Woods (60-70% improvement, softer processing)
    'ash': (20, 7),
    'bamboo': (18, 5),
    'beech': (22, 7),
    'birch': (20, 6),
    'cedar': (25, 8),
    'cherry': (18, 6),
    'fir': (30, 10),
    'hickory': (24, 8),
    'mahogany': (20, 6),
    'maple': (25, 8),
    'oak': (28, 9),
    'pine': (32, 10),
    'poplar': (26, 8),
    'redwood': (35, 12),
    'rosewood': (18, 6),
    'teak': (22, 7),
    'walnut': (24, 8),
    'willow': (28, 9),
    'mdf': (40, 12),
    'plywood': (35, 10),
    
    # Stones/Minerals (70-80% improvement, varies by hardness)
    'alabaster': (15, 4),
    'basalt': (40, 10),
    'bluestone': (35, 8),
    'breccia': (45, 11),
    'brick': (50, 12),
    'calcite': (12, 3),
    'granite': (20, 5),
    'limestone': (25, 6),
    'marble': (12.5, 3),
    'onyx': (10, 2.5),
    'porphyry': (35, 8),
    'quartzite': (30, 7),
    'sandstone': (40, 10),
    'schist': (50, 12),
    'serpentine': (25, 6),
    'shale': (80, 20),
    'slate': (30, 7),
    'soapstone': (20, 5),
    'stoneware': (15, 4),
    'travertine': (18, 4.5),
    'terracotta': (25, 6),
    
    # Ceramics/Technical Materials (75-85% improvement, high precision)
    'alumina': (3.2, 0.6),
    'silicon carbide': (1.6, 0.3),
    'silicon nitride': (2.0, 0.4),
    'zirconia': (2.5, 0.5),
    'porcelain': (3.2, 0.6),
    
    # Semiconductors (70-80% improvement, ultra-precise)
    'silicon': (1.2, 0.3),
    'gallium arsenide': (0.8, 0.2),
    'silicon germanium': (1.0, 0.25),
    
    # Glass/Composites (variable improvement)
    'borosilicate glass': (0.8, 0.2),
    'float glass': (1.0, 0.25),
    'fused silica': (0.5, 0.1),
    'lead crystal': (1.2, 0.3),
    'pyrex': (0.8, 0.2),
    'quartz glass': (0.4, 0.1),
    'soda-lime glass': (1.0, 0.25),
    'tempered glass': (1.2, 0.3),
    
    # Construction Materials (moderate improvement)
    'cement': (80, 20),
    'concrete': (100, 25),
    'mortar': (60, 15),
    'plaster': (40, 10),
    'stucco': (50, 12),
    
    # Composites/Polymers (50-70% improvement, careful processing)
    'carbon fiber reinforced polymer': (6.3, 2.5),
    'ceramic matrix composites cmcs': (4.0, 1.2),
    'epoxy resin composites': (8.0, 3.0),
    'fiber reinforced polyurethane frpu': (10, 4),
    'fiberglass': (12.5, 5),
    'glass fiber reinforced polymers gfrp': (8.0, 3.0),
    'kevlar-reinforced polymer': (6.3, 2.5),
    'metal matrix composites mmcs': (5.0, 1.5),
    'phenolic resin composites': (10, 4),
    'polyester resin composites': (12.5, 5),
    'rubber': (25, 10),
    'thermoplastic elastomer': (20, 8),
    'urethane composites': (15, 6),
}

def find_outcomes_section(content: str) -> Tuple[int, int]:
    """Find the start and end of the outcomes section"""
    lines = content.split('\n')
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        if line.strip() == 'outcomes:':
            start_idx = i
        elif start_idx != -1 and line.strip() and not line.startswith(' ') and not line.startswith('-'):
            end_idx = i
            break
    
    if start_idx == -1:
        return -1, -1
    if end_idx == -1:
        end_idx = len(lines)
    
    return start_idx, end_idx

def has_surface_roughness(content: str) -> bool:
    """Check if surface roughness entries already exist"""
    return 'Surface roughness before treatment' in content

def add_surface_roughness_to_file(filepath: str, material_name: str) -> bool:
    """Add surface roughness entries to a frontmatter file"""
    
    if material_name.lower() not in SURFACE_ROUGHNESS_DATA:
        print(f"  ⚠️  No surface roughness data for {material_name}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_surface_roughness(content):
            print(f"  ✅ {material_name} already has surface roughness values")
            return True
        
        before, after = SURFACE_ROUGHNESS_DATA[material_name.lower()]
        
        # Find outcomes section
        start_idx, end_idx = find_outcomes_section(content)
        if start_idx == -1:
            print(f"  ❌ Could not find outcomes section in {material_name}")
            return False
        
        lines = content.split('\n')
        
        # Find the last outcome entry
        last_outcome_idx = start_idx
        for i in range(start_idx + 1, end_idx):
            if lines[i].startswith('- result:'):
                last_outcome_idx = i + 1
                # Skip the metric line
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('metric:'):
                    last_outcome_idx = i + 2
        
        # Insert surface roughness entries
        new_entries = [
            "- result: Surface roughness before treatment",
            f"  metric: \"Ra {before} μm\"",
            "- result: Surface roughness after treatment",
            f"  metric: \"Ra {after} μm\""
        ]
        
        # Insert at the end of outcomes section
        for j, entry in enumerate(new_entries):
            lines.insert(last_outcome_idx + j, entry)
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"  ✅ Added surface roughness to {material_name}: Ra {before} μm → Ra {after} μm")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {material_name}: {e}")
        return False

def main():
    """Main function to process all materials"""
    
    # Load materials
    with open('data/materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    materials = sorted(data.get('material_index', {}).keys())
    processed = 0
    skipped = 0
    errors = 0
    
    print(f"🔍 Processing {len(materials)} materials for surface roughness...")
    print("=" * 60)
    
    for material in materials:
        filename = f"content/components/frontmatter/{material.lower().replace(' ', ' ')}-laser-cleaning.md"
        
        if not os.path.exists(filename):
            print(f"  ⚠️  Frontmatter file not found for {material}")
            skipped += 1
            continue
        
        success = add_surface_roughness_to_file(filename, material)
        if success:
            processed += 1
        else:
            errors += 1
    
    print("=" * 60)
    print("📊 Summary:")
    print(f"  ✅ Processed: {processed}")
    print(f"  ⚠️  Skipped: {skipped}")
    print(f"  ❌ Errors: {errors}")
    print(f"  📋 Total: {len(materials)}")

if __name__ == "__main__":
    main()
