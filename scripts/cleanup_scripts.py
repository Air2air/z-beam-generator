#!/usr/bin/env python3
"""
Script cleanup utility for Z-Beam Generator
Identifies and organizes obsolete, duplicate, and temporary scripts.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def analyze_script_usage():
    """Analyze script usage and identify candidates for cleanup."""
    
    # Categories of scripts
    cleanup_plan = {
        "obsolete_normalization": [
            "scripts/normalize_frontmatter_yaml.py",  # Superseded by simple version
            "scripts/normalize_frontmatter_quotes.py",  # One-time fix, completed
            "scripts/simple_normalize_frontmatter.py",  # Task completed
        ],
        "obsolete_image_scripts": [
            "scripts/normalize_image_names.py",  # One-time normalization, completed
            "scripts/resolve_image_conflicts.py",  # One-time fix, completed  
            "scripts/final_image_resolution.py",  # One-time fix, completed
            "scripts/compare_frontmatter_images.py",  # Analysis completed
            "scripts/comprehensive_image_analysis.py",  # Analysis completed
        ],
        "obsolete_material_scripts": [
            "scripts/enhance_materials_from_frontmatter.py",  # One-time migration, completed
            "scripts/integrate_enhanced_materials.py",  # One-time integration, completed
            "scripts/migrate_materials_metadata.py",  # One-time migration, completed
            "scripts/optimize_materials_yaml.py",  # One-time optimization, completed
            "scripts/steel_variants_analysis.py",  # Analysis completed
            "scripts/verify_materials_alignment.py",  # Verification completed
            "scripts/restore_material_specificity.py",  # One-time fix, completed
        ],
        "obsolete_frontmatter_scripts": [
            "scripts/update_frontmatter_images.py",  # One-time update, completed
            "scripts/update_frontmatter_to_standardized_naming.py",  # One-time update, completed
            "scripts/update_frontmatter_countries.py",  # One-time update, completed
            "scripts/repair_frontmatter_structure.py",  # One-time repair, completed
            "scripts/verify_frontmatter_structure.py",  # Verification completed
            "scripts/sync_frontmatter_authors.py",  # One-time sync, completed
        ],
        "obsolete_shell_scripts": [
            "scripts/update_density_format.sh",  # One-time format update, completed
            "scripts/update_propertiestable_labels.sh",  # One-time update, completed
        ],
        "obsolete_one_time_scripts": [
            "scripts/update_labels.py",  # One-time label update, completed
            "scripts/validate_imports.py",  # Validation completed
            "scripts/normalization_summary_report.py",  # Report generated
            "scripts/generate_all_metatags.py",  # One-time generation, completed
        ],
        "temporary_debug": [
            "scripts/debug_config.py",  # Debug script, can be removed
            "scripts/capture_terminal_errors.py",  # Temporary debug script
            "scripts/production_test.py",  # Test script, can be archived
        ],
        "keep_active": [
            "scripts/remove_material.py",  # Utility script - keep
            "scripts/run_error_workflow.sh",  # Error testing workflow - keep
            "scripts/validate_technical_accuracy.py",  # Validation utility - keep
            "scripts/tools/api_terminal_diagnostics.py",  # Active diagnostic tool - keep
            "scripts/tools/fix_nested_yaml_properties.py",  # Active utility - keep
            "scripts/maintenance/",  # All maintenance scripts - keep
            "scripts/evaluation/",  # All evaluation scripts - keep  
            "scripts/testing/",  # All testing scripts - keep
        ]
    }
    
    return cleanup_plan

def create_archive_structure():
    """Create organized archive structure for obsolete scripts."""
    
    archive_base = Path("scripts/archive")
    archive_dirs = [
        "normalization-legacy",
        "image-processing-legacy", 
        "material-migration-legacy",
        "frontmatter-updates-legacy",
        "one-time-scripts",
        "debug-scripts"
    ]
    
    for dir_name in archive_dirs:
        archive_dir = archive_base / dir_name
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create README explaining the archive
        readme_content = f"""# {dir_name.replace('-', ' ').title()}

This directory contains scripts that were used for one-time operations or have been superseded by better implementations.

**Archive Date**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Historical/Legacy - Not for active use
**Purpose**: Preserved for reference and rollback capabilities

## Contents

Scripts in this directory were archived during script cleanup operation.
These scripts served their purpose but are no longer needed for active development.

For current utilities, see:
- `scripts/tools/` - Active diagnostic and utility scripts
- `scripts/maintenance/` - System maintenance scripts
- `scripts/evaluation/` - Content evaluation scripts
- `scripts/testing/` - Testing utilities
"""
        
        readme_path = archive_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    
    return archive_base

def move_scripts_to_archive(cleanup_plan, archive_base):
    """Move obsolete scripts to organized archive directories."""
    
    # Mapping of cleanup categories to archive directories
    archive_mapping = {
        "obsolete_normalization": "normalization-legacy",
        "obsolete_image_scripts": "image-processing-legacy",
        "obsolete_material_scripts": "material-migration-legacy", 
        "obsolete_frontmatter_scripts": "frontmatter-updates-legacy",
        "obsolete_shell_scripts": "one-time-scripts",
        "obsolete_one_time_scripts": "one-time-scripts",
        "temporary_debug": "debug-scripts"
    }
    
    moved_files = []
    skipped_files = []
    
    for category, scripts in cleanup_plan.items():
        if category == "keep_active":
            continue
            
        archive_dir = archive_base / archive_mapping.get(category, "miscellaneous")
        
        for script_path in scripts:
            source_path = Path(script_path)
            
            if not source_path.exists():
                skipped_files.append(f"{script_path} (not found)")
                continue
                
            # Create destination path
            dest_path = archive_dir / source_path.name
            
            try:
                # Move the file
                shutil.move(str(source_path), str(dest_path))
                moved_files.append(f"{script_path} → {dest_path}")
                print(f"✅ Moved: {script_path}")
                
            except Exception as e:
                skipped_files.append(f"{script_path} (error: {e})")
                print(f"❌ Failed to move: {script_path} - {e}")
    
    return moved_files, skipped_files

def clean_empty_directories():
    """Remove empty directories after cleanup."""
    
    scripts_dir = Path("scripts")
    removed_dirs = []
    
    # Check for empty subdirectories  
    for item in scripts_dir.iterdir():
        if item.is_dir() and item.name not in ["archive", "tools", "maintenance", "evaluation", "testing"]:
            try:
                # Try to remove if empty
                if not any(item.iterdir()):
                    item.rmdir()
                    removed_dirs.append(str(item))
                    print(f"🗑️ Removed empty directory: {item}")
            except OSError:
                # Directory not empty, skip
                pass
    
    return removed_dirs

def update_root_scripts():
    """Move root-level utility scripts to appropriate locations."""
    
    root_scripts = {
        "generate_all_authors.py": "scripts/tools/generate_all_authors.py"
    }
    
    moved_scripts = []
    
    for source, dest in root_scripts.items():
        source_path = Path(source)
        dest_path = Path(dest)
        
        if source_path.exists():
            try:
                # Ensure destination directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(source_path), str(dest_path))
                moved_scripts.append(f"{source} → {dest}")
                print(f"📁 Moved to tools: {source}")
                
            except Exception as e:
                print(f"❌ Failed to move {source}: {e}")
    
    return moved_scripts

def generate_cleanup_report(moved_files, skipped_files, removed_dirs, moved_scripts):
    """Generate comprehensive cleanup report."""
    
    report_content = f"""# Script Cleanup Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Operation**: Script organization and obsolete file archival

## Summary

- **Files Archived**: {len(moved_files)}
- **Files Skipped**: {len(skipped_files)} 
- **Directories Removed**: {len(removed_dirs)}
- **Scripts Reorganized**: {len(moved_scripts)}

## Archived Files

Files moved to `scripts/archive/` for historical reference:

"""
    
    for file_info in moved_files:
        report_content += f"- {file_info}\n"
    
    if skipped_files:
        report_content += f"\n## Skipped Files\n\n"
        for file_info in skipped_files:
            report_content += f"- {file_info}\n"
    
    if removed_dirs:
        report_content += f"\n## Removed Empty Directories\n\n"
        for dir_path in removed_dirs:
            report_content += f"- {dir_path}\n"
    
    if moved_scripts:
        report_content += f"\n## Reorganized Scripts\n\n"
        for script_info in moved_scripts:
            report_content += f"- {script_info}\n"
    
    report_content += f"""
## Current Active Scripts

After cleanup, the following script categories remain active:

### Tools (`scripts/tools/`)
- **api_terminal_diagnostics.py**: API connectivity diagnostics
- **fix_nested_yaml_properties.py**: YAML property fixing utility
- **generate_all_authors.py**: Batch author generation utility
- Other diagnostic and utility scripts

### Maintenance (`scripts/maintenance/`)
- System maintenance and cleanup scripts
- Backup management utilities

### Evaluation (`scripts/evaluation/`)
- Content quality evaluation scripts
- End-to-end testing utilities

### Testing (`scripts/testing/`)
- Test automation scripts
- System validation utilities

### Root Level Utilities
- **remove_material.py**: Material removal utility
- **run_error_workflow.sh**: Error testing workflow
- **validate_technical_accuracy.py**: Technical validation script

## Archive Organization

Obsolete scripts have been organized into categorized archive directories:

- `scripts/archive/normalization-legacy/`: YAML/frontmatter normalization scripts
- `scripts/archive/image-processing-legacy/`: Image naming and processing scripts  
- `scripts/archive/material-migration-legacy/`: Material data migration scripts
- `scripts/archive/frontmatter-updates-legacy/`: One-time frontmatter update scripts
- `scripts/archive/one-time-scripts/`: Various one-time operation scripts
- `scripts/archive/debug-scripts/`: Temporary debugging scripts

All archived scripts include READMEs explaining their historical purpose and status.

## Impact

This cleanup:
1. **Reduces clutter**: Removes completed one-time scripts from active workspace
2. **Improves navigation**: Clearer separation between active and historical scripts  
3. **Preserves history**: All scripts archived for reference and potential rollback
4. **Organizes structure**: Better categorization of script purposes
5. **Maintains functionality**: All active utilities preserved and accessible

## Next Steps

1. **Verify functionality**: Test remaining active scripts after cleanup
2. **Update documentation**: Update any references to moved scripts
3. **Monitor usage**: Track which archived scripts might need restoration
4. **Regular cleanup**: Establish periodic script review process
"""
    
    # Save report
    report_path = Path("scripts/CLEANUP_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"📋 Cleanup report saved: {report_path}")
    
    return report_path

def main():
    """Execute script cleanup process."""
    
    print("🧹 Starting Script Cleanup Process")
    print("=" * 50)
    
    # Analyze current scripts
    print("\n🔍 Analyzing script usage...")
    cleanup_plan = analyze_script_usage()
    
    # Create archive structure
    print("\n📁 Creating archive structure...")
    archive_base = create_archive_structure()
    
    # Move obsolete scripts to archive
    print("\n📦 Archiving obsolete scripts...")
    moved_files, skipped_files = move_scripts_to_archive(cleanup_plan, archive_base)
    
    # Reorganize root scripts
    print("\n🔄 Reorganizing utility scripts...")
    moved_scripts = update_root_scripts()
    
    # Clean empty directories
    print("\n🗑️ Cleaning empty directories...")
    removed_dirs = clean_empty_directories()
    
    # Generate report
    print("\n📋 Generating cleanup report...")
    report_path = generate_cleanup_report(moved_files, skipped_files, removed_dirs, moved_scripts)
    
    print(f"\n🎉 Script cleanup completed!")
    print(f"📊 Summary:")
    print(f"   - {len(moved_files)} files archived")
    print(f"   - {len(moved_scripts)} scripts reorganized") 
    print(f"   - {len(removed_dirs)} empty directories removed")
    print(f"   - Report: {report_path}")
    print(f"\n✅ Scripts organized and workspace cleaned!")

if __name__ == "__main__":
    main()
