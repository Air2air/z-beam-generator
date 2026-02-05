#!/usr/bin/env python3
"""
Populate page_title fields in source data with correct domain endings.
Implements the title format requirements directly without API calls.
"""

import sys
import os
import yaml
from pathlib import Path

def main():
    """Generate proper page_title values for all domains."""
    
    domains_config = [
        ('materials', 'data/materials/Materials.yaml', 'Laser Cleaning'),
        ('contaminants', 'data/contaminants/Contaminants.yaml', 'Contaminants'),
        ('settings', 'data/settings/Settings.yaml', 'Settings'),
        ('compounds', 'data/compounds/Compounds.yaml', 'Compound')
    ]
    
    print("🎯 Updating page_title fields in source data...")
    print("   Materials: ends with 'Laser Cleaning'")
    print("   Contaminants: ends with 'Contaminants'")
    print("   Settings: ends with 'Settings'")
    print("   Compounds: ends with 'Compound'")
    
    total_processed = 0
    
    for domain, data_path, ending in domains_config:
        print(f"\n📋 Processing {domain}...")
        
        try:
            # Load data file
            with open(data_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            items = data.get(domain, {})
            processed = 0
            
            for item_id, item_data in items.items():
                # Get base name
                name = item_data.get('name') or item_data.get('title') or item_id.replace('-', ' ').title()
                
                # Clean existing endings if present to avoid duplication
                clean_name = name
                for end in ['Laser Cleaning', 'Contaminants', 'Settings', 'Compound']:
                    if clean_name.endswith(end):
                        clean_name = clean_name[:-len(end)].strip()
                
                # Create proper title with required ending
                page_title = f"{clean_name} {ending}".strip()
                
                # Update the item
                item_data['page_title'] = page_title
                processed += 1
            
            # Save updated data
            with open(data_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"   ✅ Updated {processed} items with proper page_title")
            total_processed += processed
                
        except Exception as e:
            print(f"   💥 Error in {domain}: {e}")
    
    print(f"\n🎉 Page title update complete!")
    print(f"   {total_processed} items updated across all domains")
    print("   Source YAML files now have proper page_title fields.")
    print("   Next: Run --export to apply changes to frontmatter.")

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()