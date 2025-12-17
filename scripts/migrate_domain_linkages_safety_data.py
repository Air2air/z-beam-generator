#!/usr/bin/env python3
"""
Domain Linkages Safety Data Enhancement Migration Script

Enhances domain_linkages.produces_compounds with safety/technical data
from safety_data.fumes_generated and compound frontmatter.

Phase: Data Enhancement & Dual-Write (Phase 2)
Status: Maintains both structures during transition
"""

import yaml
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys


def load_yaml(file_path: Path) -> Dict:
    """Load YAML file safely"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def save_yaml(file_path: Path, data: Dict) -> None:
    """Save YAML file with proper formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def normalize_compound_name(name: str) -> str:
    """Normalize compound name for matching"""
    return name.lower().strip()


def parse_concentration_range(concentration_str: str) -> Optional[Dict[str, float]]:
    """Parse concentration string like '5-25' into range dict"""
    if not concentration_str or not isinstance(concentration_str, str):
        return None
    
    try:
        if '-' in concentration_str:
            parts = concentration_str.split('-')
            min_val = float(parts[0].strip())
            max_val = float(parts[1].strip())
            return {
                'min_mg_m3': min_val,
                'max_mg_m3': max_val,
                'typical_mg_m3': (min_val + max_val) / 2
            }
        else:
            # Single value
            val = float(concentration_str.strip())
            return {
                'min_mg_m3': val,
                'max_mg_m3': val,
                'typical_mg_m3': val
            }
    except (ValueError, IndexError):
        return None


def load_compound_data(compound_id: str, compounds_dir: Path) -> Optional[Dict]:
    """Load compound frontmatter by ID"""
    # Try to find compound file
    compound_files = list(compounds_dir.rglob(f'{compound_id}.yaml'))
    if compound_files:
        return load_yaml(compound_files[0])
    return None


def determine_ppe_level(ppe_requirements: Optional[Dict]) -> str:
    """Determine PPE level from requirements"""
    if not ppe_requirements:
        return 'none'
    
    respiratory = str(ppe_requirements.get('respiratory', '')).lower()
    
    if 'scba' in respiratory or 'supplied_air' in respiratory or 'supplied air' in respiratory:
        return 'full'
    elif 'organic_vapor' in respiratory or 'p100' in respiratory or 'vapor' in respiratory:
        return 'enhanced'
    elif respiratory and respiratory != 'none':
        return 'basic'
    else:
        return 'none'


def enhance_produces_compounds(
    contaminant_data: Dict,
    compounds_dir: Path,
    dry_run: bool = False
) -> tuple[List[Dict], List[str]]:
    """
    Enhance domain_linkages.produces_compounds with safety data
    
    Returns:
        (enhanced_compounds, warnings)
    """
    warnings = []
    
    # Get existing domain linkages
    domain_linkages = contaminant_data.get('domain_linkages', {})
    produces_compounds = domain_linkages.get('produces_compounds', [])
    
    if not produces_compounds:
        warnings.append("No produces_compounds found in domain_linkages")
        return [], warnings
    
    # Get safety data if it exists (optional - not all files have this yet)
    safety_data = contaminant_data.get('safety_data', {})
    fumes_generated = safety_data.get('fumes_generated', [])
    
    # Create lookup by normalized compound name (if fumes data exists)
    fumes_lookup = {}
    if fumes_generated:
        fumes_lookup = {
            normalize_compound_name(fume.get('compound', '')): fume
            for fume in fumes_generated
        }
    
    # Get particulate properties (applies to all compounds, if exists)
    particulate_generation = safety_data.get('particulate_generation', {})
    ppe_requirements = safety_data.get('ppe_requirements', {})
    ventilation_requirements = safety_data.get('ventilation_requirements', {})
    
    # Enhance each compound
    enhanced_compounds = []
    for compound in produces_compounds:
        compound_id = compound.get('id', '')
        compound_title = compound.get('title', '')
        
        # Make a copy to avoid modifying original
        enhanced = compound.copy()
        
        # Load compound frontmatter for detailed data
        compound_frontmatter = load_compound_data(compound_id, compounds_dir)
        
        # 1. Add concentration data from fumes_generated (if available) or compound frontmatter
        concentration_range = None
        
        # Try fumes_generated first (legacy data source if it exists)
        if fumes_lookup:
            fume_data = fumes_lookup.get(normalize_compound_name(compound_title))
            if fume_data:
                concentration_str = fume_data.get('concentration_mg_m3')
                concentration_range = parse_concentration_range(str(concentration_str))
        
        # Try compound frontmatter typical_concentration_range
        if not concentration_range and compound_frontmatter:
            typical_range = compound_frontmatter.get('typical_concentration_range', {})
            if isinstance(typical_range, dict) and (typical_range.get('min_mg_m3') is not None):
                concentration_range = {
                    'min_mg_m3': typical_range.get('min_mg_m3', 0),
                    'max_mg_m3': typical_range.get('max_mg_m3', 0),
                    'typical_mg_m3': typical_range.get('typical_mg_m3', 
                        (typical_range.get('min_mg_m3', 0) + typical_range.get('max_mg_m3', 0)) / 2)
                }
            elif isinstance(typical_range, str):
                # Try parsing as string range (e.g., "5-25")
                concentration_range = parse_concentration_range(typical_range)
        
        # Add concentration range if found
        if concentration_range:
            enhanced['concentration_range'] = concentration_range
        
        # 2. Add exposure limits from compound frontmatter
        if compound_frontmatter:
            exposure_limits_data = compound_frontmatter.get('exposure_limits', {})
            if exposure_limits_data and any(v is not None for v in exposure_limits_data.values()):
                enhanced['exposure_limits'] = {
                    'osha_pel_mg_m3': exposure_limits_data.get('osha_pel_mg_m3'),
                    'niosh_rel_mg_m3': exposure_limits_data.get('niosh_rel_mg_m3'),
                    'acgih_tlv_mg_m3': exposure_limits_data.get('acgih_tlv_mg_m3'),
                    'idlh_mg_m3': exposure_limits_data.get('idlh_mg_m3')
                }
                
                # Calculate exceeds_limits
                if 'concentration_range' in enhanced:
                    typical_conc = enhanced['concentration_range'].get('typical_mg_m3')
                    acgih_limit = enhanced['exposure_limits'].get('acgih_tlv_mg_m3')
                    if typical_conc is not None and acgih_limit is not None and acgih_limit > 0:
                        enhanced['exceeds_limits'] = typical_conc > acgih_limit
                        # Set monitoring requirement based on exceeds_limits
                        enhanced['monitoring_required'] = enhanced['exceeds_limits']
                    else:
                        enhanced['exceeds_limits'] = False
                        enhanced['monitoring_required'] = False
                else:
                    enhanced['exceeds_limits'] = False
                    enhanced['monitoring_required'] = False
        
        # 3. Add particulate properties (if available)
        if particulate_generation:
            respirable_fraction = particulate_generation.get('respirable_fraction')
            size_range = particulate_generation.get('size_range_um')
            if respirable_fraction is not None or size_range is not None:
                enhanced['particulate_properties'] = {}
                if respirable_fraction is not None:
                    enhanced['particulate_properties']['respirable_fraction'] = respirable_fraction
                if size_range is not None:
                    enhanced['particulate_properties']['size_range_um'] = size_range
        
        # 4. Add control measures
        ppe_level = determine_ppe_level(ppe_requirements)
        enhanced['control_measures'] = {
            'ventilation_required': bool(ventilation_requirements),
            'ppe_level': ppe_level,
            'filtration_type': ventilation_requirements.get('filtration_type') if ventilation_requirements else None
        }
        
        enhanced_compounds.append(enhanced)
    
    return enhanced_compounds, warnings


def migrate_contaminant_file(
    file_path: Path,
    compounds_dir: Path,
    dry_run: bool = False
) -> tuple[bool, List[str]]:
    """
    Migrate a single contaminant file
    
    Returns:
        (success, warnings)
    """
    warnings = []
    
    try:
        # Load contaminant data
        data = load_yaml(file_path)
        
        # Enhance produces_compounds
        enhanced_compounds, enhancement_warnings = enhance_produces_compounds(
            data, compounds_dir, dry_run
        )
        warnings.extend(enhancement_warnings)
        
        if not enhanced_compounds:
            return False, warnings
        
        # Update domain_linkages with enhanced data
        if 'domain_linkages' not in data:
            data['domain_linkages'] = {}
        data['domain_linkages']['produces_compounds'] = enhanced_compounds
        
        # Add migration metadata to safety_data (don't overwrite existing safety_data)
        if 'safety_data' not in data:
            data['safety_data'] = {}
        if '_migration_status' not in data['safety_data']:
            data['safety_data']['_migration_status'] = {}
        data['safety_data']['_migration_status'].update({
            'domain_linkages_enhanced': True,
            'enhancement_date': '2025-12-17',
            'validated': True
        })
        
        # Save if not dry run
        if not dry_run:
            save_yaml(file_path, data)
        
        return True, warnings
        
    except Exception as e:
        import traceback
        warnings.append(f"ERROR: {str(e)}")
        warnings.append(f"Traceback: {traceback.format_exc()}")
        return False, warnings


def main():
    """Main migration process"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate domain linkages to include safety data'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Migrate a single file (for testing)'
    )
    
    args = parser.parse_args()
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    contaminants_dir = base_dir / 'frontmatter' / 'contaminants'
    compounds_dir = base_dir / 'frontmatter' / 'compounds'
    
    if not contaminants_dir.exists():
        print(f"❌ Contaminants directory not found: {contaminants_dir}")
        sys.exit(1)
    
    if not compounds_dir.exists():
        print(f"❌ Compounds directory not found: {compounds_dir}")
        sys.exit(1)
    
    # Determine files to process
    if args.file:
        file_path = Path(args.file)
        # Make absolute if relative
        if not file_path.is_absolute():
            file_path = base_dir / file_path
        files = [file_path]
    else:
        files = sorted(contaminants_dir.rglob('*.yaml'))
    
    # Process files
    print(f"{'='*70}")
    print(f"Domain Linkages Safety Data Migration")
    print(f"{'='*70}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Files to process: {len(files)}")
    print()
    
    total_files = 0
    successful = 0
    failed = 0
    all_warnings = []
    
    for file_path in files:
        relative_path = file_path.relative_to(base_dir)
        print(f"\n📄 Processing: {relative_path}")
        
        success, warnings = migrate_contaminant_file(
            file_path, compounds_dir, args.dry_run
        )
        
        total_files += 1
        if success:
            successful += 1
            print(f"   ✅ Enhanced domain_linkages")
        else:
            failed += 1
            print(f"   ❌ FAILED")
        
        if warnings:
            for warning in warnings:
                print(f"   ⚠️  {warning}")
                all_warnings.append(f"{relative_path}: {warning}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"Migration Summary")
    print(f"{'='*70}")
    print(f"Total files processed: {total_files}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Warnings: {len(all_warnings)}")
    
    if args.dry_run:
        print(f"\n⚠️  DRY RUN - No files were modified")
    else:
        print(f"\n✅ Migration complete!")
    
    # Show warnings summary
    if all_warnings and len(all_warnings) <= 20:
        print(f"\nWarnings:")
        for warning in all_warnings:
            print(f"  - {warning}")
    elif all_warnings:
        print(f"\n⚠️  {len(all_warnings)} warnings generated (too many to display)")
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
