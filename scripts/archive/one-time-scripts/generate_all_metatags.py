#!/usr/bin/env python3
"""
Generate Metatags for All Materials

This script automates the generation of metatags components for all materials 
defined in the data/materials.yaml file.
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from time import sleep

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.materials import load_materials

def extract_all_materials():
    """Extract all materials from the materials data"""
    data = load_materials()
    all_materials = []
    
    # Check if data is directly a dictionary of materials
    if isinstance(data, dict) and all(isinstance(value, dict) for value in data.values()):
        # It's already a dictionary of materials
        return [{"name": name, **details} for name, details in data.items()]
    
    # Otherwise, try the nested structure
    # Iterate through categories
    for category, category_data in data.get("materials", {}).items():
        # Extract items from this category
        if "items" in category_data:
            all_materials.extend(category_data["items"])
    
    return all_materials

def main():
    """Generate metatags for all materials"""
    print("🚀 Starting batch metatags generation for all materials...")
    
    # Get all materials
    materials = extract_all_materials()
    print(f"📋 Found {len(materials)} materials to process")
    
    # Track results
    success_count = 0
    failed_materials = []
    
    # Process each material
    for idx, material in enumerate(materials):
        material_name = material.get('name')
        if not material_name:
            print(f"⚠️ Material at index {idx} has no name, skipping")
            continue
            
        print(f"\n[{idx+1}/{len(materials)}] 🔍 Processing {material_name}...")
        
        # Run the generator for this material
        try:
            # Build the command
            cmd = [
                "python3", 
                "run.py",
                "--material", material_name,
                "--component", "metatags"
            ]
            
            # Execute the command
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            # Check if successful
            if result.returncode == 0 and "Generation completed" in result.stdout:
                print(f"✅ Successfully generated metatags for {material_name}")
                success_count += 1
            else:
                print(f"❌ Failed to generate metatags for {material_name}")
                failed_materials.append(material_name)
                print(f"Error: {result.stderr}")
                
            # Pause briefly to avoid overloading
            sleep(0.5)
                
        except Exception as e:
            print(f"❌ Error processing {material_name}: {str(e)}")
            failed_materials.append(material_name)
    
    # Report summary
    print("\n📊 Batch Generation Summary:")
    print(f"✅ Successfully generated: {success_count}/{len(materials)}")
    print(f"❌ Failed: {len(failed_materials)}/{len(materials)}")
    
    if failed_materials:
        print("\n❌ Failed materials:")
        for name in failed_materials:
            print(f"  - {name}")
    
    print("\n✨ Batch generation complete!")

if __name__ == "__main__":
    main()
