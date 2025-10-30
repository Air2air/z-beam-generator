#!/usr/bin/env python3
"""
Consolidate ConfigurationError to single canonical definition

CANONICAL VERSION: validation/errors.py
- Most complete implementation
- Part of unified validation error types
- Well-documented with fail-fast principles
"""

import os
from pathlib import Path
from datetime import datetime
import shutil

def consolidate_configuration_error():
    """Consolidate ConfigurationError definitions to single import"""
    
    root = Path(".")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = root / ".archive" / f"config_error_consolidation_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("🔧 CONSOLIDATING ConfigurationError CLASS")
    print("="*80)
    
    # Files that define ConfigurationError (excluding docs and canonical)
    files_to_fix = [
        "config/unified_manager.py",
        "utils/config_loader.py",
        "research/services/ai_research_service.py",
        "scripts/validation/fail_fast_materials_validator.py",
        "scripts/research/unique_values_validator.py",
        "scripts/research/batch_materials_research.py"
    ]
    
    print(f"\n✅ CANONICAL: validation/errors.py")
    print(f"   Comprehensive exception hierarchy with fail-fast principles\n")
    
    print(f"🔧 FIXING {len(files_to_fix)} FILES:\n")
    
    changes_made = []
    
    for file_path_str in files_to_fix:
        file_path = root / file_path_str
        
        if not file_path.exists():
            print(f"  ⚠️  Not found: {file_path_str}")
            continue
        
        try:
            content = file_path.read_text()
            original_content = content
            
            # Check if ConfigurationError is defined
            if "class ConfigurationError(Exception):" not in content:
                print(f"  ℹ️  No local definition: {file_path_str}")
                continue
            
            # Backup
            backup_path = backup_dir / file_path.relative_to(root)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # Remove the class definition
            lines = content.split('\n')
            new_lines = []
            skip_next = False
            in_config_error_class = False
            
            for i, line in enumerate(lines):
                if "class ConfigurationError(Exception):" in line:
                    in_config_error_class = True
                    # Don't add this line
                    # Check if there's a docstring or pass on next lines
                    continue
                elif in_config_error_class:
                    # Skip docstring and pass statement
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        if line.strip().endswith('"""') or line.strip().endswith("'''"):
                            # Single-line docstring
                            in_config_error_class = False
                        # Continue skipping until end of docstring
                        continue
                    elif '"""' in line or "'''" in line:
                        # End of multi-line docstring
                        in_config_error_class = False
                        continue
                    elif line.strip() == "pass":
                        in_config_error_class = False
                        continue
                    elif line.strip() == "" or line.strip().startswith("#"):
                        # Empty line or comment after class def
                        continue
                    else:
                        # Next class or code
                        in_config_error_class = False
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            new_content = '\n'.join(new_lines)
            
            # Add import if not already present
            if "from validation.errors import ConfigurationError" not in new_content:
                # Find where to add import
                import_section_end = 0
                for i, line in enumerate(new_lines):
                    if line.startswith("import ") or line.startswith("from "):
                        import_section_end = i + 1
                    elif import_section_end > 0 and line.strip() == "":
                        break
                
                # Insert import
                new_lines.insert(import_section_end, "from validation.errors import ConfigurationError")
                new_content = '\n'.join(new_lines)
            
            # Write updated content
            file_path.write_text(new_content)
            
            changes_made.append(file_path_str)
            print(f"  ✅ Fixed: {file_path_str}")
            print(f"     - Removed local ConfigurationError definition")
            print(f"     - Added import from validation.errors")
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path_str}: {e}")
    
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"Files modified: {len(changes_made)}")
    for file in changes_made:
        print(f"  - {file}")
    print(f"\n💾 Backups saved to: {backup_dir}")
    print(f"\n✅ ConfigurationError now centralized in validation/errors.py")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent.parent)
    consolidate_configuration_error()
