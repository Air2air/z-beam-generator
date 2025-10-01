#!/usr/bin/env python3
"""
Regenerate Broken Caption YAMLs
=====================================

Special script to regenerate the 9 materials with YAML formatting issues.
Uses raw file manipulation to remove broken caption sections, then regenerates
them with the fixed YAML formatting.

Affected materials:
- Aluminum, Steel, Platinum, Gold, Copper, Brass, Silver, Nickel, Bronze
"""

import sys
import yaml
import re
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.caption.generators.frontmatter_generator import FrontmatterCaptionGenerator
from api.client_factory import create_api_client

class BrokenCaptionRegenerator:
    """Regenerates captions for files with YAML formatting issues"""
    
    def __init__(self):
        self.caption_generator = FrontmatterCaptionGenerator()
        self.api_client = None
        
        # Materials with broken YAML
        self.broken_materials = {
            'Aluminum': 'aluminum-laser-cleaning.yaml',
            'Steel': 'steel-laser-cleaning.yaml',
            'Platinum': 'platinum-laser-cleaning.yaml',
            'Gold': 'gold-laser-cleaning.yaml',
            'Copper': 'copper-laser-cleaning.yaml',
            'Brass': 'brass-laser-cleaning.yaml',
            'Silver': 'silver-laser-cleaning.yaml',
            'Nickel': 'nickel-laser-cleaning.yaml',
            'Bronze': 'bronze-laser-cleaning.yaml'
        }
    
    def initialize_api_client(self) -> bool:
        """Initialize API client"""
        try:
            self.api_client = create_api_client('deepseek')
            print("✅ API client initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize API client: {e}")
            return False
    
    def remove_caption_section(self, content: str) -> tuple[str, bool]:
        """Remove the caption section from YAML content"""
        
        # Find the caption section - it's a top-level key
        # Pattern: "caption:" followed by nested content until next top-level key or end
        
        lines = content.split('\n')
        output_lines = []
        in_caption = False
        caption_indent = 0
        
        for i, line in enumerate(lines):
            # Check if this is the caption key (no indentation or minimal)
            if re.match(r'^caption:\s*$', line) or re.match(r'^caption:\s*\{', line):
                in_caption = True
                caption_indent = len(line) - len(line.lstrip())
                print(f"   Found caption section at line {i+1}")
                continue
            
            # If we're in caption section, skip lines until we hit same-level key
            if in_caption:
                # Check if this is a new top-level key (same or less indentation)
                current_indent = len(line) - len(line.lstrip())
                
                # Empty lines continue caption section
                if not line.strip():
                    continue
                
                # If line has same or less indentation than "caption:", we're done
                if current_indent <= caption_indent and line.strip():
                    in_caption = False
                    output_lines.append(line)
                    continue
                
                # Still in caption section, skip this line
                continue
            
            # Not in caption section, keep this line
            output_lines.append(line)
        
        cleaned_content = '\n'.join(output_lines)
        return cleaned_content, True
    
    def load_yaml_without_caption(self, file_path: Path) -> dict | None:
        """Load YAML after removing broken caption section"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file uses frontmatter format (starts with ---)
            has_frontmatter_markers = content.startswith('---')
            
            if has_frontmatter_markers:
                # Strip frontmatter markers before processing
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1].strip()
                else:
                    yaml_content = content
            else:
                yaml_content = content
            
            # Remove caption section
            cleaned_content, success = self.remove_caption_section(yaml_content)
            
            if not success:
                print("   ⚠️  Could not identify caption section")
                return None
            
            # Try to parse the cleaned YAML
            data = yaml.safe_load(cleaned_content)
            print("   ✅ Loaded YAML without caption section")
            return data
            
        except Exception as e:
            print(f"   ❌ Error loading YAML: {e}")
            return None
    
    def generate_new_caption(self, material_name: str, frontmatter_data: dict) -> dict | None:
        """Generate new caption content"""
        try:
            material_data = {
                "name": material_name,
                "category": frontmatter_data.get("category", ""),
                "subcategory": frontmatter_data.get("subcategory", "")
            }
            
            print(f"   🔄 Generating new caption for {material_name}...")
            
            result = self.caption_generator.generate_for_frontmatter(
                material_name=material_name,
                material_data=material_data,
                api_client=self.api_client,
                frontmatter_data=frontmatter_data,
                author_info=frontmatter_data.get('author', {})
            )
            
            if result.success:
                print(f"   ✅ Caption generated successfully")
                return result.content
            else:
                print(f"   ❌ Caption generation failed: {result.error_message}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error generating caption: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_frontmatter(self, file_path: Path, data: dict) -> bool:
        """Save updated frontmatter with safe YAML formatting"""
        try:
            # Update metadata
            if 'metadata' not in data:
                data['metadata'] = {}
            data['metadata']['lastUpdated'] = datetime.now().isoformat()
            data['metadata']['captionIntegrated'] = True
            
            # Create backup
            backup_path = file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"   📋 Backup created: {backup_path.name}")
            
            # Detect format
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                is_frontmatter_format = first_line == '---'
            
            # Save with safe formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                if is_frontmatter_format:
                    f.write("---\n")
                
                # Use safe YAML formatting to prevent quote issues
                yaml_content = yaml.dump(
                    data,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    width=1000,  # Prevent line wrapping
                    default_style='"'  # Safe quote handling
                )
                f.write(yaml_content)
                
                if is_frontmatter_format:
                    f.write("---\n")
            
            print(f"   ✅ Saved with safe YAML formatting")
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving file: {e}")
            return False
    
    def process_material(self, material_name: str, filename: str) -> bool:
        """Process a single material"""
        print(f"\n{'='*60}")
        print(f"🎯 Processing: {material_name}")
        print(f"{'='*60}")
        
        file_path = Path(f"content/components/frontmatter/{filename}")
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        # Step 1: Load YAML without caption section
        frontmatter_data = self.load_yaml_without_caption(file_path)
        if not frontmatter_data:
            return False
        
        # Step 2: Generate new caption
        caption_data = self.generate_new_caption(material_name, frontmatter_data)
        if not caption_data:
            return False
        
        # Step 3: Add caption to frontmatter
        frontmatter_data['caption'] = caption_data
        
        # Step 4: Remove micro image if exists
        if 'images' in frontmatter_data and 'micro' in frontmatter_data['images']:
            print("   🔄 Removing micro image from images section")
            del frontmatter_data['images']['micro']
        
        # Step 5: Save with safe formatting
        if self.save_frontmatter(file_path, frontmatter_data):
            print(f"✅ Successfully regenerated {material_name}")
            return True
        else:
            return False
    
    def run(self):
        """Main execution"""
        print("🔧 Broken Caption Regenerator")
        print("="*60)
        
        # Initialize API
        if not self.initialize_api_client():
            return
        
        print(f"\n📊 Processing {len(self.broken_materials)} materials")
        
        results = {
            'success': [],
            'failed': []
        }
        
        # Process each material
        for material_name, filename in self.broken_materials.items():
            try:
                if self.process_material(material_name, filename):
                    results['success'].append(material_name)
                else:
                    results['failed'].append(material_name)
            except Exception as e:
                print(f"❌ Unexpected error processing {material_name}: {e}")
                results['failed'].append(material_name)
        
        # Summary
        print("\n" + "="*60)
        print("📊 Summary")
        print("="*60)
        print(f"✅ Successful: {len(results['success'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        
        if results['success']:
            print(f"\n✅ Successfully regenerated:")
            for material in results['success']:
                print(f"   • {material}")
        
        if results['failed']:
            print(f"\n❌ Failed to regenerate:")
            for material in results['failed']:
                print(f"   • {material}")
        
        print("\n✅ Regeneration complete!")

def main():
    regenerator = BrokenCaptionRegenerator()
    regenerator.run()

if __name__ == "__main__":
    main()
