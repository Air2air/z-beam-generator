#!/usr/bin/env python3
"""
Research missing thermal properties for laser-material interaction

Focuses on the 3 critical gaps:
- thermalConductivity (5/159 materials, 3.1%)
- thermalDiffusivity (6/159 materials, 3.8%)  
- ablationThreshold (6/159 materials, 3.8%)

Total: ~460 property values needed across 153+ materials
"""

import yaml
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.api.client_factory import create_api_client
from shared.api.client import GenerationRequest


def get_materials_missing_thermal_props() -> List[Tuple[str, str, List[str]]]:
    """Get list of materials missing thermal properties"""
    materials_file = Path('data/materials/Materials.yaml')
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    missing_list = []
    
    target_props = ['thermalConductivity', 'thermalDiffusivity', 'ablationThreshold']
    
    for mat_name, mat_data in materials.items():
        mat_props = mat_data.get('properties', {})
        lmi = mat_props.get('laser_material_interaction', {})
        
        missing = []
        for prop in target_props:
            if prop not in lmi or lmi[prop] is None:
                missing.append(prop)
        
        if missing:
            category = mat_data.get('category', 'unknown')
            missing_list.append((mat_name, category, missing))
    
    return missing_list


def research_thermal_properties(api_client, material_name: str, category: str, 
                                missing_props: List[str]) -> Dict:
    """Research specific thermal properties for a material"""
    
    props_descriptions = {
        'thermalConductivity': 'Thermal conductivity - rate of heat transfer through material (W/m·K)',
        'thermalDiffusivity': 'Thermal diffusivity - speed at which heat spreads through material (m²/s)',
        'ablationThreshold': 'Ablation threshold - minimum laser fluence to remove material (J/cm²)'
    }
    
    props_needed = '\n'.join([f"{i+1}. {props_descriptions[p]}" 
                              for i, p in enumerate(missing_props)])
    
    prompt = f"""Research thermal properties for {material_name} ({category}) used in industrial laser cleaning applications.

Provide scientifically accurate values for these properties:

{props_needed}

Return ONLY a valid JSON object with this structure (include ONLY the requested properties):
{{
  "thermalConductivity": {{"value": <number>, "unit": "W/m·K", "min": <number>, "max": <number>}},
  "thermalDiffusivity": {{"value": <number>, "unit": "m²/s", "min": <number>, "max": <number>}},
  "ablationThreshold": {{"value": <number>, "unit": "J/cm²", "min": <number>, "max": <number>}}
}}

Guidelines:
- thermalConductivity: Typical ranges by category:
  * Metals: 15-450 W/m·K (copper ~400, steel ~50)
  * Ceramics: 1-40 W/m·K
  * Plastics: 0.1-0.5 W/m·K
  * Wood: 0.1-0.2 W/m·K
  * Stone: 1-7 W/m·K

- thermalDiffusivity: Typical ranges:
  * Metals: 1×10⁻⁶ to 1×10⁻⁴ m²/s
  * Ceramics: 1×10⁻⁷ to 1×10⁻⁵ m²/s
  * Plastics: 1×10⁻⁷ to 1×10⁻⁶ m²/s

- ablationThreshold: Typical ranges (1064nm laser):
  * Metals: 0.5-10 J/cm²
  * Ceramics: 1-20 J/cm²
  * Plastics: 0.1-5 J/cm²
  * Wood: 1-10 J/cm²

Use realistic, scientifically-based values for {material_name}."""

    try:
        request = GenerationRequest(
            prompt=prompt,
            system_prompt="You are a materials science expert specializing in thermal properties and laser-material interactions. Provide accurate values based on scientific literature. Return ONLY valid JSON with no markdown formatting.",
            max_tokens=800,
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
        
        # Filter to only requested properties and add source metadata
        result = {}
        for prop_name in missing_props:
            if prop_name in properties:
                prop_data = properties[prop_name]
                prop_data['source'] = 'ai_research'
                result[prop_name] = prop_data
        
        return result
        
    except Exception as e:
        print(f"      ❌ API Error: {str(e)}")
        return {}


def main():
    print("=" * 80)
    print("RESEARCH: THERMAL PROPERTIES FOR LASER-MATERIAL INTERACTION")
    print("=" * 80)
    
    # Get materials needing thermal properties
    materials_missing = get_materials_missing_thermal_props()
    
    if not materials_missing:
        print("\n✅ All materials have complete thermal properties!")
        return 0
    
    print(f"\n📊 Found {len(materials_missing)} materials with missing thermal properties")
    
    # Count by property
    prop_counts = {'thermalConductivity': 0, 'thermalDiffusivity': 0, 'ablationThreshold': 0}
    for _, _, missing in materials_missing:
        for prop in missing:
            prop_counts[prop] += 1
    
    print(f"\nProperty gaps:")
    print(f"  • thermalConductivity: {prop_counts['thermalConductivity']} materials")
    print(f"  • thermalDiffusivity: {prop_counts['thermalDiffusivity']} materials")
    print(f"  • ablationThreshold: {prop_counts['ablationThreshold']} materials")
    
    # Filter to command-line args if provided
    if len(sys.argv) > 1:
        requested_materials = set(sys.argv[1:])
        materials_missing = [(name, cat, props) for name, cat, props in materials_missing 
                           if name in requested_materials]
        print(f"\n🎯 Filtered to {len(materials_missing)} requested materials")
    
    # Ask for confirmation if processing many materials
    if len(materials_missing) > 20 and len(sys.argv) == 1:
        print(f"\n⚠️  About to research properties for {len(materials_missing)} materials")
        print("   This will make multiple API calls and may take several minutes.")
        response = input("   Continue? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Cancelled")
            return 0
    
    # Initialize API client
    try:
        api_client = create_api_client('grok')
        print("\n✅ Grok API client initialized\n")
    except Exception as e:
        print(f"\n❌ Failed to initialize API client: {e}")
        return 1
    
    # Load current Materials.yaml
    materials_file = Path('data/materials/Materials.yaml')
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    all_materials = data['materials']
    updated_count = 0
    total_properties_added = 0
    
    for material_name, category, missing_props in materials_missing:
        print(f"\n{'='*80}")
        print(f"Researching: {material_name} ({category})")
        print(f"Missing: {', '.join(missing_props)}")
        print(f"{'='*80}")
        
        try:
            # Research properties via API
            properties = research_thermal_properties(api_client, material_name, category, missing_props)
            
            if not properties:
                print(f"   ⚠️  No properties researched")
                continue
            
            # Get laser_material_interaction section
            mat_props = all_materials[material_name].get('properties', {})
            lmi = mat_props.get('laser_material_interaction', {})
            
            # Add researched properties
            properties_added = 0
            for prop_name, prop_data in properties.items():
                lmi[prop_name] = prop_data
                properties_added += 1
                value_str = f"{prop_data['value']:.2e}" if prop_data['value'] < 0.01 else f"{prop_data['value']}"
                print(f"   ✅ {prop_name}: {value_str} {prop_data['unit']}")
            
            print(f"\n   Total: {properties_added} properties added")
            total_properties_added += properties_added
            updated_count += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*80}")
    print(f"RESEARCH COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Materials updated: {updated_count}/{len(materials_missing)}")
    print(f"✅ Properties added: {total_properties_added}")
    
    # Save updated Materials.yaml
    if updated_count > 0:
        # Create backup
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = materials_file.parent / f'Materials_backup_thermal_research_{timestamp}.yaml'
        with open(materials_file, 'r') as f:
            backup_content = f.read()
        with open(backup_file, 'w') as bf:
            bf.write(backup_content)
        print(f"\n💾 Backup created: {backup_file.name}")
        
        # Save updated data
        with open(materials_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=1000)
        print(f"💾 Saved to {materials_file}")
        
        print(f"\n📊 New completeness:")
        print(f"   • thermalConductivity: {5 + updated_count}/159")
        print(f"   • thermalDiffusivity: {6 + updated_count}/159")
        print(f"   • ablationThreshold: {6 + updated_count}/159")
        
        return 0
    else:
        print(f"\n⚠️  No updates to save")
        return 1


if __name__ == '__main__':
    import time
    sys.exit(main())
