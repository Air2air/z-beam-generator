#!/usr/bin/env python3
"""
Validation Script: Dimensionless Unit Updates
Verifies that all "dimensionless" units have been replaced with empty strings.
"""

import subprocess
import sys
from pathlib import Path

def check_dimensionless_usage():
    """Check for remaining 'dimensionless' usage in key files."""
    
    print("🔍 Validating Dimensionless Unit Updates")
    print("=" * 50)
    
    # Key file patterns to check
    patterns_to_check = [
        "**/*.yaml",
        "**/*.yml", 
        "components/**/*.py",
        "generators/**/*.py",
        "stages/**/*.py"
    ]
    
    issues_found = []
    
    for pattern in patterns_to_check:
        print(f"📂 Checking {pattern}...")
        
        try:
            # Use grep to find dimensionless occurrences
            result = subprocess.run(
                ["grep", "-r", "-n", "--include=" + pattern.split('/')[-1], "dimensionless", "."],
                cwd="/Users/todddunning/Desktop/Z-Beam/z-beam-generator",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    # Filter out backup files and documentation
                    if not any(skip in line for skip in ['backup', 'docs/', 'README', '.md:']):
                        issues_found.append(line)
        
        except Exception as e:
            print(f"   ⚠️ Error checking {pattern}: {e}")
    
    print(f"\\n📊 Validation Results:")
    
    if issues_found:
        print(f"❌ Found {len(issues_found)} remaining 'dimensionless' occurrences:")
        for issue in issues_found:
            print(f"   📁 {issue}")
        print("\\n🔧 Action Required: Update these occurrences to use empty string (\"\") instead")
        return False
    else:
        print("✅ All 'dimensionless' units successfully updated to empty strings!")
        return True

def validate_crown_glass_update():
    """Validate that crown-glass file was updated correctly."""
    
    print("\\n🔬 Validating Crown Glass File Update")
    print("=" * 40)
    
    crown_glass_file = Path("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/frontmatter/crown-glass-laser-cleaning.yaml")
    
    if not crown_glass_file.exists():
        print("❌ Crown glass file not found")
        return False
    
    try:
        with open(crown_glass_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for dimensionless
        if 'dimensionless' in content:
            print("❌ Crown glass file still contains 'dimensionless'")
            return False
        
        # Check for refractive index with empty unit
        if 'refractiveIndex:' in content and 'unit: ""' in content:
            print("✅ Crown glass refractiveIndex correctly updated to empty unit")
            return True
        else:
            print("⚠️ Crown glass refractiveIndex unit may not be correctly updated")
            return False
            
    except Exception as e:
        print(f"❌ Error reading crown glass file: {e}")
        return False

def validate_categories_update():
    """Validate that Categories.yaml was updated correctly."""
    
    print("\\n📋 Validating Categories.yaml Update")
    print("=" * 35)
    
    categories_file = Path("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/Categories.yaml")
    
    if not categories_file.exists():
        print("❌ Categories.yaml file not found")
        return False
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for dimensionless
        if 'dimensionless' in content:
            print("❌ Categories.yaml still contains 'dimensionless'")
            print("   Found in content - manual review needed")
            return False
        
        # Check for empty unit strings in key properties
        expected_patterns = [
            'unit: ""',  # Should have empty string units
        ]
        
        found_patterns = sum(1 for pattern in expected_patterns if pattern in content)
        
        if found_patterns > 0:
            print(f"✅ Categories.yaml correctly updated - found {found_patterns} empty unit fields")
            return True
        else:
            print("⚠️ Categories.yaml may not have expected empty unit fields")
            return False
            
    except Exception as e:
        print(f"❌ Error reading Categories.yaml: {e}")
        return False

def main():
    """Run all validation checks."""
    
    print("🚀 Dimensionless Unit Update Validation")
    print("=" * 60)
    print()
    
    # Run validation checks
    checks = [
        ("File Content Check", check_dimensionless_usage),
        ("Crown Glass Update", validate_crown_glass_update), 
        ("Categories.yaml Update", validate_categories_update)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\\n📊 VALIDATION SUMMARY")
    print("=" * 25)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {check_name}")
    
    print(f"\\n📈 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\\n🎉 ALL VALIDATIONS PASSED!")
        print("   ✅ Dimensionless units successfully updated to empty strings")
        print("   ✅ Files are ready for use with Option 1 implementation")
    else:
        print("\\n⚠️ Some validations failed - manual review required")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)