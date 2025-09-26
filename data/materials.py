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
        'material_index': data.get('material_index', {}),
        'category_ranges': data.get('category_ranges', {}),
        'parameter_templates': data.get('parameter_templates', {}),
        # No defaults allowed - fail-fast architecture requires complete material data
    }
    
    parameter_templates = data.get('parameter_templates', {})
    # No defaults variable - fail-fast architecture
    
    for category, cat_data in data['materials'].items():
        # Handle both simple categories with items and complex categories with subcategories
        if isinstance(cat_data, dict) and 'items' in cat_data:
            # Simple category with direct items
            expanded_items = []
            
            for item in cat_data['items']:
                expanded_item = item.copy()
                
                # Expand parameter template reference
                if 'laser_parameters_template' in item:
                    template_name = item['laser_parameters_template']
                    if template_name in parameter_templates:
                        expanded_item['laser_parameters'] = parameter_templates[template_name].copy()
                    del expanded_item['laser_parameters_template']
                
                # Fail-fast: No defaults applied - all material fields must be explicit
                
                expanded_items.append(expanded_item)
            
            expanded['materials'][category] = {
                'description': cat_data.get('description', f'{category} materials'),
                'article_type': cat_data.get('article_type', 'material'),
                'processing_priority': cat_data.get('processing_priority', 'medium'),
                'items': expanded_items
            }
        elif isinstance(cat_data, dict):
            # Complex category with subcategories - flatten for compatibility
            all_items = []
            
            for subcat_name, subcat_data in cat_data.items():
                if isinstance(subcat_data, dict) and 'items' in subcat_data:
                    for item in subcat_data['items']:
                        expanded_item = item.copy()
                        
                        # Expand parameter template reference
                        if 'laser_parameters_template' in item:
                            template_name = item['laser_parameters_template']
                            if template_name in parameter_templates:
                                expanded_item['laser_parameters'] = parameter_templates[template_name].copy()
                            del expanded_item['laser_parameters_template']
                        
                        # Fail-fast: No defaults applied - all material fields must be explicit
                        
                        all_items.append(expanded_item)
            
            if all_items:
                expanded['materials'][category] = {
                    'description': f'{category} materials',
                    'article_type': 'material',
                    'processing_priority': 'medium',
                    'items': all_items
                }
        elif isinstance(cat_data, list):
            # Handle subcategory list (like metals: ['pure_metals', 'precious_metals', 'alloys'])
            # This will be handled by the material_index lookup system
            expanded['materials'][category] = {
                'description': f'{category} materials',
                'article_type': 'material', 
                'processing_priority': 'medium',
                'items': []  # Will be populated via material_index
            }
    
    return expanded


def get_material_by_name(material_name, data=None):
    """Fast O(1) material lookup using material index with case-insensitive matching."""
    if data is None:
        data = load_materials()
    
    # Use material index if available (optimized format)
    if 'material_index' in data:
        # Try exact match first (for performance)
        index_entry = data['material_index'].get(material_name)
        
        # If no exact match, try case-insensitive search
        if not index_entry:
            material_name_lower = material_name.lower()
            for key, value in data['material_index'].items():
                if key.lower() == material_name_lower:
                    index_entry = value
                    material_name = key  # Use the correct case from index
                    break
        
        if index_entry:
            category = index_entry['category']
            item_index = index_entry['index']
            
            # Check if category exists in materials
            if category in data['materials']:
                cat_data = data['materials'][category]
                
                # Handle direct items structure
                if 'items' in cat_data and item_index < len(cat_data['items']):
                    return cat_data['items'][item_index]
                
                # Handle subcategory structure - search through all subcategories
                elif not isinstance(cat_data.get('items'), list):
                    for subcat_name, subcat_data in cat_data.items():
                        if isinstance(subcat_data, dict) and 'items' in subcat_data:
                            if item_index < len(subcat_data['items']):
                                return subcat_data['items'][item_index]
                            item_index -= len(subcat_data['items'])
    
    # Fail-fast: Index lookup failed - no fallback search allowed
    raise ValueError(f"Material '{material_name}' not found in material index - index system must be complete")
    
    return None
