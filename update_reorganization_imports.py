#!/usr/bin/env python3
"""
Update imports after major directory reorganization.

Changes:
1. research/* → materials/research/*
2. components.frontmatter.research → materials.research
3. components.frontmatter.modules → materials.modules
4. components.frontmatter.services → materials.services
5. components.frontmatter.validation → materials.validation
6. components.caption → materials.caption
7. components.subtitle → materials.subtitle
8. components.faq → materials.faq
9. utils.property_* → materials.utils.property_*
10. utils.* (general) → shared.utils.*
"""

import re
from pathlib import Path

# Define import mappings (order matters - most specific first)
IMPORT_MAPPINGS = [
    # Research imports
    (r'from research\.', 'from materials.research.'),
    (r'import research\.', 'import materials.research.'),
    (r'from components\.frontmatter\.research', 'from materials.research'),
    (r'import components\.frontmatter\.research', 'import materials.research'),
    
    # Modules, services, validation
    (r'from components\.frontmatter\.modules', 'from materials.modules'),
    (r'import components\.frontmatter\.modules', 'import materials.modules'),
    (r'from components\.frontmatter\.services', 'from materials.services'),
    (r'import components\.frontmatter\.services', 'import materials.services'),
    (r'from components\.frontmatter\.validation', 'from materials.validation'),
    (r'import components\.frontmatter\.validation', 'import materials.validation'),
    
    # Caption, subtitle, FAQ
    (r'from components\.caption', 'from materials.caption'),
    (r'import components\.caption', 'import materials.caption'),
    (r'from components\.subtitle', 'from materials.subtitle'),
    (r'import components\.subtitle', 'import materials.subtitle'),
    (r'from components\.faq', 'from materials.faq'),
    (r'import components\.faq', 'import materials.faq'),
    
    # Material-specific utils
    (r'from utils\.property_classifier', 'from materials.utils.property_classifier'),
    (r'import utils\.property_classifier', 'import materials.utils.property_classifier'),
    (r'from utils\.property_enhancer', 'from materials.utils.property_enhancer'),
    (r'import utils\.property_enhancer', 'import materials.utils.property_enhancer'),
    (r'from utils\.property_helpers', 'from materials.utils.property_helpers'),
    (r'import utils\.property_helpers', 'import materials.utils.property_helpers'),
    (r'from utils\.unit_extractor', 'from materials.utils.unit_extractor'),
    (r'import utils\.unit_extractor', 'import materials.utils.unit_extractor'),
    (r'from utils\.category_property_cache', 'from materials.utils.category_property_cache'),
    (r'import utils\.category_property_cache', 'import materials.utils.category_property_cache'),
    
    # General utils (moved to shared)
    (r'from utils\.file_operations', 'from shared.utils.file_operations'),
    (r'import utils\.file_operations', 'import shared.utils.file_operations'),
    (r'from utils\.yaml_parser', 'from shared.utils.yaml_parser'),
    (r'import utils\.yaml_parser', 'import shared.utils.yaml_parser'),
    (r'from utils\.config_loader', 'from shared.utils.config_loader'),
    (r'import utils\.config_loader', 'import shared.utils.config_loader'),
    (r'from utils\.import_system', 'from shared.utils.import_system'),
    (r'import utils\.import_system', 'import shared.utils.import_system'),
    (r'from utils\.requirements_loader', 'from shared.utils.requirements_loader'),
    (r'import utils\.requirements_loader', 'import shared.utils.requirements_loader'),
    (r'from utils\.file_ops', 'from shared.utils.file_ops'),
    (r'import utils\.file_ops', 'import shared.utils.file_ops'),
    (r'from utils\.loaders', 'from shared.utils.loaders'),
    (r'import utils\.loaders', 'import shared.utils.loaders'),
    (r'from utils\.ai', 'from shared.utils.ai'),
    (r'import utils\.ai', 'import shared.utils.ai'),
    (r'from utils\.ai_detection_logger', 'from shared.utils.ai_detection_logger'),
    (r'import utils\.ai_detection_logger', 'import shared.utils.ai_detection_logger'),
    (r'from utils\.author_manager', 'from shared.utils.author_manager'),
    (r'import utils\.author_manager', 'import shared.utils.author_manager'),
    (r'from utils\.compact_sentence_logger', 'from shared.utils.compact_sentence_logger'),
    (r'import utils\.compact_sentence_logger', 'import shared.utils.compact_sentence_logger'),
    (r'from utils\.component_mode', 'from shared.utils.component_mode'),
    (r'import utils\.component_mode', 'import shared.utils.component_mode'),
    (r'from utils\.filename', 'from shared.utils.filename'),
    (r'import utils\.filename', 'import shared.utils.filename'),
    (r'from utils\.core', 'from shared.utils.core'),
    (r'import utils\.core', 'import shared.utils.core'),
    
    # Validation (moved to shared)
    (r'from utils\.validation', 'from shared.validation'),
    (r'import utils\.validation', 'import shared.validation'),
]

def update_file(file_path: Path) -> tuple[bool, int]:
    """Update imports in a single file. Returns (changed, num_changes)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        for old_pattern, new_pattern in IMPORT_MAPPINGS:
            new_content = re.sub(old_pattern, new_pattern, content)
            if new_content != content:
                matches = len(re.findall(old_pattern, content))
                changes += matches
                content = new_content
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        
        return False, 0
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0

def main():
    """Update all Python files in the workspace."""
    print("🔄 Updating imports after directory reorganization...")
    print()
    
    workspace_root = Path(__file__).parent
    
    # Find all Python files (exclude __pycache__, venv, etc.)
    python_files = []
    for path in workspace_root.rglob("*.py"):
        # Skip excluded directories
        if any(part in path.parts for part in ['__pycache__', '.venv', 'venv', 'node_modules', '.git']):
            continue
        python_files.append(path)
    
    print(f"📂 Found {len(python_files)} Python files")
    print()
    
    # Update files
    updated_files = []
    total_changes = 0
    
    for file_path in python_files:
        changed, num_changes = update_file(file_path)
        if changed:
            updated_files.append(file_path)
            total_changes += num_changes
            print(f"✅ {file_path.relative_to(workspace_root)} ({num_changes} changes)")
    
    print()
    print("="*80)
    print("✅ Import update complete!")
    print(f"   Updated {len(updated_files)} files")
    print(f"   Made {total_changes} import changes")
    print("="*80)
    
    if updated_files:
        print()
        print("Updated files:")
        for file_path in updated_files:
            print(f"  • {file_path.relative_to(workspace_root)}")

if __name__ == "__main__":
    main()
