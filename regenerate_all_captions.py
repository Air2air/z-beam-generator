#!/usr/bin/env python3
"""
Complete AI Caption Regeneration for All 121 Materials
Runs uninterrupted with enhanced error handling and progress tracking.
"""

import sys
import time
import yaml
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

from api.client_factory import create_api_client
from components.caption.generators.generator import CaptionComponentGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def load_all_materials():
    """Load all materials from Materials.yaml"""
    try:
        with open('data/Materials.yaml', 'r') as f:
            materials_data = yaml.safe_load(f)
        
        material_index = materials_data.get('material_index', {})
        return sorted(material_index.keys()), material_index
    except Exception as e:
        logger.error(f"❌ Error loading materials: {e}")
        return [], {}

def load_frontmatter(material_name):
    """Load frontmatter data for a material"""
    content_dir = Path("content/components/frontmatter")
    normalized_name = material_name.lower().replace('_', ' ').replace(' ', '-')
    
    potential_paths = [
        content_dir / f"{material_name.lower()}.yaml",
        content_dir / f"{material_name.lower().replace(' ', '-')}.yaml",
        content_dir / f"{material_name.lower().replace('_', '-')}.yaml",
        content_dir / f"{normalized_name}.yaml",
        content_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml",
        content_dir / f"{normalized_name}-laser-cleaning.yaml"
    ]
    
    for path in potential_paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception:
                continue
    return None

def generate_single_caption(generator, api_client, material_name, material_data):
    """Generate caption for a single material with error handling"""
    try:
        # Load frontmatter
        frontmatter_data = load_frontmatter(material_name)
        if not frontmatter_data:
            return False, "No frontmatter data found"
        
        # Generate caption
        start_time = time.time()
        result = generator.generate(
            material_name=material_name,
            material_data=material_data,
            api_client=api_client,
            frontmatter_data=frontmatter_data
        )
        
        # Check if result is a ComponentResult object or a string
        if hasattr(result, 'content'):
            # It's a ComponentResult object
            content = result.content
            success = result.success
            if not success:
                return False, f"Generation failed: {getattr(result, 'error_message', 'Unknown error')}"
        else:
            # It's a string directly
            content = result
            success = True
        
        # Save to file
        output_dir = Path("content/components/caption")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = material_name.lower().replace(' ', '-').replace('_', '-')
        output_file = output_dir / f"{safe_name}-laser-cleaning.yaml"
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        duration = time.time() - start_time
        return True, f"Generated in {duration:.1f}s → {output_file.name}"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Main regeneration function"""
    print("🚀 AI CAPTION REGENERATION - ALL MATERIALS")
    print("=" * 60)
    print("🤖 AI Provider: DeepSeek")
    print("📏 Content: 2,600+ characters (enhanced scientific depth)")
    print("🔬 Features: XPS, SEM, AFM, EDX analysis")
    print("🏷️  Title: AI-Generated Laser Cleaning Surface Analysis")
    print("=" * 60)
    
    # Load materials
    materials_list, material_index = load_all_materials()
    if not materials_list:
        print("❌ No materials found. Exiting.")
        return False
    
    total_materials = len(materials_list)
    print(f"📋 Materials to process: {total_materials}")
    print(f"⏱️  Estimated time: {total_materials * 20 / 60:.1f} minutes")
    print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Initialize API client
    try:
        api_client = create_api_client('deepseek')
        print("✅ API client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize API client: {e}")
        return False
    
    # Initialize generator
    generator = CaptionComponentGenerator()
    print("✅ Caption generator initialized")
    print()
    
    # Process all materials
    successful = 0
    failed = 0
    failed_materials = []
    start_batch_time = time.time()
    
    for i, material in enumerate(materials_list, 1):
        category = material_index[material]
        
        print(f"📝 {i:3d}/{total_materials}: {material} ({category})")
        
        success, message = generate_single_caption(
            generator, api_client, material, {"name": material, "category": category}
        )
        
        if success:
            print(f"   ✅ {message}")
            successful += 1
        else:
            print(f"   ❌ {message}")
            failed += 1
            failed_materials.append(material)
        
        # Progress update every 10 materials
        if i % 10 == 0:
            elapsed = time.time() - start_batch_time
            avg_time = elapsed / i
            remaining = total_materials - i
            eta_seconds = remaining * avg_time
            eta_minutes = eta_seconds / 60
            
            print()
            print(f"📊 Progress: {i}/{total_materials} ({(i/total_materials)*100:.1f}%)")
            print(f"   ✅ Successful: {successful}")
            print(f"   ❌ Failed: {failed}")
            print(f"   ⏱️  ETA: {eta_minutes:.1f} minutes")
            print()
        
        # Small delay to prevent API rate limiting
        time.sleep(0.5)
    
    # Final summary
    total_time = time.time() - start_batch_time
    print("=" * 60)
    print("🎯 REGENERATION COMPLETE")
    print("=" * 60)
    print(f"📊 Total processed: {total_materials}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success rate: {(successful/total_materials)*100:.1f}%")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"🕐 Completed: {datetime.now().strftime('%H:%M:%S')}")
    
    if failed_materials:
        print(f"\n❌ Failed materials ({len(failed_materials)}):")
        for material in failed_materials[:10]:  # Show first 10
            print(f"   • {material}")
        if len(failed_materials) > 10:
            print(f"   ... and {len(failed_materials) - 10} more")
    
    print("\n🚀 All AI caption regeneration completed!")
    return successful == total_materials

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)