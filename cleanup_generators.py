#!/usr/bin/env python3
"""
Cleanup Script for Content Generator System
Archives unused generator files and keeps only the production fail-fast generator.
"""

import shutil
from pathlib import Path
from datetime import datetime

def cleanup_generators():
    """Archive unused generator files."""
    print("🧹 Content Generator System Cleanup")
    print("=" * 40)
    
    content_dir = Path("components/content")
    archive_dir = content_dir / "archive"
    
    # Create archive directory
    archive_dir.mkdir(exist_ok=True)
    
    # Files to archive (keep only fail_fast_generator.py)
    files_to_archive = [
        "generator.py",
        "enhanced_generator.py", 
        "optimized_enhanced_generator.py"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    archived_count = 0
    
    for filename in files_to_archive:
        source_file = content_dir / filename
        
        if source_file.exists():
            # Create timestamped archive name
            file_path = Path(filename)
            archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            archive_file = archive_dir / archive_name
            
            try:
                shutil.move(str(source_file), str(archive_file))
                print(f"✅ Archived: {filename} → archive/{archive_name}")
                archived_count += 1
            except Exception as e:
                print(f"❌ Failed to archive {filename}: {e}")
        else:
            print(f"⚠️  File not found: {filename}")
    
    print(f"\n📊 Summary: {archived_count} files archived")
    
    # Verify only fail_fast_generator.py remains
    remaining_generators = list(content_dir.glob("*generator*.py"))
    
    if len(remaining_generators) == 1 and "fail_fast" in remaining_generators[0].name:
        print("✅ Cleanup successful - only fail_fast_generator.py remains")
        return True
    else:
        print(f"⚠️  Unexpected generators remain: {[g.name for g in remaining_generators]}")
        return False

if __name__ == "__main__":
    cleanup_generators()
