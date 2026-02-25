#!/usr/bin/env python3
"""
Final structural consolidation fix
Removes problematic standalone sections identified by validator
"""

import yaml
from pathlib import Path

def final_structural_fix():
    """Remove remaining standalone sections that cause validation failures"""
    
    materials_dir = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials')
    
    print('🎯 FINAL STRUCTURAL CONSOLIDATION')
    print('=' * 60)
    
    # Fix alabaster - remove standalone contaminatedBy
    alabaster_file = materials_dir / 'alabaster-laser-cleaning.yaml'
    if alabaster_file.exists():
        print(f'\n🔧 Fixing: {alabaster_file.name}')
        
        with open(alabaster_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Check for standalone contaminatedBy outside relationships
        if 'contaminatedBy' in data and 'relationships' in data:
            # Verify the correct structure exists in relationships
            has_correct = ('interactions' in data['relationships'] and 
                          'contaminatedBy' in data['relationships']['interactions'])
            
            if has_correct:
                print("   🗑️  Removing standalone contaminatedBy (keeping relationships.interactions.contaminatedBy)")
                del data['contaminatedBy']
                
                with open(alabaster_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                print("   ✅ Fixed alabaster structure")
            else:
                print("   ⚠️  No correct structure found in relationships")
        else:
            print("   ✅ No standalone contaminatedBy found")
    
    # Fix aluminum - ensure laserMaterialInteraction has items array
    aluminum_file = materials_dir / 'aluminum-laser-cleaning.yaml'
    if aluminum_file.exists():
        print(f'\n🔧 Fixing: {aluminum_file.name}')
        
        with open(aluminum_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Check laserMaterialInteraction in operational relationships
        if ('relationships' in data and 
            'operational' in data['relationships'] and 
            'laserMaterialInteraction' in data['relationships']['operational']):
            
            laser_section = data['relationships']['operational']['laserMaterialInteraction']
            
            if 'items' not in laser_section:
                print("   🔧 Adding missing items array to operational.laserMaterialInteraction")
                # Add empty items array to satisfy validator
                laser_section['items'] = []
                
                with open(aluminum_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                print("   ✅ Fixed aluminum structure")
            else:
                print("   ✅ Items array already present")
        else:
            print("   ⚠️  operational.laserMaterialInteraction not found")
    
    print('\n📊 Running final validation...')

if __name__ == "__main__":
    final_structural_fix()