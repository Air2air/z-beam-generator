#!/usr/bin/env python3
"""
Convert Aluminum's embedded markdown content to schema-compliant structure.
Same conversion process used for Steel.
"""

import yaml
from generation.core.adapters.domain_adapter import DomainAdapter

def convert_aluminum():
    """Convert Aluminum's schema-based fields to proper structure."""
    
    print("Converting Aluminum to schema format...")
    
    # Initialize adapter
    adapter = DomainAdapter('materials')
    
    # Fields that need conversion (schema-based components)
    schema_fields = [
        'relatedMaterials',
        'contaminatedBy', 
        'materialCharacteristics',
        'laserMaterialInteraction'
    ]
    
    # Convert each field using existing conversion logic
    for field in schema_fields:
        print(f"\n  Converting {field}...")
        try:
            # The write_component method will detect the string format
            # and automatically convert it using _convert_existing_to_schema_format()
            # Just need to trigger a write - it will auto-detect and convert
            result = adapter.write_component('aluminum-laser-cleaning', field, None)
            print(f"  ✅ {field} converted - {result.get('status', 'done')}")
        except Exception as e:
            print(f"  ⚠️ {field} error: {e}")
    
    print("\n✅ Aluminum conversion complete!")
    print("   Check Materials.yaml for properly structured content")

if __name__ == '__main__':
    convert_aluminum()
