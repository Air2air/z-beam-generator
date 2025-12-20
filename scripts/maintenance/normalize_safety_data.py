#!/usr/bin/env python3
"""
Safety Data Normalization Script
=================================
Normalizes safety_data sections across ALL domain frontmatter to comply with
SAFETY_RISK_SEVERITY_SCHEMA.md

Applies to: materials, contaminants, compounds, settings (any domain with safety_data)

Adds missing fields:
- toxic_gas_risk (derived from fumes_generated)
- visibility_hazard (derived from particulate_generation)
- ventilation_requirements (calculated from risk levels)

Standardizes PPE values:
- goggles → Safety Goggles
- dust_mask → N95/P100 Respirator (based on risk)
- gloves → Leather Gloves / Chemical-Resistant Gloves

Usage:
    python3 scripts/maintenance/normalize_safety_data.py --dry-run
    python3 scripts/maintenance/normalize_safety_data.py --apply
    python3 scripts/maintenance/normalize_safety_data.py --apply --domains materials contaminants
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

FRONTMATTER_BASE = project_root.parent / "z-beam" / "frontmatter"
AVAILABLE_DOMAINS = ['materials', 'contaminants', 'compounds', 'settings']

RISK_LEVELS = ['none', 'low', 'moderate', 'high', 'critical']

# Schema-compliant PPE values
PPE_STANDARD_VALUES = {
    'respiratory': {
        'dust_mask': 'N95 Respirator',
        'n95': 'N95 Respirator',
        'p100': 'P100 Respirator',
        'respirator': 'P100 Respirator',
        'half-face': 'Half-Face Respirator',
        'full-face': 'Full-Face Respirator',
        'scba': 'SCBA Required',
    },
    'eye_protection': {
        'goggles': 'Safety Goggles',
        'safety goggles': 'Safety Goggles',
        'glasses': 'Safety Glasses',
        'safety glasses': 'Safety Glasses',
        'face shield': 'Face Shield',
    },
    'skin_protection': {
        'gloves': 'Leather Gloves',
        'leather gloves': 'Leather Gloves',
        'chemical gloves': 'Chemical-Resistant Gloves',
        'chemical-resistant gloves': 'Chemical-Resistant Gloves',
    }
}


def load_yaml_file(filepath: Path) -> Optional[Dict[str, Any]]:
    """Load YAML file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {filepath.name}: {e}")
        return None


def save_yaml_file(filepath: Path, data: Dict[str, Any]) -> bool:
    """Save YAML file safely"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        print(f"Error saving {filepath.name}: {e}")
        return False


def derive_toxic_gas_risk(fumes_generated: List[Dict[str, Any]]) -> str:
    """Derive toxic_gas_risk from fumes_generated hazard classes"""
    if not fumes_generated:
        return 'low'
    
    hazard_classes = [f.get('hazard_class', '').lower() for f in fumes_generated]
    
    # Critical: carcinogenic or highly toxic compounds
    if 'carcinogenic' in hazard_classes or 'highly_toxic' in hazard_classes:
        return 'critical'
    
    # High: toxic compounds
    if 'toxic' in hazard_classes:
        return 'high'
    
    # Moderate: irritants
    if 'irritant' in hazard_classes:
        return 'moderate'
    
    return 'low'


def derive_visibility_hazard(respirable_fraction: float) -> str:
    """Derive visibility_hazard from particulate generation"""
    if respirable_fraction >= 0.7:
        return 'high'
    elif respirable_fraction >= 0.4:
        return 'moderate'
    else:
        return 'low'


def calculate_ventilation_requirements(fire_risk: str, toxic_gas_risk: str, visibility_hazard: str) -> Dict[str, Any]:
    """Calculate ventilation requirements based on risk levels"""
    # Get highest risk level
    risks = [fire_risk, toxic_gas_risk, visibility_hazard]
    risk_indices = [RISK_LEVELS.index(r) if r in RISK_LEVELS else 0 for r in risks]
    max_risk_index = max(risk_indices)
    max_risk = RISK_LEVELS[max_risk_index]
    
    if max_risk == 'critical':
        return {
            'minimum_air_changes_per_hour': 20,
            'exhaust_velocity_m_s': 1.2,
            'filtration_type': 'HEPA + Activated Carbon'
        }
    elif max_risk == 'high':
        return {
            'minimum_air_changes_per_hour': 15,
            'exhaust_velocity_m_s': 1.0,
            'filtration_type': 'HEPA + Activated Carbon'
        }
    elif max_risk == 'moderate':
        return {
            'minimum_air_changes_per_hour': 12,
            'exhaust_velocity_m_s': 0.75,
            'filtration_type': 'HEPA Filtration'
        }
    else:  # low or none
        return {
            'minimum_air_changes_per_hour': 8,
            'exhaust_velocity_m_s': 0.5,
            'filtration_type': 'Mechanical Filtration'
        }


def standardize_respiratory(current_value: str, respirable_fraction: float, toxic_gas_risk: str) -> str:
    """Standardize respiratory protection value"""
    current_lower = current_value.lower().strip()
    
    # Critical/high toxic gas requires advanced protection
    if toxic_gas_risk == 'critical':
        return 'SCBA Required'
    elif toxic_gas_risk == 'high':
        return 'Full-Face Respirator'
    
    # High respirable fraction requires P100
    if respirable_fraction >= 0.6:
        return 'P100 Respirator'
    
    # Try to match standard value
    for pattern, standard in PPE_STANDARD_VALUES['respiratory'].items():
        if pattern in current_lower:
            return standard
    
    # Default based on respirable fraction
    return 'P100 Respirator' if respirable_fraction >= 0.5 else 'N95 Respirator'


def standardize_eye_protection(current_value: str, fire_risk: str) -> str:
    """Standardize eye protection value"""
    current_lower = current_value.lower().strip()
    
    # High fire risk requires combination protection
    if fire_risk in ['critical', 'high']:
        return 'Combination (Goggles + Shield)'
    
    # Try to match standard value
    for pattern, standard in PPE_STANDARD_VALUES['eye_protection'].items():
        if pattern in current_lower:
            return standard
    
    # Default to Safety Goggles
    return 'Safety Goggles'


def standardize_skin_protection(current_value: str, toxic_gas_risk: str) -> str:
    """Standardize skin protection value"""
    current_lower = current_value.lower().strip()
    
    # Critical/high toxic risk requires chemical resistance
    if toxic_gas_risk in ['critical', 'high']:
        return 'Chemical-Resistant Gloves'
    
    # Try to match standard value
    for pattern, standard in PPE_STANDARD_VALUES['skin_protection'].items():
        if pattern in current_lower:
            return standard
    
    # Default to Leather Gloves
    return 'Leather Gloves'


def normalize_safety_data(data: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
    """Normalize safety_data section in frontmatter"""
    changes = []
    
    # Check if safety_data exists
    if 'safety_data' not in data:
        return data, changes
    
    safety_data = data['safety_data']
    
    # Get existing values
    fire_risk = safety_data.get('fire_explosion_risk', 'low')
    fumes_generated = safety_data.get('fumes_generated', [])
    particulate = safety_data.get('particulate_generation', {})
    respirable_fraction = particulate.get('respirable_fraction', 0.5)
    ppe_reqs = safety_data.get('ppe_requirements', {})
    
    # Derive toxic_gas_risk if missing
    if 'toxic_gas_risk' not in safety_data:
        toxic_gas_risk = derive_toxic_gas_risk(fumes_generated)
        safety_data['toxic_gas_risk'] = toxic_gas_risk
        changes.append(f"Added toxic_gas_risk: {toxic_gas_risk}")
    else:
        toxic_gas_risk = safety_data['toxic_gas_risk']
    
    # Derive visibility_hazard if missing
    if 'visibility_hazard' not in safety_data:
        visibility_hazard = derive_visibility_hazard(respirable_fraction)
        safety_data['visibility_hazard'] = visibility_hazard
        changes.append(f"Added visibility_hazard: {visibility_hazard}")
    else:
        visibility_hazard = safety_data['visibility_hazard']
    
    # Add ventilation_requirements if missing
    if 'ventilation_requirements' not in safety_data:
        vent_reqs = calculate_ventilation_requirements(fire_risk, toxic_gas_risk, visibility_hazard)
        safety_data['ventilation_requirements'] = vent_reqs
        changes.append(f"Added ventilation_requirements (ACH: {vent_reqs['minimum_air_changes_per_hour']})")
    
    # Standardize PPE values
    if 'ppe_requirements' in safety_data:
        ppe = safety_data['ppe_requirements']
        
        # Respiratory
        if 'respiratory' in ppe:
            old_value = ppe['respiratory']
            new_value = standardize_respiratory(old_value, respirable_fraction, toxic_gas_risk)
            if old_value != new_value:
                ppe['respiratory'] = new_value
                changes.append(f"Standardized respiratory: {old_value} → {new_value}")
        
        # Eye protection
        if 'eye_protection' in ppe:
            old_value = ppe['eye_protection']
            new_value = standardize_eye_protection(old_value, fire_risk)
            if old_value != new_value:
                ppe['eye_protection'] = new_value
                changes.append(f"Standardized eye_protection: {old_value} → {new_value}")
        
        # Skin protection
        if 'skin_protection' in ppe:
            old_value = ppe['skin_protection']
            new_value = standardize_skin_protection(old_value, toxic_gas_risk)
            if old_value != new_value:
                ppe['skin_protection'] = new_value
                changes.append(f"Standardized skin_protection: {old_value} → {new_value}")
    
    return data, changes


def process_domain_files(domain: str, dry_run: bool = True) -> Dict[str, Any]:
    """Process all frontmatter files for a specific domain"""
    
    domain_dir = FRONTMATTER_BASE / domain
    
    if not domain_dir.exists():
        print(f"⚠️  Domain directory not found: {domain_dir}")
        return {'success': False, 'total': 0, 'processed': 0, 'modified': 0, 'skipped': 0, 'errors': 0}
    
    files = list(domain_dir.glob("*.yaml"))
    
    if not files:
        print(f"⚠️  No YAML files found in {domain}")
        return {'success': True, 'total': 0, 'processed': 0, 'modified': 0, 'skipped': 0, 'errors': 0}
    
    print(f"\n{'='*80}")
    print(f"📁 Processing {domain.upper()} domain - {len(files)} files")
    print('='*80)
    print()
    
    stats = {
        'total': len(files),
        'processed': 0,
        'modified': 0,
        'skipped': 0,
        'errors': 0,
        'changes': []
    }
    
    for filepath in sorted(files):
        # Load file
        data = load_yaml_file(filepath)
        if data is None:
            stats['errors'] += 1
            continue
        
        # Skip if no safety_data
        if 'safety_data' not in data:
            stats['skipped'] += 1
            continue
        
        # Normalize
        normalized_data, changes = normalize_safety_data(data)
        stats['processed'] += 1
        
        if changes:
            stats['modified'] += 1
            stats['changes'].append({
                'file': filepath.name,
                'domain': domain,
                'changes': changes
            })
            
            if dry_run:
                print(f"📝 [{domain}] {filepath.name}")
                for change in changes:
                    print(f"   • {change}")
                print()
            else:
                # Save file
                if save_yaml_file(filepath, normalized_data):
                    print(f"✅ [{domain}] {filepath.name}")
                    for change in changes:
                        print(f"   • {change}")
                    print()
                else:
                    print(f"❌ [{domain}] Failed to save {filepath.name}")
                    stats['errors'] += 1
    
    print(f"\n{domain.upper()} Summary: {stats['modified']}/{stats['total']} files modified, {stats['skipped']} skipped\n")
    
    return stats


def process_all_domains(domains: List[str], dry_run: bool = True) -> Dict[str, Any]:
    """Process multiple domains"""
    
    if not FRONTMATTER_BASE.exists():
        print(f"❌ Frontmatter base directory not found: {FRONTMATTER_BASE}")
        return {'success': False}
    
    print(f"🔍 Processing domains: {', '.join(domains)}")
    
    all_stats = {
        'domains': {},
        'total_files': 0,
        'total_processed': 0,
        'total_modified': 0,
        'total_skipped': 0,
        'total_errors': 0,
        'all_changes': []
    }
    
    for domain in domains:
        stats = process_domain_files(domain, dry_run)
        all_stats['domains'][domain] = stats
        all_stats['total_files'] += stats['total']
        all_stats['total_processed'] += stats['processed']
        all_stats['total_modified'] += stats['modified']
        all_stats['total_skipped'] += stats['skipped']
        all_stats['total_errors'] += stats['errors']
        all_stats['all_changes'].extend(stats.get('changes', []))
    
    return all_stats


def main():
    parser = argparse.ArgumentParser(description='Normalize safety data across all domain frontmatter')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--apply', action='store_true', help='Apply changes to files')
    parser.add_argument('--domains', nargs='+', choices=AVAILABLE_DOMAINS, 
                        help=f'Specific domains to process (default: all). Options: {", ".join(AVAILABLE_DOMAINS)}')
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        print("Please specify --dry-run or --apply")
        return 1
    
    # Default to all domains if not specified
    domains = args.domains if args.domains else AVAILABLE_DOMAINS
    
    mode = "DRY RUN" if args.dry_run else "APPLY CHANGES"
    print("=" * 80)
    print(f"SAFETY DATA NORMALIZATION - {mode}")
    print(f"Domains: {', '.join(domains)}")
    print("=" * 80)
    
    stats = process_all_domains(domains, dry_run=args.dry_run)
    
    # Print summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    for domain, domain_stats in stats['domains'].items():
        status = "✅" if domain_stats['modified'] > 0 else "⚪"
        print(f"{status} {domain.upper()}:")
        print(f"   Total: {domain_stats['total']}, Modified: {domain_stats['modified']}, " +
              f"Skipped: {domain_stats['skipped']}, Errors: {domain_stats['errors']}")
    
    print(f"\n📊 TOTALS:")
    print(f"   Files: {stats['total_files']}")
    print(f"   Processed: {stats['total_processed']}")
    print(f"   Modified: {stats['total_modified']}")
    print(f"   Skipped: {stats['total_skipped']}")
    print(f"   Errors: {stats['total_errors']}")
    print()
    
    if args.dry_run:
        print("✨ Dry run complete. Use --apply to make changes.")
    else:
        print(f"✅ Normalization complete. {stats['total_modified']} files updated across {len(domains)} domains.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
