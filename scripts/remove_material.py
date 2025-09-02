#!/usr/bin/env python3
"""
Material Removal Script for Z-Beam Generator

Safely removes a material from the materials list and all associated generated content files.
This script provides comprehensive cleanup for materials that are no longer needed.

Usage:
    python3 remove_material.py --material "Material Name" --dry-run
    python3 remove_material.py --material "Material Name" --execute
    python3 remove_material.py --list-materials
    python3 remove_material.py --find-orphans
"""

import argparse
import yaml
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Import slug utilities for consistent naming
try:
    from utils.slug_utils import create_material_slug, create_filename_slug
except ImportError:
    # Fallback to basic slug generation if utils not available
    def create_material_slug(name: str) -> str:
        return name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')
    def create_filename_slug(name: str, suffix: str = "laser-cleaning") -> str:
        slug = create_material_slug(name)
        return f"{slug}-{suffix}" if suffix else slug

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MaterialRemover:
    """Handles safe removal of materials and their associated files"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.materials_file = self.project_root / "data" / "materials.yaml"
        self.content_dir = self.project_root / "content"
        self.components_dir = self.content_dir / "components"
        
        # Component types that generate files
        self.component_types = [
            "frontmatter", "content", "metatags", "jsonld", 
            "tags", "bullets", "caption", "table", 
            "propertiestable", "badgesymbol", "author"
        ]
    
    def load_materials(self) -> Dict[str, Dict]:
        """Load materials from YAML file"""
        if not self.materials_file.exists():
            raise FileNotFoundError(f"Materials file not found: {self.materials_file}")
        
        try:
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data.get('materials', {})
        except Exception as e:
            raise Exception(f"Error loading materials file: {e}")
    
    def save_materials(self, materials_data: Dict, backup: bool = True) -> None:
        """Save materials back to YAML file with optional backup"""
        if backup:
            backup_file = self.materials_file.with_suffix('.yaml.backup')
            shutil.copy2(self.materials_file, backup_file)
            logger.info(f"Created backup: {backup_file}")
        
        # Reconstruct full YAML structure
        full_data = {
            'materials': materials_data,
            'metadata': {
                'total_categories': len(materials_data),
                'total_materials': sum(len(cat.get('items', [])) for cat in materials_data.values()),
                'last_updated': '2025-08-28',
                'format_version': '1.0'
            }
        }
        
        try:
            with open(self.materials_file, 'w', encoding='utf-8') as f:
                yaml.dump(full_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            logger.info(f"Updated materials file: {self.materials_file}")
        except Exception as e:
            raise Exception(f"Error saving materials file: {e}")
    
    def find_material_in_list(self, material_name: str) -> Optional[Tuple[str, int]]:
        """Find material in the materials list, return (category, index) if found"""
        materials = self.load_materials()
        
        for category, category_data in materials.items():
            items = category_data.get('items', [])
            for i, item in enumerate(items):
                if item.lower() == material_name.lower():
                    return category, i
        
        return None
    
    def find_material_files(self, material_name: str) -> Dict[str, List[Path]]:
        """Find all files associated with a material"""
        material_slug = create_material_slug(material_name)
        filename_base = create_filename_slug(material_name).replace('-laser-cleaning', '')
        
        found_files = {}
        
        # Search in each component directory
        for component_type in self.component_types:
            component_dir = self.components_dir / component_type
            if not component_dir.exists():
                continue
            
            files = []
            
            # Look for exact matches
            exact_file = component_dir / f"{material_slug}-laser-cleaning.md"
            if exact_file.exists():
                files.append(exact_file)
            
            # Look for pattern matches (in case of naming variations)
            pattern_files = list(component_dir.glob(f"{filename_base}*.md"))
            for file in pattern_files:
                if file not in files:
                    files.append(file)
            
            # Look for similar slugs (fuzzy matching)
            all_files = list(component_dir.glob("*.md"))
            for file in all_files:
                file_stem = file.stem.replace('-laser-cleaning', '')
                if self._is_similar_slug(file_stem, material_slug):
                    if file not in files:
                        files.append(file)
            
            if files:
                found_files[component_type] = files
        
        return found_files
    
    def _is_similar_slug(self, file_slug: str, target_slug: str) -> bool:
        """Check if file slug is similar to target slug (for fuzzy matching)"""
        # Remove common variations
        file_clean = file_slug.lower().replace('-', ' ').replace('_', ' ')
        target_clean = target_slug.lower().replace('-', ' ').replace('_', ' ')
        
        # Simple similarity check
        file_words = set(file_clean.split())
        target_words = set(target_clean.split())
        
        # If most words match, consider it similar
        if len(target_words) == 0:
            return False
        
        overlap = len(file_words.intersection(target_words))
        similarity = overlap / len(target_words)
        
        return similarity >= 0.8  # 80% word overlap
    
    def find_orphaned_files(self) -> Dict[str, List[Path]]:
        """Find files that don't correspond to any material in the list"""
        materials = self.load_materials()
        
        # Get all material names and their slugs
        valid_slugs = set()
        for category_data in materials.values():
            for material in category_data.get('items', []):
                slug = create_material_slug(material)
                valid_slugs.add(slug)
        
        orphaned_files = {}
        
        # Check each component directory
        for component_type in self.component_types:
            component_dir = self.components_dir / component_type
            if not component_dir.exists():
                continue
            
            orphans = []
            for file in component_dir.glob("*.md"):
                # Extract material slug from filename
                file_slug = file.stem.replace('-laser-cleaning', '')
                
                # Check if this slug corresponds to any valid material
                if file_slug not in valid_slugs:
                    # Double-check with fuzzy matching
                    is_valid = False
                    for valid_slug in valid_slugs:
                        if self._is_similar_slug(file_slug, valid_slug):
                            is_valid = True
                            break
                    
                    if not is_valid:
                        orphans.append(file)
            
            if orphans:
                orphaned_files[component_type] = orphans
        
        return orphaned_files
    
    def remove_material(self, material_name: str, dry_run: bool = True) -> Dict[str, any]:
        """Remove material from list and delete associated files"""
        results = {
            'material_found': False,
            'material_removed': False,
            'files_found': {},
            'files_removed': {},
            'errors': []
        }
        
        # Find material in list
        material_location = self.find_material_in_list(material_name)
        if material_location:
            category, index = material_location
            results['material_found'] = True
            results['material_category'] = category
            results['material_index'] = index
            
            logger.info(f"Found material '{material_name}' in category '{category}' at index {index}")
        else:
            logger.warning(f"Material '{material_name}' not found in materials list")
            results['errors'].append(f"Material '{material_name}' not found in materials list")
        
        # Find associated files
        material_files = self.find_material_files(material_name)
        results['files_found'] = material_files
        
        if material_files:
            total_files = sum(len(files) for files in material_files.values())
            logger.info(f"Found {total_files} files across {len(material_files)} component types")
            
            for component_type, files in material_files.items():
                logger.info(f"  {component_type}: {len(files)} files")
                for file in files:
                    logger.info(f"    - {file.name}")
        else:
            logger.info("No associated files found")
        
        # Perform removal if not dry run
        if not dry_run:
            # Remove from materials list
            if material_location:
                try:
                    materials = self.load_materials()
                    category, index = material_location
                    materials[category]['items'].pop(index)
                    self.save_materials(materials)
                    results['material_removed'] = True
                    logger.info(f"Removed '{material_name}' from materials list")
                except Exception as e:
                    error_msg = f"Error removing material from list: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Remove files
            for component_type, files in material_files.items():
                removed_files = []
                for file in files:
                    try:
                        file.unlink()
                        removed_files.append(file)
                        logger.info(f"Removed file: {file}")
                    except Exception as e:
                        error_msg = f"Error removing file {file}: {e}"
                        logger.error(error_msg)
                        results['errors'].append(error_msg)
                
                if removed_files:
                    results['files_removed'][component_type] = removed_files
        
        return results
    
    def list_all_materials(self) -> Dict[str, List[str]]:
        """List all materials organized by category"""
        try:
            materials = self.load_materials()
            result = {}
            for category, category_data in materials.items():
                result[category] = category_data.get('items', [])
            return result
        except Exception as e:
            logger.error(f"Error loading materials: {e}")
            return {}


def main():
    """Command-line interface for material removal"""
    parser = argparse.ArgumentParser(
        description="Remove material from Z-Beam Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # List all materials
  python3 remove_material.py --list-materials
  
  # Find orphaned files
  python3 remove_material.py --find-orphans
  
  # Dry run removal (safe preview)
  python3 remove_material.py --material "Metal Matrix Composites MMCs" --dry-run
  
  # Actually remove material and files
  python3 remove_material.py --material "Metal Matrix Composites MMCs" --execute
  
  # Remove with confirmation prompt
  python3 remove_material.py --material "Aluminum" --execute --confirm
        """
    )
    
    parser.add_argument('--material', help='Material name to remove')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be removed without making changes (default)')
    parser.add_argument('--execute', action='store_true',
                       help='Actually perform the removal operations')
    parser.add_argument('--confirm', action='store_true',
                       help='Require confirmation before removal')
    parser.add_argument('--list-materials', action='store_true',
                       help='List all available materials by category')
    parser.add_argument('--find-orphans', action='store_true',
                       help='Find orphaned files that don\'t match any material')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine if this is a dry run
    dry_run = not args.execute
    
    # Initialize remover
    remover = MaterialRemover()
    
    # List materials
    if args.list_materials:
        logger.info("📋 Available materials by category:")
        logger.info("=" * 50)
        
        materials = remover.list_all_materials()
        if not materials:
            logger.error("No materials found or error loading materials")
            return 1
        
        for category, items in materials.items():
            logger.info(f"\n📂 {category.upper()} ({len(items)} materials):")
            for i, material in enumerate(items, 1):
                slug = create_material_slug(material)
                logger.info(f"   {i:2d}. {material}")
                logger.info(f"       Slug: {slug}")
        
        total_materials = sum(len(items) for items in materials.values())
        logger.info(f"\n📊 Total: {total_materials} materials across {len(materials)} categories")
        return 0
    
    # Find orphaned files
    if args.find_orphans:
        logger.info("🔍 Finding orphaned files...")
        logger.info("=" * 50)
        
        orphans = remover.find_orphaned_files()
        if not orphans:
            logger.info("✅ No orphaned files found")
            return 0
        
        total_orphans = sum(len(files) for files in orphans.values())
        logger.info(f"Found {total_orphans} orphaned files:")
        
        for component_type, files in orphans.items():
            logger.info(f"\n📂 {component_type} ({len(files)} files):")
            for file in files:
                logger.info(f"   - {file.name}")
        
        logger.info("\n💡 Use --material with --execute to remove specific materials")
        logger.info("   Or manually review and delete orphaned files")
        return 0
    
    # Remove material
    if args.material:
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")
        else:
            logger.info("🚀 EXECUTION MODE - Changes will be made")
        
        logger.info("=" * 60)
        logger.info(f"Processing material: {args.material}")
        
        # Confirmation check
        if not dry_run and args.confirm:
            response = input(f"\nAre you sure you want to remove '{args.material}' and all its files? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("❌ Removal cancelled by user")
                return 0
        
        # Perform removal
        results = remover.remove_material(args.material, dry_run=dry_run)
        
        # Report results
        logger.info("\n📊 REMOVAL RESULTS:")
        logger.info("=" * 40)
        
        if results['material_found']:
            logger.info(f"✅ Material found in category: {results.get('material_category', 'unknown')}")
            if results['material_removed']:
                logger.info("✅ Material removed from materials list")
            elif not dry_run:
                logger.error("❌ Failed to remove material from list")
        else:
            logger.warning("⚠️  Material not found in materials list")
        
        # File results
        files_found = results['files_found']
        if files_found:
            total_files = sum(len(files) for files in files_found.values())
            logger.info(f"📁 Found {total_files} files to remove:")
            
            for component_type, files in files_found.items():
                logger.info(f"   {component_type}: {len(files)} files")
            
            if not dry_run:
                files_removed = results['files_removed']
                if files_removed:
                    total_removed = sum(len(files) for files in files_removed.values())
                    logger.info(f"✅ Successfully removed {total_removed} files")
                else:
                    logger.error("❌ No files were removed")
        else:
            logger.info("📁 No associated files found")
        
        # Errors
        if results['errors']:
            logger.error(f"\n❌ {len(results['errors'])} errors occurred:")
            for error in results['errors']:
                logger.error(f"   - {error}")
        
        # Summary
        logger.info("\n" + "=" * 60)
        if dry_run:
            logger.info("🔍 DRY RUN COMPLETE - Use --execute to apply changes")
        else:
            if results['errors']:
                logger.error("🚀 REMOVAL COMPLETED WITH ERRORS")
            else:
                logger.info("🚀 REMOVAL COMPLETED SUCCESSFULLY")
        
        return 1 if results['errors'] else 0
    
    # No action specified
    logger.error("❌ No action specified")
    logger.info("Use --list-materials, --find-orphans, or --material")
    parser.print_help()
    return 1


if __name__ == "__main__":
    exit(main())
