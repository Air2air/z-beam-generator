#!/usr/bin/env python3
"""
Demo Content Extraction Fix

Demonstrates how to extract only the target text content from files with embedded logging.
This addresses the critical issue where optimization is treating logging metadata as content.
"""

import re
from pathlib import Path
from typing import Optional


def extract_target_content(file_content: str) -> str:
    """
    Extract only the target text content from a file, excluding all logging metadata.
    
    Args:
        file_content: Full file content including potential logging data
        
    Returns:
        Clean text content without logging, version logs, or analysis metadata
    """
    # Define clear markers for content boundaries
    version_log_pattern = r'\n\n\nVersion Log - Generated:'
    ai_detection_pattern = r'\n\n---\nai_detection_analysis:'
    quality_analysis_pattern = r'\nquality_analysis:'
    frontmatter_pattern = r'^---\n.*?\n---\n'
    
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
    
    # Additional cleanup: remove any remaining metadata patterns
    # Remove embedded analysis data that might appear in sentences
    clean_content = re.sub(r"'length': \d+, 'score': [\d.]+, 'text': '.*?'", '', clean_content)
    clean_content = re.sub(r"sentences: \[.*?\]", '', clean_content, flags=re.DOTALL)
    clean_content = re.sub(r"failing_sentences_count: \d+", '', clean_content)
    clean_content = re.sub(r"provider: \"winston\"", '', clean_content)
    clean_content = re.sub(r"credits_used: \d+", '', clean_content)
    
    # Clean up any excessive whitespace
    clean_content = re.sub(r'\n{3,}', '\n\n', clean_content)
    clean_content = clean_content.strip()
    
    return clean_content


def demo_content_extraction():
    """Demonstrate the content extraction fix on actual files."""
    print("🔧 Content Extraction Fix Demo\n")
    
    # Test on the problematic files
    test_files = [
        "content/components/text/alumina-laser-cleaning.md",
        "content/components/text/aluminum-laser-cleaning.md"
    ]
    
    for file_path in test_files:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"📄 Processing: {file_path}")
        
        # Read the full content
        with open(full_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
        
        # Extract clean content
        clean_content = extract_target_content(full_content)
        
        # Show the difference
        print(f"   📏 Original size: {len(full_content):,} characters")
        print(f"   📏 Clean size: {len(clean_content):,} characters")
        print(f"   📊 Reduction: {((len(full_content) - len(clean_content)) / len(full_content) * 100):.1f}%")
        
        # Show first 200 chars of clean content
        preview = clean_content[:200] + "..." if len(clean_content) > 200 else clean_content
        print(f"   📝 Clean preview: {preview}")
        
        # Check for remaining logging artifacts
        artifacts = [
            ("Version Log", "Version Log" in clean_content),
            ("AI Detection", "ai_detection_analysis" in clean_content),
            ("Winston data", "'score':" in clean_content),
            ("Sentence arrays", "sentences:" in clean_content)
        ]
        
        print("   🔍 Remaining artifacts:")
        for artifact_name, found in artifacts:
            status = "❌ FOUND" if found else "✅ CLEAN"
            print(f"      {artifact_name}: {status}")
        
        print()


if __name__ == "__main__":
    demo_content_extraction()
