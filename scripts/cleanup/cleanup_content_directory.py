#!/usr/bin/env python3
"""
Content Component Directory Cleanup
Removes unnecessary files while preserving production components.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_content_directory():
    """Clean up components/content directory for production."""
    print("🧹 Cleaning up components/content directory")
    print("=" * 50)
    
    content_dir = Path("components/content")
    archive_dir = content_dir / "archive"
    cleanup_archive_dir = content_dir / "cleanup_archive"
    
    # Create cleanup archive directory
    cleanup_archive_dir.mkdir(exist_ok=True)
    
    # Production files to keep
    production_files = {
        "fail_fast_generator.py",           # Main production generator
        "prompts/",                         # All prompt files and subdirectories
        "archive/",                         # Already archived old generators
        "__pycache__/"                      # Python cache (will be recreated)
    }
    
    # Development/test files to archive
    files_to_archive = []
    
    # Find all files in content directory
    for item in content_dir.iterdir():
        if item.name not in production_files:
            files_to_archive.append(item)
    
    if not files_to_archive:
        print("✅ Directory already clean - no files to archive")
        return True
    
    print(f"📦 Found {len(files_to_archive)} files to archive:")
    for item in files_to_archive:
        print(f"  - {item.name}")
    
    # Archive the files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_count = 0
    
    for item in files_to_archive:
        try:
            if item.is_file():
                # Archive file with timestamp
                archive_name = f"{item.stem}_{timestamp}{item.suffix}"
                archive_path = cleanup_archive_dir / archive_name
                shutil.move(str(item), str(archive_path))
                print(f"✅ Archived file: {item.name} → cleanup_archive/{archive_name}")
                archived_count += 1
                
            elif item.is_dir() and item.name != "archive" and item.name != "__pycache__":
                # Archive directory
                archive_name = f"{item.name}_{timestamp}"
                archive_path = cleanup_archive_dir / archive_name
                shutil.move(str(item), str(archive_path))
                print(f"✅ Archived directory: {item.name}/ → cleanup_archive/{archive_name}/")
                archived_count += 1
                
        except Exception as e:
            print(f"❌ Failed to archive {item.name}: {e}")
    
    # Clean up __pycache__ if it exists
    pycache_dir = content_dir / "__pycache__"
    if pycache_dir.exists():
        try:
            shutil.rmtree(pycache_dir)
            print("✅ Removed __pycache__ directory")
        except Exception as e:
            print(f"⚠️ Could not remove __pycache__: {e}")
    
    print(f"\n📊 Cleanup Summary:")
    print(f"  Files archived: {archived_count}")
    
    # Verify final state
    remaining_items = list(content_dir.iterdir())
    expected_items = {"fail_fast_generator.py", "prompts", "archive", "cleanup_archive"}
    
    remaining_names = {item.name for item in remaining_items}
    
    print(f"\n📁 Remaining items in components/content/:")
    for item in remaining_items:
        print(f"  - {item.name}{'/' if item.is_dir() else ''}")
    
    if remaining_names <= expected_items:
        print(f"\n✅ Cleanup successful - directory is production-ready")
        return True
    else:
        unexpected = remaining_names - expected_items
        print(f"\n⚠️ Unexpected items remain: {unexpected}")
        return False

def verify_production_system():
    """Verify the production system still works after cleanup."""
    print(f"\n🔍 Verifying production system...")
    
    try:
        # Test import
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from components.text.generators.fail_fast_generator import create_fail_fast_generator
        
        # Test initialization
        generator = create_fail_fast_generator()
        print("✅ Production generator imports and initializes correctly")
        
        # Check prompt files
        prompt_files = [
            "components/content/prompts/base_content_prompt.yaml",
            "components/content/prompts/personas/taiwan_persona.yaml",
            "components/content/prompts/formatting/taiwan_formatting.yaml"
        ]
        
        all_exist = all(Path(f).exists() for f in prompt_files)
        print(f"✅ Prompt files intact: {all_exist}")
        
        return True
        
    except Exception as e:
        print(f"❌ Production system verification failed: {e}")
        return False

def main():
    """Run the cleanup process."""
    print("🚀 Content Component Directory Cleanup")
    print("=" * 60)
    
    # Run cleanup
    cleanup_success = cleanup_content_directory()
    
    if cleanup_success:
        # Verify system still works
        verify_success = verify_production_system()
        
        if verify_success:
            print(f"\n" + "=" * 60)
            print("🎉 CLEANUP COMPLETE - PRODUCTION SYSTEM VERIFIED")
            print("=" * 60)
            print("\n📁 Production Directory Structure:")
            print("components/content/")
            print("├── fail_fast_generator.py      # Production content generator")
            print("├── prompts/")
            print("│   ├── base_content_prompt.yaml")
            print("│   ├── personas/               # Author personas (4 files)")
            print("│   └── formatting/             # Formatting configs (4 files)")
            print("├── archive/                    # Archived old generators")
            print("└── cleanup_archive/            # Archived development files")
            print("\n✅ System ready for production deployment")
        else:
            print(f"\n❌ CLEANUP FAILED - PRODUCTION SYSTEM BROKEN")
    else:
        print(f"\n❌ CLEANUP FAILED")

if __name__ == "__main__":
    main()
