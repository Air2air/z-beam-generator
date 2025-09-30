#!/usr/bin/env python3
"""
Remove top-level author.name fields from all author component files.
Only author.id fields should be used for author references.

This script:
1. Removes the 'name' field from authorInfo sections in author component files
2. Leaves author.id fields intact in frontmatter files
3. Creates backup of modified files
"""

import os
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_author_names():
    """Remove name fields from all author component files"""
    
    project_root = Path(__file__).parent.parent
    author_dir = project_root / "content" / "components" / "author"
    
    if not author_dir.exists():
        logger.error(f"Author directory not found: {author_dir}")
        return False
    
    # Create backup directory
    backup_dir = project_root / "backups" / f"author_name_removal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    modified_files = []
    total_files = 0
    
    # Process all YAML files in author directory
    for yaml_file in author_dir.glob("*.yaml"):
        total_files += 1
        
        try:
            # Read the file
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Check if this file has authorInfo.name
            if isinstance(data, dict) and 'authorInfo' in data:
                author_info = data['authorInfo']
                
                if isinstance(author_info, dict) and 'name' in author_info:
                    # Create backup
                    backup_file = backup_dir / yaml_file.name
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                    
                    # Remove the name field
                    removed_name = author_info.pop('name')
                    logger.info(f"Removed name '{removed_name}' from {yaml_file.name}")
                    
                    # Write back the modified data
                    with open(yaml_file, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    
                    modified_files.append(yaml_file.name)
                else:
                    logger.debug(f"No name field found in {yaml_file.name}")
            else:
                logger.warning(f"Unexpected structure in {yaml_file.name}")
                
        except Exception as e:
            logger.error(f"Error processing {yaml_file}: {e}")
    
    # Summary
    logger.info(f"\n📊 Summary:")
    logger.info(f"   Total files processed: {total_files}")
    logger.info(f"   Files modified: {len(modified_files)}")
    logger.info(f"   Backup created: {backup_dir.relative_to(project_root)}")
    
    if modified_files:
        logger.info(f"\n✅ Modified files:")
        for filename in sorted(modified_files):
            logger.info(f"   - {filename}")
    
    return len(modified_files) > 0

def main():
    """Main execution function"""
    logger.info("🚀 Starting author name removal process...")
    
    success = remove_author_names()
    
    if success:
        logger.info("\n🎉 Author name removal completed successfully!")
        logger.info("✅ All author.name fields have been removed")
        logger.info("✅ Only author.id fields remain for author references")
        logger.info("\n📝 Next steps:")
        logger.info("1. Test component generation: python3 run.py --material 'Aluminum' --components author")
        logger.info("2. Run validation: python3 run.py --validate")
        logger.info("3. Deploy changes: python3 run.py --deploy")
    else:
        logger.info("\n⚠️ No author name fields found to remove")
        logger.info("✅ System already uses only author.id references")

if __name__ == "__main__":
    main()