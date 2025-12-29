#!/usr/bin/env python3
"""
Populate component_summary field for all Settings.
This field becomes section_description in relationships and provides
a brief explanation of the laser parameter settings for each material.
"""

import yaml
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.api.client_factory import APIClientFactory
from shared.api.client import GenerationRequest

def load_settings():
    """Load Settings.yaml"""
    with open('data/settings/Settings.yaml', 'r') as f:
        return yaml.safe_load(f)

def save_settings(data):
    """Save Settings.yaml"""
    with open('data/settings/Settings.yaml', 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def generate_component_summary(material_name, machine_settings, api_client):
    """Generate concise component summary for laser settings"""
    
    # Extract key parameters
    power = machine_settings.get('power', {}).get('value', 'N/A')
    wavelength = machine_settings.get('wavelength', {}).get('value', 'N/A')
    pulse_width = machine_settings.get('pulseWidth', {}).get('value', 'N/A')
    
    prompt = f"""Write a single concise sentence (20-30 words) explaining the laser parameter settings for cleaning {material_name}.

Current settings:
- Power: {power} W
- Wavelength: {wavelength} nm
- Pulse width: {pulse_width} ns

Focus on: What makes these settings appropriate for this specific material.

Examples:
"These settings balance gentle cleaning with effective contamination removal, using lower power and shorter pulses to protect the delicate surface."
"Higher power and faster scan speeds enable efficient cleaning of durable metals without thermal damage."

Write ONE sentence for {material_name}:"""

    try:
        request = GenerationRequest(
            prompt=prompt,
            temperature=0.7,
            max_tokens=100
        )
        response = api_client.generate(request)
        text = response.content.strip()
        
        # Clean up any quotes or extra formatting
        text = text.strip('"').strip("'").strip()
        
        # Ensure it ends with a period
        if not text.endswith('.'):
            text += '.'
            
        return text
    except Exception as e:
        print(f"  ❌ Error generating summary: {e}")
    return None

def main():
    print("🔬 Populating Settings Component Summaries\n")
    
    api_client = APIClientFactory.create_client('grok')
    data = load_settings()
    settings = data['settings']
    
    updated_count = 0
    total = len(settings)
    
    for idx, (setting_id, setting_data) in enumerate(settings.items(), 1):
        # Extract material name from the ID (e.g., "alabaster-settings" -> "Alabaster")
        material_name = setting_id.replace('-settings', '').replace('-', ' ').title()
        
        print(f"\n📋 [{idx}/{total}] {material_name}")
        
        # Skip if already has component_summary
        if setting_data.get('component_summary'):
            print(f"  ✓ Already has summary")
            continue
        
        # Get machine settings
        machine_settings = setting_data.get('machine_settings', {})
        if not machine_settings:
            print(f"  ⚠️  No machine_settings found")
            continue
        
        # Generate summary
        print(f"  💭 Generating component summary...")
        summary = generate_component_summary(material_name, machine_settings, api_client)
        
        if summary:
            setting_data['component_summary'] = summary
            updated_count += 1
            print(f"  ✅ Summary: {summary[:70]}...")
    
    # Save changes
    if updated_count > 0:
        print(f"\n💾 Saving {updated_count} updated settings...")
        save_settings(data)
        print("✅ Complete!")
        print(f"   Updated: {updated_count}/{total} settings ({100*updated_count//total}%)")
    else:
        print("\n✅ No updates needed - all fields populated!")

if __name__ == '__main__':
    main()
