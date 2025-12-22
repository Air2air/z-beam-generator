#!/usr/bin/env python3
"""
Populate settings relationship data

Intelligently populates:
- optimized_for_materials: Match settings to materials they're designed for
- removes_contaminants: Match settings to contaminants they can remove
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil
import re

def load_data():
    """Load all data files."""
    with open('data/materials/Materials.yaml', 'r', encoding='utf-8') as f:
        materials = yaml.safe_load(f)
    
    with open('data/contaminants/Contaminants.yaml', 'r', encoding='utf-8') as f:
        contaminants = yaml.safe_load(f)
    
    with open('data/settings/Settings.yaml', 'r', encoding='utf-8') as f:
        settings = yaml.safe_load(f)
    
    return materials, contaminants, settings

def categorize_materials():
    """Categorize materials by type."""
    categories = {
        'metals': ['steel', 'aluminum', 'copper', 'brass', 'bronze', 'titanium',
                   'iron', 'zinc', 'nickel', 'stainless-steel-316', 'gold', 'silver'],
        'stones': ['granite', 'marble', 'limestone', 'sandstone', 'slate', 'basalt',
                   'bluestone', 'travertine'],
        'woods': ['oak', 'maple', 'pine', 'walnut', 'cherry', 'mahogany', 'teak',
                  'ash', 'beech', 'birch'],
        'ceramics': ['ceramic', 'porcelain', 'terracotta', 'stoneware'],
        'plastics': ['plastic', 'acrylic', 'polycarbonate', 'pvc', 'abs'],
        'composites': ['composite', 'fiberglass', 'carbon-fiber']
    }
    return categories

def match_setting_to_materials(setting_id, setting_data, material_categories):
    """Match a laser setting to appropriate materials."""
    matches = []
    
    # Extract key terms from setting ID
    setting_lower = setting_id.replace('-laser-cleaning-settings', '').lower()
    
    # Direct material match
    for category, materials in material_categories.items():
        for material in materials:
            if material in setting_lower:
                matches.append({
                    'id': f"{material}-laser-cleaning",
                    'effectiveness': 'high'
                })
    
    # Category-based matching
    if not matches:  # If no direct match, use category heuristics
        # High power settings → metals
        laser_params = setting_data.get('laser_parameters', {})
        fluence = laser_params.get('fluence_range', {})
        max_fluence = fluence.get('max_j_cm2', 0)
        
        if max_fluence > 5.0:
            # High power → metals
            for material in material_categories['metals'][:5]:
                matches.append({
                    'id': f"{material}-laser-cleaning",
                    'effectiveness': 'high'
                })
        elif max_fluence > 2.0:
            # Medium power → stones, ceramics
            for material in (material_categories['stones'][:3] + 
                           material_categories['ceramics'][:2]):
                matches.append({
                    'id': f"{material}-laser-cleaning",
                    'effectiveness': 'medium'
                })
        else:
            # Low power → delicate materials
            for material in (material_categories['woods'][:3] + 
                           material_categories['plastics'][:2]):
                matches.append({
                    'id': f"{material}-laser-cleaning",
                    'effectiveness': 'medium'
                })
    
    # Remove duplicates
    seen = set()
    unique_matches = []
    for match in matches:
        if match['id'] not in seen:
            seen.add(match['id'])
            unique_matches.append(match)
    
    return unique_matches

def match_setting_to_contaminants(setting_id, setting_data, contaminant_ids):
    """Match a laser setting to contaminants it can remove."""
    matches = []
    
    # All settings can potentially remove common contaminants
    common_contaminants = [
        'rust-oxidation-contamination',
        'oil-grease-contamination',
        'paint-coatings-contamination',
        'dirt-dust-contamination'
    ]
    
    for contam_id in common_contaminants:
        if contam_id in contaminant_ids:
            matches.append({
                'id': contam_id,
                'effectiveness': 'high'
            })
    
    # High fluence settings → heavy contamination
    laser_params = setting_data.get('laser_parameters', {})
    fluence = laser_params.get('fluence_range', {})
    max_fluence = fluence.get('max_j_cm2', 0)
    
    if max_fluence > 5.0:
        heavy_contaminants = [
            'industrial-scale-contamination',
            'corrosion-contamination',
            'heavy-oxidation-contamination'
        ]
        for contam_id in heavy_contaminants:
            if contam_id in contaminant_ids:
                matches.append({
                    'id': contam_id,
                    'effectiveness': 'high'
                })
    
    # Low fluence → delicate contamination
    elif max_fluence < 2.0:
        light_contaminants = [
            'adhesive-residue-contamination',
            'biological-growth-contamination',
            'surface-oxidation-contamination'
        ]
        for contam_id in light_contaminants:
            if contam_id in contaminant_ids:
                matches.append({
                    'id': contam_id,
                    'effectiveness': 'medium'
                })
    
    # Remove duplicates
    seen = set()
    unique_matches = []
    for match in matches:
        if match['id'] not in seen:
            seen.add(match['id'])
            unique_matches.append(match)
    
    return unique_matches

def populate_settings_relationships():
    """Populate optimized_for_materials and removes_contaminants for all settings."""
    
    print("🔄 Loading data...")
    materials, contaminants, settings_data = load_data()
    
    material_categories = categorize_materials()
    contaminant_ids = list(contaminants['contamination_patterns'].keys())
    
    print(f"✅ Loaded {len(materials['materials'])} materials, {len(contaminant_ids)} contaminants")
    
    # Backup
    settings_path = Path("data/settings/Settings.yaml")
    backup_path = settings_path.with_suffix(f'.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(settings_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Process each setting
    settings = settings_data['settings']
    materials_added = 0
    contaminants_added = 0
    
    for setting_id, setting_data in settings.items():
        relationships = setting_data.get('relationships', {})
        
        # Populate optimized_for_materials
        material_matches = match_setting_to_materials(
            setting_id,
            setting_data,
            material_categories
        )
        if material_matches:
            relationships['optimized_for_materials'] = material_matches
            materials_added += len(material_matches)
        
        # Populate removes_contaminants
        contaminant_matches = match_setting_to_contaminants(
            setting_id,
            setting_data,
            contaminant_ids
        )
        if contaminant_matches:
            relationships['removes_contaminants'] = contaminant_matches
            contaminants_added += len(contaminant_matches)
        
        setting_data['relationships'] = relationships
    
    # Save
    with open(settings_path, 'w', encoding='utf-8') as f:
        yaml.dump(settings_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    print(f"\n✅ Population complete:")
    print(f"   • {materials_added} material relationships added")
    print(f"   • {contaminants_added} contaminant relationships added")
    print(f"   • Processed {len(settings)} settings")
    
    # Summary stats
    settings_with_materials = sum(1 for s in settings.values() 
                                 if s.get('relationships', {}).get('optimized_for_materials'))
    settings_with_contaminants = sum(1 for s in settings.values() 
                                    if s.get('relationships', {}).get('removes_contaminants'))
    
    print(f"\n📊 Coverage:")
    print(f"   • Settings with material links: {settings_with_materials}/{len(settings)} ({settings_with_materials/len(settings)*100:.1f}%)")
    print(f"   • Settings with contaminant links: {settings_with_contaminants}/{len(settings)} ({settings_with_contaminants/len(settings)*100:.1f}%)")

if __name__ == "__main__":
    populate_settings_relationships()
