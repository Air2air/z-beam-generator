#!/usr/bin/env python3
"""
Optimize materials.yaml structure by implementing parameter templates and material index.
This script creates an optimized version while maintaining full backward compatibility.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict

def analyze_and_optimize_materials():
    """Analyze current materials.yaml and create optimized version."""
    
    # Load current materials
    with open('data/materials.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Define common parameter templates based on analysis
    parameter_templates = {
        'standard_fiber_laser': {
            'fluence_threshold': '0.5–5 J/cm²',
            'pulse_duration': '10-100ns',
            'wavelength_optimal': '1064nm',
            'power_range': '20-100W',
            'repetition_rate': '10-50kHz',
            'spot_size': '0.1-2.0mm',
            'laser_type': 'Pulsed fiber laser'
        },
        'standard_fiber_laser_alt': {
            'fluence_threshold': '0.5-5 J/cm²',
            'pulse_duration': '10-100ns',
            'wavelength_optimal': '1064nm',
            'power_range': '20-100W',
            'repetition_rate': '10-50kHz',
            'spot_size': '0.1-2.0mm',
            'laser_type': 'Pulsed fiber laser'
        },
        'high_power_fiber_laser': {
            'fluence_threshold': '1.0–10 J/cm²',
            'pulse_duration': '10-200ns',
            'wavelength_optimal': '1064nm',
            'power_range': '50-200W',
            'repetition_rate': '20-100kHz',
            'spot_size': '0.1-1.0mm',
            'laser_type': 'Pulsed fiber laser'
        },
        'precision_fiber_laser': {
            'fluence_threshold': '0.5-3.0 J/cm²',
            'pulse_duration': '10-50ns',
            'wavelength_optimal': '1064nm',
            'power_range': '20-100W',
            'repetition_rate': '20-100kHz',
            'spot_size': '0.1-1.0mm',
            'laser_type': 'Pulsed fiber laser'
        },
        'high_precision_fiber_laser': {
            'fluence_threshold': '1.0–10 J/cm²',
            'pulse_duration': '10-200ns',
            'wavelength_optimal': '1064nm',
            'power_range': '50-200W',
            'repetition_rate': '20-100kHz',
            'spot_size': '0.05-1.0mm',
            'laser_type': 'Pulsed fiber laser'
        },
        'ultra_precision_fiber_laser': {
            'fluence_threshold': '1.0–10 J/cm²',
            'pulse_duration': '10-50ns',
            'wavelength_optimal': '1064nm',
            'power_range': '50-200W',
            'repetition_rate': '20-100kHz',
            'spot_size': '0.1-1.0mm',
            'laser_type': 'Pulsed fiber laser'
        }
    }
    
    # Define common defaults
    defaults = {
        'surface_treatments': ['Laser Ablation', 'Laser Cleaning', 'Non-Contact Cleaning'],
        'documentation_status': 'generated_frontmatter',
        'last_updated': '2025-08-31'
    }
    
    # Create material index for O(1) lookups
    material_index = {}
    
    # Process materials and optimize
    optimized_materials = {}
    
    for category, cat_data in data['materials'].items():
        optimized_items = []
        
        for i, item in enumerate(cat_data['items']):
            # Add to material index
            material_index[item['name']] = {
                'category': category,
                'index': i
            }
            
            # Optimize the item
            optimized_item = {'name': item['name']}
            
            # Add non-default fields only
            for field in ['author_id', 'complexity', 'difficulty_score', 'category']:
                if field in item:
                    optimized_item[field] = item[field]
            
            # Only add if different from default
            if item.get('documentation_status') != defaults['documentation_status']:
                optimized_item['documentation_status'] = item['documentation_status']
            
            if item.get('last_updated') != defaults['last_updated']:
                optimized_item['last_updated'] = item['last_updated']
            
            # Add formula and symbol if present
            for field in ['formula', 'symbol']:
                if field in item:
                    optimized_item[field] = item[field]
            
            # Match laser parameters to templates
            if 'laser_parameters' in item:
                params = item['laser_parameters']
                template_matched = False
                
                for template_name, template_params in parameter_templates.items():
                    if all(params.get(k) == v for k, v in template_params.items()):
                        optimized_item['laser_parameters_template'] = template_name
                        template_matched = True
                        break
                
                # If no template matches, keep original parameters
                if not template_matched:
                    optimized_item['laser_parameters'] = params
            
            # Applications - keep as is for now
            if 'applications' in item:
                optimized_item['applications'] = item['applications']
            
            # Surface treatments - only add if different from default
            if 'surface_treatments' in item and item['surface_treatments'] != defaults['surface_treatments']:
                optimized_item['surface_treatments'] = item['surface_treatments']
            
            # Industry tags
            if 'industry_tags' in item:
                optimized_item['industry_tags'] = item['industry_tags']
            
            optimized_items.append(optimized_item)
        
        optimized_materials[category] = {
            'description': cat_data['description'],
            'article_type': cat_data['article_type'],
            'processing_priority': cat_data['processing_priority'],
            'items': optimized_items
        }
    
    # Create the optimized structure
    optimized_data = {
        'parameter_templates': parameter_templates,
        'defaults': defaults,
        'material_index': material_index,
        'materials': optimized_materials,
        'metadata': data['metadata']
    }
    
    # Update metadata
    optimized_data['metadata']['optimization_version'] = '1.0'
    optimized_data['metadata']['optimization_date'] = '2025-09-16'
    optimized_data['metadata']['optimization_features'] = [
        'parameter_templates',
        'material_index',
        'default_compression'
    ]
    
    return optimized_data

def create_compatibility_loader():
    """Create a loader that maintains backward compatibility."""
    loader_content = '''"""
Enhanced materials data loader with optimization support.
Maintains full backward compatibility with existing code.
"""

from pathlib import Path
import yaml


def load_materials():
    """Load materials data from YAML file with optimization support."""
    materials_file = Path(__file__).parent / "materials.yaml"

    try:
        with open(materials_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # If optimized format detected, expand it for compatibility
        if 'parameter_templates' in data:
            expanded_data = expand_optimized_materials(data)
            return expanded_data
        
        # Return original format as-is
        return data
    except Exception as e:
        print(f"Error loading materials data: {e}")
        return {"materials": {}}


def expand_optimized_materials(data):
    """Expand optimized materials format to original structure for compatibility."""
    expanded = {
        'materials': {},
        'metadata': data.get('metadata', {})
    }
    
    parameter_templates = data.get('parameter_templates', {})
    defaults = data.get('defaults', {})
    
    for category, cat_data in data['materials'].items():
        expanded_items = []
        
        for item in cat_data['items']:
            expanded_item = item.copy()
            
            # Expand parameter template reference
            if 'laser_parameters_template' in item:
                template_name = item['laser_parameters_template']
                if template_name in parameter_templates:
                    expanded_item['laser_parameters'] = parameter_templates[template_name].copy()
                del expanded_item['laser_parameters_template']
            
            # Apply defaults for missing fields
            for field, default_value in defaults.items():
                if field not in expanded_item:
                    expanded_item[field] = default_value
            
            expanded_items.append(expanded_item)
        
        expanded['materials'][category] = {
            'description': cat_data['description'],
            'article_type': cat_data['article_type'],
            'processing_priority': cat_data['processing_priority'],
            'items': expanded_items
        }
    
    return expanded


def get_material_by_name(material_name, data=None):
    """Fast O(1) material lookup using material index."""
    if data is None:
        data = load_materials()
    
    # Use material index if available (optimized format)
    if 'material_index' in data:
        index_entry = data['material_index'].get(material_name)
        if index_entry:
            category = index_entry['category']
            item_index = index_entry['index']
            return data['materials'][category]['items'][item_index]
    
    # Fallback to linear search (original format)
    for category, cat_data in data['materials'].items():
        for item in cat_data['items']:
            if item['name'] == material_name:
                return item
    
    return None
'''
    
    return loader_content

def main():
    """Main optimization process."""
    print("🔧 Optimizing materials.yaml structure...")
    
    # Analyze and create optimized version
    optimized_data = analyze_and_optimize_materials()
    
    # Calculate optimization statistics
    original_size = Path('data/materials.yaml').stat().st_size
    
    # Write optimized materials.yaml
    with open('data/materials_optimized.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(optimized_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Calculate new size
    optimized_size = Path('data/materials_optimized.yaml').stat().st_size
    size_reduction = ((original_size - optimized_size) / original_size) * 100
    
    print(f"📊 Optimization Results:")
    print(f"   Original size: {original_size:,} bytes")
    print(f"   Optimized size: {optimized_size:,} bytes")
    print(f"   Size reduction: {size_reduction:.1f}%")
    print(f"   Parameter templates: {len(optimized_data['parameter_templates'])}")
    print(f"   Material index entries: {len(optimized_data['material_index'])}")
    
    # Update the loader with compatibility support
    loader_content = create_compatibility_loader()
    with open('data/materials_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(loader_content)
    
    print("\n✅ Optimization complete!")
    print("📁 Files created:")
    print("   - data/materials_optimized.yaml (optimized structure)")
    print("   - data/materials_enhanced.py (enhanced loader with compatibility)")
    
    print("\n🔄 To apply optimization:")
    print("   1. Review data/materials_optimized.yaml")
    print("   2. Replace data/materials.yaml with optimized version")
    print("   3. Replace data/materials.py with enhanced loader")

if __name__ == "__main__":
    main()
