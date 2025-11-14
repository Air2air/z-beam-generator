#!/usr/bin/env python3
"""
Preview Subtitle Generation - Test on 10 Random Materials

Shows what the new subtitles will look like with different focus areas.
"""

import yaml
import random
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.api.client_factory import create_api_client

# Same focus areas as main script
SUBTITLE_FOCUS_AREAS = [
    {"id": "unique_characteristics", "name": "Unique Material Characteristics"},
    {"id": "sibling_comparison", "name": "Compare to Sibling Materials"},
    {"id": "cleaning_techniques", "name": "Special Cleaning Techniques"},
    {"id": "industry_applications", "name": "Industry-Specific Applications"},
    {"id": "critical_challenges", "name": "Critical Cleaning Challenges"},
    {"id": "preservation_benefits", "name": "Preservation Over Traditional Methods"},
    {"id": "material_vulnerabilities", "name": "Material Vulnerability Concerns"},
    {"id": "surface_outcomes", "name": "Surface Finish Outcomes"},
    {"id": "contamination_types", "name": "Material-Specific Contamination"},
    {"id": "parameter_optimization", "name": "Critical Parameter Optimization"}
]

def main():
    print("=" * 100)
    print("SUBTITLE PREVIEW - 10 RANDOM MATERIALS WITH DIFFERENT FOCUS AREAS")
    print("=" * 100)
    print()
    
    # Load materials
    materials_file = Path('materials/data/Materials.yaml')
    with open(materials_file, 'r') as f:
        materials_data = yaml.safe_load(f)
    
    materials = materials_data.get('materials', {})
    
    # Select 10 random materials
    sample_materials = random.sample(list(materials.items()), min(10, len(materials)))
    
    print("📋 FOCUS AREA OPTIONS:")
    print("-" * 100)
    for i, focus in enumerate(SUBTITLE_FOCUS_AREAS, 1):
        print(f"{i:2d}. {focus['name']}")
    print()
    
    print("=" * 100)
    print("PREVIEW EXAMPLES (These are NOT generated, just showing focus distribution)")
    print("=" * 100)
    print()
    
    for i, (material_name, material_data) in enumerate(sample_materials, 1):
        category = material_data.get('category', 'unknown')
        current_subtitle = material_data.get('subtitle', 'N/A')
        
        # Randomly assign focus
        focus = random.choice(SUBTITLE_FOCUS_AREAS)
        
        print(f"{i}. {material_name.upper()} ({category})")
        print("-" * 100)
        print(f"   Current: {current_subtitle}")
        print(f"   Focus:   {focus['name']}")
        print(f"   → Will generate subtitle emphasizing: {focus['id'].replace('_', ' ')}")
        print()
    
    print("=" * 100)
    print("NEXT STEPS")
    print("=" * 100)
    print()
    print("To regenerate all 132 subtitles with these focus areas, run:")
    print("  python3 scripts/regenerate_subtitles.py")
    print()
    print("This will:")
    print("  ✅ Randomly assign one of 10 focus areas to each material")
    print("  ✅ Generate professional, voice-free subtitles")
    print("  ✅ Validate against voice markers")
    print("  ✅ Create backup before saving")
    print("  ✅ Track focus area distribution")
    print()

if __name__ == '__main__':
    main()
