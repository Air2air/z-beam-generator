#!/usr/bin/env python3
"""
Final YAML Structure Fix
Repairs YAML structure corruption in outcomes sections to ensure proper parsing.
Converts mixed dictionary/list formats to consistent structure.
"""

import yaml
from pathlib import Path

def fix_yaml_structure():
    """Fix YAML structure issues in all frontmatter files."""
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print(f"Error: Directory {frontmatter_dir} does not exist")
        return
    
    files_processed = 0
    files_fixed = 0
    
    for file_path in frontmatter_dir.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split content into frontmatter and body
            parts = content.split('---\n', 2)
            if len(parts) < 3:
                print(f"Skipping {file_path.name}: No valid frontmatter structure")
                continue
            
            yaml_content = parts[1]
            body_content = parts[2] if len(parts) > 2 else ""
            
            # Parse YAML
            try:
                data = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                print(f"YAML parsing error in {file_path.name}: {e}")
                continue
            
            # Fix outcomes structure if needed
            if 'outcomes' in data and isinstance(data['outcomes'], dict):
                outcomes = data['outcomes']
                needs_fix = False
                
                # Check if we have mixed format (some simple values, some dictionaries)
                for key, value in outcomes.items():
                    if isinstance(value, dict) and 'result' in value and 'metric' in value:
                        # This is the old format that needs conversion
                        needs_fix = True
                        break
                
                if needs_fix:
                    print(f"Fixing YAML structure in {file_path.name}")
                    
                    # Create new outcomes structure
                    new_outcomes = {}
                    
                    # Preserve surface roughness values (should be simple numbers)
                    for key in ['surface_roughness_before', 'surface_roughness_after']:
                        if key in outcomes:
                            new_outcomes[key] = outcomes[key]
                    
                    # Convert other outcomes to proper format
                    for key, value in outcomes.items():
                        if key not in ['surface_roughness_before', 'surface_roughness_after']:
                            if isinstance(value, dict) and 'result' in value and 'metric' in value:
                                # Convert old format to new format
                                new_outcomes[key] = value['metric']
                            else:
                                # Keep as is
                                new_outcomes[key] = value
                    
                    data['outcomes'] = new_outcomes
                    files_fixed += 1
            
            # Write back the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("---\n")
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                f.write("---\n")
                f.write(body_content)
            
            files_processed += 1
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue
    
    print("\nYAML Structure Fix Summary:")
    print(f"Files processed: {files_processed}")
    print(f"Files fixed: {files_fixed}")

if __name__ == "__main__":
    fix_yaml_structure()
