#!/usr/bin/env python3
"""
Final conflict resolution strategy.
Handles duplicate wood materials and other conflicts with intelligent merging.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

def create_final_resolution_strategy():
    """Create the final strategy for resolving all conflicts."""
    
    strategy = {
        # WOOD CONFLICTS: We have both wood-{material} and {material}
        # Strategy: Keep the better quality/more appropriate image
        'wood_conflicts': {
            'action': 'merge_best_quality',
            'conflicts': [
                'teak', 'pine', 'rosewood', 'birch', 'poplar', 'oak', 
                'mahogany', 'hickory', 'cedar', 'ash', 'cherry', 'maple', 'beech'
            ],
            'approach': 'manual_comparison'  # Could be automated based on file size/date
        },
        
        # STEEL CONFLICTS: Multiple steel variants → single steel
        'steel_consolidation': {
            'action': 'prioritized_merge',
            'priority_order': ['carbon-steel', 'galvanized-steel', 'tool-steel', 'steel'],
            'target': 'steel',
            'reason': 'Use most comprehensive steel variant'
        },
        
        # IRON CONFLICTS: cast-iron → iron
        'iron_consolidation': {
            'action': 'use_specific_as_base',
            'specific': 'cast-iron',
            'target': 'iron',
            'reason': 'Cast iron represents general iron cleaning'
        },
        
        # TERRA-COTTA vs TERRACOTTA: Standardize hyphenation
        'terracotta_standardization': {
            'action': 'standardize_naming',
            'from': 'terra-cotta',
            'to': 'terracotta',
            'reason': 'Standardize hyphenation'
        },
        
        # INDIUM-GLASS vs INDIUM: Use base material
        'indium_consolidation': {
            'action': 'use_base_material',
            'specific': 'indium-glass',
            'target': 'indium',
            'reason': 'Indium glass represents indium material cleaning'
        }
    }
    
    return strategy

def analyze_wood_conflicts(images_dir):
    """Analyze wood conflicts to determine best resolution."""
    images_path = Path(images_dir)
    wood_materials = ['teak', 'pine', 'rosewood', 'birch', 'poplar', 'oak', 
                     'mahogany', 'hickory', 'cedar', 'ash', 'cherry', 'maple', 'beech']
    
    wood_analysis = {}
    
    for material in wood_materials:
        base_hero = images_path / f"{material}-laser-cleaning-hero.jpg"
        wood_hero = images_path / f"wood-{material}-laser-cleaning-hero.jpg"
        base_micro = images_path / f"{material}-laser-cleaning-micro.jpg" 
        wood_micro = images_path / f"wood-{material}-laser-cleaning-micro.jpg"
        
        analysis = {
            'base_exists': {'hero': base_hero.exists(), 'micro': base_micro.exists()},
            'wood_exists': {'hero': wood_hero.exists(), 'micro': wood_micro.exists()},
            'resolution': None
        }
        
        # Determine resolution strategy
        if analysis['base_exists']['hero'] and analysis['base_exists']['micro']:
            if analysis['wood_exists']['hero'] or analysis['wood_exists']['micro']:
                # Both exist - need to choose or merge
                analysis['resolution'] = 'choose_base'  # Prefer existing base
            else:
                analysis['resolution'] = 'keep_base'
        elif analysis['wood_exists']['hero'] and analysis['wood_exists']['micro']:
            # Only wood version exists
            analysis['resolution'] = 'rename_wood_to_base'
        elif analysis['wood_exists']['hero'] or analysis['wood_exists']['micro']:
            # Partial wood version - use to complete base
            analysis['resolution'] = 'merge_partial'
        else:
            analysis['resolution'] = 'missing_both'
        
        wood_analysis[material] = analysis
    
    return wood_analysis

def create_final_resolution_plan(images_dir):
    """Create the final resolution plan with intelligent conflict handling."""
    images_path = Path(images_dir)
    
    # Analyze wood conflicts
    wood_analysis = analyze_wood_conflicts(images_dir)
    
    plan = {
        'renames': [],
        'deletions': [],  # Files to delete (duplicates)
        'backups': [],    # Files to backup before overwrite
        'keep_as_is': [],
        'manual_review': []  # Files that need manual decision
    }
    
    # Handle wood conflicts
    for material, analysis in wood_analysis.items():
        base_hero = f"{material}-laser-cleaning-hero.jpg"
        wood_hero = f"wood-{material}-laser-cleaning-hero.jpg"
        base_micro = f"{material}-laser-cleaning-micro.jpg"
        wood_micro = f"wood-{material}-laser-cleaning-micro.jpg"
        
        if analysis['resolution'] == 'choose_base':
            # Keep base, delete wood versions
            if analysis['wood_exists']['hero']:
                plan['deletions'].append((wood_hero, f"Duplicate of {base_hero}"))
            if analysis['wood_exists']['micro']:
                plan['deletions'].append((wood_micro, f"Duplicate of {base_micro}"))
                
        elif analysis['resolution'] == 'rename_wood_to_base':
            # Rename wood versions to base names
            if analysis['wood_exists']['hero']:
                plan['renames'].append((wood_hero, base_hero, f"Use wood-{material} as {material}"))
            if analysis['wood_exists']['micro']:
                plan['renames'].append((wood_micro, base_micro, f"Use wood-{material} as {material}"))
                
        elif analysis['resolution'] == 'merge_partial':
            # Use wood version to fill missing base images
            if analysis['wood_exists']['hero'] and not analysis['base_exists']['hero']:
                plan['renames'].append((wood_hero, base_hero, f"Fill missing {base_hero}"))
            if analysis['wood_exists']['micro'] and not analysis['base_exists']['micro']:
                plan['renames'].append((wood_micro, base_micro, f"Fill missing {base_micro}"))
            
            # Delete remaining wood duplicates
            if analysis['wood_exists']['hero'] and analysis['base_exists']['hero']:
                plan['deletions'].append((wood_hero, f"Duplicate of {base_hero}"))
            if analysis['wood_exists']['micro'] and analysis['base_exists']['micro']:
                plan['deletions'].append((wood_micro, f"Duplicate of {base_micro}"))
    
    # Handle steel consolidation
    steel_variants = ['carbon-steel', 'galvanized-steel', 'tool-steel']
    base_steel_hero = images_path / "steel-laser-cleaning-hero.jpg"
    base_steel_micro = images_path / "steel-laser-cleaning-micro.jpg"
    
    # Find best steel variant to use as base
    for variant in steel_variants:
        variant_hero = images_path / f"{variant}-laser-cleaning-hero.jpg"
        variant_micro = images_path / f"{variant}-laser-cleaning-micro.jpg"
        
        if variant_hero.exists():
            if base_steel_hero.exists():
                plan['backups'].append((base_steel_hero.name, f"backup-{base_steel_hero.name}"))
            plan['renames'].append((variant_hero.name, base_steel_hero.name, f"Use {variant} as steel"))
        
        if variant_micro.exists():
            if base_steel_micro.exists():
                plan['backups'].append((base_steel_micro.name, f"backup-{base_steel_micro.name}"))
            plan['renames'].append((variant_micro.name, base_steel_micro.name, f"Use {variant} as steel"))
    
    # Handle iron consolidation
    cast_iron_hero = images_path / "cast-iron-laser-cleaning-hero.jpg"
    cast_iron_micro = images_path / "cast-iron-laser-cleaning-micro.jpg"
    base_iron_hero = images_path / "iron-laser-cleaning-hero.jpg"
    base_iron_micro = images_path / "iron-laser-cleaning-micro.jpg"
    
    if cast_iron_hero.exists():
        if base_iron_hero.exists():
            plan['backups'].append((base_iron_hero.name, f"backup-{base_iron_hero.name}"))
        plan['renames'].append((cast_iron_hero.name, base_iron_hero.name, "Use cast-iron as iron"))
    
    if cast_iron_micro.exists():
        if base_iron_micro.exists():
            plan['backups'].append((base_iron_micro.name, f"backup-{base_iron_micro.name}"))
        plan['renames'].append((cast_iron_micro.name, base_iron_micro.name, "Use cast-iron as iron"))
    
    # Handle other simple renames
    simple_renames = [
        ('terra-cotta-laser-cleaning-hero.jpg', 'terracotta-laser-cleaning-hero.jpg'),
        ('terra-cotta-laser-cleaning-micro.jpg', 'terracotta-laser-cleaning-micro.jpg'),
        ('indium-glass-laser-cleaning-hero.jpg', 'indium-laser-cleaning-hero.jpg')
    ]
    
    for old_name, new_name in simple_renames:
        old_path = images_path / old_name
        new_path = images_path / new_name
        
        if old_path.exists():
            if new_path.exists():
                plan['backups'].append((new_name, f"backup-{new_name}"))
            plan['renames'].append((old_name, new_name, "Standardize naming"))
    
    return plan, wood_analysis

def preview_final_plan(images_dir):
    """Preview the final resolution plan."""
    print("🎯 FINAL CONFLICT RESOLUTION PLAN")
    print("="*50)
    
    plan, wood_analysis = create_final_resolution_plan(images_dir)
    
    # Show wood analysis
    print(f"\n🌳 WOOD MATERIAL ANALYSIS:")
    for material, analysis in wood_analysis.items():
        base_complete = analysis['base_exists']['hero'] and analysis['base_exists']['micro']
        wood_complete = analysis['wood_exists']['hero'] and analysis['wood_exists']['micro']
        
        status = "✅" if base_complete else "⚠️" if wood_complete else "❌"
        print(f"   {status} {material}: {analysis['resolution']}")
    
    if plan['backups']:
        print(f"\n📦 BACKUPS NEEDED ({len(plan['backups'])}):")
        for original, backup in plan['backups']:
            print(f"   {original} → {backup}")
    
    if plan['renames']:
        print(f"\n🔄 RENAMES ({len(plan['renames'])}):")
        for old_name, new_name, reason in plan['renames']:
            print(f"   {old_name}")
            print(f"   → {new_name}")
            print(f"   📝 {reason}")
            print()
    
    if plan['deletions']:
        print(f"\n🗑️  DELETIONS ({len(plan['deletions'])}):")
        for filename, reason in plan['deletions']:
            print(f"   ❌ {filename} - {reason}")
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   Backups: {len(plan['backups'])}")
    print(f"   Renames: {len(plan['renames'])}")
    print(f"   Deletions: {len(plan['deletions'])}")
    
    return plan

def apply_final_plan(images_dir, plan, dry_run=True):
    """Apply the final resolution plan."""
    images_path = Path(images_dir)
    
    if dry_run:
        print("\n🧪 FINAL DRY RUN")
    else:
        print("\n🚀 APPLYING FINAL RESOLUTION")
        backup_dir = images_path / f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
    
    print("="*40)
    
    # Apply backups
    for original, backup in plan['backups']:
        if dry_run:
            print(f"Would backup: {original}")
        else:
            shutil.copy2(images_path / original, backup_dir / backup)
            print(f"📦 Backed up: {original}")
    
    # Apply renames
    for old_name, new_name, reason in plan['renames']:
        if dry_run:
            print(f"Would rename: {old_name} → {new_name}")
        else:
            (images_path / old_name).rename(images_path / new_name)
            print(f"✅ Renamed: {old_name} → {new_name}")
    
    # Apply deletions
    for filename, reason in plan['deletions']:
        if dry_run:
            print(f"Would delete: {filename}")
        else:
            (images_path / filename).unlink()
            print(f"🗑️  Deleted: {filename}")

def main():
    """Main execution."""
    images_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/public/images"
    
    plan = preview_final_plan(images_dir)
    apply_final_plan(images_dir, plan, dry_run=True)
    
    print(f"\n🔧 To apply changes, run with --apply flag")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        images_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/public/images"
        plan, _ = create_final_resolution_plan(images_dir)
        apply_final_plan(images_dir, plan, dry_run=False)
    else:
        main()
