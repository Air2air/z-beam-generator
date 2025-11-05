#!/usr/bin/env python3
"""
Research laser_material_interaction properties for materials using Grok API

This script directly calls Grok API to research laser-specific properties
that aren't in the standard PropertyValueResearcher registry.
"""

import yaml
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.api.client_factory import create_api_client
from shared.api.client import GenerationRequest

def research_lmi_properties(api_client, material_name: str, category: str) -> dict:
    """Research laser_material_interaction properties for a material"""
    
    prompt = f"""Research laser-material interaction properties for {material_name} ({category}) used in industrial laser cleaning applications.

Provide scientifically accurate values for these 7 REQUIRED properties:

1. absorptivity - Fraction of laser energy absorbed (dimensionless, typically 0.01-0.95)
2. absorptionCoefficient - Optical absorption coefficient (m⁻¹, typically 10⁴-10⁸)
3. laserDamageThreshold - Laser-induced damage threshold (J/cm², typically 0.1-50)
4. thermalShockResistance - Thermal shock resistance parameter (MW/m, typically 0.5-5)
5. reflectivity - Fraction of laser energy reflected (dimensionless, typically 0.05-0.95)
6. thermalDestructionPoint - Temperature causing material degradation (K, typically 400-3700)
7. vaporPressure - Vapor pressure at operating temperature (Pa, typically 0.001-10000)

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "absorptivity": {{"value": <number>, "unit": "dimensionless", "min": <number>, "max": <number>}},
  "absorptionCoefficient": {{"value": <number>, "unit": "m⁻¹", "min": <number>, "max": <number>}},
  "laserDamageThreshold": {{"value": <number>, "unit": "J/cm²", "min": <number>, "max": <number>}},
  "thermalShockResistance": {{"value": <number>, "unit": "MW/m", "min": <number>, "max": <number>}},
  "reflectivity": {{"value": <number>, "unit": "dimensionless", "min": <number>, "max": <number>}},
  "thermalDestructionPoint": {{"value": <number>, "unit": "K", "min": <number>, "max": <number>}},
  "vaporPressure": {{"value": <number>, "unit": "Pa", "min": <number>, "max": <number>}}
}}

Use realistic values for {material_name}. Base min/max on material science literature."""

    try:
        request = GenerationRequest(
            prompt=prompt,
            system_prompt="You are a materials science expert. Provide accurate, scientifically-based property values for laser cleaning applications. Return ONLY valid JSON with no markdown formatting.",
            max_tokens=1500,
            temperature=0.3
        )
        response = api_client.generate(request)
        
        # Parse response
        response_text = response.content.strip() if hasattr(response, 'content') else str(response).strip()
        
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        properties = json.loads(response_text)
        
        # Add source metadata
        for prop_name, prop_data in properties.items():
            prop_data['source'] = 'ai_research'
        
        return properties
        
    except Exception as e:
        print(f"      ❌ API Error: {str(e)}")
        return {}


def main():
    print("=" * 70)
    print("RESEARCH: LASER_MATERIAL_INTERACTION PROPERTIES")
    print("=" * 70)
    
    # Materials to research
    materials_to_research = [
        ('Stainless Steel', 'metal'),
        ('Tantalum', 'metal'),
        ('Tin', 'metal'),
        ('Titanium', 'metal'),
        ('Tool Steel', 'metal'),
        ('Tungsten', 'metal'),
        ('Vanadium', 'metal'),
        ('Zinc', 'metal'),
        ('Zirconium', 'metal'),
        ('Terbium', 'rare-earth'),
        ('Yttrium', 'rare-earth')
    ]
    
    print(f"\nTarget: {len(materials_to_research)} materials")
    print(f"Properties per material: 7 (core laser interaction properties)\n")
    
    # Initialize API client
    try:
        api_client = create_api_client('grok')
        print("✅ Grok API client initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize API client: {e}")
        sys.exit(1)
    
    # Load current materials.yaml
    materials_file = Path('materials/data/materials.yaml')
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    all_materials = data['materials']
    updated_count = 0
    total_properties_added = 0
    
    for material_name, category in materials_to_research:
        print(f"\n{'='*70}")
        print(f"Researching: {material_name} ({category})")
        print(f"{'='*70}")
        
        if material_name not in all_materials:
            print(f"   ❌ Material not found in database")
            continue
        
        try:
            # Research properties via API
            properties = research_lmi_properties(api_client, material_name, category)
            
            if not properties:
                print(f"   ⚠️  No properties researched")
                continue
            
            # Initialize materialProperties if needed
            if 'materialProperties' not in all_materials[material_name]:
                all_materials[material_name]['materialProperties'] = {}
            
            mat_props = all_materials[material_name]['materialProperties']
            
            # Create or update laser_material_interaction
            if 'laser_material_interaction' not in mat_props:
                mat_props['laser_material_interaction'] = {
                    'label': 'Laser-Material Interaction',
                    'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds',
                    'percentage': 40.0
                }
            
            lmi = mat_props['laser_material_interaction']
            
            # Add researched properties
            properties_added = 0
            for prop_name, prop_data in properties.items():
                lmi[prop_name] = prop_data
                properties_added += 1
                print(f"   ✅ {prop_name}: {prop_data['value']} {prop_data['unit']}")
            
            print(f"\n   Total: {properties_added} properties added")
            total_properties_added += properties_added
            updated_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*70}")
    print(f"RESEARCH COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Materials updated: {updated_count}/{len(materials_to_research)}")
    print(f"✅ Properties added: {total_properties_added}")
    
    # Save updated materials.yaml
    if updated_count > 0:
        backup_file = materials_file.parent / 'materials_backup_before_lmi_research.yaml'
        with open(materials_file, 'r') as f:
            backup_content = f.read()
        with open(backup_file, 'w') as bf:
            bf.write(backup_content)
        print(f"\n💾 Backup created: {backup_file}")
        
        with open(materials_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
        print(f"💾 Saved to {materials_file}")
        
        # Return success for further processing
        return updated_count
    else:
        print(f"\n⚠️  No updates to save")
        return 0


if __name__ == '__main__':
    updated = main()
    sys.exit(0 if updated > 0 else 1)
