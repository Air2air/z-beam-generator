#!/usr/bin/env python3
"""
Populate Visual Appearances at Category Level

More efficient approach: researches contamination appearance
at the CATEGORY level (metal, ceramic, glass, etc.) rather than
individual materials. One comprehensive description applies to
all materials in each category.

Usage:
    # Single pattern, single category
    python3 scripts/research/populate_visual_appearances_by_category.py \\
        --pattern industrial-oil --category metal
    
    # Single pattern, all categories
    python3 scripts/research/populate_visual_appearances_by_category.py \\
        --pattern industrial-oil --all-categories
    
    # All patterns, all categories
    python3 scripts/research/populate_visual_appearances_by_category.py \\
        --all

Author: AI Assistant
Date: November 26, 2025
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from domains.contaminants.research.visual_appearance_researcher import VisualAppearanceResearcher


# All material categories
CATEGORIES = [
    'metal', 'ceramic', 'glass', 'stone',
    'composite', 'plastic', 'wood', 'masonry',
    'rare-earth', 'semiconductor'
]


def load_contaminants_yaml() -> Dict:
    """Load Contaminants.yaml data."""
    contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    if not contaminants_file.exists():
        print(f"❌ Contaminants.yaml not found at {contaminants_file}")
        sys.exit(1)
    
    with open(contaminants_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_contaminants_yaml(data: Dict):
    """Save updated Contaminants.yaml data."""
    contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    # Create backup
    backup_file = contaminants_file.with_suffix('.yaml.bak')
    if contaminants_file.exists() and not backup_file.exists():
        print(f"📦 Creating backup: {backup_file.name}")
        import shutil
        shutil.copy2(contaminants_file, backup_file)
    
    # Save
    print(f"💾 Saving to {contaminants_file.name}...")
    with open(contaminants_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("✅ Saved successfully")


def populate_pattern_category(
    researcher: VisualAppearanceResearcher,
    pattern_data: Dict,
    pattern_id: str,
    category: str,
    force: bool = False
) -> bool:
    """
    Populate visual appearance for one pattern on one category.
    
    Returns:
        True if populated, False if skipped
    """
    # Check if already exists
    visual_chars = pattern_data.get('visual_characteristics', {})
    appearances = visual_chars.get('appearance_on_categories', {})
    
    if category in appearances and not force:
        print(f"⏭️  Skipping {category} (already researched, use --force to override)")
        return False
    
    # Get pattern name and composition
    pattern_name = pattern_data.get('name', pattern_id)
    chemical_comp = pattern_data.get('chemical_composition')
    
    print(f"\n🔬 Researching {pattern_name} on {category.upper()} category...")
    
    try:
        # Research appearance
        appearance = researcher.research_appearance_on_category(
            contaminant_id=pattern_id,
            contaminant_name=pattern_name,
            category_name=category,
            chemical_composition=chemical_comp
        )
        
        # Format for YAML
        formatted = researcher.format_for_yaml(appearance)
        
        # Update pattern data
        if 'visual_characteristics' not in pattern_data:
            pattern_data['visual_characteristics'] = {}
        
        if 'appearance_on_categories' not in pattern_data['visual_characteristics']:
            pattern_data['visual_characteristics']['appearance_on_categories'] = {}
        
        pattern_data['visual_characteristics']['appearance_on_categories'][category] = formatted
        
        print(f"✅ {category.upper()}: {len(formatted)} fields populated")
        return True
        
    except Exception as e:
        print(f"❌ Research failed for {category}: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Populate visual appearance data at CATEGORY level',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single pattern, single category
  populate_visual_appearances_by_category.py --pattern industrial-oil --category metal
  
  # Single pattern, all categories
  populate_visual_appearances_by_category.py --pattern industrial-oil --all-categories
  
  # All patterns, all categories
  populate_visual_appearances_by_category.py --all
  
  # Force re-research existing data
  populate_visual_appearances_by_category.py --pattern industrial-oil --category metal --force
"""
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Research all contamination patterns across all categories'
    )
    
    parser.add_argument(
        '--pattern',
        type=str,
        help='Research specific pattern ID (e.g., industrial-oil, rust-oxidation)'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Single category (metal, ceramic, glass, etc.)'
    )
    
    parser.add_argument(
        '--all-categories',
        action='store_true',
        help='Research across all material categories'
    )
    
    parser.add_argument(
        '--list-patterns',
        action='store_true',
        help='List all available contamination patterns and exit'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-research patterns that already have category data'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Gemini API key (uses GEMINI_API_KEY env var if not provided)'
    )
    
    args = parser.parse_args()
    
    # Load contaminants data
    print("\n📂 Loading Contaminants.yaml...")
    data = load_contaminants_yaml()
    patterns = data.get('contamination_patterns', {})
    print(f"✅ Loaded {len(patterns)} contamination patterns")
    
    # List patterns and exit
    if args.list_patterns:
        print("\n📊 Available Contamination Patterns:")
        print("=" * 80)
        for pattern_id, pattern_data in list(patterns.items())[:20]:
            name = pattern_data.get('name', 'N/A')
            print(f"  {pattern_id:30} {name}")
        if len(patterns) > 20:
            print(f"  ... and {len(patterns) - 20} more")
        print(f"\nTotal: {len(patterns)} patterns")
        return
    
    # Validate arguments
    if not args.all and not args.pattern:
        print("❌ Error: Specify --pattern <id> or --all")
        sys.exit(1)
    
    if args.pattern and not args.category and not args.all_categories:
        print("❌ Error: Specify --category <name> or --all-categories")
        sys.exit(1)
    
    # Initialize researcher
    print("\n🔬 Initializing Visual Appearance Researcher...")
    try:
        researcher = VisualAppearanceResearcher(api_key=args.api_key)
        print("✅ Researcher initialized")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("   Set GEMINI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Determine categories to research
    if args.category:
        categories = [args.category]
    else:
        categories = CATEGORIES
    
    # Determine patterns to research
    if args.all:
        patterns_to_research = list(patterns.items())
        print(f"\n🚀 Starting batch research: ALL patterns × {len(categories)} categories")
    else:
        pattern_id = args.pattern
        if pattern_id not in patterns:
            print(f"❌ Error: Pattern '{pattern_id}' not found")
            print(f"   Available: {', '.join(list(patterns.keys())[:10])}")
            sys.exit(1)
        patterns_to_research = [(pattern_id, patterns[pattern_id])]
        print(f"\n🚀 Starting research: {pattern_id} × {len(categories)} categories")
    
    # Research loop
    print(f"📈 Total operations: {len(patterns_to_research)} patterns × {len(categories)} categories")
    print("=" * 80)
    
    total_populated = 0
    
    for i, (pattern_id, pattern_data) in enumerate(patterns_to_research, 1):
        pattern_name = pattern_data.get('name', pattern_id)
        
        print(f"\n{'='*80}")
        print(f"Pattern {i}/{len(patterns_to_research)}: {pattern_name} ({pattern_id})")
        print(f"{'='*80}")
        
        populated_count = 0
        
        for j, category in enumerate(categories, 1):
            print(f"\n[{j}/{len(categories)}] Category: {category.upper()}")
            
            if populate_pattern_category(researcher, pattern_data, pattern_id, category, args.force):
                populated_count += 1
                total_populated += 1
                
                # Save after each category (incremental save)
                patterns[pattern_id] = pattern_data
                data['contamination_patterns'] = patterns
                save_contaminants_yaml(data)
                print(f"💾 Progress saved ({populated_count}/{len(categories)} categories complete)")
        
        print(f"\n✅ Pattern {pattern_id}: {populated_count}/{len(categories)} categories populated")
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"✨ COMPLETE: {total_populated} category-level appearances researched")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
