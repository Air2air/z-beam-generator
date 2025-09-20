"""
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
        'metadata': data.get('metadata', {}),
        'material_index': data.get('material_index', {})  # Preserve material_index
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
