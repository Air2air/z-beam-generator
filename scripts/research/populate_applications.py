#!/usr/bin/env python3
"""
Populate applications/data.yaml with AI-researched content.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.research.content_researcher import ContentResearcher

# Applications to research (from applications/data.yaml)
APPLICATIONS = [
    # Existing basic applications
    {"name": "Aerospace Component Cleaning", "industry": "Aerospace", "category": "manufacturing"},
    {"name": "Automotive Parts Cleaning", "industry": "Automotive", "category": "manufacturing"},
    {"name": "Marine Equipment Maintenance", "industry": "Marine", "category": "maintenance"},
    {"name": "Industrial Equipment Restoration", "industry": "Manufacturing", "category": "maintenance"},
    {"name": "Electronics Manufacturing", "industry": "Electronics", "category": "manufacturing"},
    {"name": "Medical Device Cleaning", "industry": "Healthcare", "category": "manufacturing"},
    {"name": "Construction Equipment Maintenance", "industry": "Construction", "category": "maintenance"},
    {"name": "Rail Transport Maintenance", "industry": "Transportation", "category": "maintenance"},
    {"name": "Power Generation Equipment", "industry": "Energy", "category": "maintenance"},
    {"name": "Petrochemical Equipment", "industry": "Energy", "category": "maintenance"},
    {"name": "Mining Equipment Maintenance", "industry": "Mining", "category": "maintenance"},
    {"name": "Food Processing Equipment", "industry": "Food & Beverage", "category": "manufacturing"},
    
    # New detailed applications
    {"name": "Battery Manufacturing", "industry": "Energy Storage", "category": "manufacturing"},
    {"name": "Pharmaceutical Manufacturing", "industry": "Healthcare", "category": "manufacturing"},
    {"name": "Wind Turbine Maintenance", "industry": "Renewable Energy", "category": "maintenance"},
    {"name": "Semiconductor Wafer Processing", "industry": "Electronics", "category": "manufacturing"},
    {"name": "3D Printing Post-Processing", "industry": "Additive Manufacturing", "category": "manufacturing"},
    {"name": "Tool & Die Maintenance", "industry": "Manufacturing", "category": "maintenance"},
    {"name": "Automotive Restoration", "industry": "Automotive", "category": "restoration"},
    {"name": "Architectural Conservation", "industry": "Historic Preservation", "category": "restoration"},
    {"name": "Art Conservation", "industry": "Cultural Heritage", "category": "restoration"},
    {"name": "Archaeological Artifacts", "industry": "Cultural Heritage", "category": "restoration"},
    {"name": "Nuclear Decommissioning", "industry": "Energy", "category": "maintenance"},
    {"name": "Defense Systems Maintenance", "industry": "Defense", "category": "maintenance"},
    {"name": "Telecommunications Infrastructure", "industry": "Telecommunications", "category": "maintenance"},
    {"name": "Shipbuilding & Repair", "industry": "Marine", "category": "manufacturing"},
    {"name": "Pipeline Maintenance", "industry": "Energy", "category": "maintenance"},
    {"name": "HVAC Systems Cleaning", "industry": "Building Services", "category": "maintenance"},
    {"name": "Solar Panel Maintenance", "industry": "Renewable Energy", "category": "maintenance"},
    {"name": "Printed Circuit Board Manufacturing", "industry": "Electronics", "category": "manufacturing"},
]


def main():
    """Research all applications and save to YAML."""
    print(f"\n🔬 Starting Application Research")
    print(f"   Applications to research: {len(APPLICATIONS)}")
    
    researcher = ContentResearcher()
    results = []
    
    for i, app_data in enumerate(APPLICATIONS, 1):
        name = app_data['name']
        industry = app_data['industry']
        category = app_data['category']
        
        print(f"\n📝 [{i}/{len(APPLICATIONS)}] Researching: {name}")
        print(f"   Industry: {industry}")
        print(f"   Category: {category}")
        
        try:
            result = researcher.research_application(name, industry, category)
            results.append(result)
            print(f"   ✅ Success: {len(result.get('use_cases', []))} use cases, {len(result.get('common_materials', []))} materials")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            # Create basic placeholder
            results.append({
                'name': name,
                'category': category,
                'industry': industry,
                'description': f'Laser cleaning application in {industry}',
                'use_cases': [],
                'common_materials': [],
                'common_contaminants': [],
                'process_requirements': {
                    'automation_level': 'medium',
                    'throughput': 'medium',
                    'precision_level': 'medium',
                    'quality_standards': []
                },
                'benefits': [],
                'challenges': []
            })
    
    # Build complete data structure
    data = {
        'applications': results,
        '_metadata': {
            'version': '2.1.0',
            'last_updated': '2025-10-30',
            'description': 'Laser cleaning applications with AI-researched content',
            'total_applications': len(results),
            'ai_researched': True
        }
    }
    
    # Save to file
    output_path = project_root / 'applications' / 'data.yaml'
    print(f"\n💾 Saving to: {output_path}")
    
    with open(output_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    print(f"\n✅ Complete! Researched {len(results)} applications")
    print(f"   File: {output_path}")
    print(f"   Size: {output_path.stat().st_size:,} bytes")


if __name__ == '__main__':
    main()
