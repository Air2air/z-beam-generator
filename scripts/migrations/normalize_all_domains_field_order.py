#!/usr/bin/env python3
"""
Comprehensive field order normalization across all 4 domains.

COMPLIANCE: docs/BACKEND_FRONTMATTER_FIELD_ORDER_JAN6_2026.md

Fixes all identified normalization opportunities:

CRITICAL:
- Add datePublished, dateModified to all entries
- Add contentType field to all entries  
- Add schemaVersion to individual entries (not just file level)

HIGH:
- Standardize displayName field across domains
- Add image dimensions to Settings
- Standardize author placement (move to end - Priority 7)
- Standardize images placement (Priority 5)

MEDIUM:
- Remove duplicate formula field from Compounds
- Standardize image field order (url → alt → width → height)
- Standardize relationships structure
"""

import yaml
from pathlib import Path
from collections import OrderedDict
import shutil
from datetime import datetime


# Universal field order per BACKEND_FRONTMATTER_FIELD_ORDER_JAN6_2026.md
FIELD_ORDER = [
    # Priority 1: Critical routing (MUST be first 10 lines)
    'id',
    'name',
    'displayName',
    'category',
    'subcategory',
    'hazard_class',
    'datePublished',
    'dateModified',
    'contentType',
    'schemaVersion',
    
    # Priority 2: Navigation & SEO (Lines 11-30)
    'fullPath',
    'breadcrumb',
    'pageTitle',
    'pageDescription',
    'metaDescription',
    
    # Priority 3: Technical Properties
    'chemical_formula',
    'cas_number',
    'molecular_weight',
    'density',
    'melting_point',
    'thermal_conductivity',
    'relatedMaterial',
    'machine_settings',
    'characteristics',
    'properties',
    'valid_materials',
    
    # Priority 4: Content Fields
    'component_summary',
    'micro',
    'description',
    'subtitle',
    'health_effects',
    'health_effects_keywords',
    'exposure_guidelines',
    'detection_methods',
    'first_aid',
    'ppe_requirements',
    'regulatory_standards',
    'monitoring_required',
    
    # Priority 5: Media Assets
    'images',
    
    # Priority 6: Relationships
    'relationships',
    
    # Priority 7: Complex Objects (End)
    'author',
    'card',
]


def get_domain_display_name(name, domain):
    """Generate displayName from name based on domain."""
    if domain == 'materials':
        return f"{name} Laser Cleaning"
    elif domain == 'compounds':
        # Compounds already have display_name, we'll convert it
        return name  # Will be populated from existing display_name
    elif domain == 'contaminants':
        # Contaminants have title field
        return name  # Will be populated from existing title
    elif domain == 'settings':
        return f"{name} Laser Cleaning Settings"
    return name


def normalize_images(images_data):
    """Normalize image field order: url → alt → width → height"""
    if not images_data:
        return images_data
    
    normalized = OrderedDict()
    for img_type, img_data in images_data.items():
        if isinstance(img_data, dict):
            ordered_img = OrderedDict()
            # Standard order
            if 'url' in img_data:
                ordered_img['url'] = img_data['url']
            if 'alt' in img_data:
                ordered_img['alt'] = img_data['alt']
            if 'width' in img_data:
                ordered_img['width'] = img_data['width']
            else:
                # Add default dimensions if missing
                if img_type == 'hero':
                    ordered_img['width'] = 1200
                    ordered_img['height'] = 630
                elif img_type == 'micro':
                    ordered_img['width'] = 800
                    ordered_img['height'] = 600
            if 'height' in img_data:
                ordered_img['height'] = img_data['height']
            elif img_type == 'hero' and 'width' in ordered_img:
                ordered_img['height'] = 630
            elif img_type == 'micro' and 'width' in ordered_img:
                ordered_img['height'] = 600
                
            # Add any remaining fields
            for key, value in img_data.items():
                if key not in ordered_img:
                    ordered_img[key] = value
            
            normalized[img_type] = dict(ordered_img)
        else:
            normalized[img_type] = img_data
    
    return dict(normalized)


def normalize_entry(entry_data, entry_id, domain):
    """Normalize a single entry according to field order."""
    ordered = OrderedDict()
    
    # Add fields in specified order
    for key in FIELD_ORDER:
        if key in entry_data:
            value = entry_data[key]
            
            # Normalize images structure
            if key == 'images':
                value = normalize_images(value)
            
            ordered[key] = value
    
    # Add missing critical fields
    if 'datePublished' not in ordered:
        ordered['datePublished'] = '2026-01-06T00:00:00.000Z'
    if 'dateModified' not in ordered:
        ordered['dateModified'] = '2026-01-06T00:00:00.000Z'
    if 'contentType' not in ordered:
        ordered['contentType'] = domain.rstrip('s')  # materials → material
    if 'schemaVersion' not in ordered:
        ordered['schemaVersion'] = '5.0.0'
    
    # Handle displayName
    if 'displayName' not in ordered:
        if 'display_name' in entry_data:
            # Compounds have display_name
            ordered['displayName'] = entry_data['display_name']
        elif 'title' in entry_data and domain == 'contaminants':
            # Contaminants have title
            ordered['title'] = entry_data['title']  # Keep title for now
            ordered['displayName'] = entry_data['title']
        else:
            # Generate from name
            ordered['displayName'] = get_domain_display_name(ordered.get('name', ''), domain)
    
    # Remove duplicate formula field (Compounds only)
    if domain == 'compounds' and 'formula' in entry_data and 'chemical_formula' in ordered:
        # Skip formula, we keep chemical_formula
        pass
    
    # Re-insert displayName after name (Priority 1)
    if 'displayName' in ordered:
        display_name_value = ordered.pop('displayName')
        new_ordered = OrderedDict()
        for k, v in ordered.items():
            new_ordered[k] = v
            if k == 'name':
                new_ordered['displayName'] = display_name_value
        ordered = new_ordered
    
    # Add any remaining fields not in FIELD_ORDER
    for key, value in entry_data.items():
        if key not in ordered and key not in ['display_name', 'formula']:
            ordered[key] = value
    
    return ordered


def normalize_domain(domain_name):
    """Normalize a single domain file."""
    domain_files = {
        'materials': 'data/materials/Materials.yaml',
        'compounds': 'data/compounds/Compounds.yaml',
        'contaminants': 'data/contaminants/Contaminants.yaml',
        'settings': 'data/settings/Settings.yaml'
    }
    
    file_path = Path(domain_files[domain_name])
    
    if not file_path.exists():
        print(f"❌ ERROR: {file_path} not found")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = file_path.with_suffix(f'.backup-normalize-{timestamp}.yaml')
    shutil.copy(file_path, backup_file)
    print(f"✅ Created backup: {backup_file.name}")
    
    # Load data
    print(f"📖 Loading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Get the entries container
    if domain_name == 'materials':
        entries_key = 'materials'
    elif domain_name == 'compounds':
        entries_key = 'compounds'
    elif domain_name == 'contaminants':
        entries_key = 'contaminants'
    elif domain_name == 'settings':
        entries_key = 'settings'
    
    if entries_key not in data:
        print(f"❌ ERROR: '{entries_key}' key not found")
        return False
    
    entries = data[entries_key]
    total = len(entries)
    print(f"📊 Found {total} {domain_name} entries")
    
    # Normalize each entry
    normalized_count = 0
    for entry_id, entry_data in entries.items():
        normalized = normalize_entry(entry_data, entry_id, domain_name)
        data[entries_key][entry_id] = dict(normalized)
        normalized_count += 1
        
        # Show first 2 examples
        if normalized_count <= 2:
            print(f"\n📝 Example {normalized_count}: {entry_id}")
            print(f"   First 10 fields: {list(normalized.keys())[:10]}")
    
    # Save normalized data
    print(f"\n💾 Saving normalized data to {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f,
                  default_flow_style=False,
                  allow_unicode=True,
                  sort_keys=False,
                  width=1000,
                  indent=2)
    
    print(f"\n✅ COMPLETE: Normalized {normalized_count}/{total} {domain_name} entries")
    return True


def main():
    """Normalize all 4 domains."""
    print("=" * 80)
    print("COMPREHENSIVE FIELD ORDER NORMALIZATION")
    print("=" * 80)
    print("\nCOMPLIANCE: docs/BACKEND_FRONTMATTER_FIELD_ORDER_JAN6_2026.md")
    print("\nNORMALIZATIONS:")
    print("✅ Add datePublished, dateModified, contentType, schemaVersion")
    print("✅ Standardize displayName across all domains")
    print("✅ Normalize image field order (url → alt → width → height)")
    print("✅ Add missing image dimensions")
    print("✅ Standardize author placement (Priority 7: end)")
    print("✅ Standardize images placement (Priority 5: after content)")
    print("✅ Remove duplicate formula field (Compounds)")
    print()
    
    domains = ['materials', 'compounds', 'contaminants', 'settings']
    results = {}
    
    for domain in domains:
        print(f"\n{'=' * 80}")
        print(f"NORMALIZING: {domain.upper()}")
        print('=' * 80)
        results[domain] = normalize_domain(domain)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for domain, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{domain:20s}: {status}")
    
    if all(results.values()):
        print("\n✅ ALL DOMAINS NORMALIZED SUCCESSFULLY")
        print("\nNEXT STEPS:")
        print("1. Verify changes with git diff")
        print("2. Re-export all domains:")
        print("   python3 run.py --export --domain materials")
        print("   python3 run.py --export --domain compounds")
        print("   python3 run.py --export --domain contaminants")
        print("   python3 run.py --export --domain settings")
        print("\n3. Verify frontmatter has correct field order")
        print("4. Test routing (no 404 errors)")
        print("5. Commit changes")
        return True
    else:
        print("\n❌ SOME DOMAINS FAILED")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
