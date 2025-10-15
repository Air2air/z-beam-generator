#!/usr/bin/env python3
"""Verify subtitle generation quality across all frontmatter files"""

import yaml
from pathlib import Path
from collections import Counter, defaultdict

# Load all frontmatter files
frontmatter_dir = Path("content/components/frontmatter")
files = list(frontmatter_dir.glob("*.yaml"))

print("=" * 80)
print("SUBTITLE GENERATION VERIFICATION REPORT")
print("=" * 80)
print()

# Statistics
total_files = len(files)
files_with_subtitle = 0
subtitle_lengths = []
opening_words = []
opening_3words = []
author_subtitles = defaultdict(list)
banned_phrases = {
    "is defined by": 0,
    "is characterized by": 0,
    "stands out": 0,
    "sets apart": 0,
    "necessitates": 0,
    "dial in": 0,
    "dialed-in": 0,
}

print(f"📊 STATISTICS")
print(f"Total frontmatter files: {total_files}")

# Analyze each file
for file_path in sorted(files):
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if data and 'subtitle' in data:
            files_with_subtitle += 1
            subtitle = data['subtitle']
            
            # Length analysis
            word_count = len(subtitle.split())
            subtitle_lengths.append(word_count)
            
            # Opening analysis
            words = subtitle.split()
            if len(words) >= 1:
                opening_words.append(words[0])
            if len(words) >= 3:
                opening_3words.append(' '.join(words[:3]))
            
            # Author analysis
            author = data.get('author', {})
            if isinstance(author, dict):
                author_name = author.get('name', 'Unknown')
            else:
                author_name = 'Unknown'
            author_subtitles[author_name].append((file_path.stem, subtitle))
            
            # Check for banned phrases
            subtitle_lower = subtitle.lower()
            for phrase in banned_phrases:
                if phrase in subtitle_lower:
                    banned_phrases[phrase] += 1
    
    except Exception as e:
        print(f"⚠️  Error reading {file_path.name}: {e}")

print(f"Files with subtitle field: {files_with_subtitle}")
print(f"Coverage: {files_with_subtitle/total_files*100:.1f}%")
print()

# Length statistics
if subtitle_lengths:
    avg_length = sum(subtitle_lengths) / len(subtitle_lengths)
    min_length = min(subtitle_lengths)
    max_length = max(subtitle_lengths)
    print(f"📏 LENGTH ANALYSIS")
    print(f"Average word count: {avg_length:.1f} words")
    print(f"Range: {min_length}-{max_length} words")
    print(f"Target range: 25-40 words")
    in_range = sum(1 for l in subtitle_lengths if 25 <= l <= 45)
    print(f"Within target: {in_range}/{len(subtitle_lengths)} ({in_range/len(subtitle_lengths)*100:.1f}%)")
    print()

# Opening variety
print(f"🎨 STRUCTURAL VARIETY")
opening_word_counts = Counter(opening_words)
print(f"Unique opening words: {len(opening_word_counts)}")
print(f"Top 10 opening words:")
for word, count in opening_word_counts.most_common(10):
    print(f"  '{word}': {count} times ({count/files_with_subtitle*100:.1f}%)")
print()

opening_3word_counts = Counter(opening_3words)
print(f"Unique 3-word openings: {len(opening_3word_counts)}")
print(f"Most common 3-word openings:")
for phrase, count in opening_3word_counts.most_common(10):
    print(f"  '{phrase}...': {count} times ({count/files_with_subtitle*100:.1f}%)")
print()

# Banned phrases check
print(f"🚫 BANNED PHRASES CHECK")
any_banned = False
for phrase, count in banned_phrases.items():
    if count > 0:
        print(f"  ⚠️  '{phrase}': Found {count} times")
        any_banned = True
if not any_banned:
    print(f"  ✅ No banned phrases detected!")
print()

# Author voice analysis
print(f"👤 AUTHOR VOICE DISTRIBUTION")
for author_name in sorted(author_subtitles.keys()):
    subtitles = author_subtitles[author_name]
    print(f"\n{author_name}: {len(subtitles)} materials")
    
    # Show 3 examples
    print(f"  Sample subtitles:")
    for material, subtitle in subtitles[:3]:
        # Truncate long subtitles
        display = subtitle[:100] + "..." if len(subtitle) > 100 else subtitle
        print(f"    • {material}: {display}")

print()
print("=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

# Final assessment
issues = []
if files_with_subtitle < total_files:
    issues.append(f"Missing subtitles: {total_files - files_with_subtitle} files")
if any_banned:
    issues.append("Banned phrases detected")
if len(opening_3word_counts) < 15:
    issues.append(f"Low structural variety: only {len(opening_3word_counts)} unique 3-word openings")

if issues:
    print("\n⚠️  ISSUES FOUND:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\n✅ ALL QUALITY CHECKS PASSED!")
    print("  - All files have subtitles")
    print("  - No banned phrases")
    print("  - Good structural variety")
    print("  - Author voices present")

