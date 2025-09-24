#!/usr/bin/env python3
"""
Frontmatter Converter Script
Converts migrated Markdown frontmatter files to pure YAML format.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontmatterConverter:
    """Converts Markdown frontmatter files to YAML format"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.materials_dir = self.project_root / "frontmatter" / "materials"
        self.stats = {
            'total_files': 0,
            'converted_files': 0,
            'failed_files': 0,
            'skipped_files': 0
        }
    
    def extract_frontmatter_from_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Extract YAML frontmatter from a Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file starts with frontmatter delimiter
            if not content.startswith('---'):
                raise ValueError("No frontmatter found - file doesn't start with '---'")
            
            # Split content to extract frontmatter
            parts = content.split('---')
            if len(parts) < 3:
                raise ValueError("Invalid frontmatter format - less than 3 parts after split")
            
            # The frontmatter is the second part (index 1)
            frontmatter_content = parts[1].strip()
            
            # Parse YAML
            frontmatter_data = yaml.safe_load(frontmatter_content)
            
            if frontmatter_data is None:
                raise ValueError("Frontmatter parsed to None - invalid YAML")
            
            return frontmatter_data
            
        except Exception as e:
            raise ValueError(f"Failed to extract frontmatter: {e}")
    
    def convert_filename(self, old_filename: str) -> str:
        """Convert filename from old format to new format"""
        # Remove -laser-cleaning.md and add .yaml
        if old_filename.endswith('-laser-cleaning.md'):
            base_name = old_filename.replace('-laser-cleaning.md', '')
            return f"{base_name}.yaml"
        else:
            # Fallback - just change extension
            return old_filename.replace('.md', '.yaml')
    
    def convert_file(self, md_file_path: Path) -> bool:
        """Convert a single Markdown file to YAML"""
        try:
            # Extract frontmatter
            frontmatter_data = self.extract_frontmatter_from_markdown(md_file_path)
            
            # Generate new filename
            new_filename = self.convert_filename(md_file_path.name)
            yaml_file_path = self.materials_dir / new_filename
            
            # Write YAML file
            with open(yaml_file_path, 'w', encoding='utf-8') as f:
                yaml.dump(frontmatter_data, f, default_flow_style=False, sort_keys=False, indent=2)
            
            logger.info(f"✅ Converted: {md_file_path.name} → {new_filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to convert {md_file_path.name}: {e}")
            return False
    
    def convert_all_files(self) -> Dict[str, Any]:
        """Convert all Markdown files in the materials directory to YAML"""
        logger.info("🔄 Starting frontmatter conversion...")
        
        if not self.materials_dir.exists():
            logger.error(f"❌ Materials directory not found: {self.materials_dir}")
            return self.stats
        
        # Find all Markdown files
        md_files = list(self.materials_dir.glob("*.md"))
        self.stats['total_files'] = len(md_files)
        
        if self.stats['total_files'] == 0:
            logger.info("ℹ️ No Markdown files found to convert")
            return self.stats
        
        logger.info(f"🔍 Found {self.stats['total_files']} Markdown files to convert")
        
        # Convert each file
        for md_file in md_files:
            if self.convert_file(md_file):
                self.stats['converted_files'] += 1
                
                # Remove the original Markdown file after successful conversion
                try:
                    md_file.unlink()
                    logger.debug(f"🗑️ Removed original: {md_file.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not remove original file {md_file.name}: {e}")
            else:
                self.stats['failed_files'] += 1
        
        # Report results
        logger.info("=" * 50)
        logger.info("📊 CONVERSION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"📁 Total files: {self.stats['total_files']}")
        logger.info(f"✅ Converted: {self.stats['converted_files']}")
        logger.info(f"❌ Failed: {self.stats['failed_files']}")
        
        if self.stats['failed_files'] == 0:
            logger.info("🎉 All files converted successfully!")
        else:
            logger.warning(f"⚠️ {self.stats['failed_files']} files failed to convert")
        
        return self.stats

def main():
    """Main execution function"""
    converter = FrontmatterConverter()
    stats = converter.convert_all_files()
    
    # Exit with error code if any conversions failed
    if stats['failed_files'] > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    main()
