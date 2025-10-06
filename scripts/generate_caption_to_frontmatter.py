#!/usr/bin/env python3
"""
Caption to Frontmatter Integration Script
Generates caption content and integrates it directly into frontmatter files 
under the caption key, preserving existing frontmatter data and working 
with the micro-image-only caption structure.
"""

import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.caption.generators.frontmatter_generator import FrontmatterCaptionGenerator
from api.client_factory import create_api_client

class CaptionFrontmatterIntegrator:
    """Integrates caption generation directly into frontmatter files."""
    
    def __init__(self):
        self.caption_generator = FrontmatterCaptionGenerator()
        self.api_client = None
        
    def initialize_api_client(self) -> bool:
        """Initialize API client for caption generation."""
        try:
            self.api_client = create_api_client('grok')
            print("✅ API client initialized (Grok)")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize API client: {e}")
            return False
    
    def find_frontmatter_file(self, material_name: str) -> Optional[Path]:
        """Find the frontmatter file for a material."""
        # Normalize material name for filename
        material_slug = material_name.lower().replace(' ', '-').replace('_', '-')
        
        # Check possible frontmatter file locations
        possible_paths = [
            f"content/components/frontmatter/{material_slug}-laser-cleaning.yaml",
            f"content/components/frontmatter/{material_slug}.yaml", 
            f"content/components/frontmatter/{material_name.lower()}-laser-cleaning.yaml",
            f"content/components/frontmatter/{material_name.lower()}.yaml"
        ]
        
        for path_str in possible_paths:
            path = Path(path_str)
            if path.exists():
                return path
                
        return None
    
    def load_frontmatter(self, frontmatter_path: Path) -> Optional[Dict[str, Any]]:
        """Load existing frontmatter data."""
        try:
            with open(frontmatter_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle YAML format (may have --- separators or be pure YAML)
            if content.startswith('---'):
                # Extract YAML content between --- markers
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                else:
                    yaml_content = content
            else:
                # Pure YAML file
                yaml_content = content
            
            frontmatter_data = yaml.safe_load(yaml_content)
            return frontmatter_data if frontmatter_data else {}
            
        except Exception as e:
            print(f"❌ Error loading frontmatter from {frontmatter_path}: {e}")
            return None
    
    def generate_caption_content(self, material_name: str, frontmatter_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate caption content using the frontmatter-integrated caption generator."""
        try:
            # Prepare material data from frontmatter
            material_data = {
                "name": material_name,
                "category": frontmatter_data.get("category", ""),
                "subcategory": frontmatter_data.get("subcategory", "")
            }
            
            print(f"🔄 Generating caption content for {material_name}...")
            
            # Generate caption using new frontmatter-integrated generator
            result = self.caption_generator.generate_for_frontmatter(
                material_name=material_name,
                material_data=material_data,
                api_client=self.api_client,
                frontmatter_data=frontmatter_data,
                author_info=frontmatter_data.get('author', {})
            )
            
            if result.success:
                print(f"✅ Caption data generated: {len(str(result.content))} chars")
                return result.content
            else:
                error_msg = result.error_message or 'Unknown error'
                print(f"❌ Caption generation failed: {error_msg}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating caption content: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_frontmatter_structure(self, frontmatter_data: Dict[str, Any], caption_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update frontmatter data with caption structure and remove micro from images."""
        
        # Add/update caption key with the structured data from generator
        frontmatter_data['caption'] = caption_data
        
        # Remove micro image from images section if it exists (per requirement)
        if 'images' in frontmatter_data and 'micro' in frontmatter_data['images']:
            print("🔄 Removing micro image from images section...")
            del frontmatter_data['images']['micro']
            
            # If images section is now empty except for hero, clean it up
            if len(frontmatter_data['images']) == 1 and 'hero' in frontmatter_data['images']:
                pass  # Keep hero image as specified
            elif not frontmatter_data['images']:
                # Remove empty images section
                del frontmatter_data['images']
        
        # Update metadata
        if 'metadata' not in frontmatter_data:
            frontmatter_data['metadata'] = {}
            
        frontmatter_data['metadata']['lastUpdated'] = datetime.now().isoformat()
        frontmatter_data['metadata']['captionIntegrated'] = True
        
        return frontmatter_data
    
    def save_frontmatter(self, frontmatter_path: Path, frontmatter_data: Dict[str, Any]) -> bool:
        """Save updated frontmatter data back to file."""
        try:
            # Skip backup creation - disabled to prevent clutter
            # backup_path = frontmatter_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
            # if frontmatter_path.exists():
            #     import shutil
            #     shutil.copy2(frontmatter_path, backup_path)
            #     print(f"📋 Backup created: {backup_path}")
            
            # Detect original file format by checking if it starts with ---
            if frontmatter_path.exists():
                with open(frontmatter_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    is_frontmatter_format = first_line == '---'
            else:
                is_frontmatter_format = False
            
            # Save updated frontmatter in original format with clean YAML formatting
            with open(frontmatter_path, 'w', encoding='utf-8') as f:
                if is_frontmatter_format:
                    # Write with YAML frontmatter format (Jekyll/Hugo style)
                    f.write("---\n")
                    yaml_content = yaml.dump(frontmatter_data, 
                                           default_flow_style=False, 
                                           sort_keys=False, 
                                           allow_unicode=True, 
                                           width=120,  # Reasonable line width
                                           indent=2)  # Clean indentation - no default_style for clean output
                    f.write(yaml_content)
                    f.write("---\n")
                else:
                    # Write as regular YAML file (original format)
                    yaml_content = yaml.dump(frontmatter_data, 
                                           default_flow_style=False, 
                                           sort_keys=False, 
                                           allow_unicode=True, 
                                           width=120,  # Reasonable line width
                                           indent=2)  # Clean indentation - no default_style for clean output
                    f.write(yaml_content)
            
            print(f"✅ Updated frontmatter saved to: {frontmatter_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving frontmatter: {e}")
            return False
    
    def process_material(self, material_name: str) -> bool:
        """Process a single material for caption integration."""
        print(f"\n🎯 Processing caption integration for: {material_name}")
        
        # Step 1: Find frontmatter file
        frontmatter_path = self.find_frontmatter_file(material_name)
        if not frontmatter_path:
            print(f"❌ No frontmatter file found for {material_name}")
            return False
        
        print(f"📄 Found frontmatter: {frontmatter_path}")
        
        # Step 2: Load existing frontmatter
        frontmatter_data = self.load_frontmatter(frontmatter_path)
        if frontmatter_data is None:
            print(f"❌ Failed to load frontmatter for {material_name}")
            return False
        
        # Step 3: Generate caption content (already in correct structure)
        caption_data = self.generate_caption_content(material_name, frontmatter_data)
        if not caption_data:
            print(f"❌ Failed to generate caption content for {material_name}")
            return False
        
        print("✅ Caption content generated successfully")
        
        # Step 4: Update frontmatter structure (caption data is already structured correctly)
        updated_frontmatter = self.update_frontmatter_structure(frontmatter_data, caption_data)
        
        # Step 5: Save updated frontmatter
        success = self.save_frontmatter(frontmatter_path, updated_frontmatter)
        
        if success:
            print(f"🎉 Caption integration completed for {material_name}")
            print("   📝 Caption added under 'caption' key")
            print("   🖼️ Micro image moved from images.micro to caption.imageUrl")
            print("   🔄 Frontmatter metadata updated")
            return True
        else:
            return False


def main():
    parser = argparse.ArgumentParser(description="Generate captions and integrate into frontmatter files")
    parser.add_argument("--material", type=str, help="Material name to process")
    parser.add_argument("--all", action="store_true", help="Process all materials with frontmatter files")
    parser.add_argument("--list", action="store_true", help="List available materials")
    
    args = parser.parse_args()
    
    integrator = CaptionFrontmatterIntegrator()
    
    # Initialize API client
    if not integrator.initialize_api_client():
        print("❌ Cannot proceed without API client")
        return False
    
    if args.list:
        # List available materials
        frontmatter_dir = Path("content/components/frontmatter")
        if frontmatter_dir.exists():
            print("📋 Available materials with frontmatter:")
            for file_path in frontmatter_dir.glob("*.yaml"):
                material_name = file_path.stem.replace("-laser-cleaning", "").replace("-", " ").title()
                print(f"  • {material_name}")
        return True
    
    elif args.material:
        # Process single material
        return integrator.process_material(args.material)
    
    elif args.all:
        # Process all materials with frontmatter
        frontmatter_dir = Path("content/components/frontmatter")
        if not frontmatter_dir.exists():
            print("❌ No frontmatter directory found")
            return False
        
        success_count = 0
        failure_count = 0
        
        for file_path in frontmatter_dir.glob("*.yaml"):
            material_name = file_path.stem.replace("-laser-cleaning", "").replace("-", " ").title()
            
            if integrator.process_material(material_name):
                success_count += 1
            else:
                failure_count += 1
        
        print("\n🏁 Batch processing completed:")
        print(f"   ✅ Successes: {success_count}")
        print(f"   ❌ Failures: {failure_count}")
        
        return failure_count == 0
    
    else:
        parser.print_help()
        return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)