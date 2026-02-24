#!/usr/bin/env python3
"""
Phase 2: Auto-Populate Relationships
Programmatically populates ExtractedLinkages.yaml based on data analysis.

CRITICAL FIX (Dec 20, 2025):
- Changed target file: DomainAssociations.yaml → ExtractedLinkages.yaml
- Changed format: Dictionary → Array (material_contaminant_associations: [...])
- Added required fields: frequency, severity, verified, typical_context
"""

import sys
import yaml
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_yaml(file_path):
    """Load YAML file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f) or {}

def save_yaml(data, file_path):
    """Save YAML file preserving metadata"""
    # Add/update metadata
    if 'metadata' not in data:
        data['metadata'] = {}
    
    data['metadata'].update({
        'version': '2.0.0',
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'description': 'Auto-populated domain associations using pattern matching'
    })
    
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def get_slug(name):
    """Convert name to slug format"""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def infer_frequency(contaminant_name, material_props):
    """Infer contamination frequency based on patterns"""
    name_lower = contaminant_name.lower()
    
    # Very common contaminants
    if any(x in name_lower for x in ['dust', 'dirt', 'oil', 'grease', 'oxidation', 'rust', 'paint']):
        return 'very_common'
    # Common contaminants
    elif any(x in name_lower for x in ['coating', 'residue', 'scale', 'debris']):
        return 'common'
    # Occasional contaminants
    elif any(x in name_lower for x in ['adhesive', 'sealant', 'biological']):
        return 'occasional'
    # Rare contaminants
    else:
        return 'rare'

def infer_severity(contaminant_name, material_props):
    """Infer contamination severity based on patterns"""
    name_lower = contaminant_name.lower()
    
    # Critical severity
    if any(x in name_lower for x in ['corrosion', 'rust', 'oxidation']) and material_props.get('is_ferrous'):
        return 'critical'
    # High severity
    elif any(x in name_lower for x in ['paint', 'coating', 'scale']):
        return 'high'
    # Moderate severity
    elif any(x in name_lower for x in ['oil', 'grease', 'adhesive']):
        return 'moderate'
    # Low severity
    else:
        return 'low'

def get_typical_context(contaminant_name):
    """Infer typical context where contamination occurs"""
    name_lower = contaminant_name.lower()
    
    if any(x in name_lower for x in ['marine', 'salt', 'seawater']):
        return 'Marine environments, coastal installations'
    elif any(x in name_lower for x in ['industrial', 'manufacturing', 'factory']):
        return 'Industrial facilities, manufacturing plants'
    elif any(x in name_lower for x in ['outdoor', 'environmental', 'weather']):
        return 'Outdoor installations, exposed surfaces'
    elif any(x in name_lower for x in ['automotive', 'vehicle']):
        return 'Automotive applications, transportation'
    elif any(x in name_lower for x in ['food', 'kitchen', 'commercial']):
        return 'Food processing, commercial kitchens'
    else:
        return 'General industrial and commercial applications'

def main():
    print("=" * 80)
    print("PHASE 2: AUTO-POPULATE RELATIONSHIPS (FIXED FORMAT)")
    print("=" * 80)
    print()
    
    # Load all data files
    print("📁 Loading data files...")
    materials_data = load_yaml(project_root / "data/materials/Materials.yaml")
    contaminants_data = load_yaml(project_root / "data/contaminants/Contaminants.yaml")
    compounds_data = load_yaml(project_root / "data/compounds/Compounds.yaml")
    settings_data = load_yaml(project_root / "data/settings/Settings.yaml")
    
    materials = materials_data.get('materials', {})
    contaminants = contaminants_data.get('contamination_patterns', {})
    compounds = compounds_data.get('compounds', {})
    settings = settings_data.get('settings', {})
    
    print(f"   Materials: {len(materials)}")
    print(f"   Contaminants: {len(contaminants)}")
    print(f"   Compounds: {len(compounds)}")
    print(f"   Settings: {len(settings)}")
    print()
    
    # Initialize associations structure (ARRAY FORMAT)
    associations = {
        'metadata': {},
        'material_contaminant_associations': [],
        'contaminant_compound_associations': []
    }
    
    print("🔗 Strategy: Material ↔ Contaminant (Pattern Matching)")
    print("-" * 80)
    
    material_contaminant_count = 0
    
    # Build material category index
    material_categories = {}
    for material_name, material_data in materials.items():
        if isinstance(material_data, dict):
            cat1 = material_data.get('category1', '').lower()
            cat2 = material_data.get('category2', '').lower()
            material_categories[material_name] = {
                'category1': cat1,
                'category2': cat2,
                'is_metal': cat1 == 'metal',
                'is_ferrous': cat2 == 'ferrous',
                'is_non_ferrous': cat2 == 'non-ferrous',
                'is_plastic': cat1 == 'plastic',
                'is_wood': cat1 == 'wood',
                'is_stone': cat1 == 'stone',
                'is_ceramic': cat1 == 'ceramic'
            }
    
    # Match contaminants to materials (ARRAY FORMAT with bidirectional pairs)
    for contaminant_name, contaminant_data in contaminants.items():
        if not isinstance(contaminant_data, dict):
            continue
        
        # Get contaminant categories
        cont_cat1 = contaminant_data.get('category1', '').lower()
        cont_cat2 = contaminant_data.get('category2', '').lower()
        
        # Match based on contamination type
        for material_name, mat_props in material_categories.items():
            should_link = False
            
            # Rust/oxidation → ferrous metals
            if cont_cat1 in ['oxidation', 'corrosion'] and cont_cat2 == 'ferrous':
                if mat_props['is_ferrous']:
                    should_link = True
            
            # Oxidation → all metals
            elif cont_cat1 in ['oxidation', 'corrosion']:
                if mat_props['is_metal']:
                    should_link = True
            
            # Oil/grease → metals and plastics
            elif 'oil' in contaminant_name.lower() or 'grease' in contaminant_name.lower():
                if mat_props['is_metal'] or mat_props['is_plastic']:
                    should_link = True
            
            # Paint → all materials
            elif 'paint' in contaminant_name.lower() or 'coating' in contaminant_name.lower():
                should_link = True
            
            # Dirt/dust → all materials
            elif 'dirt' in contaminant_name.lower() or 'dust' in contaminant_name.lower():
                should_link = True
            
            # Scale → metals
            elif 'scale' in contaminant_name.lower():
                if mat_props['is_metal']:
                    should_link = True
            
            # Biological → wood and stone
            elif cont_cat1 in ['biological', 'organic']:
                if mat_props['is_wood'] or mat_props['is_stone']:
                    should_link = True
            
            if should_link:
                # Create association record (ARRAY FORMAT)
                association = {
                    'material_id': material_name,
                    'contaminant_id': contaminant_name,
                    'frequency': infer_frequency(contaminant_name, mat_props),
                    'severity': infer_severity(contaminant_name, mat_props),
                    'typical_context': get_typical_context(contaminant_name),
                    'verified': False  # Auto-populated, not manually verified
                }
                
                associations['material_contaminant_associations'].append(association)
                material_contaminant_count += 1
    
    print(f"   Added {material_contaminant_count} bidirectional material↔contaminant pairs")
    print()
    
    # Save updated associations
    print("💾 Saving to ExtractedLinkages.yaml...")
    
    associations_file = project_root / "data/associations/ExtractedLinkages.yaml"
    backup_file = project_root / "data/associations/ExtractedLinkages.yaml.backup"
    
    # Create backup
    if associations_file.exists():
        import shutil
        shutil.copy2(associations_file, backup_file)
        print(f"   ✅ Backup created: {backup_file}")
    
    save_yaml(associations, associations_file)
    print(f"   ✅ Saved: {associations_file}")
    print()
    
    # Summary
    print("=" * 80)
    print("✅ PHASE 2 COMPLETE")
    print("=" * 80)
    print(f"\n📊 RELATIONSHIPS CREATED:")
    print(f"   • Material ↔ Contaminant: {material_contaminant_count} associations")
    print(f"\n📁 Target File: ExtractedLinkages.yaml (correct format for enrichers)")
    print(f"📁 Format: Array with required fields (frequency, severity, verified)")
    print(f"\n🔄 Next: Phase 3 will enable enrichers to use these relationships")
    print()

if __name__ == '__main__':
    main()
