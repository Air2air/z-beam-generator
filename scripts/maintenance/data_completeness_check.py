#!/usr/bin/env python3
"""
Comprehensive Data Completeness Check with Tier-Based Reporting

Categorizes fields into 4 tiers:
- Tier 1 (Critical AI Content): BLOCKING - Must be 100% for production
- Tier 2 (Structural Metadata): SYSTEM - Auto-populated, should be 100%
- Tier 3 (Technical Research): NON-BLOCKING - Separate research process
- Tier 4 (Relationships): NON-BLOCKING - Curation/import process
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple


# TIER DEFINITIONS
FIELD_TIERS = {
    'critical_ai_content': {
        'materials': ['material_description', 'caption', 'faq'],
        'settings': ['settings_description'],
        'description': 'AI-generated text content',
        'required': True,
        'blocking': True,
        'target': 100.0
    },
    'structural_metadata': {
        'materials': ['name', 'category', 'title', 'author', 'images', 'breadcrumb'],
        'settings': ['name', 'category', 'title', 'author', 'images', 'breadcrumb'],
        'description': 'System-generated metadata',
        'required': True,
        'blocking': False,
        'target': 100.0
    },
    'technical_research': {
        'materials': ['materialProperties', 'materialCharacteristics', 'regulatoryStandards'],
        'settings': ['machineSettings', 'material_challenges'],
        'description': 'Technical data from research',
        'required': False,
        'blocking': False,
        'target': None  # No target, separate process
    },
    'relationships': {
        'materials': ['applications'],
        'settings': [],
        'description': 'Curated relationships',
        'required': False,
        'blocking': False,
        'target': None  # No target, ongoing curation
    }
}


def check_materials_completeness() -> Dict:
    """Check Materials.yaml completeness with tier-based reporting"""
    materials_path = Path("data/materials/Materials.yaml")
    
    if not materials_path.exists():
        print("❌ Materials.yaml not found")
        return {}
    
    with open(materials_path) as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    
    print("=" * 80)
    print("📦 MATERIALS DATA COMPLETENESS (Tier-Based)")
    print("=" * 80)
    print()
    print(f"Total materials: {len(materials)}")
    print()
    
    tier_results = {}
    
    # Check each tier
    for tier_name, tier_config in FIELD_TIERS.items():
        fields = tier_config['materials']
        if not fields:
            continue
        
        tier_stats = {}
        for field in fields:
            tier_stats[field] = {
                'present': 0,
                'missing': 0,
                'missing_list': []
            }
        
        # Check each material
        for mat_name, mat_data in materials.items():
            for field in fields:
                value = mat_data.get(field)
                
                # Determine field type
                if field in ['material_description', 'faq', 'name', 'category', 'title']:
                    field_type = 'string'
                elif field in ['caption', 'author', 'images', 'materialProperties']:
                    field_type = 'dict'
                elif field in ['applications', 'materialCharacteristics', 'regulatoryStandards', 'breadcrumb']:
                    field_type = 'list'
                else:
                    field_type = 'string'
                
                is_present = check_field_present(value, field_type)
                
                if is_present:
                    tier_stats[field]['present'] += 1
                else:
                    tier_stats[field]['missing'] += 1
                    if len(tier_stats[field]['missing_list']) < 25:
                        tier_stats[field]['missing_list'].append(mat_name)
        
        tier_results[tier_name] = tier_stats
        
        # Print tier results
        print(f"\n{'🔴 ' if tier_config['blocking'] else '🟢 '}TIER: {tier_config['description'].upper()}")
        if tier_config['blocking']:
            print("   ⚠️  BLOCKING - Must be 100% for production")
        print("-" * 80)
        
        for field, stats in tier_stats.items():
            present = stats['present']
            total = len(materials)
            pct = (present / total * 100) if total > 0 else 0
            
            # Determine status
            if pct >= 95:
                status = "✅"
            elif pct >= 80:
                status = "⚠️"
            else:
                status = "❌"
            
            print(f"{status} {field:30s}: {present:3d}/{total:3d} ({pct:5.1f}%)")
            
            # Show gaps for critical tiers
            if tier_config['blocking'] and 0 < stats['missing'] <= 10:
                print(f"   Missing: {', '.join(stats['missing_list'])}")
            elif stats['missing'] > 0 and stats['missing'] <= 25:
                shown = stats['missing_list'][:10]
                remaining = stats['missing'] - len(shown)
                materials_str = ', '.join(shown)
                if remaining > 0:
                    materials_str += f"... +{remaining} more"
                print(f"   Missing: {materials_str}")
    
    print()
    return tier_results


def check_settings_completeness() -> Dict:
    """Check Settings.yaml completeness with tier-based reporting"""
    settings_path = Path("data/materials/Settings.yaml")
    
    if not settings_path.exists():
        print("❌ Settings.yaml not found")
        return {}
    
    with open(settings_path) as f:
        data = yaml.safe_load(f)
    
    settings = data.get('settings', {})
    
    print("=" * 80)
    print("⚙️  SETTINGS DATA COMPLETENESS (Tier-Based)")
    print("=" * 80)
    print()
    print(f"Total settings: {len(settings)}")
    print()
    
    tier_results = {}
    
    # Check each tier
    for tier_name, tier_config in FIELD_TIERS.items():
        fields = tier_config['settings']
        if not fields:
            continue
        
        tier_stats = {}
        for field in fields:
            tier_stats[field] = {
                'present': 0,
                'missing': 0,
                'missing_list': []
            }
        
        # Check each setting
        for setting_key, setting_data in settings.items():
            for field in fields:
                value = setting_data.get(field)
                
                # Determine field type
                if field in ['settings_description', 'name', 'category', 'title']:
                    field_type = 'string'
                elif field in ['author', 'images', 'machineSettings', 'material_challenges']:
                    field_type = 'dict'
                elif field in ['breadcrumb']:
                    field_type = 'list'
                else:
                    field_type = 'string'
                
                is_present = check_field_present(value, field_type)
                
                if is_present:
                    tier_stats[field]['present'] += 1
                else:
                    tier_stats[field]['missing'] += 1
                    if len(tier_stats[field]['missing_list']) < 25:
                        tier_stats[field]['missing_list'].append(setting_key)
        
        tier_results[tier_name] = tier_stats
        
        # Print tier results
        print(f"\n{'🔴 ' if tier_config['blocking'] else '🟢 '}TIER: {tier_config['description'].upper()}")
        if tier_config['blocking']:
            print("   ⚠️  BLOCKING - Must be 100% for production")
        print("-" * 80)
        
        for field, stats in tier_stats.items():
            present = stats['present']
            total = len(settings)
            pct = (present / total * 100) if total > 0 else 0
            
            # Determine status
            if pct >= 95:
                status = "✅"
            elif pct >= 80:
                status = "⚠️"
            else:
                status = "❌"
            
            print(f"{status} {field:30s}: {present:3d}/{total:3d} ({pct:5.1f}%)")
            
            # Show gaps for critical tiers
            if tier_config['blocking'] and 0 < stats['missing'] <= 10:
                print(f"   Missing: {', '.join(stats['missing_list'])}")
    
    print()
    return tier_results


def check_field_present(value, field_type: str) -> bool:
    """Check if a field value is present and valid"""
    if field_type == 'string':
        return value is not None and str(value).strip() != ''
    elif field_type == 'dict':
        return value is not None and isinstance(value, dict) and len(value) > 0
    elif field_type == 'list':
        return value is not None and isinstance(value, list) and len(value) > 0
    elif field_type == 'bool':
        return value is not None
    return False


def print_summary(materials_stats: Dict, settings_stats: Dict):
    """Print tier-based summary and recommendations"""
    print("=" * 80)
    print("📊 TIER-BASED SUMMARY")
    print("=" * 80)
    print()
    
    # Calculate tier completeness
    for tier_name, tier_config in FIELD_TIERS.items():
        print(f"\n{'🔴' if tier_config['blocking'] else '🟢'} {tier_config['description'].upper()}")
        
        if tier_config['blocking']:
            print("   Status: BLOCKING - Must be 100% for production")
        else:
            print("   Status: NON-BLOCKING - Separate process")
        
        # Materials tier completion
        mat_fields = tier_config['materials']
        if mat_fields and tier_name in materials_stats:
            total_items = 0
            present_items = 0
            for field in mat_fields:
                if field in materials_stats[tier_name]:
                    present_items += materials_stats[tier_name][field]['present']
                    total_items += materials_stats[tier_name][field]['present'] + materials_stats[tier_name][field]['missing']
            
            if total_items > 0:
                pct = (present_items / total_items * 100)
                status = "✅" if pct >= 95 else "⚠️" if pct >= 80 else "❌"
                print(f"   Materials: {status} {present_items}/{total_items} ({pct:.1f}%)")
        
        # Settings tier completion
        set_fields = tier_config['settings']
        if set_fields and tier_name in settings_stats:
            total_items = 0
            present_items = 0
            for field in set_fields:
                if field in settings_stats[tier_name]:
                    present_items += settings_stats[tier_name][field]['present']
                    total_items += settings_stats[tier_name][field]['present'] + settings_stats[tier_name][field]['missing']
            
            if total_items > 0:
                pct = (present_items / total_items * 100)
                status = "✅" if pct >= 95 else "⚠️" if pct >= 80 else "❌"
                print(f"   Settings: {status} {present_items}/{total_items} ({pct:.1f}%)")
    
    print()
    print("=" * 80)
    print("🎯 PRODUCTION READINESS")
    print("=" * 80)
    print()
    print("✅ READY if:")
    print("   • Tier 1 (Critical AI Content) = 100%")
    print("   • Tier 2 (Structural Metadata) = 100%")
    print()
    print("💡 Quick Commands:")
    print("   python3 run.py --caption \"MaterialName\" --skip-integrity-check")
    print("   python3 run.py --material-description \"MaterialName\" --skip-integrity-check")
    print("   python3 run.py --faq \"MaterialName\" --skip-integrity-check")
    print()
    print("📚 Tier 3 & 4 fields populate through separate research/import processes.")
    print()


if __name__ == "__main__":
    materials_stats = check_materials_completeness()
    settings_stats = check_settings_completeness()
    print_summary(materials_stats, settings_stats)
