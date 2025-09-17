#!/usr/bin/env python3
"""
Restore Material Specificity

Corrects the overly aggressive material consolidation that lost important distinctions.
Only applies naming standardization for actual conflicts, not material variants.
"""

import os
import yaml
import frontmatter
from pathlib import Path


def apply_corrected_naming(material_name_lower: str) -> str:
    """Apply corrected naming that preserves material specificity"""
    # Basic kebab-case conversion
    slug = material_name_lower.replace(" ", "-")
    
    # Only apply naming standardizations for actual conflicts, not material variants
    naming_mappings = {
        # Only hyphenation/spelling standardizations - NOT material consolidation
        "terra-cotta": "terracotta",
        "indium-glass": "indium-glass",  # Keep this distinct from pure indium
    }
    
    # Apply standardization only if material matches known conflicts
    if slug in naming_mappings:
        slug = naming_mappings[slug]
        
    # Remove wood- prefix if present (this is the only consolidation that makes sense)
    if slug.startswith("wood-"):
        slug = slug[5:]  # Remove "wood-" prefix
        
    return slug


def restore_steel_variants():
    """Restore the specific steel types that were incorrectly consolidated"""
    steel_variants = {
        "carbon-steel": {
            "name": "Carbon Steel",
            "formula": "Fe-C",
            "category": "metal",
            "description": "Technical overview of Carbon Steel, Fe-C, for laser cleaning applications, including optimal 1064nm wavelength interaction, and industrial applications in surface preparation."
        },
        "galvanized-steel": {
            "name": "Galvanized Steel", 
            "formula": "Fe-Zn",
            "category": "metal",
            "description": "Technical overview of Galvanized Steel, Fe-Zn, for laser cleaning applications, including optimal 1064nm wavelength interaction, and industrial applications in surface preparation."
        },
        "tool-steel": {
            "name": "Tool Steel",
            "formula": "Fe-C-Cr-V-W",
            "category": "metal", 
            "description": "Technical overview of Tool Steel, Fe-C-Cr-V-W, for laser cleaning applications, including optimal 1064nm wavelength interaction, and industrial applications in surface preparation."
        }
    }
    
    print("🔧 RESTORING STEEL MATERIAL SPECIFICITY")
    print("=" * 50)
    
    # Check if we need to create these as separate materials
    for slug, info in steel_variants.items():
        frontmatter_file = Path(f"content/components/frontmatter/{slug}-laser-cleaning.md")
        
        if not frontmatter_file.exists():
            print(f"📄 Need to create: {slug}-laser-cleaning.md")
        else:
            print(f"✅ Already exists: {slug}-laser-cleaning.md")
    
    return steel_variants


def update_generator_naming():
    """Update generators to use corrected naming that preserves specificity"""
    
    # Update frontmatter generator
    frontmatter_gen_path = Path("components/frontmatter/generator.py")
    if frontmatter_gen_path.exists():
        with open(frontmatter_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the overly aggressive naming function
        old_function = '''    def _apply_standardized_naming(self, material_name_lower: str) -> str:
        """Apply the same standardized naming convention used in image resolution"""
        # Basic kebab-case conversion
        slug = material_name_lower.replace(" ", "-")
        
        # Apply specific naming standardizations that match the image resolution
        naming_mappings = {
            "carbon-steel": "steel",
            "galvanized-steel": "steel", 
            "tool-steel": "steel",
            "cast-iron": "iron",
            "terra-cotta": "terracotta",
            "indium-glass": "indium"
        }
        
        # Apply standardization if material matches known conflicts
        if slug in naming_mappings:
            slug = naming_mappings[slug]
            
        # Remove wood- prefix if present (matching image resolution strategy)
        if slug.startswith("wood-"):
            slug = slug[5:]  # Remove "wood-" prefix
            
        return slug'''
        
        new_function = '''    def _apply_standardized_naming(self, material_name_lower: str) -> str:
        """Apply corrected naming that preserves material specificity"""
        # Basic kebab-case conversion
        slug = material_name_lower.replace(" ", "-")
        
        # Only apply naming standardizations for actual conflicts, not material variants
        naming_mappings = {
            # Only hyphenation/spelling standardizations - NOT material consolidation
            "terra-cotta": "terracotta",
            # Keep steel variants distinct - they have different properties
            # Keep iron variants distinct where they represent different materials
        }
        
        # Apply standardization only if material matches known conflicts
        if slug in naming_mappings:
            slug = naming_mappings[slug]
            
        # Remove wood- prefix if present (this is the only consolidation that makes sense)
        if slug.startswith("wood-"):
            slug = slug[5:]  # Remove "wood-" prefix
            
        return slug'''
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            
            with open(frontmatter_gen_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Updated frontmatter generator to preserve material specificity")
        else:
            print("⚠️  Frontmatter generator function not found in expected format")
    
    # Update metatags generator
    metatags_gen_path = Path("components/metatags/generator.py")
    if metatags_gen_path.exists():
        with open(metatags_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the overly aggressive naming function
        old_function = '''    def _apply_standardized_naming(self, material_name_lower: str) -> str:
        """Apply the same standardized naming convention used in image resolution"""
        # Basic kebab-case conversion
        slug = material_name_lower.replace(" ", "-")
        
        # Apply specific naming standardizations that match the image resolution
        naming_mappings = {
            "carbon-steel": "steel",
            "galvanized-steel": "steel", 
            "tool-steel": "steel",
            "cast-iron": "iron",
            "terra-cotta": "terracotta",
            "indium-glass": "indium"
        }
        
        # Apply standardization if material matches known conflicts
        if slug in naming_mappings:
            slug = naming_mappings[slug]
            
        # Remove wood- prefix if present (matching image resolution strategy)
        if slug.startswith("wood-"):
            slug = slug[5:]  # Remove "wood-" prefix
            
        return slug'''
        
        new_function = '''    def _apply_standardized_naming(self, material_name_lower: str) -> str:
        """Apply corrected naming that preserves material specificity"""
        # Basic kebab-case conversion
        slug = material_name_lower.replace(" ", "-")
        
        # Only apply naming standardizations for actual conflicts, not material variants
        naming_mappings = {
            # Only hyphenation/spelling standardizations - NOT material consolidation
            "terra-cotta": "terracotta",
            # Keep steel variants distinct - they have different properties
            # Keep iron variants distinct where they represent different materials
        }
        
        # Apply standardization only if material matches known conflicts
        if slug in naming_mappings:
            slug = naming_mappings[slug]
            
        # Remove wood- prefix if present (this is the only consolidation that makes sense)
        if slug.startswith("wood-"):
            slug = slug[5:]  # Remove "wood-" prefix
            
        return slug'''
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            
            with open(metatags_gen_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Updated metatags generator to preserve material specificity")
        else:
            print("⚠️  Metatags generator function not found in expected format")


def main():
    """Main function to restore material specificity"""
    print("🎯 CORRECTING OVERLY AGGRESSIVE MATERIAL CONSOLIDATION")
    print("=" * 60)
    print()
    
    print("❌ ISSUE IDENTIFIED:")
    print("   The previous normalization incorrectly consolidated:")
    print("   • carbon-steel, galvanized-steel, tool-steel → steel")
    print("   • This loses important material distinctions!")
    print()
    
    print("✅ CORRECTED APPROACH:")
    print("   • Preserve material specificity for steel variants")
    print("   • Only resolve actual naming conflicts (hyphenation, etc.)")
    print("   • Keep wood- prefix removal (this makes sense)")
    print()
    
    # Restore steel variants
    steel_variants = restore_steel_variants()
    print()
    
    # Update generators
    update_generator_naming()
    print()
    
    print("📋 SUMMARY OF CORRECTED NAMING:")
    print("  ✅ PRESERVE: carbon-steel, galvanized-steel, tool-steel (distinct materials)")
    print("  ✅ PRESERVE: cast-iron (distinct from pure iron)")
    print("  ✅ STANDARDIZE: terra-cotta → terracotta (hyphenation fix)")
    print("  ✅ CONSOLIDATE: wood-{material} → {material} (prefix removal)")
    print()
    
    print("🎯 NEXT STEPS:")
    print("  1. Restore frontmatter files for steel variants")
    print("  2. Restore image files for steel variants") 
    print("  3. Test updated generators")
    print("  4. Verify material specificity is preserved")


if __name__ == "__main__":
    main()
