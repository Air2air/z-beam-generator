#!/usr/bin/env python3
"""
Frontmatter YAML Formatter
Automatically fixes common YAML parsing issues in frontmatter files.
"""

import os
import re
import yaml
from pathlib import Path


def fix_yaml_issues(content):
    """Fix common YAML parsing issues in frontmatter content."""
    lines = content.split('\n')
    fixed_lines = []
    in_frontmatter = False
    i = 0
    
    # Special handling for files that start directly with YAML content (no --- delimiter)
    if not content.strip().startswith('---'):
        in_frontmatter = True
    
    while i < len(lines):
        line = lines[i]
        
        # Handle frontmatter delimiters
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
            fixed_lines.append(line)
            i += 1
            continue
        
        # If we haven't seen a --- yet, assume we're in frontmatter (for broken files)
        if not in_frontmatter and i == 0 and ':' in line:
            in_frontmatter = True
            
        if not in_frontmatter:
            fixed_lines.append(line)
            i += 1
            continue
            
        # Fix 1: Quote unquoted symbols with parentheses or special characters
        if 'symbol:' in line and ('(' in line or 'N/A' in line or 'based' in line):
            match = re.match(r'^(\s*symbol:\s*)(.*)', line)
            if match:
                indent, value = match.groups()
                value = value.strip()
                if not (value.startswith('"') and value.endswith('"')):
                    value = f'"{value}"'
                line = f"{indent}{value}"
        
        # Fix 2: Handle multi-line formulas and descriptions  
        if any(field in line for field in ['formula:', 'description:', 'density:', 'symbol:']) and '"' in line:
            # Check if this starts a multi-line string that's broken
            if line.count('"') == 1 and not line.strip().endswith('"'):
                # This is the start of a multi-line value
                value_lines = [line]
                j = i + 1
                
                # Collect continuation lines until we find the closing quote or a new field
                while j < len(lines):
                    next_line = lines[j]
                    value_lines.append(next_line)
                    
                    # Check if this line ends the multi-line value
                    if '"' in next_line:
                        break
                    # Check if we hit a new YAML field (line starts with letters followed by colon)
                    if next_line.strip() and re.match(r'^\s*[a-zA-Z]\w*:', next_line):
                        # Remove this line from value_lines since it's a new field
                        value_lines.pop()
                        j -= 1
                        break
                    j += 1
                
                # Join all value parts into a single line if we found multiple
                if len(value_lines) > 1:
                    # Extract field name and combine all content
                    field_match = re.match(r'^(\s*)(\w+:\s*)', value_lines[0])
                    if field_match:
                        indent = field_match.group(1)
                        field_prefix = field_match.group(2)
                        
                        # Combine all the value parts, removing field prefix from first line
                        first_value = value_lines[0].replace(field_match.group(0), '').strip()
                        other_values = [vl.strip() for vl in value_lines[1:]]
                        
                        all_content = ' '.join([first_value] + other_values)
                        
                        # Clean up quotes and spaces
                        all_content = re.sub(r'\s+', ' ', all_content).strip()
                        all_content = all_content.replace('""', '"')
                        
                        # Ensure proper quoting - if it has quotes, make sure they're balanced
                        if '"' in all_content:
                            # Remove all quotes and re-add them properly
                            all_content = all_content.replace('"', '')
                            all_content = f'"{all_content}"'
                        
                        # Create the fixed line
                        line = f"{indent}{field_prefix}{all_content}"
                        
                        # Skip the lines we've processed
                        i = j
                
        # Fix 3: Quote complex density, power, and wavelength ranges
        if any(field in line for field in ['density:', 'powerRange:', 'wavelengthRange:']):
            match = re.match(r'^(\s*\w+:\s*)(.*)', line)
            if match:
                indent, value = match.groups()
                value = value.strip()
                # Quote values with special characters, ranges, or units
                if any(char in value for char in ['(', ')', '-', 'W', 'nm', 'µm', 'kg/m³', 'g/cm³']) and not (value.startswith('"') and value.endswith('"')):
                    if not value.startswith('"'):
                        value = f'"{value}"'
                    line = f"{indent}{value}"
        
        # Fix 4: Handle result arrays with broken YAML structure
        if ('- result:' in line or line.strip().startswith('- result')) and not line.strip().endswith('"'):
            # Check if this is a broken multi-line result
            result_lines = [line]
            j = i + 1
            
            # Collect continuation lines until we hit another array item or field
            while j < len(lines):
                next_line = lines[j]
                
                # Stop if we hit another array item or a new field
                if (next_line.strip().startswith('-') or 
                    (next_line.strip() and re.match(r'^\s*[a-zA-Z]\w*:', next_line)) or
                    not next_line.strip()):
                    break
                    
                result_lines.append(next_line)
                j += 1
            
            if len(result_lines) > 1:
                # Extract the result prefix and combine all content
                result_match = re.match(r'^(\s*-\s*result:\s*)', result_lines[0])
                if result_match:
                    indent = result_match.group(1)
                    
                    # Get the first value
                    first_value = result_lines[0].replace(result_match.group(0), '').strip()
                    
                    # Combine all content
                    all_parts = [first_value] + [rl.strip() for rl in result_lines[1:]]
                    combined_result = ' '.join(all_parts)
                    
                    # Clean up the result format
                    combined_result = re.sub(r'\s+', ' ', combined_result).strip()
                    
                    # Handle quotes properly
                    if '"' in combined_result:
                        # Remove all quotes and re-add them properly
                        combined_result = combined_result.replace('"', '')
                        combined_result = f'"{combined_result}"'
                    elif any(char in combined_result for char in [':', ',', '[', ']', '{', '}']):
                        # Quote if contains special YAML characters
                        combined_result = f'"{combined_result}"'
                    
                    # Create the fixed line
                    line = f"{indent}{combined_result}"
                    
                    # Skip the lines we've processed
                    i = j - 1  # Will be incremented at the end of the loop
        
        fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines)


def validate_yaml_frontmatter(content):
    """Validate that the frontmatter YAML is parseable."""
    try:
        # Handle different frontmatter formats
        if content.startswith('---'):
            parts = content.split('---', 2)
            
            if len(parts) == 3:
                # Standard frontmatter with opening and closing ---
                frontmatter_yaml = parts[1].strip()
            elif len(parts) == 2:
                # YAML file with just opening --- (our case)
                frontmatter_yaml = parts[1].strip()
            else:
                return False, "Invalid frontmatter structure"
            
            yaml.safe_load(frontmatter_yaml)
            return True, None
        return False, "No valid frontmatter found"
    except yaml.YAMLError as e:
        return False, str(e)


def fix_frontmatter_file(file_path):
    """Fix YAML issues in a single frontmatter file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if already valid
        is_valid, error = validate_yaml_frontmatter(original_content)
        if is_valid:
            return True, "Already valid"
        
        # Apply fixes
        fixed_content = fix_yaml_issues(original_content)
        
        # Validate the fix
        is_valid_after, error_after = validate_yaml_frontmatter(fixed_content)
        if not is_valid_after:
            return False, f"Fix failed: {error_after}"
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
            
        return True, "Fixed successfully"
        
    except Exception as e:
        return False, f"Error processing file: {e}"


def main():
    """Main function to fix all frontmatter files."""
    # Use absolute path to the frontmatter directory
    script_dir = Path(__file__).parent.parent.parent
    frontmatter_dir = script_dir / "content" / "components" / "frontmatter"
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return
    
    # Find all frontmatter files
    frontmatter_files = list(frontmatter_dir.glob("*-laser-cleaning.md"))
    
    print(f"🔍 Found {len(frontmatter_files)} frontmatter files")
    print("🛠️ Fixing YAML parsing issues...\n")
    
    fixed_count = 0
    error_count = 0
    already_valid_count = 0
    
    for file_path in sorted(frontmatter_files):
        material_name = file_path.stem.replace('-laser-cleaning', '')
        success, message = fix_frontmatter_file(file_path)
        
        if success:
            if "Already valid" in message:
                print(f"✅ {material_name}: {message}")
                already_valid_count += 1
            else:
                print(f"🔧 {material_name}: {message}")
                fixed_count += 1
        else:
            print(f"❌ {material_name}: {message}")
            error_count += 1
    
    print("\n📊 Summary:")
    print(f"   Already valid: {already_valid_count}")
    print(f"   Fixed: {fixed_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total: {len(frontmatter_files)}")
    
    if fixed_count > 0:
        print(f"\n🎉 Fixed {fixed_count} files! Ready for tag regeneration.")


if __name__ == "__main__":
    main()
