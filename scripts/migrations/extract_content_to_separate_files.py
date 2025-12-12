#!/usr/bin/env python3
"""
Extract Content from Materials.yaml to Separate Files

Extracts caption, faq, and regulatoryStandards from Materials.yaml into:
- materials/data/content/Micros.yaml
- materials/data/content/FAQs.yaml
- materials/data/content/RegulatoryStandards.yaml

This reduces Materials.yaml from 2.8MB to ~800KB while maintaining all data
through orchestration in TrivialFrontmatterExporter.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def extract_content():
    """Extract content fields from Materials.yaml to separate files."""
    
    print("\n" + "="*80)
    print("EXTRACT CONTENT FROM MATERIALS.YAML")
    print("="*80 + "\n")
    
    # Paths
    materials_file = project_root / 'materials' / 'data' / 'Materials.yaml'
    content_dir = project_root / 'materials' / 'data' / 'content'
    
    captions_file = content_dir / 'Micros.yaml'
    faqs_file = content_dir / 'FAQs.yaml'
    regulatory_file = content_dir / 'RegulatoryStandards.yaml'
    
    # Load Materials.yaml
    print(f"📂 Loading {materials_file.name}...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    materials_section = materials_data.get('materials', {})
    print(f"✅ Loaded {len(materials_section)} materials\n")
    
    # Extract data
    micros = {}
    faqs = {}
    regulatory_standards = {}
    
    micro_count = 0
    faq_count = 0
    regulatory_count = 0
    
    print("🔄 Extracting content...")
    for material_name, material_data in materials_section.items():
        # Extract micros
        if 'micro' in material_data:
            micros[material_name] = material_data['micro']
            micro_count += 1
        
        # Extract FAQs
        if 'faq' in material_data:
            faqs[material_name] = material_data['faq']
            faq_count += 1
        
        # Extract regulatory standards
        if 'regulatoryStandards' in material_data:
            regulatory_standards[material_name] = material_data['regulatoryStandards']
            regulatory_count += 1
    
    print(f"   ✅ Extracted {micro_count} micros")
    print(f"   ✅ Extracted {faq_count} FAQ sets")
    print(f"   ✅ Extracted {regulatory_count} regulatory standard sets\n")
    
    # Create metadata
    extraction_metadata = {
        'extracted_date': datetime.now().isoformat(),
        'source_file': 'Materials.yaml',
        'total_materials': len(materials_section),
        'schema_version': '1.0.0'
    }
    
    # Write Micros.yaml
    print(f"💾 Writing {captions_file.name}...")
    captions_output = {
        '_metadata': {
            **extraction_metadata,
            'description': 'Material-specific before/after micros extracted from Materials.yaml',
            'total_entries': len(micros)
        },
        'micros': micros
    }
    with open(captions_file, 'w', encoding='utf-8') as f:
        yaml.dump(captions_output, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    print(f"   ✅ Wrote {len(micros)} micros ({captions_file.stat().st_size // 1024}KB)")
    
    # Write FAQs.yaml
    print(f"💾 Writing {faqs_file.name}...")
    faqs_output = {
        '_metadata': {
            **extraction_metadata,
            'description': 'Material-specific frequently asked questions extracted from Materials.yaml',
            'total_entries': len(faqs)
        },
        'faqs': faqs
    }
    with open(faqs_file, 'w', encoding='utf-8') as f:
        yaml.dump(faqs_output, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    print(f"   ✅ Wrote {len(faqs)} FAQ sets ({faqs_file.stat().st_size // 1024}KB)")
    
    # Write RegulatoryStandards.yaml
    print(f"💾 Writing {regulatory_file.name}...")
    regulatory_output = {
        '_metadata': {
            **extraction_metadata,
            'description': 'Material-specific regulatory standards extracted from Materials.yaml',
            'total_entries': len(regulatory_standards)
        },
        'regulatory_standards': regulatory_standards
    }
    with open(regulatory_file, 'w', encoding='utf-8') as f:
        yaml.dump(regulatory_output, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    print(f"   ✅ Wrote {len(regulatory_standards)} regulatory standard sets ({regulatory_file.stat().st_size // 1024}KB)")
    
    # Summary
    print("\n" + "="*80)
    print("📊 EXTRACTION SUMMARY")
    print("="*80)
    print(f"   Micros:            {len(micros)} materials → {captions_file.name}")
    print(f"   FAQs:                {len(faqs)} materials → {faqs_file.name}")
    print(f"   Regulatory Standards: {len(regulatory_standards)} materials → {regulatory_file.name}")
    print(f"\n   Total extracted entries: {micro_count + faq_count + regulatory_count}")
    print("="*80 + "\n")
    
    print("✅ Content extraction complete!")
    print("📝 Next step: Update TrivialFrontmatterExporter to orchestrate these files")
    

if __name__ == '__main__':
    extract_content()
