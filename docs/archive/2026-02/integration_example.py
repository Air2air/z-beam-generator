"""
Example: Integrating Validation into Domain Generators

This example shows how to add reference validation to any generator.
"""

from pathlib import Path
from typing import Dict, List

import yaml

from shared.validation.validation_schema import ValidationSchema
from shared.validation.validator_mixin import ReferenceValidatorMixin


class ValidatedMaterialsGenerator(ReferenceValidatorMixin):
    """
    Materials generator with integrated reference validation
    
    Example usage:
        generator = ValidatedMaterialsGenerator()
        generator.enable_auto_fix(True)  # Auto-fix broken references
        generator.generate_material('aluminum-laser-cleaning')
    """
    
    def __init__(self, project_root: Path = None):
        # Initialize validator mixin
        self.init_validator(project_root=project_root, auto_load=True)
        
        # Enable auto-fix by default
        self.enable_auto_fix(True)
        
        self.project_root = project_root or Path.cwd()
    
    def generate_material(self, material_id: str) -> Dict:
        """
        Generate material data with validated references
        """
        print(f"\n🔧 Generating: {material_id}")
        
        # Simulate loading existing data
        material_data = self._load_material(material_id)
        
        # Validate relationships
        if 'relationships' in material_data:
            print("   Validating relationships...")
            
            # Get relationships
            relationships = material_data['relationships']
            
            # Validate each relationship type
            cleaned_relationships = self.validate_relationship_dict(
                relationships,
                field_to_domain=ValidationSchema.FIELD_TO_DOMAIN,
                auto_fix=True
            )
            
            # Update with cleaned relationships
            material_data['relationships'] = cleaned_relationships
        
        # Show stats
        stats = self.get_validation_stats()
        print(f"   📊 Validated: {stats['checked']} refs, Fixed: {stats['fixed']}, Removed: {stats['removed']}")
        self.reset_validation_stats()
        
        return material_data
    
    def _load_material(self, material_id: str) -> Dict:
        """Load material data (placeholder)"""
        # This would load from Materials.yaml
        return {
            'name': 'Aluminum',
            'category': 'metal',
            'relationships': {
                'related_contaminants': [
                    'rust',  # Invalid - missing suffix
                    'rust-contamination',  # Valid
                    'aluminum-oxidation',  # Invalid - missing suffix
                    'nonexistent-contamination',  # Invalid - doesn't exist
                ],
                'related_compounds': [
                    'iron-oxide',  # Valid
                ],
            }
        }


class ValidatedExporter(ReferenceValidatorMixin):
    """
    Frontmatter exporter with integrated validation
    
    Validates all references before exporting frontmatter files.
    """
    
    def __init__(self, domain: str, project_root: Path = None):
        self.domain = domain
        self.init_validator(project_root=project_root, auto_load=True)
        self.enable_auto_fix(True)
        
        self.project_root = project_root or Path.cwd()
    
    def export_item(self, item_id: str, item_data: Dict) -> bool:
        """
        Export single item with validated references
        
        Returns:
            True if export succeeded
        """
        print(f"\n📦 Exporting: {self.domain}/{item_id}")
        
        # Validate relationships before export
        if 'relationships' in item_data:
            relationships = item_data['relationships']
            
            # Get relationship fields for this domain
            rel_fields = ValidationSchema.get_relationships(self.domain)
            
            for rel_field in rel_fields:
                if rel_field not in relationships:
                    continue
                
                target_domain = ValidationSchema.get_target_domain(rel_field)
                if not target_domain:
                    continue
                
                # Extract IDs from relationship objects
                ref_objects = relationships[rel_field]
                ref_ids = [obj.get('id') for obj in ref_objects if isinstance(obj, dict) and 'id' in obj]
                
                # Validate and fix
                valid_ids, invalid = self.validate_and_fix_references(
                    target_domain,
                    ref_ids,
                    auto_fix=True,
                    remove_invalid=True
                )
                
                # Update relationship objects with valid IDs only
                relationships[rel_field] = [
                    obj for obj in ref_objects 
                    if isinstance(obj, dict) and obj.get('id') in valid_ids
                ]
        
        # Export (placeholder)
        print(f"   ✅ Exported with validated references")
        
        stats = self.get_validation_stats()
        if stats['fixed'] > 0 or stats['removed'] > 0:
            print(f"   📊 Fixed: {stats['fixed']}, Removed: {stats['removed']}")
        
        self.reset_validation_stats()
        return True


def example_usage():
    """Demonstrate validator integration"""
    print("="*80)
    print("EXAMPLE: Generator with Integrated Validation")
    print("="*80)
    
    # Example 1: Materials generator
    print("\n1️⃣  Materials Generator")
    generator = ValidatedMaterialsGenerator()
    result = generator.generate_material('aluminum-laser-cleaning')
    
    # Example 2: Exporter with validation
    print("\n2️⃣  Frontmatter Exporter")
    exporter = ValidatedExporter('materials')
    exporter.export_item('aluminum-laser-cleaning', result)
    
    print("\n" + "="*80)
    print("✅ Examples complete")
    print("="*80)


if __name__ == '__main__':
    example_usage()
