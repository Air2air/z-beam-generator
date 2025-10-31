#!/usr/bin/env python3
"""
Populate Region Image Prompts

Generates AI-ready image prompts for all regions, counties, and cities.
Can operate in two modes:
1. Prompts-only: Generate and save prompts to data.yaml (no API cost)
2. Full generation: Generate prompts + actual images via Gemini API (costs ~$4.64)

Created: October 30, 2025
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from regions.prompts.image_prompts import RegionImagePromptGenerator
from shared.api.gemini_image_client import GeminiImageClient


def generate_prompts_only():
    """Generate prompts and save to regions/data.yaml (no images, no API cost)"""
    
    print("=" * 80)
    print("📝 MODE: PROMPTS ONLY")
    print("=" * 80)
    print("Generating image prompts for regions, counties, and cities.")
    print("Prompts will be saved to regions/data.yaml")
    print("No images will be generated (no API cost)")
    print()
    
    # Load regions data
    data_file = project_root / "regions" / "data.yaml"
    print(f"📂 Loading data from: {data_file}")
    
    with open(data_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Initialize generator (no gemini client needed for prompts-only)
    generator = RegionImagePromptGenerator()
    
    total_entries = 0
    
    # Process each region
    print("\n" + "=" * 80)
    print("🌍 PROCESSING REGIONS")
    print("=" * 80)
    
    for region_key, region_data in data["regions"].items():
        region_name = region_data["name"]
        print(f"\n📍 {region_name}")
        
        # Generate prompts
        prompts = generator.generate_prompts(
            region_name,
            region_data,
            entry_type="region"
        )
        
        # Save to data structure
        region_data["imagePrompts"] = prompts
        total_entries += 1
        
        print(f"  ✅ Historical: {prompts['historical'][:80]}...")
        print(f"  ✅ Business: {prompts['business'][:80]}...")
        
        # Process Bay Area counties if present
        if "bay_area" in region_data and "counties" in region_data["bay_area"]:
            print(f"\n  🏛️  Processing Bay Area counties...")
            
            for county_key, county_data in region_data["bay_area"]["counties"].items():
                county_name = county_data["name"]
                print(f"    📍 {county_name}")
                
                # Generate county prompts
                county_prompts = generator.generate_prompts(
                    county_name,
                    county_data,
                    entry_type="county"
                )
                
                county_data["imagePrompts"] = county_prompts
                total_entries += 1
                
                print(f"      ✅ Historical: {county_prompts['historical'][:60]}...")
                print(f"      ✅ Business: {county_prompts['business'][:60]}...")
    
    # Update metadata
    if "_metadata" not in data:
        data["_metadata"] = {}
    
    data["_metadata"]["image_prompts_generated"] = True
    data["_metadata"]["image_prompt_count"] = total_entries
    data["_metadata"]["image_generation_mode"] = "prompts_only"
    
    # Save updated data
    print("\n" + "=" * 80)
    print("💾 SAVING RESULTS")
    print("=" * 80)
    
    with open(data_file, 'w') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=120)
    
    print(f"✅ Saved {total_entries} prompt sets to: {data_file}")
    print(f"📊 Total entries: {total_entries} (regions + counties)")
    print()
    print("🎉 COMPLETE! Prompts saved to regions/data.yaml")
    print()
    print("Next steps:")
    print("  1. Review prompts in regions/data.yaml")
    print("  2. Edit prompts if needed")
    print("  3. Run with --generate-images to create actual images")
    print()


def generate_with_images():
    """Generate prompts AND images using Gemini API (costs ~$4.64)"""
    
    print("=" * 80)
    print("🎨 MODE: FULL GENERATION (Prompts + Images)")
    print("=" * 80)
    print("⚠️  WARNING: This will use Gemini API and incur costs")
    print("💰 Estimated cost: ~$4.64 for all regions + counties")
    print()
    
    # Confirm
    response = input("Continue with image generation? (yes/no): ").strip().lower()
    if response != "yes":
        print("❌ Cancelled")
        return
    
    # Load regions data
    data_file = project_root / "regions" / "data.yaml"
    print(f"\n📂 Loading data from: {data_file}")
    
    with open(data_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Initialize Gemini client
    print("\n🔧 Initializing Gemini API client...")
    try:
        gemini_client = GeminiImageClient()
        generator = RegionImagePromptGenerator(gemini_client)
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        print("\nMake sure:")
        print("  1. pip install google-genai")
        print("  2. export GEMINI_API_KEY='your-key-here'")
        print("  3. Get key from: https://aistudio.google.com/apikey")
        return
    
    # Create output directory in public for web serving
    output_dir = project_root / "public" / "images" / "regions"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Images will be saved to: {output_dir}")
    
    total_entries = 0
    total_images = 0
    
    # Process each region
    print("\n" + "=" * 80)
    print("🌍 PROCESSING REGIONS")
    print("=" * 80)
    
    for region_key, region_data in data["regions"].items():
        region_name = region_data["name"]
        print(f"\n📍 {region_name}")
        
        # Generate prompts
        prompts = generator.generate_prompts(
            region_name,
            region_data,
            entry_type="region"
        )
        
        # Save to data structure
        region_data["imagePrompts"] = prompts
        total_entries += 1
        
        # Generate images (will save to public/images/regions)
        try:
            result = generator.generate_and_save(
                region_name,
                region_data,
                output_dir=None,  # Uses default public/images/regions
                entry_type="region"
            )
            
            # Save image URLs to data (web-accessible paths)
            region_data["imageFiles"] = {
                "historical": result["historical"]["url"],
                "business": result["business"]["url"]
            }
            
            total_images += 2
            print(f"  ✅ Images saved: {result['historical']['url']}, {result['business']['url']}")
            
        except Exception as e:
            print(f"  ❌ Image generation failed: {e}")
        
        # Process Bay Area counties
        if "bay_area" in region_data and "counties" in region_data["bay_area"]:
            print(f"\n  🏛️  Processing Bay Area counties...")
            
            for county_key, county_data in region_data["bay_area"]["counties"].items():
                county_name = county_data["name"]
                print(f"    📍 {county_name}")
                
                # Generate county prompts
                county_prompts = generator.generate_prompts(
                    county_name,
                    county_data,
                    entry_type="county"
                )
                
                county_data["imagePrompts"] = county_prompts
                total_entries += 1
                
                # Generate images (will save to public/images/regions)
                try:
                    result = generator.generate_and_save(
                        county_name,
                        county_data,
                        output_dir=None,  # Uses default public/images/regions
                        entry_type="county"
                    )
                    
                    county_data["imageFiles"] = {
                        "historical": result["historical"]["url"],
                        "business": result["business"]["url"]
                    }
                    
                    total_images += 2
                    print(f"      ✅ Images saved: {result['historical']['url']}")
                    
                except Exception as e:
                    print(f"      ❌ Image generation failed: {e}")
    
    # Update metadata
    if "_metadata" not in data:
        data["_metadata"] = {}
    
    data["_metadata"]["image_prompts_generated"] = True
    data["_metadata"]["image_prompt_count"] = total_entries
    data["_metadata"]["images_generated"] = total_images
    data["_metadata"]["image_generation_mode"] = "full"
    
    # Save updated data
    print("\n" + "=" * 80)
    print("💾 SAVING RESULTS")
    print("=" * 80)
    
    with open(data_file, 'w') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=120)
    
    print(f"✅ Saved {total_entries} prompt sets to: {data_file}")
    print(f"🖼️  Generated {total_images} images to: {output_dir}")
    print()
    print("🎉 COMPLETE!")
    print()


def main():
    """Main entry point"""
    
    print()
    print("=" * 80)
    print("🎨 REGION IMAGE GENERATION")
    print("=" * 80)
    print()
    print("This script generates image prompts for regions, counties, and cities.")
    print()
    print("Choose mode:")
    print("  1. Prompts only  - Generate prompts and save to YAML (no cost)")
    print("  2. Full          - Generate prompts + images via Gemini API (~$4.64)")
    print()
    
    try:
        mode = input("Select mode (1/2): ").strip()
        print()
        
        if mode == "1":
            generate_prompts_only()
        elif mode == "2":
            generate_with_images()
        else:
            print("❌ Invalid selection. Please choose 1 or 2.")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
