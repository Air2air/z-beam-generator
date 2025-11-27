#!/usr/bin/env python3
"""
Populate Visual Appearances for ALL Material Categories

Extended version that researches contamination appearances across ALL materials
in Materials.yaml, organized by category:
- Metals (Aluminum, Steel, Copper, Brass, Titanium, etc.)
- Ceramics (Alumina, Silicon Carbide, Zirconia, etc.)
- Glasses (Borosilicate, Tempered, Soda-Lime, etc.)
- Stones (Granite, Marble, Limestone, Sandstone, etc.)
- Composites (Carbon Fiber, Fiberglass, etc.)
- Plastics (Acrylic, Polycarbonate, PVC, etc.)
- Woods (Oak, Maple, Pine, etc.)
- Masonry (Brick, Concrete, etc.)

Uses VisualAppearanceResearcher with Gemini API to generate detailed,
material-specific visual descriptions for AI image generation.

Usage:
    # Single pattern, ALL materials (all categories)
    python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease
    
    # Single pattern, specific category
    python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal
    
    # Single pattern, multiple categories
    python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal,ceramic,glass
    
    # All patterns, ALL materials
    python3 scripts/research/populate_visual_appearances_all_categories.py --all
    
    # All patterns, specific category
    python3 scripts/research/populate_visual_appearances_all_categories.py --all --category stone
    
    # Show available categories
    python3 scripts/research/populate_visual_appearances_all_categories.py --list-categories
    
    # Force re-research existing data
    python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --force

Author: AI Assistant
Date: November 26, 2025
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from domains.contaminants.research.visual_appearance_researcher import VisualAppearanceResearcher


def load_materials_by_category() -> Dict[str, List[str]]:
    """
    Load all materials from Materials.yaml organized by category.
    
    Returns:
        Dict mapping category name to list of material names
        Example: {
            'metal': ['Aluminum', 'Steel', 'Copper', ...],
            'ceramic': ['Alumina', 'Silicon Carbide', ...],
            ...
        }
    """
    materials_file = project_root / 'data' / 'materials' / 'Materials.yaml'
    
    if not materials_file.exists():
        print(f"❌ Materials.yaml not found at {materials_file}")
        sys.exit(1)
    
    print(f"📂 Loading Materials.yaml...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials_by_category = {}
    
    if 'materials' in data:
        for material_name, material_data in data['materials'].items():
            category = material_data.get('category', 'unknown')
            
            if category not in materials_by_category:
                materials_by_category[category] = []
            
            materials_by_category[category].append(material_name)
    
    # Sort materials within each category
    for category in materials_by_category:
        materials_by_category[category].sort()
    
    return materials_by_category


def get_materials_for_categories(
    categories: Optional[List[str]] = None,
    materials_by_category: Optional[Dict[str, List[str]]] = None
) -> List[str]:
    """
    Get list of materials for specified categories.
    
    Args:
        categories: List of category names (metal, ceramic, etc.)
                   If None, returns materials from ALL categories
        materials_by_category: Pre-loaded materials dict (loads if None)
    
    Returns:
        List of material names
    """
    if materials_by_category is None:
        materials_by_category = load_materials_by_category()
    
    if not categories:
        # Return ALL materials from ALL categories
        all_materials = []
        for materials in materials_by_category.values():
            all_materials.extend(materials)
        return sorted(set(all_materials))
    
    # Return materials for specified categories
    selected_materials = []
    for category in categories:
        if category not in materials_by_category:
            print(f"⚠️  Category '{category}' not found")
            continue
        selected_materials.extend(materials_by_category[category])
    
    return sorted(set(selected_materials))


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
    
    # Create backup (only once)
    backup_file = contaminants_file.with_suffix('.yaml.backup')
    if not backup_file.exists():
        import shutil
        shutil.copy2(contaminants_file, backup_file)
        print(f"📦 Backup created: {backup_file.name}")
    
    with open(contaminants_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"💾 Saved to Contaminants.yaml")


def populate_pattern(
    researcher: VisualAppearanceResearcher,
    pattern_data: Dict,
    pattern_id: str,
    materials: List[str],
    force: bool = False
) -> bool:
    """
    Populate visual appearances for one contamination pattern.
    
    Args:
        researcher: VisualAppearanceResearcher instance
        pattern_data: Pattern data from Contaminants.yaml
        pattern_id: Pattern ID (e.g., "oil-grease")
        materials: List of materials to research
        force: Re-research existing data
    
    Returns:
        True if research performed, False if skipped
    """
    contaminant_name = pattern_data.get('name', pattern_id)
    
    # Check if already has appearance data
    if not force:
        visual = pattern_data.get('visual_characteristics', {})
        existing = visual.get('appearance_on_materials', {})
        if existing and len(existing) > 0:
            print(f"⏭️  Skipping {pattern_id} (already has {len(existing)} materials)")
            return False
    
    print(f"\n{'='*80}")
    print(f"📝 Pattern: {contaminant_name} ({pattern_id})")
    print(f"🎯 Materials: {len(materials)} total")
    print(f"{'='*80}\n")
    
    # Get chemical composition if available
    composition = None
    if 'chemical_composition' in pattern_data:
        comp_data = pattern_data['chemical_composition']
        if 'primary_compounds' in comp_data:
            composition = ', '.join(comp_data['primary_compounds'])
    
    # Research appearances for all materials
    print(f"🔬 Researching {len(materials)} materials...")
    appearances = {}
    
    for i, material in enumerate(materials, 1):
        print(f"[{i}/{len(materials)}] Researching {material}...", end=' ', flush=True)
        
        try:
            appearance = researcher.research_appearance_on_material(
                contaminant_id=pattern_id,
                contaminant_name=contaminant_name,
                material_name=material,
                chemical_composition=composition
            )
            
            if appearance:
                appearances[material.lower().replace(' ', '-')] = appearance
                print("✅")
            else:
                print("⚠️ No data")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    if not appearances:
        print(f"⚠️  No appearances generated for {pattern_id}")
        return False
    
    # Add to pattern data
    if 'visual_characteristics' not in pattern_data:
        pattern_data['visual_characteristics'] = {}
    
    pattern_data['visual_characteristics']['appearance_on_materials'] = {}
    
    # Format and add each material's appearance
    for material_key, appearance in appearances.items():
        formatted = researcher.format_for_yaml(appearance)
        pattern_data['visual_characteristics']['appearance_on_materials'][material_key] = formatted
    
    print(f"\n✅ Populated {len(appearances)}/{len(materials)} materials for {pattern_id}")
    return True


def populate_all_patterns(
    researcher: VisualAppearanceResearcher,
    data: Dict,
    materials: List[str],
    force: bool = False
) -> int:
    """
    Populate visual appearances for all patterns.
    
    Args:
        researcher: VisualAppearanceResearcher instance
        data: Contaminants.yaml data
        materials: List of materials to research
        force: Re-research existing data
    
    Returns:
        Number of patterns populated
    """
    patterns = data.get('contamination_patterns', {})
    
    if not isinstance(patterns, dict):
        print("❌ Error: contamination_patterns is not a dict")
        return 0
    
    print(f"📊 Found {len(patterns)} contamination patterns")
    print(f"🎯 Researching {len(materials)} materials per pattern")
    print(f"📈 Total research operations: {len(patterns) * len(materials)}")
    
    populated_count = 0
    
    for i, (pattern_id, pattern_data) in enumerate(patterns.items(), 1):
        print(f"\n{'='*80}")
        print(f"Pattern {i}/{len(patterns)}: {pattern_id}")
        print(f"{'='*80}")
        
        if populate_pattern(researcher, pattern_data, pattern_id, materials, force):
            populated_count += 1
            
            # Save after each pattern (incremental save)
            data['contamination_patterns'] = patterns
            save_contaminants_yaml(data)
            print(f"💾 Progress saved ({populated_count}/{len(patterns)} patterns complete)")
    
    return populated_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Populate visual appearance data for ALL material categories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single pattern, all materials (all categories)
  %(prog)s --pattern oil-grease
  
  # Single pattern, metals only
  %(prog)s --pattern oil-grease --category metal
  
  # Single pattern, metals and ceramics
  %(prog)s --pattern oil-grease --category metal,ceramic
  
  # All patterns, all materials
  %(prog)s --all
  
  # All patterns, stones only
  %(prog)s --all --category stone
  
  # List available categories
  %(prog)s --list-categories
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Research all contamination patterns'
    )
    
    parser.add_argument(
        '--pattern',
        type=str,
        help='Research specific pattern ID (e.g., oil-grease, rust-oxidation)'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Material categories (comma-separated). If omitted, uses ALL categories. Examples: metal, ceramic, glass, stone'
    )
    
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List all available material categories and exit'
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
    
    # Load materials by category
    materials_by_category = load_materials_by_category()
    
    # List categories and exit
    if args.list_categories:
        print("\n📊 Available Material Categories:")
        print("=" * 80)
        for category, materials in sorted(materials_by_category.items()):
            print(f"\n{category.upper()} ({len(materials)} materials)")
            print("-" * 80)
            for material in materials[:10]:  # Show first 10
                print(f"  • {material}")
            if len(materials) > 10:
                print(f"  ... and {len(materials) - 10} more")
        print("\n" + "=" * 80)
        print(f"Total: {sum(len(m) for m in materials_by_category.values())} materials across {len(materials_by_category)} categories")
        return
    
    # Validate arguments
    if not args.all and not args.pattern:
        parser.error("Must specify --all or --pattern (or use --list-categories)")
    
    # Parse categories
    categories = None
    if args.category:
        categories = [c.strip() for c in args.category.split(',')]
        
        # Validate categories
        invalid = [c for c in categories if c not in materials_by_category]
        if invalid:
            print(f"❌ Invalid categories: {', '.join(invalid)}")
            print(f"   Available: {', '.join(sorted(materials_by_category.keys()))}")
            sys.exit(1)
        
        print(f"🎯 Categories: {', '.join(categories)}")
    else:
        print(f"🌍 Using ALL categories: {', '.join(sorted(materials_by_category.keys()))}")
    
    # Get materials for specified categories
    materials = get_materials_for_categories(categories, materials_by_category)
    
    if not materials:
        print("❌ No materials selected")
        sys.exit(1)
    
    print(f"✅ Selected {len(materials)} materials for research")
    
    # Initialize researcher
    print("\n🔬 Initializing Visual Appearance Researcher...")
    try:
        researcher = VisualAppearanceResearcher(api_key=args.api_key)
        print("✅ Researcher initialized")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("   Set GEMINI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Load contaminants data
    print("\n📂 Loading Contaminants.yaml...")
    data = load_contaminants_yaml()
    print("✅ Loaded contamination patterns")
    
    # Process
    if args.all:
        # Research all patterns
        print("\n🚀 Starting batch research (ALL patterns)...")
        populated = populate_all_patterns(
            researcher=researcher,
            data=data,
            materials=materials,
            force=args.force
        )
        
        print(f"\n{'='*80}")
        print(f"✨ COMPLETE: Populated {populated} patterns")
        print(f"{'='*80}")
        
    else:
        # Research single pattern
        pattern_id = args.pattern
        patterns = data.get('contamination_patterns', {})
        
        # Find pattern by ID
        pattern_data = patterns.get(pattern_id)
        
        if not pattern_data:
            available = list(patterns.keys())
            print(f"❌ Error: Pattern '{pattern_id}' not found")
            print(f"   Available: {', '.join(available[:10])}")
            if len(available) > 10:
                print(f"   ... and {len(available) - 10} more")
            sys.exit(1)
        
        # Populate
        print(f"\n🚀 Starting research for {pattern_id}...")
        if populate_pattern(researcher, pattern_data, pattern_id, materials, args.force):
            # Save
            data['contamination_patterns'] = patterns
            save_contaminants_yaml(data)
            print(f"\n✨ COMPLETE: {pattern_id} populated with {len(materials)} materials")
        else:
            print(f"\n⏭️  Skipped: {pattern_id} (use --force to re-research)")


if __name__ == '__main__':
    main()
