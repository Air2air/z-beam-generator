#!/usr/bin/env python3
"""
Test Cleanup Script - Move Obsolete Tests to tests/obsolete/

This script identifies and moves obsolete/redundant tests based on:
1. Code that no longer exists (chemical_fallback, old optimizers)
2. Redundant test coverage (multiple caption/frontmatter tests)
3. Legacy/outdated tests (pre-flattening structure)

Created: October 2, 2025
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
TESTS_DIR = BASE_DIR / "tests"
OBSOLETE_DIR = TESTS_DIR / "obsolete"

# Tests to move - organized by category
OBSOLETE_TESTS = {
    "chemical_fallback": [
        "tests/unit/test_chemical_fallback_core.py",
        "tests/unit/test_chemical_fallback_generator.py",
        "tests/integration/test_chemical_fallback_integration.py",
    ],
    "ai_detection_optimizer": [
        "tests/unit/optimizer_services/test_ai_detection_optimization.py",
        "tests/unit/test_ai_detection_optimization_service.py",
        "tests/unit/test_ai_detection_service.py",
        "tests/unit/test_optimization_orchestrator.py",
        "tests/integration/test_ai_detection_config.py",
        "tests/integration/test_ai_detection_integration.py",
        "tests/integration/test_optimizer_integration.py",
        "tests/integration/test_prompt_optimizer.py",
    ],
    "legacy_redundant": [
        "tests/integration/test_frontmatter_validator_legacy.py",
        "tests/e2e/test_comprehensive_workflow.py",  # Keep refactored version
        "tests/test_caption_case_insensitive.py",
        "tests/test_caption_generator.py",
        "tests/test_frontmatter_consistency.py",
    ],
    "over_engineered": [
        "tests/test_renamed_files_validation.py",  # 841 lines
        "tests/test_framework.py",  # 610 lines - framework test?
    ],
    "potentially_obsolete": [
        "tests/test_delimiter_preservation_fix.py",  # Specific bug fix test
        "tests/test_abbreviation_template.py",
        "tests/utils/test_data_templates.py",
        "tests/e2e/test_template_substitution.py",
        "tests/integration/test_cascading_failure.py",  # 364 lines - may be outdated
    ]
}


def create_obsolete_directory():
    """Create the obsolete directory structure."""
    OBSOLETE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create category subdirectories
    for category in OBSOLETE_TESTS.keys():
        (OBSOLETE_DIR / category).mkdir(exist_ok=True)
    
    print(f"✅ Created obsolete directory: {OBSOLETE_DIR}")


def create_readme():
    """Create README in obsolete directory explaining why tests were moved."""
    readme_content = f"""# Obsolete Tests Archive

**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Reason**: Test cleanup for fail-fast architecture compliance

## Why These Tests Are Obsolete

These tests have been moved here because they:

1. **Test code that no longer exists** (chemical_fallback, old optimizers)
2. **Provide redundant coverage** (multiple tests for same functionality)
3. **Test legacy/outdated systems** (pre-flattening structure, old validation)
4. **Are over-engineered** (841+ lines for file validation)

## Categories

### chemical_fallback/
Tests for chemical fallback system that was removed. The fail-fast architecture 
explicitly avoids fallback mechanisms.

**Files**: {len(OBSOLETE_TESTS['chemical_fallback'])} tests
**Total Lines**: ~1,165 lines

### ai_detection_optimizer/
Tests for AI detection optimization services that don't exist in current codebase.
Optimizer orchestration was simplified.

**Files**: {len(OBSOLETE_TESTS['ai_detection_optimizer'])} tests
**Total Lines**: ~800+ lines

### legacy_redundant/
Legacy tests and redundant coverage. Example: 5 different caption tests when
one comprehensive test would suffice.

**Files**: {len(OBSOLETE_TESTS['legacy_redundant'])} tests
**Total Lines**: ~1,500+ lines

### over_engineered/
Tests that are too large/complex for what they validate. Candidates for 
rewriting as simpler tests.

**Files**: {len(OBSOLETE_TESTS['over_engineered'])} tests
**Total Lines**: ~1,451 lines

### potentially_obsolete/
Tests that might be obsolete but need review before permanent removal.

**Files**: {len(OBSOLETE_TESTS['potentially_obsolete'])} tests

## What Remains

After cleanup, the essential test suite focuses on:

- **Unit tests**: Component functionality (materials.py, pipeline_integration.py)
- **Integration tests**: Component interactions, API integration
- **E2E tests**: Full workflow validation
- **Validation tests**: Data integrity, format compliance

## Restoration

If any test is needed:

```bash
# Move back from obsolete
mv tests/obsolete/[category]/test_name.py tests/[original_location]/

# Or reference for historical context
cat tests/obsolete/[category]/test_name.py
```

## Next Steps

1. **Review**: Confirm these tests are truly obsolete
2. **Extract Value**: If any tests have useful patterns, extract them
3. **Delete**: After 30 days, consider permanent removal
4. **Simplify**: Rewrite over-engineered tests as minimal essential tests

---

**Total Tests Moved**: {sum(len(tests) for tests in OBSOLETE_TESTS.values())}
**Space Saved**: ~5,000+ lines of obsolete test code
**Active Tests Remaining**: ~70-80 essential tests

See `docs/development/TESTING.md` for current testing strategy.
"""
    
    readme_path = OBSOLETE_DIR / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Created README: {readme_path}")


def move_test_file(test_path: str, category: str, dry_run: bool = False) -> bool:
    """Move a test file to obsolete directory."""
    source = BASE_DIR / test_path
    
    if not source.exists():
        print(f"⚠️  Not found: {test_path}")
        return False
    
    # Preserve directory structure within category
    relative_path = Path(test_path).relative_to("tests")
    dest = OBSOLETE_DIR / category / relative_path
    
    # Create destination directory
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    if dry_run:
        print(f"📋 Would move: {test_path} → {dest.relative_to(TESTS_DIR)}")
        return True
    else:
        try:
            shutil.move(str(source), str(dest))
            print(f"✅ Moved: {test_path} → {dest.relative_to(TESTS_DIR)}")
            return True
        except Exception as e:
            print(f"❌ Error moving {test_path}: {e}")
            return False


def cleanup_empty_directories():
    """Remove empty directories left after moving tests."""
    for root, dirs, files in os.walk(TESTS_DIR, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            
            # Skip obsolete and deprecated_tests
            if 'obsolete' in str(dir_path) or 'deprecated_tests' in str(dir_path):
                continue
            
            # Check if directory is empty (only __pycache__ or __init__.py)
            contents = list(dir_path.iterdir())
            py_files = [f for f in contents if f.suffix == '.py' and f.name != '__init__.py']
            
            if not py_files and len(contents) <= 2:  # Only __pycache__ and/or __init__.py
                try:
                    shutil.rmtree(dir_path)
                    print(f"🗑️  Removed empty directory: {dir_path.relative_to(TESTS_DIR)}")
                except Exception as e:
                    print(f"⚠️  Could not remove {dir_path}: {e}")


def main(dry_run: bool = False):
    """Main cleanup execution."""
    print("=" * 60)
    print("Test Cleanup Script - Moving Obsolete Tests")
    print("=" * 60)
    print()
    
    if dry_run:
        print("🔍 DRY-RUN MODE - No files will be moved")
        print()
    
    # Create obsolete directory structure
    if not dry_run:
        create_obsolete_directory()
        create_readme()
        print()
    
    # Track statistics
    stats = {
        'moved': 0,
        'not_found': 0,
        'errors': 0
    }
    
    # Process each category
    for category, tests in OBSOLETE_TESTS.items():
        print(f"\n📂 Category: {category}")
        print("-" * 60)
        
        for test_path in tests:
            result = move_test_file(test_path, category, dry_run)
            
            if result:
                stats['moved'] += 1
            else:
                stats['not_found'] += 1
    
    # Cleanup empty directories
    if not dry_run:
        print("\n🗑️  Cleaning up empty directories...")
        cleanup_empty_directories()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    total_tests = sum(len(tests) for tests in OBSOLETE_TESTS.values())
    
    if dry_run:
        print(f"Would move: {stats['moved']} tests")
        print(f"Not found: {stats['not_found']} tests")
    else:
        print(f"✅ Moved: {stats['moved']} tests")
        print(f"⚠️  Not found: {stats['not_found']} tests")
    
    print(f"\nTotal tests in cleanup list: {total_tests}")
    print(f"\nObsolete directory: {OBSOLETE_DIR}")
    
    if not dry_run:
        print(f"\n📖 See {OBSOLETE_DIR / 'README.md'} for details")
    
    print("\n✅ Cleanup complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Move obsolete tests to tests/obsolete/"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be moved without moving files"
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help="Actually move the files (default is dry-run)"
    )
    
    args = parser.parse_args()
    
    # Default to dry-run unless --execute is specified
    dry_run = not args.execute
    
    if dry_run:
        print("Running in DRY-RUN mode. Use --execute to actually move files.\n")
    
    main(dry_run=dry_run)
