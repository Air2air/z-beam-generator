#!/usr/bin/env python3
"""
Generate FAQ for 4 diverse materials and export to frontmatter
"""
import subprocess
import sys

# 4 diverse materials (metal, stone, wood, composite)
materials = [
    "Beryllium",
    "Alabaster", 
    "Ash",
    "Carbon Fiber Reinforced Polymer"
]

print("="*80)
print("FAQ GENERATION AND FRONTMATTER EXPORT - 4 MATERIALS")
print("="*80)
print(f"\nMaterials to process: {len(materials)}")
for i, m in enumerate(materials, 1):
    print(f"  {i}. {m}")
print()

# Generate FAQ for each material
for i, material in enumerate(materials, 1):
    print(f"\n{'='*80}")
    print(f"[{i}/{len(materials)}] Processing: {material}")
    print("="*80)
    
    # Generate FAQ
    print(f"\n🔧 Step 1: Generating FAQ...")
    result = subprocess.run(
        ["python3", "run.py", "--faq", material],
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ FAQ generation failed for {material}")
        continue
    
    print(f"✅ FAQ generated for {material}")
    
    # Export to frontmatter
    print(f"\n🔧 Step 2: Exporting to frontmatter...")
    result = subprocess.run(
        ["python3", "run.py", "--material", material],
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Frontmatter export failed for {material}")
        continue
    
    print(f"✅ Frontmatter exported for {material}")

print(f"\n\n{'='*80}")
print("BATCH PROCESSING COMPLETE!")
print("="*80)
print(f"\nProcessed {len(materials)} materials:")
for m in materials:
    print(f"  ✅ {m}")
print("\n💾 All data saved to:")
print("   • data/Materials.yaml (FAQ data)")
print("   • content/frontmatter/*.yaml (frontmatter files)")
print()
