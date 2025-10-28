#!/usr/bin/env python3
"""Batch generate FAQs for 4 materials and export to frontmatter"""

import subprocess
import sys
import time
import yaml
from pathlib import Path

# Materials to generate (diverse set)
MATERIALS = [
    "Beryllium",      # Metal (Yi-Chun Lin - Taiwan)
    "Alabaster",      # Stone (Alessandro Moretti - Italy)
    "Ash",            # Wood (Todd Dunning - USA)
    "Carbon Fiber Reinforced Polymer"  # Composite (Yi-Chun Lin - Taiwan)
]

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*80}")
    print(f"🚀 {description}")
    print(f"{'='*80}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    
    # Show relevant output
    output_lines = result.stdout.split('\n')
    for line in output_lines:
        if any(marker in line for marker in ['✅', '❌', '📊', '💾', 'Statistics:', 'Preview:']):
            print(line)
    
    return True

def main():
    print("="*80)
    print("BATCH FAQ GENERATION & EXPORT")
    print("="*80)
    print(f"Materials: {', '.join(MATERIALS)}")
    print()
    
    # Step 1: Generate FAQs for all materials
    for i, material in enumerate(MATERIALS, 1):
        description = f"Generating FAQ {i}/{len(MATERIALS)}: {material}"
        cmd = f'python3 run.py --faq "{material}"'
        
        if not run_command(cmd, description):
            print(f"❌ Failed to generate FAQ for {material}")
            sys.exit(1)
        
        # Brief delay between API calls
        if i < len(MATERIALS):
            time.sleep(2)
    
    print("\n" + "="*80)
    print("✅ All FAQs generated successfully!")
    print("="*80)
    
    # Step 2: Export to frontmatter
    print("\n" + "="*80)
    print("📤 Exporting FAQs to frontmatter files...")
    print("="*80)
    
    # Load Materials.yaml
    materials_path = Path("data/Materials.yaml")
    with open(materials_path, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    # Export each material's FAQ to frontmatter
    exported = 0
    for material_name in MATERIALS:
        material = materials_data['materials'].get(material_name)
        if not material or 'faq' not in material:
            print(f"⚠️  No FAQ data for {material_name}")
            continue
        
        # Generate frontmatter filename
        frontmatter_name = material_name.lower().replace(' ', '-')
        frontmatter_path = Path(f"content/frontmatter/{frontmatter_name}-laser-cleaning.yaml")
        
        if not frontmatter_path.exists():
            print(f"⚠️  Frontmatter file not found: {frontmatter_path}")
            continue
        
        # Load existing frontmatter
        with open(frontmatter_path, 'r', encoding='utf-8') as f:
            frontmatter_data = yaml.safe_load(f)
        
        # Update FAQ section
        frontmatter_data['faq'] = material['faq']
        
        # Save back to frontmatter
        with open(frontmatter_path, 'w', encoding='utf-8') as f:
            yaml.dump(frontmatter_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        
        print(f"✅ Exported: {material_name} → {frontmatter_path.name}")
        print(f"   Questions: {material['faq']['total_questions']}, Words: {material['faq']['total_words']}")
        exported += 1
    
    print("\n" + "="*80)
    print(f"✅ COMPLETE: {exported}/{len(MATERIALS)} FAQs exported to frontmatter")
    print("="*80)
    
    # Summary
    print("\n📊 SUMMARY:")
    with open(materials_path, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    for material_name in MATERIALS:
        material = materials_data['materials'].get(material_name)
        if material and 'faq' in material:
            faq = material['faq']
            print(f"   {material_name}:")
            print(f"      Author: {faq['author']} ({faq['author_country']})")
            print(f"      Questions: {faq['total_questions']}, Avg: {faq['avg_words_per_answer']}w")

if __name__ == "__main__":
    main()
