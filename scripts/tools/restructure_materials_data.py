#!/usr/bin/env python3
"""
Restructure Materials.yaml to match example.yaml format

Changes:
1. regulatoryStandards: String array → Structured objects with name, description, url, image
2. environmentalImpact: {benefit: "name", ...} → {"name": {...}}
3. outcomeMetrics: {metric: "name", ...} → {"name": {...}}
"""

import yaml
from pathlib import Path
from datetime import datetime

# Standard organization mappings
STANDARD_LOGOS = {
    'ANSI': '/images/logo/logo-org-ansi.png',
    'IEC': '/images/logo/logo-org-iec.png',
    'FDA': '/images/logo/logo-org-fda.png',
    'OSHA': '/images/logo/logo-org-osha.png',
    'ISO': '/images/logo/logo-org-iso.png',
    'EN': '/images/logo/logo-org-en.png',
    'ASTM': '/images/logo/logo-org-astm.png',
}

STANDARD_URLS = {
    'ANSI Z136': 'https://webstore.ansi.org/standards/lia/ansiz1362022',
    'IEC 60825': 'https://webstore.iec.ch/en/publication/3587',
    'FDA 21 CFR': 'https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10',
    'OSHA 29 CFR': 'https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.95',
    'ISO': 'https://www.iso.org/',
    'EN': 'https://www.cencenelec.eu/',
    'ASTM': 'https://www.astm.org/',
}


def restructure_regulatory_standards(standards_list):
    """
    Transform regulatory standards from strings to structured objects.
    
    Input: ["FDA 21 CFR 1040.10 - Laser Product Performance Standards", ...]
    Output: [{name: "FDA", description: "FDA 21 CFR 1040.10 - ...", url: "...", image: "..."}, ...]
    """
    if not standards_list:
        return []
    
    structured = []
    
    for standard_str in standards_list:
        if not isinstance(standard_str, str):
            # Already structured, keep as-is
            structured.append(standard_str)
            continue
        
        # Parse "CODE - Description" format
        parts = standard_str.split(' - ', 1)
        if len(parts) == 2:
            code, description = parts
            code = code.strip()
            description = description.strip()
        else:
            code = standard_str.strip()
            description = ''
        
        # Determine organization name from code
        org_name = None
        for prefix in STANDARD_LOGOS.keys():
            if code.startswith(prefix):
                org_name = prefix
                break
        
        if not org_name:
            # Fallback: use first word as org name
            org_name = code.split()[0] if code else 'Unknown'
        
        # Find matching logo
        logo = STANDARD_LOGOS.get(org_name)
        
        # Find matching URL
        url = None
        for prefix, url_path in STANDARD_URLS.items():
            if code.startswith(prefix):
                url = url_path
                break
        
        # Create structured object
        standard_obj = {
            'name': org_name,
            'description': f"{code} - {description}" if description else code
        }
        
        if url:
            standard_obj['url'] = url
        
        if logo:
            standard_obj['image'] = logo
        
        structured.append(standard_obj)
    
    return structured


def restructure_environmental_impact(impact_list):
    """
    Transform environmental impact from object array to key-value array.
    
    Input: [{benefit: "Chemical Waste Elimination", description: "...", ...}, ...]
    Output: [{"Chemical Waste Elimination": {description: "...", ...}}, ...]
    """
    if not impact_list:
        return []
    
    restructured = []
    
    for item in impact_list:
        if not isinstance(item, dict):
            restructured.append(item)
            continue
        
        # Check if already restructured (no 'benefit' key)
        if 'benefit' not in item:
            restructured.append(item)
            continue
        
        # Extract benefit name and create new structure
        benefit_name = item.pop('benefit')
        restructured.append({benefit_name: item})
    
    return restructured


def restructure_outcome_metrics(metrics_list):
    """
    Transform outcome metrics from object array to key-value array.
    
    Input: [{metric: "Contaminant Removal Efficiency", description: "...", ...}, ...]
    Output: [{"Contaminant Removal Efficiency": {description: "...", ...}}, ...]
    """
    if not metrics_list:
        return []
    
    restructured = []
    
    for item in metrics_list:
        if not isinstance(item, dict):
            restructured.append(item)
            continue
        
        # Check if already restructured (no 'metric' key)
        if 'metric' not in item:
            restructured.append(item)
            continue
        
        # Extract metric name and create new structure
        metric_name = item.pop('metric')
        restructured.append({metric_name: item})
    
    return restructured


def restructure_material(material_data):
    """Restructure a single material's data."""
    changes_made = []
    
    # 1. Restructure regulatoryStandards
    if 'regulatoryStandards' in material_data:
        old_standards = material_data['regulatoryStandards']
        if old_standards and isinstance(old_standards[0], str):
            material_data['regulatoryStandards'] = restructure_regulatory_standards(old_standards)
            changes_made.append('regulatoryStandards')
    
    # 2. Restructure environmentalImpact
    if 'environmentalImpact' in material_data:
        old_impact = material_data['environmentalImpact']
        if old_impact and isinstance(old_impact, list) and isinstance(old_impact[0], dict):
            if 'benefit' in old_impact[0]:
                material_data['environmentalImpact'] = restructure_environmental_impact(old_impact)
                changes_made.append('environmentalImpact')
    
    # 3. Restructure outcomeMetrics
    if 'outcomeMetrics' in material_data:
        old_metrics = material_data['outcomeMetrics']
        if old_metrics and isinstance(old_metrics, list) and isinstance(old_metrics[0], dict):
            if 'metric' in old_metrics[0]:
                material_data['outcomeMetrics'] = restructure_outcome_metrics(old_metrics)
                changes_made.append('outcomeMetrics')
    
    return changes_made


def main():
    """Main execution function."""
    print("=" * 80)
    print("MATERIALS.YAML RESTRUCTURING TOOL")
    print("=" * 80)
    print()
    print("This script will restructure Materials.yaml to match example.yaml format:")
    print("  1. regulatoryStandards: String array → Structured objects")
    print("  2. environmentalImpact: Object array → Key-value array")
    print("  3. outcomeMetrics: Object array → Key-value array")
    print()
    
    # Load Materials.yaml
    materials_path = Path(__file__).resolve().parents[2] / "data" / "Materials.yaml"
    
    print(f"Loading {materials_path}...")
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"✅ Loaded {len(materials)} materials")
    print()
    
    # Create backup
    backup_path = materials_path.parent / f"Materials.backup_restructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    print(f"Creating backup: {backup_path.name}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("✅ Backup created")
    print()
    
    # Process each material
    print("Processing materials...")
    total_changes = {
        'regulatoryStandards': 0,
        'environmentalImpact': 0,
        'outcomeMetrics': 0
    }
    
    for material_name, material_data in materials.items():
        changes = restructure_material(material_data)
        for change in changes:
            total_changes[change] += 1
    
    print()
    print("=" * 80)
    print("RESTRUCTURING SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ regulatoryStandards restructured: {total_changes['regulatoryStandards']} materials")
    print(f"✅ environmentalImpact restructured: {total_changes['environmentalImpact']} materials")
    print(f"✅ outcomeMetrics restructured: {total_changes['outcomeMetrics']} materials")
    print()
    
    # Save updated data
    print(f"Saving updated data to {materials_path}...")
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print("✅ Materials.yaml updated successfully")
    print()
    print("=" * 80)
    print("🎉 RESTRUCTURING COMPLETE!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Run export: python3 -m components.frontmatter.core.trivial_exporter")
    print("  2. Deploy: python3 run.py --deploy")
    print()


if __name__ == "__main__":
    main()
