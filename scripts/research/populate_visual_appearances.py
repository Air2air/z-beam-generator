#!/usr/bin/env python3
"""
Populate Visual Appearances

Use VisualAppearanceResearcher to populate appearance_on_materials
for contamination patterns in Contaminants.yaml.

This adds detailed visual descriptions needed for realistic AI image generation.

Usage:
    # Research all patterns
    python3 scripts/research/populate_visual_appearances.py --all
    
    # Research specific pattern
    python3 scripts/research/populate_visual_appearances.py --pattern rust-oxidation
    
    # Research with custom materials
    python3 scripts/research/populate_visual_appearances.py --pattern oil-grease --materials "Steel,Aluminum,Copper"

Author: AI Assistant
Date: November 26, 2025
"""

import os
import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from domains.contaminants.research.visual_appearance_researcher import VisualAppearanceResearcher
from domains.contaminants.library import get_library


def load_contaminants_yaml() -> Dict:
    """Load Contaminants.yaml data."""
    contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    with open(contaminants_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_contaminants_yaml(data: Dict):
    """Save updated Contaminants.yaml data."""
    contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    # Backup original
    backup_file = contaminants_file.with_suffix('.yaml.backup')
    if not backup_file.exists():
        import shutil
        shutil.copy2(contaminants_file, backup_file)
        print(f"📦 Backup created: {backup_file}")
    
    with open(contaminants_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"💾 Saved: {contaminants_file}")


def populate_pattern(
    researcher: VisualAppearanceResearcher,
    pattern_id: str,
    pattern_data: Dict,
    materials: List[str] = None
) -> Dict:
    """
    Populate visual appearances for one contamination pattern.
    
    Args:
        researcher: VisualAppearanceResearcher instance
        pattern_id: Pattern ID (e.g., "rust-oxidation")
        pattern_data: Pattern data from Contaminants.yaml
        materials: Optional list of materials (uses valid_materials if None)
    
    Returns:
        Updated pattern_data with appearance_on_materials populated
    """
    contaminant_name = pattern_data.get('name', pattern_id)
    
    # Get materials to research
    if materials is None:
        materials = pattern_data.get('valid_materials', [])
    
    if not materials:
        print(f"⚠️  No valid materials for {pattern_id}")
        return pattern_data
    
    print(f"\n{'='*80}")
    print(f"📝 Pattern: {contaminant_name} ({pattern_id})")
    print(f"🎯 Materials: {', '.join(materials)}")
    print(f"{'='*80}")
    
    # Get chemical composition if available
    composition = None
    if 'composition' in pattern_data:
        composition = ', '.join(pattern_data['composition'])
    elif 'chemical_formula' in pattern_data:
        composition = pattern_data['chemical_formula']
    
    # Research appearances
    appearances = researcher.research_multiple_materials(
        contaminant_id=pattern_id,
        contaminant_name=contaminant_name,
        material_names=materials,
        chemical_composition=composition
    )
    
    # Add to pattern data
    if 'visual_characteristics' not in pattern_data:
        pattern_data['visual_characteristics'] = {}
    
    if 'appearance_on_materials' not in pattern_data['visual_characteristics']:
        pattern_data['visual_characteristics']['appearance_on_materials'] = {}
    
    # Format and add each material's appearance
    for material_key, appearance in appearances.items():
        formatted = researcher.format_for_yaml(appearance)
        pattern_data['visual_characteristics']['appearance_on_materials'][material_key] = formatted
    
    return pattern_data


def populate_all_patterns(
    researcher: VisualAppearanceResearcher,
    data: Dict,
    skip_existing: bool = True
) -> Dict:
    """
    Populate visual appearances for all patterns.
    
    Args:
        researcher: VisualAppearanceResearcher instance
        data: Contaminants.yaml data
        skip_existing: Skip patterns that already have appearance data
    
    Returns:
        Updated data
    """
    patterns = data.get('contamination_patterns', {})
    total = len(patterns)
    processed = 0
    skipped = 0
    
    print(f"\n🚀 Starting batch research for {total} patterns")
    
    for i, (pattern_id, pattern_data) in enumerate(patterns.items(), 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{total}] {pattern_id}")
        print(f"{'='*80}")
        
        # Check if already has appearance data
        if skip_existing:
            has_appearances = (
                'visual_characteristics' in pattern_data and
                'appearance_on_materials' in pattern_data.get('visual_characteristics', {}) and
                len(pattern_data['visual_characteristics']['appearance_on_materials']) > 0
            )
            
            if has_appearances:
                print(f"⏭️  Skipping - already has appearance data")
                skipped += 1
                continue
        
        try:
            # Populate this pattern
            pattern_data = populate_pattern(
                researcher=researcher,
                pattern_id=pattern_id,
                pattern_data=pattern_data
            )
            
            # Update in data
            patterns[pattern_id] = pattern_data
            processed += 1
            
            # Save after each pattern (in case of interruption)
            data['contamination_patterns'] = patterns
            save_contaminants_yaml(data)
            
        except Exception as e:
            print(f"\n❌ Error processing {pattern_id}: {e}")
            print("   Continuing with next pattern...")
            continue
    
    print(f"\n{'='*80}")
    print(f"✅ Batch research complete:")
    print(f"   - Processed: {processed}")
    print(f"   - Skipped: {skipped}")
    print(f"   - Total: {total}")
    print(f"{'='*80}")
    
    return data


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Populate visual appearance data for contamination patterns'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Research all patterns'
    )
    
    parser.add_argument(
        '--pattern',
        type=str,
        help='Research specific pattern ID'
    )
    
    parser.add_argument(
        '--materials',
        type=str,
        help='Comma-separated list of materials (overrides valid_materials)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-research patterns that already have appearance data'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Gemini API key (uses GEMINI_API_KEY env var if not provided)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.pattern:
        parser.error("Must specify --all or --pattern")
    
    # Initialize researcher
    print("🔬 Initializing Visual Appearance Researcher...")
    try:
        researcher = VisualAppearanceResearcher(api_key=args.api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("   Set GEMINI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Load data
    print("📂 Loading Contaminants.yaml...")
    data = load_contaminants_yaml()
    
    # Process
    if args.all:
        # Research all patterns
        data = populate_all_patterns(
            researcher=researcher,
            data=data,
            skip_existing=not args.force
        )
        
    else:
        # Research single pattern
        pattern_id = args.pattern
        patterns = data.get('contamination_patterns', {})
        
        if pattern_id not in patterns:
            print(f"❌ Error: Pattern '{pattern_id}' not found")
            print(f"   Available patterns: {', '.join(patterns.keys())}")
            sys.exit(1)
        
        # Parse materials if provided
        materials = None
        if args.materials:
            materials = [m.strip() for m in args.materials.split(',')]
        
        # Populate
        pattern_data = populate_pattern(
            researcher=researcher,
            pattern_id=pattern_id,
            pattern_data=patterns[pattern_id],
            materials=materials
        )
        
        # Update and save
        patterns[pattern_id] = pattern_data
        data['contamination_patterns'] = patterns
        save_contaminants_yaml(data)
    
    print("\n✨ Visual appearance population complete!")


if __name__ == '__main__':
    main()
