#!/usr/bin/env python3
"""Convert existing Steel content to proper schema format."""

from generation.core.adapters.domain_adapter import DomainAdapter

# Initialize adapter for materials
adapter = DomainAdapter('materials')

# Fields to convert
fields = ['relatedMaterials', 'contaminatedBy', 'materialCharacteristics', 'laserMaterialInteraction']

for field in fields:
    try:
        # Load existing content
        all_data = adapter.load_all_data()
        steel_data = all_data['materials']['steel-laser-cleaning']
        
        # Get the existing content
        if field in ['relatedMaterials', 'contaminatedBy']:
            existing_content = steel_data.get('relationships', {}).get(field)
        elif field in ['materialCharacteristics', 'laserMaterialInteraction']:
            existing_content = steel_data.get('properties', {}).get(field)
        else:
            existing_content = steel_data.get(field)
        
        if existing_content and isinstance(existing_content, str):
            # Save it again - this will trigger schema conversion
            adapter.write_component('steel-laser-cleaning', field, existing_content)
            print(f'✅ Converted {field}')
        else:
            print(f'⏭️  Skipped {field} (not string or missing)')
    except Exception as e:
        print(f'❌ Error converting {field}: {e}')

print('\n✅ Conversion complete! Check data/materials/Materials.yaml for steel-laser-cleaning')
