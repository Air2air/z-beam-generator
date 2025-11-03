#!/usr/bin/env python3
"""
Normalize Materials.yaml Structure

Standardizes field names and structures across all materials:
1. Caption: beforeText/afterText → before/after
2. FAQ: direct list → dict with questions key
3. Subtitle: dict → string (if needed)

This ensures the voice enhancement script can process all materials consistently.
"""

import sys
import yaml
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def normalize_caption(caption):
    """
    Normalize caption structure to use 'before' and 'after' keys.
    
    Args:
        caption: Caption dict with potential beforeText/afterText keys
        
    Returns:
        Normalized caption dict with before/after keys
    """
    if not isinstance(caption, dict):
        return caption
    
    normalized = {}
    
    # Convert beforeText → before
    if 'beforeText' in caption:
        normalized['before'] = caption['beforeText']
    elif 'before' in caption:
        normalized['before'] = caption['before']
    
    # Convert afterText → after
    if 'afterText' in caption:
        normalized['after'] = caption['afterText']
    elif 'after' in caption:
        normalized['after'] = caption['after']
    
    # Preserve other fields
    for key, value in caption.items():
        if key not in ['beforeText', 'afterText', 'before', 'after']:
            normalized[key] = value
    
    return normalized


def normalize_faq(faq):
    """
    Normalize FAQ structure to dict with questions key.
    
    Args:
        faq: FAQ as either direct list or dict with questions
        
    Returns:
        Normalized FAQ as dict with questions key
    """
    if isinstance(faq, dict) and 'questions' in faq:
        # Already normalized
        return faq
    elif isinstance(faq, list):
        # Convert direct list to dict with questions key
        return {'questions': faq}
    else:
        # Unknown structure, return as-is
        return faq


def normalize_subtitle(subtitle):
    """
    Normalize subtitle to string type.
    
    Args:
        subtitle: Subtitle as string or dict
        
    Returns:
        Normalized subtitle as string
    """
    if isinstance(subtitle, str):
        return subtitle
    elif isinstance(subtitle, dict):
        # Try to extract string from dict
        if 'text' in subtitle:
            return subtitle['text']
        elif 'content' in subtitle:
            return subtitle['content']
        else:
            # Return first string value found
            for value in subtitle.values():
                if isinstance(value, str):
                    return value
            return str(subtitle)
    else:
        return str(subtitle)


def normalize_materials_yaml(dry_run=False):
    """
    Normalize all materials in Materials.yaml.
    
    Args:
        dry_run: If True, only show what would change without saving
        
    Returns:
        Dict with normalization statistics
    """
    materials_path = Path('materials/data/Materials.yaml')
    
    print('🔧 NORMALIZING Materials.yaml STRUCTURE')
    print('=' * 70)
    print()
    
    # Load Materials.yaml
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials = data['materials']
    stats = {
        'total': len(materials),
        'caption_normalized': 0,
        'faq_normalized': 0,
        'subtitle_normalized': 0,
        'no_changes': 0
    }
    
    # Normalize each material
    for name, material in materials.items():
        changed = False
        
        # Normalize caption
        if 'caption' in material:
            old_caption = material['caption']
            if isinstance(old_caption, dict) and ('beforeText' in old_caption or 'afterText' in old_caption):
                material['caption'] = normalize_caption(old_caption)
                stats['caption_normalized'] += 1
                changed = True
                print(f'📸 {name}: Caption normalized (beforeText/afterText → before/after)')
        
        # Normalize FAQ
        if 'faq' in material:
            old_faq = material['faq']
            if isinstance(old_faq, list):
                material['faq'] = normalize_faq(old_faq)
                stats['faq_normalized'] += 1
                changed = True
                print(f'❓ {name}: FAQ normalized (list → dict with questions)')
        
        # Normalize subtitle
        if 'subtitle' in material:
            old_subtitle = material['subtitle']
            if isinstance(old_subtitle, dict):
                material['subtitle'] = normalize_subtitle(old_subtitle)
                stats['subtitle_normalized'] += 1
                changed = True
                print(f'🎭 {name}: Subtitle normalized (dict → string)')
        
        if not changed:
            stats['no_changes'] += 1
    
    print()
    print('📊 NORMALIZATION SUMMARY')
    print('=' * 70)
    print(f'Total materials: {stats["total"]}')
    print(f'Caption normalized: {stats["caption_normalized"]}')
    print(f'FAQ normalized: {stats["faq_normalized"]}')
    print(f'Subtitle normalized: {stats["subtitle_normalized"]}')
    print(f'No changes needed: {stats["no_changes"]}')
    print()
    
    if dry_run:
        print('🔍 DRY RUN - No changes saved')
        return stats
    
    # Save with atomic write
    print('💾 Saving normalized Materials.yaml...')
    
    temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=materials_path.parent)
    try:
        import os
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        
        # Atomic replace
        import shutil
        shutil.move(temp_path, materials_path)
        
        print('✅ Normalization complete - Materials.yaml saved')
        print()
        print(f'📅 Normalized at: {datetime.now(timezone.utc).isoformat()}')
        
    except Exception as e:
        # Clean up temp file on error
        try:
            Path(temp_path).unlink()
        except:
            pass
        raise e
    
    return stats


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Normalize Materials.yaml structure for consistency'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without saving'
    )
    
    args = parser.parse_args()
    
    try:
        stats = normalize_materials_yaml(dry_run=args.dry_run)
        
        print()
        print('✅ NORMALIZATION COMPLETE')
        print()
        print('Next steps:')
        print('1. Run voice enhancement: python3 scripts/voice/enhance_materials_voice.py --all')
        print('2. Export to frontmatter: python3 run.py --all --data-only')
        
        return 0
        
    except Exception as e:
        print(f'❌ Normalization failed: {e}')
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
