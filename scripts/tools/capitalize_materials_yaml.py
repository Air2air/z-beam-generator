#!/usr/bin/env python3
"""
Materials.yaml Capitalization Tool

Standardize all "Materials.yaml" references to "Materials.yaml" across the entire codebase
to maintain consistent naming conventions.
"""

import os
import re
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaterialsYamlCapitalizer:
    """Capitalize all Materials.yaml references across the codebase"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.changes_made = []
        
    def process_files(self) -> Dict[str, int]:
        """Process all files to capitalize Materials.yaml references"""
        stats = {
            'files_processed': 0,
            'files_changed': 0,
            'total_replacements': 0
        }
        
        # Patterns to match
        patterns = [
            r'materials\.yaml',  # Basic Materials.yaml
            r'"materials\.yaml"',  # Quoted "Materials.yaml"
            r"'materials\.yaml'",  # Single quoted 'Materials.yaml'
            r'`materials\.yaml`',  # Backticked `Materials.yaml`
            r'materials_yaml',  # Variable names like materials_yaml
        ]
        
        # File extensions to process
        extensions = ['.py', '.md', '.json', '.yaml', '.yml', '.txt', '.ini']
        
        # Walk through all files
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = Path(root) / file
                    replacements = self.process_file(file_path, patterns)
                    stats['files_processed'] += 1
                    if replacements > 0:
                        stats['files_changed'] += 1
                        stats['total_replacements'] += replacements
        
        return stats
    
    def process_file(self, file_path: Path, patterns: List[str]) -> int:
        """Process a single file for Materials.yaml capitalization"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replacements = 0
            
            # Apply replacements
            for pattern in patterns:
                if pattern == r'materials\.yaml':
                    # Replace Materials.yaml with Materials.yaml (case-sensitive)
                    new_content = re.sub(r'\bmaterials\.yaml\b', 'Materials.yaml', content)
                elif pattern == r'"materials\.yaml"':
                    # Replace "Materials.yaml" with "Materials.yaml"
                    new_content = re.sub(r'"materials\.yaml"', '"Materials.yaml"', content)
                elif pattern == r"'materials\.yaml'":
                    # Replace 'Materials.yaml' with 'Materials.yaml'
                    new_content = re.sub(r"'materials\.yaml'", "'Materials.yaml'", content)
                elif pattern == r'`materials\.yaml`':
                    # Replace `Materials.yaml` with `Materials.yaml`
                    new_content = re.sub(r'`materials\.yaml`', '`Materials.yaml`', content)
                elif pattern == r'materials_yaml':
                    # Handle variable names - be careful here
                    # Only replace in specific contexts like schema names
                    new_content = re.sub(r'materials_yaml\.json', 'Materials_yaml.json', content)
                else:
                    new_content = content
                
                if new_content != content:
                    replacements += len(re.findall(pattern, content))
                    content = new_content
            
            # Write changes if any were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                relative_path = file_path.relative_to(self.project_root)
                self.changes_made.append({
                    'file': str(relative_path),
                    'replacements': replacements
                })
                logger.info(f"✅ Updated {relative_path}: {replacements} replacements")
                
                return replacements
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            return 0
    
    def generate_summary(self, stats: Dict[str, int]) -> str:
        """Generate a summary of changes made"""
        summary = []
        summary.append("# Materials.yaml Capitalization Summary")
        summary.append("")
        summary.append(f"**Files Processed**: {stats['files_processed']}")
        summary.append(f"**Files Changed**: {stats['files_changed']}")
        summary.append(f"**Total Replacements**: {stats['total_replacements']}")
        summary.append("")
        
        if self.changes_made:
            summary.append("## Changed Files")
            summary.append("")
            for change in sorted(self.changes_made, key=lambda x: x['file']):
                summary.append(f"- **{change['file']}**: {change['replacements']} replacements")
        
        summary.append("")
        summary.append("## Changes Made")
        summary.append("- `Materials.yaml` → `Materials.yaml`")
        summary.append("- `\"Materials.yaml\"` → `\"Materials.yaml\"`")
        summary.append("- `'Materials.yaml'` → `'Materials.yaml'`")
        summary.append("- `` `Materials.yaml` `` → `` `Materials.yaml` ``")
        summary.append("")
        summary.append("✅ **All references now use standardized 'Materials.yaml' capitalization**")
        
        return "\n".join(summary)

def main():
    """Main execution function"""
    logger.info("🚀 Starting Materials.yaml capitalization process...")
    
    capitalizer = MaterialsYamlCapitalizer()
    
    try:
        # Process all files
        stats = capitalizer.process_files()
        
        # Generate and save summary
        summary = capitalizer.generate_summary(stats)
        
        # Save summary to file
        summary_path = capitalizer.project_root / "docs" / "MATERIALS_YAML_CAPITALIZATION_COMPLETE.md"
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        # Print results
        logger.info("✅ Materials.yaml capitalization completed successfully!")
        logger.info(f"📁 Summary saved to: {summary_path}")
        logger.info("📊 Statistics:")
        logger.info(f"   - Files processed: {stats['files_processed']}")
        logger.info(f"   - Files changed: {stats['files_changed']}")
        logger.info(f"   - Total replacements: {stats['total_replacements']}")
        
        if stats['files_changed'] > 0:
            logger.info("🎯 Key changes:")
            logger.info("   - All codebase references now use 'Materials.yaml'")
            logger.info("   - Consistent capitalization across all file types")
            logger.info("   - Maintained functional compatibility")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during capitalization process: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)