#!/usr/bin/env python3
"""
Materials.yaml Cleanup Tool for Categories.yaml Integration

Removes redundant sections from Materials.yaml that are now provided by Categories.yaml:
- Removes category_ranges section (fully covered by Categories.yaml)
- Preserves machineSettingsRanges (machine-specific, not in Categories.yaml)
- Preserves material_index and materials sections (material-specific data)
- Creates backup before cleanup

Author: Z-Beam Content Generator
Date: 2025-09-26
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MaterialsYamlCleaner:
    """Clean Materials.yaml by removing redundant data now in Categories.yaml"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.materials_path = self.base_dir / "data" / "Materials.yaml"
        
    def load_materials_yaml(self) -> Dict[str, Any]:
        """Load current Materials.yaml"""
        try:
            with open(self.materials_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading Materials.yaml: {e}")
            raise
            
    def create_backup(self) -> Path:
        """Create timestamped backup of Materials.yaml"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.base_dir / "data" / f"materials_pre_categories_cleanup_{timestamp}.yaml"
        
        try:
            shutil.copy2(self.materials_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
            
    def clean_materials_data(self, materials_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove redundant sections from materials data"""
        cleaned_data = materials_data.copy()
        
        # Remove category_ranges - now fully provided by Categories.yaml
        if 'category_ranges' in cleaned_data:
            logger.info("Removing category_ranges section (now in Categories.yaml)")
            del cleaned_data['category_ranges']
        
        # Keep machineSettingsRanges - this is machine-specific, not material category data
        if 'machineSettingsRanges' in cleaned_data:
            logger.info("Preserving machineSettingsRanges (machine-specific data)")
            
        # Keep material_index - this is material indexing data
        if 'material_index' in cleaned_data:
            logger.info("Preserving material_index (material-specific indexing)")
            
        # Keep materials - this is the core material database
        if 'materials' in cleaned_data:
            logger.info("Preserving materials section (core material database)")
            
        return cleaned_data
        
    def save_cleaned_materials(self, cleaned_data: Dict[str, Any]) -> None:
        """Save cleaned Materials.yaml"""
        try:
            with open(self.materials_path, 'w', encoding='utf-8') as file:
                yaml.dump(cleaned_data, file, 
                         default_flow_style=False, 
                         allow_unicode=True,
                         sort_keys=False,
                         indent=2,
                         width=1000)  # Prevent line wrapping
            logger.info(f"Saved cleaned Materials.yaml: {self.materials_path}")
        except Exception as e:
            logger.error(f"Error saving cleaned Materials.yaml: {e}")
            raise
            
    def validate_cleaned_structure(self, cleaned_data: Dict[str, Any]) -> bool:
        """Validate that cleaned Materials.yaml has required structure"""
        required_sections = ['machineSettingsRanges', 'material_index', 'materials']
        removed_sections = ['category_ranges']
        
        # Check required sections exist
        for section in required_sections:
            if section not in cleaned_data:
                logger.error(f"Missing required section after cleanup: {section}")
                return False
                
        # Check removed sections are gone
        for section in removed_sections:
            if section in cleaned_data:
                logger.error(f"Section should have been removed: {section}")
                return False
                
        # Validate materials section structure
        if 'materials' in cleaned_data:
            materials_section = cleaned_data['materials']
            if not isinstance(materials_section, dict):
                logger.error("Materials section should be a dictionary")
                return False
                
            # Check for categories
            categories = list(materials_section.keys())
            if len(categories) == 0:
                logger.error("No material categories found")
                return False
                
            logger.info(f"Validated {len(categories)} material categories")
            
        logger.info("✅ Cleaned Materials.yaml structure validation passed")
        return True
        
    def generate_cleanup_summary(self, original_data: Dict[str, Any], cleaned_data: Dict[str, Any]) -> str:
        """Generate summary of cleanup changes"""
        summary = []
        summary.append("# Materials.yaml Cleanup Summary")
        summary.append(f"**Cleanup Date**: {datetime.now().isoformat()}")
        summary.append("")
        
        # Sections removed
        removed_sections = []
        for section in original_data:
            if section not in cleaned_data:
                removed_sections.append(section)
                
        if removed_sections:
            summary.append("## Sections Removed")
            for section in removed_sections:
                if section == 'category_ranges':
                    summary.append(f"- **{section}**: Moved to Categories.yaml (enhanced with additional properties)")
                else:
                    summary.append(f"- **{section}**: Redundant data")
            summary.append("")
            
        # Sections preserved
        preserved_sections = list(cleaned_data.keys())
        summary.append("## Sections Preserved")
        for section in preserved_sections:
            if section == 'machineSettingsRanges':
                summary.append(f"- **{section}**: Machine-specific settings (not category-based)")
            elif section == 'material_index':
                summary.append(f"- **{section}**: Material indexing and metadata")
            elif section == 'materials':
                summary.append(f"- **{section}**: Core material database with specific material instances")
            else:
                summary.append(f"- **{section}**: Material-specific data")
        summary.append("")
        
        # Size reduction
        original_size = len(str(original_data))
        cleaned_size = len(str(cleaned_data))
        size_reduction = original_size - cleaned_size
        reduction_percent = (size_reduction / original_size) * 100
        
        summary.append("## File Size Impact")
        summary.append(f"- **Original Size**: ~{original_size:,} characters")
        summary.append(f"- **Cleaned Size**: ~{cleaned_size:,} characters")
        summary.append(f"- **Reduction**: ~{size_reduction:,} characters ({reduction_percent:.1f}%)")
        summary.append("")
        
        summary.append("## Integration Status")
        summary.append("- ✅ Categories.yaml contains enhanced category_ranges data")
        summary.append("- ✅ Materials.yaml focused on material-specific instances")
        summary.append("- ✅ Machine settings preserved for equipment configuration")
        summary.append("- 🔄 **Next Step**: Update frontmatter generator to load Categories.yaml")
        
        return "\\n".join(summary)
        
    def run_cleanup(self) -> bool:
        """Run complete cleanup process"""
        logger.info("🧹 Starting Materials.yaml cleanup for Categories.yaml integration...")
        
        try:
            # Load original data
            logger.info("Loading Materials.yaml...")
            original_data = self.load_materials_yaml()
            
            # Create backup
            backup_path = self.create_backup()
            
            # Clean data
            logger.info("Cleaning redundant sections...")
            cleaned_data = self.clean_materials_data(original_data)
            
            # Validate cleaned structure
            if not self.validate_cleaned_structure(cleaned_data):
                logger.error("Cleaned structure validation failed")
                return False
                
            # Save cleaned data
            self.save_cleaned_materials(cleaned_data)
            
            # Generate summary
            summary = self.generate_cleanup_summary(original_data, cleaned_data)
            summary_path = self.base_dir / "docs" / "MATERIALS_CLEANUP_SUMMARY.md"
            
            try:
                with open(summary_path, 'w', encoding='utf-8') as file:
                    file.write(summary)
                logger.info(f"📄 Cleanup summary saved: {summary_path}")
            except Exception as e:
                logger.warning(f"Could not save summary: {e}")
                
            logger.info("✅ Materials.yaml cleanup completed successfully!")
            logger.info(f"📁 Original backed up: {backup_path}")
            logger.info(f"📁 Cleaned Materials.yaml: {self.materials_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return False

def main():
    """Main execution"""
    cleaner = MaterialsYamlCleaner()
    success = cleaner.run_cleanup()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())