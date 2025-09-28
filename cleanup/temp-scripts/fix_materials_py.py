#!/usr/bin/env python3
"""
Fix materials.py to handle string format in material_index.
"""

def fix_materials_py():
    """Fix the materials.py file to handle string format in material_index."""
    
    materials_py_path = "data/materials.py"
    
    # Read the current content
    with open(materials_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the problematic section
    old_code = """    for material_name, index_data in material_index.items():
        category = index_data.get('category')
        if category:
            if category not in category_materials:
                category_materials[category] = []
            category_materials[category].append((material_name, index_data.get('index', 0)))"""
    
    new_code = """    for material_name, index_data in material_index.items():
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
            category_materials[category].append((material_name, index_num))"""
    
    # Replace all occurrences
    updated_content = content.replace(old_code, new_code)
    
    if updated_content != content:
        # Create backup
        import shutil
        from datetime import datetime
        backup_path = f"data/materials_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        shutil.copy(materials_py_path, backup_path)
        print(f"📂 Created backup: {backup_path}")
        
        # Write the fix
        with open(materials_py_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Fixed materials.py to handle string format in material_index")
        return True
    else:
        print("ℹ️  No changes needed in materials.py")
        return False

if __name__ == "__main__":
    fix_materials_py()