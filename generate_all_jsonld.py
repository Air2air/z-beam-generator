#!/usr/bin/env python3
"""
Generate JSON-LD component for all materials.

This script processes all materials found in the frontmatter directory
and generates JSON-LD components for each one using the working CLI command.
"""

import subprocess
import sys
from pathlib import Path

def get_all_materials():
    """Get list of all materials from frontmatter directory."""
    frontmatter_dir = Path("frontmatter/materials")
    materials = []
    
    if not frontmatter_dir.exists():
        print(f"❌ Error: Frontmatter directory not found: {frontmatter_dir}")
        return []
    
    for file in frontmatter_dir.glob("*-laser-cleaning.md"):
        material_name = file.stem.replace("-laser-cleaning", "")
        materials.append(material_name)
    
    materials.sort()
    return materials

def generate_jsonld_for_material(material_name):
    """Generate JSON-LD for a specific material."""
    try:
        print(f"🔧 Generating JSON-LD for: {material_name}")
        
        # Use the working CLI command format
        cmd = ["python3", "run.py", "--material", material_name, "--components", "jsonld"]
        
        # Get timeout from centralized configuration
        try:
            from run import get_batch_timeout
            timeout = get_batch_timeout("jsonld_generation")
        except ImportError:
            timeout = 120  # Fallback if run.py not available
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Success: {material_name}")
            return True
        else:
            print(f"❌ Error generating {material_name}:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {material_name} (skipping)")
        return False
    except Exception as e:
        print(f"💥 Exception for {material_name}: {e}")
        return False

def main():
    """Main execution function."""
    print("🎯 Starting JSON-LD generation for all materials")
    print("=" * 50)
    
    # Get all materials
    materials = get_all_materials()
    
    if not materials:
        print("❌ No materials found!")
        sys.exit(1)
    
    print(f"📋 Found {len(materials)} materials to process")
    print("")
    
    # Generate JSON-LD for each material
    successful = 0
    failed = 0
    
    for i, material in enumerate(materials, 1):
        print(f"[{i}/{len(materials)}] Processing: {material}")
        
        if generate_jsonld_for_material(material):
            successful += 1
        else:
            failed += 1
        
        # Small delay to prevent overwhelming the system
        import time
        time.sleep(0.5)
    
    print("")
    print("=" * 50)
    print("🏁 JSON-LD Generation Complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(materials)}")
    
    # Verify results
    jsonld_dir = Path("content/components/jsonld")
    if jsonld_dir.exists():
        jsonld_files = list(jsonld_dir.glob("*-laser-cleaning.md"))
        print(f"📁 JSON-LD files created: {len(jsonld_files)}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
