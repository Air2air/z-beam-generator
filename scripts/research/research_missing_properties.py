#!/usr/bin/env python3
"""
Research missing properties for materials using Grok API

This script researches specific missing properties (laserDamageThreshold, ablationThreshold, etc.)
identified by the data gaps analysis.
"""

import yaml
import os
import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.api.client_factory import create_api_client
from shared.api.client import GenerationRequest


def research_property(api_client, material_name: str, category: str, property_name: str) -> dict:
    """Research a single property for a material"""
    
    # Property-specific prompts
    prompts = {
        'laserDamageThreshold': f"""Research the laser damage threshold (LIDT) for {material_name} ({category}) used in industrial laser cleaning applications.

The laser damage threshold is the maximum laser fluence (energy density) that the material can withstand without permanent damage. This is critical for determining safe operating parameters.

Provide a scientifically accurate value for:
- laserDamageThreshold: Maximum laser fluence before damage (J/cm², typically 0.1-50 for industrial cleaning)

Consider:
- Typical laser wavelengths: 355nm (UV), 532nm (green), 1064nm (IR)
- Pulse duration: nanosecond regime (10-100 ns)
- Material thermal and mechanical properties
- Surface condition and contamination effects

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "value": <number>,
  "unit": "J/cm²",
  "confidence": <integer 0-100>
}}

Base the value on materials science literature and laser damage databases.""",

        'ablationThreshold': f"""Research the ablation threshold for {material_name} ({category}) in industrial laser cleaning applications.

The ablation threshold is the minimum laser fluence required to initiate material removal from the surface. This is essential for cleaning without substrate damage.

Provide a scientifically accurate value for:
- ablationThreshold: Minimum fluence for material removal (J/cm², typically 0.05-10)

Consider:
- Material's thermal properties (conductivity, diffusivity)
- Bond energies and vaporization temperature
- Surface absorption characteristics
- Typical contaminants (oxides, organics, coatings)

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "value": <number>,
  "unit": "J/cm²",
  "confidence": <integer 0-100>
}}

Base the value on peer-reviewed literature and laser processing data.""",

        'thermalDiffusivity': f"""Research the thermal diffusivity for {material_name} ({category}).

Thermal diffusivity measures how quickly heat spreads through a material. It's calculated as: α = k/(ρ×Cp)
where k=thermal conductivity, ρ=density, Cp=specific heat capacity.

Provide a scientifically accurate value for:
- thermalDiffusivity: Rate of heat propagation (m²/s, typically 10⁻⁷ to 10⁻⁴)

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "value": <number>,
  "unit": "m²/s",
  "confidence": <integer 0-100>
}}

Use scientific notation (e.g., 2.1e-07 for 2.1×10⁻⁷) and base on thermal property databases.""",

        'fractureToughness': f"""Research the fracture toughness for {material_name} ({category}).

Fracture toughness (K_IC) measures resistance to crack propagation, important for preventing damage during laser processing.

Provide a scientifically accurate value for:
- fractureToughness: Critical stress intensity factor (MPa√m, typically 0.5-150)

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "value": <number>,
  "unit": "MPa√m",
  "confidence": <integer 0-100>
}}

Base on materials property databases and scientific literature.""",

        'oxidationResistance': f"""Research the oxidation resistance for {material_name} ({category}).

Oxidation resistance indicates how well a material resists oxide formation at elevated temperatures during laser processing.
Expressed as a dimensionless factor from 0 (poor) to 1 (excellent).

Provide a scientifically accurate value for:
- oxidationResistance: Resistance to oxidation (dimensionless, 0-1)

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "value": <number>,
  "unit": "",
  "confidence": <integer 0-100>
}}

Base on high-temperature oxidation behavior and corrosion resistance data.""",

        'electricalResistivity': f"""Research the electrical resistivity for {material_name} ({category}).

Electrical resistivity measures how strongly a material opposes the flow of electric current. Important for laser processing applications where electrical properties matter.

Provide a scientifically accurate value for:
- electricalResistivity: Resistance to electrical current (Ω·m, typically 10⁻⁸ to 10¹⁵)

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "value": <number>,
  "unit": "Ω·m",
  "confidence": <integer 0-100>
}}

Use scientific notation (e.g., 1.7e-08) and base on electrical property databases.""",

        'vaporPressure': f"""Research the vapor pressure for {material_name} ({category}).

Vapor pressure at operating temperature is critical for understanding material vaporization during laser processing.

Provide a scientifically accurate value for:
- vaporPressure: Vapor pressure at typical operating temperatures (Pa, typically 0.001-10000)

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "value": <number>,
  "unit": "Pa",
  "confidence": <integer 0-100>
}}

Base on thermodynamic data and vapor pressure curves."""
    }
    
    if property_name not in prompts:
        print(f"      ⚠️  No prompt defined for property: {property_name}")
        return {}
    
    try:
        request = GenerationRequest(
            prompt=prompts[property_name],
            system_prompt="You are a materials science expert. Provide accurate, scientifically-based property values. Return ONLY valid JSON with no markdown formatting.",
            max_tokens=500,
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
        
        property_data = json.loads(response_text)
        
        # Add source metadata
        property_data['source'] = 'ai_research'
        
        return property_data
        
    except Exception as e:
        print(f"      ❌ API Error: {str(e)}")
        return {}


def get_materials_missing_property(materials_data: dict, property_name: str) -> List[Tuple[str, str]]:
    """Get list of (material_name, category) tuples missing a specific property"""
    missing = []
    
    for material_name, material_data in materials_data.items():
        if 'properties' not in material_data:
            continue
            
        mat_props = material_data['properties']
        category = material_data.get('category', 'unknown')
        
        # Check both property groups
        found = False
        for group_name in ['material_characteristics', 'laser_material_interaction']:
            if group_name in mat_props:
                if property_name in mat_props[group_name]:
                    found = True
                    break
        
        if not found:
            missing.append((material_name, category))
    
    return missing


def main():
    print("=" * 80)
    print("RESEARCH: MISSING MATERIAL PROPERTIES")
    print("=" * 80)
    
    # Load Materials.yaml
    materials_file = Path('data/materials/Materials.yaml')
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    all_materials = data.get('materials', {})
    
    # Properties to research (in order of priority)
    properties_to_research = [
        'laserDamageThreshold',
        'ablationThreshold',
        'thermalDiffusivity',
        'fractureToughness',
        'oxidationResistance',
        'electricalResistivity',
        'vaporPressure'
    ]
    
    # Allow targeting specific property from command line
    if len(sys.argv) > 1:
        property_filter = sys.argv[1]
        if property_filter in properties_to_research:
            properties_to_research = [property_filter]
            print(f"\n🎯 Targeting property: {property_filter}")
        else:
            print(f"⚠️  Unknown property: {property_filter}")
            print(f"Available: {', '.join(properties_to_research)}")
            sys.exit(1)
    
    # Initialize API client
    try:
        api_client = create_api_client('grok')
        print("✅ Grok API client initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize API client: {e}")
        sys.exit(1)
    
    total_updated = 0
    total_properties_added = 0
    
    for property_name in properties_to_research:
        print(f"\n{'='*80}")
        print(f"RESEARCHING: {property_name}")
        print(f"{'='*80}")
        
        # Find materials missing this property
        missing_materials = get_materials_missing_property(all_materials, property_name)
        
        if not missing_materials:
            print(f"✅ All materials have {property_name}")
            continue
        
        print(f"Found {len(missing_materials)} materials missing {property_name}\n")
        
        updated_count = 0
        
        for material_name, category in missing_materials:
            print(f"  Researching: {material_name} ({category})...", end=' ')
            
            try:
                property_data = research_property(api_client, material_name, category, property_name)
                
                if not property_data:
                    print("⚠️  No data")
                    continue
                
                # Determine which property group this belongs to
                if property_name in ['laserDamageThreshold', 'ablationThreshold', 'vaporPressure']:
                    group_name = 'laser_material_interaction'
                else:
                    group_name = 'material_characteristics'
                
                # Ensure structure exists
                if 'properties' not in all_materials[material_name]:
                    all_materials[material_name]['properties'] = {}
                
                mat_props = all_materials[material_name]['properties']
                
                if group_name not in mat_props:
                    if group_name == 'laser_material_interaction':
                        mat_props[group_name] = {
                            'label': 'Laser-Material Interaction',
                            'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds'
                        }
                    else:
                        mat_props[group_name] = {
                            'label': 'Material Characteristics',
                            'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
                        }
                
                # Add the property
                mat_props[group_name][property_name] = property_data
                
                print(f"✅ {property_data['value']} {property_data['unit']} (confidence: {property_data['confidence']}%)")
                updated_count += 1
                total_properties_added += 1
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
        
        print(f"\n✅ Updated {updated_count} materials with {property_name}")
        total_updated += updated_count
    
    print(f"\n{'='*80}")
    print(f"RESEARCH COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Total properties added: {total_properties_added}")
    print(f"✅ Total material updates: {total_updated}")
    
    # Save updated Materials.yaml
    if total_updated > 0:
        backup_file = materials_file.parent / 'Materials_backup_before_property_research.yaml'
        with open(materials_file, 'r') as f:
            backup_content = f.read()
        with open(backup_file, 'w') as bf:
            bf.write(backup_content)
        print(f"\n💾 Backup created: {backup_file}")
        
        with open(materials_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
        print(f"💾 Saved to {materials_file}")
        
        return total_updated
    else:
        print(f"\n⚠️  No updates to save")
        return 0


if __name__ == '__main__':
    updated = main()
    sys.exit(0 if updated > 0 else 1)
