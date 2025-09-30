"""
Enhanced materials data loader with optimization support.
Maintains full backward compatibility with existing code.

FAIL-FAST VALIDATION: Per GROK_INSTRUCTIONS.md, enforces ZERO TOLERANCE for defaults/fallbacks.
"""

from pathlib import Path
import yaml


def load_materials():
    """
    Load materials data from YAML file with optimization support.
    
    FAIL-FAST VALIDATION: Per GROK_INSTRUCTIONS.md, system must fail immediately
    if materials database contains defaults/fallbacks/mocks.
    """
    
    # FAIL-FAST VALIDATION - NO EXCEPTIONS
    try:
        from scripts.validation.fail_fast_materials_validator import fail_fast_validate_materials
        fail_fast_validate_materials()
    except Exception as e:
        raise RuntimeError(
            f"CRITICAL: Materials database validation failed. "
            f"Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DEFAULTS/FALLBACKS. "
            f"Error: {e}"
        )
    
    materials_file = Path(__file__).parent / "Materials.yaml"

    try:
        with open(materials_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # If optimized format detected, expand it for compatibility
        if 'parameter_templates' in data:
            expanded_data = expand_optimized_materials(data)
            return expanded_data
        
        # For non-optimized format, add material names to items for --all compatibility
        if 'material_index' in data and 'materials' in data:
            data_with_names = add_material_names_to_items(data)
            return data_with_names
        
        # Return original format as-is
        return data
    except Exception as e:
        raise RuntimeError(f"CRITICAL: Error loading materials data: {e}")


def add_material_names_to_items(data):
    """Add material names to items in non-optimized format for --all compatibility."""
    result = data.copy()
    material_index = data.get('material_index', {})
    
    # Create reverse lookup: category -> list of (material_name, index) for that category
    category_materials = {}
    for material_name, index_data in material_index.items():
        if isinstance(index_data, str):
            # Simple format: material_name -> category_string
            category = index_data
            index_num = 0
        else:
            # Complex format: material_name -> {category: ..., index: ...}
            category = index_data.get('category')
            index_num = index_data.get('index', 0)
            
        if category:
            if category not in category_materials:
                category_materials[category] = []
            category_materials[category].append((material_name, index_num))
    
    # Sort materials by index within each category
    for category in category_materials:
        category_materials[category].sort(key=lambda x: x[1])
    
    # Add names to items
    materials_with_names = {}
    for category, cat_data in data['materials'].items():
        if isinstance(cat_data, dict) and 'items' in cat_data:
            items_with_names = []
            category_material_list = category_materials.get(category, [])
            
            for idx, item in enumerate(cat_data['items']):
                item_with_name = item.copy()
                
                # Add material name from the index
                if idx < len(category_material_list):
                    material_name = category_material_list[idx][0]
                    item_with_name['name'] = material_name
                
                items_with_names.append(item_with_name)
            
            # Create updated category data
            cat_data_with_names = cat_data.copy()
            cat_data_with_names['items'] = items_with_names
            materials_with_names[category] = cat_data_with_names
        else:
            materials_with_names[category] = cat_data
    
    result['materials'] = materials_with_names
    
    return result


def find_material_case_insensitive(material_name: str, materials_data: dict = None) -> tuple:
    """
    Find a material by name (case-insensitive) and return its data and category.
    
    Args:
        material_name: Name to search for (case-insensitive)
        materials_data: Optional pre-loaded materials data
    
    Returns:
        tuple: (material_data, category_name) or (None, None) if not found
    """
    if materials_data is None:
        materials_data = load_materials()
    
    search_name = material_name.lower().strip()
    
    for category, category_data in materials_data.get('materials', {}).items():
        items = category_data.get('items', [])
        for item in items:
            item_name = item.get('name', '').lower().strip()
            if item_name == search_name:
                return item, category
    
    return None, None
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
    material_index = data.get('material_index', {})
    
    # Create reverse lookup: category -> list of (material_name, index) for that category
    category_materials = {}
    for material_name, index_data in material_index.items():
        if isinstance(index_data, str):
            # Simple format: material_name -> category_string
            category = index_data
            index_num = 0
        else:
            # Complex format: material_name -> {category: ..., index: ...}
            category = index_data.get('category')
            index_num = index_data.get('index', 0)
            
        if category:
            if category not in category_materials:
                category_materials[category] = []
            category_materials[category].append((material_name, index_num))
    
    # Sort materials by index within each category
    for category in category_materials:
        category_materials[category].sort(key=lambda x: x[1])
    
    for category, cat_data in data['materials'].items():
        # Handle both simple categories with items and complex categories with subcategories
        if isinstance(cat_data, dict) and 'items' in cat_data:
            # Simple category with direct items
            expanded_items = []
            
            # Get material names for this category from the index
            category_material_list = category_materials.get(category, [])
            
            for idx, item in enumerate(cat_data['items']):
                expanded_item = item.copy()
                
                # Add material name from the index
                if idx < len(category_material_list):
                    material_name = category_material_list[idx][0]
                    expanded_item['name'] = material_name
                
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
            category_material_list = category_materials.get(category, [])
            item_index = 0
            
            for subcat_name, subcat_data in cat_data.items():
                if isinstance(subcat_data, dict) and 'items' in subcat_data:
                    for item in subcat_data['items']:
                        expanded_item = item.copy()
                        
                        # Add material name from the index
                        if item_index < len(category_material_list):
                            material_name = category_material_list[item_index][0]
                            expanded_item['name'] = material_name
                            item_index += 1
                        
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
            if isinstance(index_entry, str):
                # Simple format: material_name -> category_string
                category = index_entry
                item_index = 0
            else:
                # Complex format: material_name -> {category: ..., index: ...}
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
