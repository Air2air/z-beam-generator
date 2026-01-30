#!/usr/bin/env python3
"""
Remove Unused Fields from Materials.yaml

Removes fields that are:
1. Not consumed by the frontend (MaterialsLayout.tsx)
2. Replaced by structured properties
3. Marked as deprecated in export/config/materials.yaml

This fixes Layer 1 (source data) per FRONTMATTER_SOURCE_OF_TRUTH_POLICY.
"""

import sys
from pathlib import Path
import yaml
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))


class UnusedFieldRemover:
    """Removes unused fields from Materials.yaml source data."""
    
    # Fields to remove (based on export/config/materials.yaml deprecated_fields)
    FIELDS_TO_REMOVE = [
        # Root-level text fields (not consumed by frontend)
        'excerpt',
        'section_description',
        'materialCharacteristics_description',
        'laserMaterialInteraction_description',
        'related_materials',
        'micro_before_after',
        
        # Root-level structured fields (superseded by properties.*)
        'materialCharacteristics',
        'laserMaterialInteraction',
        
        # Legacy fields
        'characteristics',  # Superseded by properties
        'keywords',
        'technicalSpecifications',
        'chemicalProperties',
        'safetyGuidelines',
        'dataValidation',
        'generatedDate',
        'lastModified',
        'breadcrumb',
        
        # Legacy relationship fields (text, not arrays)
        'relationships.relatedMaterials',
        '_distinctive_materialCharacteristics_description',
    ]
    
    def __init__(self, materials_file: Path):
        self.materials_file = materials_file
        self.stats = {
            'materials_processed': 0,
            'fields_removed': 0,
            'removed_by_field': {},
        }
    
    def load_data(self) -> Dict[str, Any]:
        """Load Materials.yaml."""
        print(f"Loading {self.materials_file}...")
        with open(self.materials_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_data(self, data: Dict[str, Any]):
        """Save Materials.yaml."""
        print(f"Saving {self.materials_file}...")
        with open(self.materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def remove_nested_field(self, obj: Dict[str, Any], field_path: str) -> bool:
        """Remove a nested field like 'relationships.relatedMaterials'."""
        parts = field_path.split('.')
        current = obj
        
        # Navigate to parent
        for part in parts[:-1]:
            if part not in current:
                return False
            current = current[part]
        
        # Remove field
        final_key = parts[-1]
        if final_key in current:
            del current[final_key]
            return True
        return False
    
    def clean_material(self, material_id: str, material_data: Dict[str, Any]) -> int:
        """Clean a single material entry. Returns count of fields removed."""
        removed_count = 0
        
        for field in self.FIELDS_TO_REMOVE:
            if '.' in field:
                # Nested field
                if self.remove_nested_field(material_data, field):
                    removed_count += 1
                    self.stats['removed_by_field'][field] = self.stats['removed_by_field'].get(field, 0) + 1
            else:
                # Root-level field
                if field in material_data:
                    del material_data[field]
                    removed_count += 1
                    self.stats['removed_by_field'][field] = self.stats['removed_by_field'].get(field, 0) + 1
        
        return removed_count
    
    def process(self):
        """Process all materials."""
        print("\n" + "="*70)
        print("REMOVING UNUSED FIELDS FROM MATERIALS.YAML")
        print("="*70 + "\n")
        
        # Load data
        data = self.load_data()
        materials = data.get('materials', {})
        
        print(f"Found {len(materials)} materials\n")
        
        # Process each material
        for material_id, material_data in materials.items():
            removed = self.clean_material(material_id, material_data)
            if removed > 0:
                print(f"✓ {material_id}: Removed {removed} fields")
                self.stats['fields_removed'] += removed
            self.stats['materials_processed'] += 1
        
        # Save cleaned data
        self.save_data(data)
        
        # Print summary
        print("\n" + "="*70)
        print("CLEANUP SUMMARY")
        print("="*70)
        print(f"Materials processed: {self.stats['materials_processed']}")
        print(f"Total fields removed: {self.stats['fields_removed']}")
        print("\nFields removed by type:")
        for field, count in sorted(self.stats['removed_by_field'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {field}: {count}")
        print("\n✅ Source data cleanup complete")
        print("   Next: Run export to regenerate frontmatter")
        print("   Command: python3 run.py --export --domain materials\n")


def main():
    """Main entry point."""
    materials_file = project_root / 'data' / 'materials' / 'Materials.yaml'
    
    if not materials_file.exists():
        print(f"❌ Materials.yaml not found: {materials_file}")
        sys.exit(1)
    
    remover = UnusedFieldRemover(materials_file)
    remover.process()


if __name__ == '__main__':
    main()
