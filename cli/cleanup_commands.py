#!/usr/bin/env python3
"""
Z-Beam CLI Cleanup Commands

Extracted cleanup functionality from run.py for better modularity.
Handles all cleanup-related operations including content cleanup,
scan operations, and root directory organization.
"""

import shutil
from pathlib import Path


def clean_content_components():
    """Clean all generated content files from content/components subfolders."""

    print("🗂️  CONTENT COMPONENTS CLEANUP")
    print("=" * 50)
    print("Removing all generated content files from component subfolders...")
    print("=" * 50)

    try:
        content_components_dir = Path("content/components")

        if not content_components_dir.exists():
            print("❌ Content/components directory not found!")
            return False

        # Get all component subdirectories
        component_dirs = [d for d in content_components_dir.iterdir() if d.is_dir()]

        if not component_dirs:
            print("📁 No component subdirectories found.")
            return True

        total_files_removed = 0
        total_dirs_processed = 0

        for component_dir in sorted(component_dirs):
            component_name = component_dir.name
            print(f"\n📂 Processing {component_name}/")

            # Find all markdown files in this component directory
            md_files = list(component_dir.glob("*.md"))

            if not md_files:
                print(f"   📄 No files to remove")
                continue

            files_removed = 0
            for md_file in md_files:
                try:
                    md_file.unlink()  # Delete the file
                    print(f"   🗑️  Removed: {md_file.name}")
                    files_removed += 1
                except Exception as e:
                    print(f"   ❌ Error removing {md_file.name}: {e}")

            total_files_removed += files_removed
            total_dirs_processed += 1
            print(f"   ✅ {files_removed} files removed from {component_name}/")

        # Summary
        print("\n📊 CLEANUP COMPLETE")
        print("=" * 50)
        print(f"📁 Directories processed: {total_dirs_processed}")
        print(f"🗑️  Total files removed: {total_files_removed}")

        if total_files_removed > 0:
            print(
                f"\n✅ Successfully cleaned {total_files_removed} files from {total_dirs_processed} component directories!"
            )
            print(
                "💡 Content/components directories are now ready for fresh generation."
            )
        else:
            print("\n📝 No files found to remove. Directories are already clean.")

        return True

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False


def run_cleanup_scan():
    """Run comprehensive cleanup scan (dry-run only)."""
    print("🧹 Z-BEAM CLEANUP SCAN")
    print("=" * 50)
    print("Scanning for cleanup opportunities (dry-run mode)...")
    print("=" * 50)
    
    try:
        # Import standalone cleanup manager (decoupled from tests)
        from cleanup.cleanup_manager import CleanupManager
        
        # Initialize cleanup manager in safe dry-run mode
        cleanup_manager = CleanupManager(Path.cwd(), dry_run=True)
        
        # Run comprehensive cleanup scan
        results = cleanup_manager.scan()
        
        # Display results
        print("\n📊 CLEANUP SCAN RESULTS")
        print("=" * 50)
        
        total_issues = results['total_issues']
        for category, items in results['categories'].items():
            count = len(items) if isinstance(items, list) else 0
            
            category_name = category.replace('_', ' ').title()
            print(f"📋 {category_name}: {count} items")
            
            if count > 0 and count <= 5:  # Show details for small lists
                for item_path, reason in items[:5]:
                    print(f"   • {item_path} - {reason}")
            elif count > 5:
                for item_path, reason in items[:3]:
                    print(f"   • {item_path} - {reason}")
                print(f"   ... and {count - 3} more items")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total cleanup opportunities: {total_issues}")
        
        if total_issues == 0:
            print("   ✅ No cleanup needed - project is clean!")
        elif total_issues <= 10:
            print("   🟡 Minor cleanup opportunities found")
        else:
            print("   🔴 Significant cleanup opportunities found")
        
        print(f"\n💡 NEXT STEPS:")
        if total_issues > 0:
            print("   • Review the items listed above")
            print("   • Run --cleanup-report for detailed analysis")
            print("   • Use --clean to remove generated content files")
        else:
            print("   • Project is clean, no action needed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing cleanup system: {e}")
        print("   Make sure tests/test_cleanup.py is available")
        return False
    except Exception as e:
        print(f"❌ Error during cleanup scan: {e}")
        return False


def run_cleanup_report():
    """Generate comprehensive cleanup report."""
    print("📋 Z-BEAM CLEANUP REPORT GENERATION")
    print("=" * 50)
    print("Generating comprehensive cleanup report...")
    print("=" * 50)
    
    try:
        # Import standalone cleanup manager (decoupled from tests)
        from cleanup.cleanup_manager import CleanupManager
        
        # Initialize cleanup manager in safe dry-run mode
        cleanup_manager = CleanupManager(Path.cwd(), dry_run=True)
        
        # Run comprehensive cleanup scan
        report_path = cleanup_manager.generate_report()
        results = cleanup_manager.scan()
        
        # Display summary
        print("\n📊 CLEANUP REPORT SUMMARY")
        print("=" * 50)
        
        for category, items in results['categories'].items():
            count = len(items) if isinstance(items, list) else 0
            category_name = category.replace('_', ' ').title()
            print(f"📋 {category_name}: {count} items")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total cleanup opportunities: {results['total_issues']}")
        print(f"   Report timestamp: {results['timestamp']}")
        print(f"   Dry-run mode: True")
        
        print(f"\n💾 REPORT SAVED:")
        print(f"   File: {report_path}")
        print(f"   Size: {Path(report_path).stat().st_size} bytes")
        
        print(f"\n💡 USAGE:")
        print("   • Review cleanup/cleanup_report.json for detailed analysis")
        print("   • Use --cleanup-scan for quick overview")
        print("   • Use --clean to remove generated content files")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing cleanup system: {e}")
        print("   Make sure tests/test_cleanup.py is available")
        return False
    except Exception as e:
        print(f"❌ Error generating cleanup report: {e}")
        return False


def run_root_cleanup():
    """Clean up root directory by organizing files into appropriate subdirectories."""
    print("🧹 ROOT DIRECTORY CLEANUP")
    print("=" * 50)
    print("Organizing root directory files into appropriate subdirectories...")
    print("=" * 50)
    
    try:
        root_dir = Path(".")
        
        # Define cleanup rules - where to move different file types
        cleanup_rules = {
            # Documentation files - already mostly moved to docs/
            "docs": {
                "patterns": ["*.md"],
                "exclude": ["README.md"],  # Keep README.md in root
                "description": "Documentation files"
            },
            
            # Test and debug files  
            "tests": {
                "patterns": ["test_*.py", "debug_*.py", "*_test.py", "test.py", "*verification*.py"],
                "exclude": [],
                "description": "Test and debug files"
            },
            
            # Utility and shell scripts
            "scripts": {
                "patterns": [
                    "*_material.py", "update_*.py", "*_labels.py", "*enhancement*.py", 
                    "*.sh"
                ],
                "exclude": ["run.py", "z_beam_generator.py"],  # Keep main scripts in root
                "description": "Utility, maintenance and shell scripts"
            },
            
            # Cleanup utilities
            "cleanup": {
                "patterns": ["cleanup_*.py", "*cleanup*.py"],
                "exclude": [],
                "description": "Cleanup utility scripts"
            },
            
            # Temporary and generated files to delete
            "delete": {
                "patterns": [
                    "*.pyc", "*.pyo", "__pycache__", ".pytest_cache",
                    "*.tmp", "*.temp", "*~", ".DS_Store",
                    "cleanup_report.json"  # Will be regenerated in cleanup/ folder
                ],
                "exclude": [],
                "description": "Temporary and cache files"
            }
        }
        
        moved_files = {}
        deleted_files = []
        skipped_files = []
        
        # Process each cleanup rule
        for target_dir, rule in cleanup_rules.items():
            moved_files[target_dir] = []
            
            if target_dir == "delete":
                # Special handling for deletion
                for pattern in rule["patterns"]:
                    for file_path in root_dir.glob(pattern):
                        if file_path.is_file() and file_path.name not in rule["exclude"]:
                            try:
                                file_path.unlink()
                                deleted_files.append(file_path.name)
                                print(f"   🗑️  Deleted: {file_path.name}")
                            except Exception as e:
                                print(f"   ❌ Error deleting {file_path.name}: {e}")
                        elif file_path.is_dir() and file_path.name not in rule["exclude"]:
                            try:
                                shutil.rmtree(file_path)
                                deleted_files.append(f"{file_path.name}/")
                                print(f"   🗑️  Deleted directory: {file_path.name}/")
                            except Exception as e:
                                print(f"   ❌ Error deleting directory {file_path.name}: {e}")
                continue
            
            # Create target directory if it doesn't exist
            target_path = Path(target_dir)
            if not target_path.exists():
                target_path.mkdir(parents=True, exist_ok=True)
                print(f"   📁 Created directory: {target_dir}/")
            
            # Find and move files matching patterns
            for pattern in rule["patterns"]:
                for file_path in root_dir.glob(pattern):
                    # Skip if it's a directory or in exclude list
                    if not file_path.is_file() or file_path.name in rule["exclude"]:
                        if file_path.name in rule["exclude"]:
                            skipped_files.append(f"{file_path.name} (excluded)")
                        continue
                    
                    # Skip if file is already in target directory
                    if file_path.parent.name == target_dir:
                        continue
                    
                    # Move file to target directory
                    dest_path = target_path / file_path.name
                    
                    # Handle name conflicts
                    counter = 1
                    original_dest = dest_path
                    while dest_path.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_path = target_path / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    try:
                        file_path.rename(dest_path)
                        moved_files[target_dir].append(f"{file_path.name} → {dest_path.name}")
                        print(f"   📦 Moved: {file_path.name} → {target_dir}/{dest_path.name}")
                    except Exception as e:
                        print(f"   ❌ Error moving {file_path.name}: {e}")
        
        # Display summary
        print("\n📊 ROOT CLEANUP SUMMARY")
        print("=" * 50)
        
        total_actions = sum(len(files) for files in moved_files.values()) + len(deleted_files)
        
        for target_dir, files in moved_files.items():
            if files:
                rule_desc = cleanup_rules[target_dir]["description"]
                print(f"📁 {target_dir}/ ({rule_desc}): {len(files)} files")
                for file_move in files[:3]:  # Show first 3
                    print(f"   • {file_move}")
                if len(files) > 3:
                    print(f"   ... and {len(files) - 3} more files")
        
        if deleted_files:
            print(f"🗑️  Deleted: {len(deleted_files)} items")
            for item in deleted_files[:5]:  # Show first 5
                print(f"   • {item}")
            if len(deleted_files) > 5:
                print(f"   ... and {len(deleted_files) - 5} more items")
        
        if skipped_files:
            print(f"⏭️  Skipped: {len(skipped_files)} files")
            for item in skipped_files[:3]:  # Show first 3
                print(f"   • {item}")
            if len(skipped_files) > 3:
                print(f"   ... and {len(skipped_files) - 3} more files")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total actions performed: {total_actions}")
        
        if total_actions == 0:
            print("   ✅ Root directory is already clean!")
        elif total_actions <= 5:
            print("   ✅ Minor cleanup completed")
        else:
            print("   ✅ Major cleanup completed - root directory organized!")
        
        print("\n💡 NEXT STEPS:")
        print("   • Review organized files in their new locations")
        print("   • Update any import paths if needed")  
        print("   • Use --cleanup-scan to verify no issues remain")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during root cleanup: {e}")
        return False
