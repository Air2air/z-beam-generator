#!/usr/bin/env python3
"""
Wood and Composite Subcategorization Implementation

Implements subcategorization for:
1. Wood category: hardwoods, softwoods, engineered_wood
2. Composite category: advanced_composites, polymer_composites, basic_composites

Based on analysis showing wood subcategorization is highly beneficial,
and composite subcategorization has moderate benefit.
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime

def create_backup(file_path):
    """Create timestamped backup."""
    timestamp = int(datetime.now().timestamp())
    backup_path = f"{file_path}_subcategorization_backup_{timestamp}.yaml"
    shutil.copy2(file_path, backup_path)
    return backup_path

def subcategorize_wood(wood_items):
    """Subcategorize wood materials by botanical classification."""
    
    hardwoods = []
    softwoods = []
    engineered = []
    
    # Define classifications
    hardwood_species = {
        'Ash', 'Beech', 'Cherry', 'Hickory', 'Mahogany', 'Maple', 'Oak', 
        'Poplar', 'Rosewood', 'Teak', 'Walnut', 'Birch', 'Willow'
    }
    
    softwood_species = {
        'Cedar', 'Fir', 'Pine', 'Redwood', 'Spruce', 'Whitewood', 'Bamboo'
    }
    
    engineered_products = {
        'MDF', 'Plywood'
    }
    
    for item in wood_items:
        name = item.get('name', '')
        
        if name in engineered_products:
            engineered.append(item)
        elif name in softwood_species:
            softwoods.append(item)
        elif name in hardwood_species:
            hardwoods.append(item)
        else:
            # Default to hardwood for unclassified
            hardwoods.append(item)
    
    return {
        'hardwoods': {
            'description': 'Hardwood species - typically denser woods from deciduous trees',
            'items': hardwoods
        },
        'softwoods': {
            'description': 'Softwood species - typically lighter woods from coniferous trees and bamboo',
            'items': softwoods
        },
        'engineered_wood': {
            'description': 'Manufactured wood products - MDF, plywood, and other engineered materials',
            'items': engineered
        }
    }

def subcategorize_composites(composite_items):
    """Subcategorize composite materials by matrix type and complexity."""
    
    advanced_composites = []
    polymer_composites = []
    basic_composites = []
    
    for item in composite_items:
        name = item.get('name', '')
        name_lower = name.lower()
        
        # Advanced composites (fiber-reinforced and matrix composites)
        if any(term in name_lower for term in [
            'carbon fiber', 'kevlar', 'glass fiber reinforced polymers', 
            'fiber reinforced polyurethane', 'metal matrix', 'ceramic matrix'
        ]):
            advanced_composites.append(item)
        
        # Polymer matrix composites (resin-based)
        elif any(term in name_lower for term in [
            'epoxy', 'phenolic', 'polyester', 'urethane'
        ]) and 'resin' in name_lower:
            polymer_composites.append(item)
        
        # Basic composites (simple composites and elastomers)
        else:
            basic_composites.append(item)
    
    return {
        'advanced_composites': {
            'description': 'High-performance fiber-reinforced and matrix composites',
            'items': advanced_composites
        },
        'polymer_composites': {
            'description': 'Resin-matrix composite materials',
            'items': polymer_composites
        },
        'basic_composites': {
            'description': 'Basic composite materials and elastomers',
            'items': basic_composites
        }
    }

def implement_subcategorization():
    """Main implementation function."""
    
    materials_path = Path("data/materials.yaml")
    
    print("🌲 IMPLEMENTING WOOD & COMPOSITE SUBCATEGORIZATION")
    print("=" * 60)
    print()
    
    # Create backup
    backup_path = create_backup(materials_path)
    print(f"📁 Backup created: {backup_path}")
    print()
    
    # Load current data
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print("🌲 Phase 1: Subcategorizing wood materials...")
    
    # Extract and subcategorize wood
    wood_items = data['materials']['wood']['items']
    subcategorized_wood = subcategorize_wood(wood_items)
    
    print(f"   ✅ Split {len(wood_items)} wood materials into:")
    for subcat, subdata in subcategorized_wood.items():
        count = len(subdata['items'])
        print(f"      🌳 {subcat}: {count} materials")
        
        # Show examples
        examples = [item.get('name', 'Unknown') for item in subdata['items'][:3]]
        if len(subdata['items']) > 3:
            examples.append(f'... +{len(subdata['items'])-3} more')
        print(f"         Examples: {', '.join(examples)}")
    
    print()
    print("🧪 Phase 2: Subcategorizing composite materials...")
    
    # Extract and subcategorize composites
    composite_items = data['materials']['composite']['items']
    subcategorized_composites = subcategorize_composites(composite_items)
    
    print(f"   ✅ Split {len(composite_items)} composite materials into:")
    for subcat, subdata in subcategorized_composites.items():
        count = len(subdata['items'])
        print(f"      🧪 {subcat}: {count} materials")
        
        # Show examples
        examples = [item.get('name', 'Unknown') for item in subdata['items'][:3]]
        if len(subdata['items']) > 3:
            examples.append(f'... +{len(subdata['items'])-3} more')
        print(f"         Examples: {', '.join(examples)}")
    
    print()
    print("📊 Phase 3: Updating materials structure...")
    
    # Update the materials section
    data['materials']['wood'] = subcategorized_wood
    data['materials']['composite'] = subcategorized_composites
    
    print("   ✅ Materials section updated with subcategories")
    print()
    
    print("💾 Phase 4: Saving subcategorized structure...")
    
    # Save updated data
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print("   ✅ Subcategorized materials.yaml saved")
    print()
    
    # Generate summary
    print("📊 SUBCATEGORIZATION SUMMARY")
    print("=" * 35)
    print()
    
    print("🌲 Wood subcategories:")
    wood_total = 0
    for subcat, subdata in subcategorized_wood.items():
        count = len(subdata['items'])
        wood_total += count
        print(f"   📂 {subcat}: {count} materials")
    
    print()
    print("🧪 Composite subcategories:")
    comp_total = 0
    for subcat, subdata in subcategorized_composites.items():
        count = len(subdata['items'])
        comp_total += count
        print(f"   📂 {subcat}: {count} materials")
    
    print()
    print(f"📈 Total materials: {wood_total + comp_total} (wood + composite)")
    print(f"📁 Backup preserved: {backup_path}")
    print()
    
    # Calculate new balance scores
    wood_sizes = [len(subdata['items']) for subdata in subcategorized_wood.values()]
    comp_sizes = [len(subdata['items']) for subdata in subcategorized_composites.values()]
    
    wood_balance = min(wood_sizes) / max(wood_sizes) if wood_sizes else 0
    comp_balance = min(comp_sizes) / max(comp_sizes) if comp_sizes else 0
    
    print("📊 BALANCE ANALYSIS:")
    print(f"   🌲 Wood balance: {wood_balance:.2f} ({'Good' if wood_balance > 0.3 else 'Moderate'})")
    print(f"   🧪 Composite balance: {comp_balance:.2f} ({'Good' if comp_balance > 0.4 else 'Moderate'})")
    print()
    
    print("✅ SUBCATEGORIZATION COMPLETE!")
    print()
    print("🎯 BENEFITS ACHIEVED:")
    print("   ✅ Industry-standard wood classification")
    print("   ✅ Better organization for laser operators")
    print("   ✅ Logical grouping by material properties")
    print("   ✅ Enhanced navigation efficiency")
    print("   ✅ Maintained all existing material data")
    
    return backup_path

if __name__ == "__main__":
    implement_subcategorization()
