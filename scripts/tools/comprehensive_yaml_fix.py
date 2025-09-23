#!/usr/bin/env python3
"""
Comprehensive YAML Fix - Advanced automated fixes for all frontmatter parsing issues.
"""

import yaml
import re
from pathlib import Path

def fix_comprehensive_yaml_issues(content):
    """Apply comprehensive fixes to YAML content"""
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            i += 1
            continue
        
        # Pattern 1: Files that start without --- (like serpentine, silver, tungsten)
        if i == 0 and not line.strip().startswith('---') and ':' in line:
            # Insert missing frontmatter delimiter
            fixed_lines.append('---')
            # Continue processing this line
        
        # Pattern 2: Multi-line formulas and descriptions
        if any(field in line for field in ['formula:', 'description:', 'symbol:', 'density:', 'chemicalFormula:']):
            # Check if this line has an unmatched quote or broken structure
            if '"' in line and (line.count('"') == 1 or not line.strip().endswith('"')):
                # Collect all continuation lines
                collected_lines = [line]
                j = i + 1
                
                # Keep collecting until we find a proper end or new field
                while j < len(lines):
                    next_line = lines[j]
                    
                    # Stop conditions
                    if not next_line.strip():  # Empty line
                        break
                    if next_line.strip().startswith('---'):  # Frontmatter end
                        break
                    if re.match(r'^\s*[a-zA-Z]\w*:', next_line):  # New field
                        break
                    if next_line.strip().startswith('-'):  # Array item
                        break
                    
                    collected_lines.append(next_line)
                    j += 1
                
                # If we collected multiple lines, fix them
                if len(collected_lines) > 1:
                    # Extract field info from first line
                    field_match = re.match(r'^(\s*)(\w+:\s*)(.*)', collected_lines[0])
                    if field_match:
                        indent = field_match.group(1)
                        field_name = field_match.group(2)
                        first_value = field_match.group(3)
                        
                        # Combine all values
                        all_values = [first_value] + [cl.strip() for cl in collected_lines[1:]]
                        combined_value = ' '.join(all_values)
                        
                        # Clean up the combined value
                        combined_value = re.sub(r'\s+', ' ', combined_value).strip()
                        combined_value = combined_value.replace('""', '"')
                        
                        # Remove existing quotes and re-add properly
                        combined_value = combined_value.strip('"')
                        combined_value = f'"{combined_value}"'
                        
                        # Create the fixed line
                        fixed_line = f"{indent}{field_name}{combined_value}"
                        fixed_lines.append(fixed_line)
                        
                        # Skip the processed lines
                        i = j - 1
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Pattern 3: Multi-line result arrays
        elif line.strip().startswith('- result:') and not line.strip().endswith('"'):
            # Collect the multi-line result
            result_lines = [line]
            j = i + 1
            
            # Collect continuation lines
            while j < len(lines):
                next_line = lines[j]
                
                # Stop conditions
                if not next_line.strip():  # Empty line
                    break
                if next_line.strip().startswith('-'):  # New array item
                    break
                if re.match(r'^\s*[a-zA-Z]\w*:', next_line):  # New field
                    break
                
                result_lines.append(next_line)
                j += 1
            
            # Fix the result if multi-line
            if len(result_lines) > 1:
                # Extract result prefix
                result_match = re.match(r'^(\s*-\s*result:\s*)(.*)', result_lines[0])
                if result_match:
                    prefix = result_match.group(1)
                    first_value = result_match.group(2)
                    
                    # Combine all parts
                    all_parts = [first_value] + [rl.strip() for rl in result_lines[1:]]
                    combined = ' '.join(all_parts)
                    
                    # Clean up
                    combined = re.sub(r'\s+', ' ', combined).strip()
                    combined = combined.replace('""', '"').strip('"')
                    
                    # Quote the result
                    combined = f'"{combined}"'
                    
                    # Create fixed line
                    fixed_line = f"{prefix}{combined}"
                    fixed_lines.append(fixed_line)
                    
                    # Skip processed lines
                    i = j - 1
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Pattern 4: Multi-line density/powerRange values
        elif any(field in line for field in ['density:', 'powerRange:', 'wavelengthRange:']):
            # Check for multi-line pattern
            if '"' in line and not line.strip().endswith('"'):
                # Similar logic to formulas
                collected_lines = [line]
                j = i + 1
                
                while j < len(lines):
                    next_line = lines[j]
                    if (not next_line.strip() or 
                        next_line.strip().startswith('-') or 
                        re.match(r'^\s*[a-zA-Z]\w*:', next_line)):
                        break
                    collected_lines.append(next_line)
                    j += 1
                
                if len(collected_lines) > 1:
                    field_match = re.match(r'^(\s*)(\w+:\s*)(.*)', collected_lines[0])
                    if field_match:
                        indent = field_match.group(1)
                        field_name = field_match.group(2)
                        first_value = field_match.group(3)
                        
                        all_values = [first_value] + [cl.strip() for cl in collected_lines[1:]]
                        combined_value = ' '.join(all_values)
                        combined_value = re.sub(r'\s+', ' ', combined_value).strip()
                        combined_value = combined_value.replace('""', '"').strip('"')
                        combined_value = f'"{combined_value}"'
                        
                        fixed_line = f"{indent}{field_name}{combined_value}"
                        fixed_lines.append(fixed_line)
                        i = j - 1
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)

def fix_file_comprehensive(file_path):
    """Apply comprehensive fixes to a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse original
        try:
            # Handle frontmatter extraction
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = parts[1].strip()
                    yaml.safe_load(frontmatter)
                    return True, "Already valid"
            else:
                # File doesn't start with ---, try to parse as direct YAML
                yaml.safe_load(content)
                return True, "Already valid"
        except yaml.YAMLError:
            pass
        
        # Apply comprehensive fixes
        fixed_content = fix_comprehensive_yaml_issues(content)
        
        # Validate the fix
        try:
            if fixed_content.startswith('---'):
                parts = fixed_content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = parts[1].strip()
                    yaml.safe_load(frontmatter)
            else:
                yaml.safe_load(fixed_content)
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return True, "Fixed successfully"
            
        except yaml.YAMLError as e:
            return False, f"Fix failed: {str(e)[:100]}"
    
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def main():
    """Apply comprehensive fixes to all frontmatter files"""
    script_dir = Path(__file__).parent.parent.parent
    frontmatter_dir = script_dir / "content" / "components" / "frontmatter"
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return
    
    frontmatter_files = list(frontmatter_dir.glob("*-laser-cleaning.md"))
    
    print(f"🔧 Applying comprehensive YAML fixes to {len(frontmatter_files)} files...")
    
    fixed_count = 0
    error_count = 0
    already_valid_count = 0
    
    for file_path in sorted(frontmatter_files):
        material_name = file_path.stem.replace('-laser-cleaning', '')
        success, message = fix_file_comprehensive(file_path)
        
        if success:
            if "Already valid" in message:
                already_valid_count += 1
            else:
                print(f"✅ {material_name}: {message}")
                fixed_count += 1
        else:
            print(f"❌ {material_name}: {message}")
            error_count += 1
    
    print("\n📊 Comprehensive Fix Summary:")
    print(f"   Already valid: {already_valid_count}")
    print(f"   Fixed: {fixed_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total: {len(frontmatter_files)}")
    
    if fixed_count > 0:
        print(f"\n🎉 Fixed {fixed_count} additional files! Ready for tag regeneration.")

if __name__ == "__main__":
    main()
