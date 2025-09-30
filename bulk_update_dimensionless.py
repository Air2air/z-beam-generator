#!/usr/bin/env python3
"""
Bulk Update Script: Replace dimensionless units with empty strings
Updates all YAML frontmatter files to use Option 1 (empty string for dimensionless units).
"""

import sys
import re
from pathlib import Path

def bulk_update_dimensionless_units():
    """Update all YAML files to replace 'dimensionless' with empty string."""
    
    print("🔧 Bulk Updating Dimensionless Units")
    print("=" * 50)
    
    # Target directory
    frontmatter_dir = Path("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print("❌ Frontmatter directory not found")
        return False
    
    # Find all YAML files
    yaml_files = list(frontmatter_dir.glob("*.yaml")) + list(frontmatter_dir.glob("*.yml"))
    
    print(f"📁 Found {len(yaml_files)} YAML files to process")
    
    updated_files = []
    failed_files = []
    
    # Patterns to replace
    patterns = [
        (r'unit: dimensionless', 'unit: ""'),
        (r'unit: "dimensionless"', 'unit: ""'),
        (r"unit: 'dimensionless'", 'unit: ""'),
        (r'unit: dimensionless \(.*?\)', 'unit: ""'),  # Handle "dimensionless (0-1)" etc.
        (r'unit: dimensionless at .*', 'unit: ""'),    # Handle "dimensionless at 1064nm" etc.
    ]
    
    for yaml_file in yaml_files:
        try:
            print(f"🔄 Processing {yaml_file.name}...")
            
            # Read file
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Track if any changes were made
            original_content = content
            changes_made = 0
            
            # Apply all replacement patterns
            for pattern, replacement in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    changes_made += len(matches)
            
            # Write back if changes were made
            if changes_made > 0:
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append((yaml_file.name, changes_made))
                print(f"   ✅ Updated {changes_made} occurrences")
            else:
                print(f"   ⚪ No changes needed")
                
        except Exception as e:
            print(f"   ❌ Failed to process {yaml_file.name}: {e}")
            failed_files.append((yaml_file.name, str(e)))
    
    # Summary
    print(f"\\n📊 Bulk Update Results:")
    print(f"   ✅ Files updated: {len(updated_files)}")
    print(f"   ⚪ Files unchanged: {len(yaml_files) - len(updated_files) - len(failed_files)}")
    print(f"   ❌ Files failed: {len(failed_files)}")
    
    if updated_files:
        print(f"\\n📝 Updated files:")
        for filename, count in updated_files:
            print(f"   • {filename}: {count} changes")
    
    if failed_files:
        print(f"\\n❌ Failed files:")
        for filename, error in failed_files:
            print(f"   • {filename}: {error}")
    
    total_changes = sum(count for _, count in updated_files)
    print(f"\\n🎯 Total changes made: {total_changes}")
    
    return len(failed_files) == 0

def verify_updates():
    """Verify that updates were successful."""
    print("\\n🔍 Verifying Updates")
    print("=" * 25)
    
    frontmatter_dir = Path("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/frontmatter")
    yaml_files = list(frontmatter_dir.glob("*.yaml")) + list(frontmatter_dir.glob("*.yml"))
    
    remaining_dimensionless = []
    
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for remaining "dimensionless" occurrences
            if 'dimensionless' in content:
                # Count occurrences
                count = content.count('dimensionless')
                remaining_dimensionless.append((yaml_file.name, count))
        
        except Exception as e:
            print(f"❌ Error checking {yaml_file.name}: {e}")
    
    if remaining_dimensionless:
        print(f"⚠️ Found {len(remaining_dimensionless)} files with remaining 'dimensionless':")
        for filename, count in remaining_dimensionless:
            print(f"   • {filename}: {count} occurrences")
        return False
    else:
        print("✅ All frontmatter files successfully updated!")
        return True

def main():
    """Run the bulk update process."""
    
    print("🚀 Dimensionless Units Bulk Update")
    print("=" * 60)
    print("🎯 Goal: Replace all 'dimensionless' units with empty strings (Option 1)")
    print()
    
    # Run bulk update
    update_success = bulk_update_dimensionless_units()
    
    # Verify updates
    verify_success = verify_updates()
    
    # Overall result
    print("\\n📊 FINAL RESULT")
    print("=" * 20)
    
    if update_success and verify_success:
        print("🎉 SUCCESS! All dimensionless units updated to empty strings")
        print("   ✅ Bulk update completed without errors")
        print("   ✅ Verification confirmed no remaining 'dimensionless' units")
        print("   ✅ Option 1 implementation complete")
        return True
    else:
        print("⚠️ PARTIAL SUCCESS - Some issues remain")
        if not update_success:
            print("   ❌ Some files failed to update")
        if not verify_success:
            print("   ❌ Some 'dimensionless' units remain")
        print("   🔧 Manual review may be required")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)