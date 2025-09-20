#!/usr/bin/env python3
"""
Generate research checklist for materials.yaml validation.
"""

import yaml
import csv
from datetime import datetime

def generate_research_checklist():
    """Generate comprehensive research checklist for all materials."""
    
    # Load materials data
    with open('data/materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    checklist = []
    
    for category, cat_data in data.get('materials', {}).items():
        for item in cat_data.get('items', []):
            name = item.get('name', 'Unknown')
            
            # Chemical verification needed
            chemical_research = {
                'Material': name,
                'Category': category,
                'Current_Symbol': item.get('symbol', 'MISSING'),
                'Current_Formula': item.get('formula', 'MISSING'),
                'Research_Status': 'PENDING',
                'NIST_Verified': '',
                'Source_URL': '',
                'Expert_Verified': '',
                'Notes': '',
                'Recommended_Action': ''
            }
            checklist.append(chemical_research)
    
    # Save to CSV for easy research tracking
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'materials_research_checklist_{timestamp}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        if checklist:
            fieldnames = checklist[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in checklist:
                writer.writerow(item)
    
    print(f"📋 Research checklist generated: {filename}")
    print(f"   Total materials to research: {len(checklist)}")
    
    # Summary by category
    category_counts = {}
    for item in checklist:
        cat = item['Category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("\n📊 Research breakdown by category:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count} materials")
    
    # Identify priority items (missing critical fields)
    missing_symbols = [item for item in checklist if item['Current_Symbol'] == 'MISSING']
    missing_formulas = [item for item in checklist if item['Current_Formula'] == 'MISSING']
    
    print(f"\n🚨 Priority research needed:")
    print(f"   Missing symbols: {len(missing_symbols)}")
    print(f"   Missing formulas: {len(missing_formulas)}")
    
    if missing_symbols:
        print("\n   Materials missing symbols:")
        for item in missing_symbols[:10]:  # Show first 10
            print(f"     • {item['Material']} ({item['Category']})")
        if len(missing_symbols) > 10:
            print(f"     ... and {len(missing_symbols) - 10} more")
    
    return filename

if __name__ == "__main__":
    generate_research_checklist()
