#!/usr/bin/env python3
"""
Content Extraction and Optimization Fix Implementation

This script implements the critical fix for the optimization system treating 
logging metadata as content to be optimized.

Key fixes:
1. Clean existing files to extract only target content
2. Update optimization system to use content extraction
3. Provide clear content markers for future use
"""

import re
import logging
from pathlib import Path
from typing import Optional, List


def extract_target_content_only(file_content: str) -> str:
    """
    Extract only the target text content from a file, excluding all logging metadata.
    
    This is critical for optimization - we must only analyze the actual content,
    not the embedded version logs, AI analysis data, or iteration metadata.
    """
    # Define clear markers for content boundaries
    version_log_pattern = r'\n\n\nVersion Log - Generated:'
    ai_detection_pattern = r'\n\n---\nai_detection_analysis:'
    quality_analysis_pattern = r'\nquality_analysis:'
    frontmatter_pattern = r'^---\n.*?\n---\n'
    
    original_size = len(file_content)
    
    # Remove frontmatter first
    content = re.sub(frontmatter_pattern, '', file_content, flags=re.DOTALL)
    
    # Find the first occurrence of any logging marker
    markers = [
        (version_log_pattern, version_log_pattern),
        (ai_detection_pattern, ai_detection_pattern),
        (quality_analysis_pattern, quality_analysis_pattern)
    ]
    
    earliest_marker_pos = len(content)
    
    for pattern, _ in markers:
        match = re.search(pattern, content)
        if match:
            earliest_marker_pos = min(earliest_marker_pos, match.start())
    
    # Extract content up to the first logging marker
    if earliest_marker_pos < len(content):
        clean_content = content[:earliest_marker_pos].strip()
    else:
        clean_content = content.strip()
    
    # Additional cleanup: remove any remaining metadata patterns that may be embedded
    clean_content = re.sub(r"'length': \d+, 'score': [\d.]+, 'text': '.*?'", '', clean_content)
    clean_content = re.sub(r"sentences: \[.*?\]", '', clean_content, flags=re.DOTALL)
    clean_content = re.sub(r"failing_sentences_count: \d+", '', clean_content)
    clean_content = re.sub(r"provider: \"winston\"", '', clean_content)
    clean_content = re.sub(r"credits_used: \d+", '', clean_content)
    clean_content = re.sub(r"classification: \"[^\"]*\"", '', clean_content)
    clean_content = re.sub(r"confidence: [\d.]+", '', clean_content)
    clean_content = re.sub(r"processing_time: [\d.]+", '', clean_content)
    
    # Clean up any excessive whitespace
    clean_content = re.sub(r'\n{3,}', '\n\n', clean_content)
    clean_content = clean_content.strip()
    
    clean_size = len(clean_content)
    reduction_percent = ((original_size - clean_size) / original_size * 100) if original_size > 0 else 0
    
    print(f"   📏 Content extraction: {original_size:,} → {clean_size:,} chars ({reduction_percent:.1f}% reduction)")
    
    return clean_content


def clean_existing_files(file_paths: List[str]) -> None:
    """Clean existing files to remove embedded logging metadata."""
    print("🧹 Cleaning existing files to remove embedded logging metadata\n")
    
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"📄 Processing: {file_path}")
        
        # Read the full content
        with open(path, 'r', encoding='utf-8') as f:
            full_content = f.read()
        
        # Extract clean content
        clean_content = extract_target_content_only(full_content)
        
        if not clean_content or len(clean_content) < 50:
            print(f"   ⚠️  Warning: Very short content extracted ({len(clean_content)} chars)")
            continue
        
        # Create backup
        backup_path = path.with_suffix(path.suffix + '.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"   💾 Backup created: {backup_path}")
        
        # Save clean content
        with open(path, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        print(f"   ✅ Clean content saved")
        
        # Validate the cleaned file
        artifacts = [
            ("Version Log", "Version Log" in clean_content),
            ("AI Detection", "ai_detection_analysis" in clean_content),
            ("Winston data", "'score':" in clean_content),
            ("Sentence arrays", "sentences:" in clean_content)
        ]
        
        remaining_artifacts = [name for name, found in artifacts if found]
        if remaining_artifacts:
            print(f"   ⚠️  Remaining artifacts: {', '.join(remaining_artifacts)}")
        else:
            print(f"   ✅ No logging artifacts remaining")
        
        print()


def add_content_markers(content: str, material_name: str) -> str:
    """
    Add clear content markers to distinguish target content from metadata.
    
    This provides a future-proof way to identify content boundaries.
    """
    return f"""<!-- TARGET_CONTENT_START: {material_name} -->
{content}
<!-- TARGET_CONTENT_END: {material_name} -->"""


def extract_marked_content(file_content: str, material_name: str) -> str:
    """Extract content between content markers if they exist."""
    start_marker = f"<!-- TARGET_CONTENT_START: {material_name} -->"
    end_marker = f"<!-- TARGET_CONTENT_END: {material_name} -->"
    
    start_pos = file_content.find(start_marker)
    end_pos = file_content.find(end_marker)
    
    if start_pos != -1 and end_pos != -1:
        start_pos += len(start_marker)
        return file_content[start_pos:end_pos].strip()
    
    # Fallback to general extraction if markers not found
    return extract_target_content_only(file_content)


def main():
    """Main execution function."""
    print("🔧 Content Extraction and Optimization Fix Implementation\n")
    
    # Files to clean
    problematic_files = [
        "content/components/text/alumina-laser-cleaning.md",
        "content/components/text/aluminum-laser-cleaning.md"
    ]
    
    # Check if files exist
    existing_files = [f for f in problematic_files if Path(f).exists()]
    
    if not existing_files:
        print("❌ No problematic files found. The files may have already been cleaned.")
        return
    
    print(f"📋 Found {len(existing_files)} files to clean:")
    for file_path in existing_files:
        file_size = Path(file_path).stat().st_size
        print(f"   • {file_path} ({file_size:,} bytes)")
    print()
    
    # Ask for confirmation
    response = input("Do you want to proceed with cleaning these files? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Operation cancelled.")
        return
    
    # Clean the files
    clean_existing_files(existing_files)
    
    print("✅ Content extraction fix completed!")
    print("\nNext steps:")
    print("1. Test the optimization system with the cleaned files")
    print("2. Verify that only target content is being analyzed")
    print("3. Monitor future optimizations for proper content extraction")


if __name__ == "__main__":
    main()
