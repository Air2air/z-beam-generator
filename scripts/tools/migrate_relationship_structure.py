#!/usr/bin/env python3
"""
Migrate Relationship Structure

Reorganizes relationship fields into logical categories:
- identity (intrinsic properties)
- interactions (cross-references)
- operational (practical usage)
- safety (health/compliance)
- environmental (environmental impact)
- detection_monitoring (detection/measurement)
- visual (visual characteristics)

Based on: docs/FRONTMATTER_RELATIONSHIPS_RESTRUCTURE.md
"""

import yaml
from pathlib import Path
from collections import defaultdict

# Category mapping per content type
CATEGORY_MAPS = {
    'materials': {
        # Current field → (new_category, new_field)
        'contaminated_by': ('interactions', 'contaminated_by'),
        'industry_applications': ('operational', 'industry_applications'),
        'regulatory_standards': ('safety', 'regulatory_standards'),
    },
    
    'contaminants': {
        'affects_materials': ('interactions', 'affects_materials'),
        'produces_compounds': ('interactions', 'produces_compounds'),
        'regulatory_standards': ('safety', 'regulatory_standards'),
        'visual_characteristics': ('visual', 'appearance_on_categories'),
        'laser_properties': ('operational', 'laser_properties'),
    },
    
    'compounds': {
        # Identity
        'chemical_properties': ('identity', 'chemical_properties'),
        'physical_properties': ('identity', 'physical_properties'),
        'synonyms_identifiers': ('identity', 'synonyms_identifiers'),
        
        # Interactions
        'produced_from_contaminants': ('interactions', 'produced_from_contaminants'),
        'produced_from_materials': ('interactions', 'produced_from_materials'),
        'reactivity': ('interactions', 'reactivity'),
        
        # Safety
        'exposure_limits': ('safety', 'exposure_limits'),
        'health_effects': ('safety', 'health_effects'),
        'emergency_response': ('safety', 'emergency_response'),
        'ppe_requirements': ('safety', 'ppe_requirements'),
        'regulatory_classification': ('safety', 'regulatory_classification'),
        'storage_requirements': ('safety', 'storage_requirements'),
        
        # Environmental
        'environmental_impact': ('environmental', 'environmental_impact'),
        
        # Detection/Monitoring
        'detection_monitoring': ('detection_monitoring', 'detection_monitoring'),
        
        # Operational (nested structure)
        'operational': None,  # Special handling - already a category
    },
    
    'settings': {
        # Identity
        'composition': ('identity', 'composition'),
        'characteristics': ('identity', 'characteristics'),
        
        # Interactions
        'works_on_materials': ('interactions', 'works_on_materials'),
        'removes_contaminants': ('interactions', 'removes_contaminants'),
        'contamination': ('interactions', 'contamination'),
        
        # Operational
        'machine_settings': ('operational', 'machine_settings'),
        'sources_in_laser_cleaning': ('operational', 'sources_in_laser_cleaning'),
        'typical_concentration_range': ('operational', 'typical_concentration_range'),
        'common_challenges': ('operational', 'common_challenges'),
        
        # Safety
        'health_effects_keywords': ('safety', 'health_effects_keywords'),
        'health_effects': ('safety', 'health_effects'),
        'exposure_guidelines': ('safety', 'exposure_guidelines'),
        'first_aid': ('safety', 'first_aid'),
        'monitoring_required': ('safety', 'monitoring_required'),
        'regulatory_standards': ('safety', 'regulatory_standards'),
        
        # Detection/Monitoring
        'detection_methods': ('detection_monitoring', 'detection_methods'),
    }
}


def migrate_relationships(relationships: dict, content_type: str) -> dict:
    """Migrate flat relationship structure to categorized structure."""
    
    if not relationships:
        return relationships
    
    # Get mapping for this content type
    mapping = CATEGORY_MAPS.get(content_type, {})
    if not mapping:
        print(f"  ⚠️  No mapping for content type: {content_type}")
        return relationships
    
    new_structure = {}
    
    for field_name, field_data in relationships.items():
        # Get target category and field name
        target = mapping.get(field_name)
        
        if target is None:
            # Special handling for 'operational' in compounds (already categorized)
            if field_name == 'operational' and content_type == 'compounds':
                # Flatten operational subcategories
                if isinstance(field_data, dict):
                    for subfield, subdata in field_data.items():
                        sub_target = mapping.get(subfield)
                        if sub_target:
                            category, new_field = sub_target
                            if category not in new_structure:
                                new_structure[category] = {}
                            new_structure[category][new_field] = subdata
            else:
                print(f"  ⚠️  No mapping for field: {field_name} in {content_type}")
            continue
        
        category, new_field = target
        
        # Create category if it doesn't exist
        if category not in new_structure:
            new_structure[category] = {}
        
        # Move field to new category
        new_structure[category][new_field] = field_data
    
    return new_structure


def migrate_file(file_path: Path, content_type: str, domain_key: str, dry_run: bool = True):
    """Migrate a single YAML file."""
    
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        items = data.get(domain_key, {})
        migrated_count = 0
        
        for item_name, item_data in items.items():
            if 'relationships' in item_data:
                old_structure = item_data['relationships']
                new_structure = migrate_relationships(old_structure, content_type)
                
                if new_structure != old_structure:
                    item_data['relationships'] = new_structure
                    migrated_count += 1
        
        if migrated_count > 0 and not dry_run:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return migrated_count
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return 0


def main():
    """Main migration function."""
    
    print("🔄 RELATIONSHIP STRUCTURE MIGRATION")
    print("=" * 70)
    print("\nBased on: docs/FRONTMATTER_RELATIONSHIPS_RESTRUCTURE.md")
    print()
    
    # File mappings
    files = {
        'materials': ('data/materials/Materials.yaml', 'materials'),
        'contaminants': ('data/contaminants/Contaminants.yaml', 'contamination_patterns'),
        'compounds': ('data/compounds/Compounds.yaml', 'compounds'),
        'settings': ('data/settings/Settings.yaml', 'settings'),
    }
    
    # Dry run first
    print("DRY RUN - Preview changes:")
    print("-" * 70)
    
    for content_type, (file_path, domain_key) in files.items():
        print(f"\n{content_type.upper()}:")
        count = migrate_file(Path(file_path), content_type, domain_key, dry_run=True)
        print(f"  Would migrate {count} items")
    
    print("\n" + "=" * 70)
    response = input("\nProceed with migration? (yes/no): ").strip().lower()
    
    if response == 'yes':
        print("\n" + "=" * 70)
        print("LIVE MIGRATION - Applying changes:")
        print("-" * 70)
        
        total = 0
        for content_type, (file_path, domain_key) in files.items():
            print(f"\n{content_type.upper()}:")
            count = migrate_file(Path(file_path), content_type, domain_key, dry_run=False)
            print(f"  ✅ Migrated {count} items")
            total += count
        
        print("\n" + "=" * 70)
        print(f"✅ MIGRATION COMPLETE: {total} items restructured")
        print("\nNew structure:")
        print("  • identity: Intrinsic properties and composition")
        print("  • interactions: Cross-references between entities")
        print("  • operational: Practical usage and processing")
        print("  • safety: Health, safety, and compliance")
        print("  • environmental: Environmental impact")
        print("  • detection_monitoring: Detection and measurement")
        print("  • visual: Visual characteristics")
    else:
        print("\nMigration cancelled.")


if __name__ == '__main__':
    main()
