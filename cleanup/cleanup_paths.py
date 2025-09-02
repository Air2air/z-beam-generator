#!/usr/bin/env python3
"""
File Cleanup Script for Z-Beam Generator

Renames all content files with parentheses in their names to use clean slug naming.
This ensures consistent, clean paths without parentheses for all generated content.
"""

import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import logging

# Import our new slug utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils.slug_utils import create_filename_slug, get_clean_material_mapping


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def find_files_with_parentheses(base_dir: Path) -> List[Path]:
    """Find all files with parentheses in their names."""
    files_with_parens = []
    
    if not base_dir.exists():
        logger.warning(f"Directory {base_dir} does not exist")
        return files_with_parens
    
    for file_path in base_dir.rglob("*"):
        if file_path.is_file() and ('(' in file_path.name or ')' in file_path.name):
            files_with_parens.append(file_path)
    
    return files_with_parens


def extract_material_name_from_old_filename(filename: str) -> str:
    """Extract material name from old filename format with parentheses."""
    # Remove extension
    basename = filename.replace('.md', '').replace('.yaml', '').replace('.json', '')
    
    # Remove -laser-cleaning suffix
    if basename.endswith('-laser-cleaning'):
        basename = basename[:-len('-laser-cleaning')]
    
    # Convert slug back to material name with parentheses
    # Example: "metal-matrix-composites-(mmcs)" -> "Metal Matrix Composites (MMCs)"
    
    # Handle special cases with known mappings
    known_mappings = {
        'metal-matrix-composites-(mmcs)': 'Metal Matrix Composites (MMCs)',
        'ceramic-matrix-composites-(cmcs)': 'Ceramic Matrix Composites (CMCs)',
        'fiber-reinforced-polyurethane-(frpu)': 'Fiber-Reinforced Polyurethane (FRPU)',
        'glass-fiber-reinforced-polymers-(gfrp)': 'Glass Fiber Reinforced Polymers (GFRP)'
    }
    
    if basename in known_mappings:
        return known_mappings[basename]
    
    # For other cases, try to reconstruct
    # Convert hyphens to spaces and title case
    words = basename.replace('-', ' ').split()
    
    # Look for patterns like "word (acronym)"
    if len(words) >= 2 and words[-1].startswith('(') and words[-1].endswith(')'):
        # Last word is in parentheses format
        material_words = words[:-1]
        acronym = words[-1]
        material_name = ' '.join(word.capitalize() for word in material_words)
        return f"{material_name} {acronym.upper()}"
    
    # Default: just title case
    return ' '.join(word.capitalize() for word in words)


def create_rename_plan(files: List[Path]) -> List[Tuple[Path, Path]]:
    """Create a plan for renaming files with parentheses."""
    rename_plan = []
    
    for old_path in files:
        # Extract material name from old filename
        old_filename = old_path.name
        material_name = extract_material_name_from_old_filename(old_filename)
        
        # Create new clean filename
        if old_filename.endswith('.md'):
            new_filename = create_filename_slug(material_name) + '.md'
        elif old_filename.endswith('.yaml'):
            new_filename = create_filename_slug(material_name) + '.yaml'
        elif old_filename.endswith('.json'):
            new_filename = create_filename_slug(material_name) + '.json'
        else:
            # Keep original extension
            extension = old_path.suffix
            new_filename = create_filename_slug(material_name) + extension
        
        new_path = old_path.parent / new_filename
        
        # Only add to plan if names are different
        if old_path.name != new_filename:
            rename_plan.append((old_path, new_path))
    
    return rename_plan


def execute_rename_plan(rename_plan: List[Tuple[Path, Path]], dry_run: bool = True) -> Dict[str, int]:
    """Execute the rename plan."""
    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0
    }
    
    logger.info(f"{'DRY RUN: ' if dry_run else ''}Processing {len(rename_plan)} file renames...")
    
    for old_path, new_path in rename_plan:
        try:
            # Check if target already exists
            if new_path.exists():
                logger.warning(f"Target already exists: {new_path}")
                results['skipped'] += 1
                continue
            
            if dry_run:
                logger.info(f"WOULD RENAME: {old_path.name} → {new_path.name}")
                results['success'] += 1
            else:
                # Perform the actual rename
                old_path.rename(new_path)
                logger.info(f"RENAMED: {old_path.name} → {new_path.name}")
                results['success'] += 1
                
        except Exception as e:
            logger.error(f"Failed to rename {old_path}: {e}")
            results['failed'] += 1
    
    return results


def update_materials_yaml(dry_run: bool = True) -> bool:
    """Update materials.yaml to use clean names."""
    materials_file = Path("data/materials.yaml")
    
    if not materials_file.exists():
        logger.warning("materials.yaml not found")
        return False
    
    try:
        with open(materials_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get mapping of old names to clean names
        clean_mapping = get_clean_material_mapping()
        
        # Replace parenthetical names with clean names
        updated_content = content
        changes_made = False
        
        for old_name, clean_slug in clean_mapping.items():
            # Convert clean slug back to a clean display name
            clean_display_name = clean_slug.replace('-', ' ').title()
            # Handle acronyms
            clean_display_name = clean_display_name.replace(' Mmcs', ' MMCs')
            clean_display_name = clean_display_name.replace(' Cmcs', ' CMCs') 
            clean_display_name = clean_display_name.replace(' Frpu', ' FRPU')
            clean_display_name = clean_display_name.replace(' Gfrp', ' GFRP')
            
            if old_name in updated_content:
                if dry_run:
                    logger.info(f"WOULD UPDATE: '{old_name}' → '{clean_display_name}'")
                else:
                    updated_content = updated_content.replace(old_name, clean_display_name)
                    logger.info(f"UPDATED: '{old_name}' → '{clean_display_name}'")
                changes_made = True
        
        if changes_made and not dry_run:
            # Backup original file
            backup_file = materials_file.with_suffix('.yaml.backup')
            shutil.copy2(materials_file, backup_file)
            logger.info(f"Backed up original to {backup_file}")
            
            # Write updated content
            with open(materials_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            logger.info("Updated materials.yaml")
        
        return changes_made
        
    except Exception as e:
        logger.error(f"Error updating materials.yaml: {e}")
        return False


def main():
    """Main cleanup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up Z-Beam file paths by removing parentheses")
    parser.add_argument('--dry-run', action='store_true', default=True, 
                       help='Show what would be done without making changes (default)')
    parser.add_argument('--execute', action='store_true', 
                       help='Actually perform the rename operations')
    parser.add_argument('--content-only', action='store_true',
                       help='Only process content files, skip materials.yaml')
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = not args.execute
    
    if dry_run:
        logger.info("🔍 DRY RUN MODE - No files will be modified")
    else:
        logger.info("🚀 EXECUTION MODE - Files will be renamed")
    
    logger.info("=" * 60)
    
    # Find all files with parentheses in content directory
    content_dir = Path("content")
    files_with_parens = find_files_with_parentheses(content_dir)
    
    if not files_with_parens:
        logger.info("✅ No files with parentheses found in content directory")
    else:
        logger.info(f"📂 Found {len(files_with_parens)} files with parentheses")
        
        # Create rename plan
        rename_plan = create_rename_plan(files_with_parens)
        
        if not rename_plan:
            logger.info("✅ All files already have clean names")
        else:
            logger.info(f"📋 Created rename plan for {len(rename_plan)} files")
            
            # Show rename plan
            logger.info("\n📝 Rename Plan:")
            logger.info("-" * 40)
            for old_path, new_path in rename_plan:
                logger.info(f"  {old_path.name}")
                logger.info(f"  → {new_path.name}")
                logger.info("")
            
            # Execute rename plan
            results = execute_rename_plan(rename_plan, dry_run)
            
            logger.info("\n📊 Results:")
            logger.info(f"  ✅ Successful: {results['success']}")
            logger.info(f"  ❌ Failed: {results['failed']}")
            logger.info(f"  ⏭️  Skipped: {results['skipped']}")
    
    # Update materials.yaml unless content-only flag is set
    if not args.content_only:
        logger.info("\n📄 Updating materials.yaml...")
        logger.info("-" * 40)
        materials_updated = update_materials_yaml(dry_run)
        
        if materials_updated:
            logger.info("✅ Materials.yaml update plan created")
        else:
            logger.info("✅ Materials.yaml already clean or no changes needed")
    
    logger.info("\n" + "=" * 60)
    if dry_run:
        logger.info("🔍 DRY RUN COMPLETE - Use --execute to apply changes")
    else:
        logger.info("🚀 CLEANUP COMPLETE - All file paths are now clean!")
    
    logger.info("\n💡 Future generations will automatically use clean paths")
    logger.info("   All new content will be generated with clean slugs")


if __name__ == "__main__":
    main()
