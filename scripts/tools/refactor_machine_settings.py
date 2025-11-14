#!/usr/bin/env python3
"""
Refactor MachineSettings.yaml to remove duplicated sections.
Removes parameterRanges and parameterDescriptions sections that now live in ParameterDefinitions.yaml.
"""

import yaml
from pathlib import Path


def refactor_machine_settings():
    """Remove duplicated sections from MachineSettings.yaml."""
    
    data_dir = Path(__file__).parent.parent.parent / "data" / "materials"
    input_file = data_dir / "MachineSettings.yaml"
    backup_file = data_dir / "backups" / "MachineSettings_before_normalization.yaml"
    
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Backup original
    print(f"Creating backup at {backup_file}...")
    with open(backup_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Remove duplicated sections
    removed_sections = []
    
    if 'parameterRanges' in data:
        removed_sections.append(f"parameterRanges ({len(data['parameterRanges'])} parameters)")
        del data['parameterRanges']
    
    if 'parameterDescriptions' in data:
        removed_sections.append(f"parameterDescriptions ({len(data['parameterDescriptions'])} descriptions)")
        del data['parameterDescriptions']
    
    # Update metadata
    data['_metadata']['version'] = '3.0.0'
    data['_metadata']['last_updated'] = '2025-11-13'
    data['_metadata']['normalized_architecture'] = True
    data['_metadata']['parameter_definitions_ref'] = 'ParameterDefinitions.yaml'
    
    print(f"\nRefactoring complete:")
    print(f"  Materials with settings: {len(data.get('settings', {}))}")
    print(f"\n  Removed sections:")
    for section in removed_sections:
        print(f"    - {section} → ParameterDefinitions.yaml")
    
    # Calculate size reduction
    with open(input_file, 'r', encoding='utf-8') as f:
        original_size = len(f.read())
    
    new_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    new_size = len(new_content)
    reduction = ((original_size - new_size) / original_size) * 100
    
    print(f"\n  Original size: {original_size // 1024}KB")
    print(f"  New size: {new_size // 1024}KB")
    print(f"  Reduction: {reduction:.1f}%")
    
    # Write the refactored file
    print(f"\nWriting refactored {input_file}...")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write("# Machine Settings - Material-Specific Laser Parameters\n")
        f.write("# Parameter definitions and ranges → ParameterDefinitions.yaml\n")
        f.write("# This file contains ONLY material-specific parameter values\n")
        f.write("# Version: 3.0.0 (Normalized Architecture)\n")
        f.write("# Last Updated: 2025-11-13\n\n")
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ MachineSettings.yaml refactored successfully!")
    print(f"   {len(data.get('settings', {}))} materials with parameter values")
    print(f"   Backup saved to {backup_file.name}")
    
    return data


if __name__ == '__main__':
    refactor_machine_settings()
