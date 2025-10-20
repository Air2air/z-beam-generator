#!/usr/bin/env python3
"""
Batch Frontmatter Generation Script

Generates frontmatter for all materials in Materials.yaml:
- ✅ AI research enabled for missing property values (materialProperties)
- ❌ AI generation disabled for text content (caption, subtitle, description)

This populates all property data while skipping expensive text generation.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_materials():
    """Load all materials from Materials.yaml"""
    import yaml
    materials_path = project_root / "data" / "Materials.yaml"
    with open(materials_path) as f:
        data = yaml.safe_load(f)
    
    material_index = data.get('material_index', {})
    return sorted(material_index.keys())


def generate_frontmatter_for_material(material_name):
    """
    Generate frontmatter for a single material using run.py
    
    This uses the existing run.py infrastructure which:
    - Enables AI research for missing properties ONLY
    - Skips AI text generation (no --generate-caption or --generate-subtitle flags)
    - Skips AI applications generation (uses existing industryTags or empty list)
    """
    try:
        print(f"\n{'='*70}")
        print(f"Generating: {material_name}")
        print(f"{'='*70}")
        
        # Call run.py with material name
        # By not including --generate-caption or --generate-subtitle:
        # - AI research for properties: ENABLED (only missing properties)
        # - AI text generation: DISABLED
        # - AI applications generation: DISABLED (will use existing or fail-fast)
        cmd = [
            "python3", "run.py",
            "--material", material_name,
            "--components", "frontmatter"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per material
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {material_name}")
            return True
        else:
            print(f"❌ FAILED: {material_name}")
            print(f"   Exit code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr[:500]}")  # First 500 chars
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT: {material_name} (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {material_name}")
        print(f"   Exception: {e}")
        return False


def main():
    """Main batch generation function"""
    import argparse
    parser = argparse.ArgumentParser(description='Batch generate frontmatter for materials')
    parser.add_argument('--limit', type=int, help='Limit number of materials to process (for testing)')
    parser.add_argument('--start', type=int, default=0, help='Start index (0-based)')
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              BATCH FRONTMATTER GENERATION                            ║
║              Property Research: ENABLED (AI fills missing data)      ║
║              Text Generation: DISABLED (caption, subtitle, etc.)     ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    
    # Load materials
    all_materials = load_materials()
    
    # Apply start/limit if specified
    if args.limit:
        materials = all_materials[args.start:args.start + args.limit]
        print(f"Processing {len(materials)} materials (indices {args.start}-{args.start + args.limit - 1} of {len(all_materials)} total)")
    else:
        materials = all_materials[args.start:]
        print(f"Found {len(all_materials)} materials in Materials.yaml")
        if args.start > 0:
            print(f"Starting from index {args.start}")
    
    total = len(materials)
    print()
    
    # Track statistics
    stats = {
        'total': total,
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    start_time = datetime.now()
    
    # Generate for each material
    for i, material in enumerate(materials, 1):
        print(f"\n[{i}/{total}] Processing: {material}")
        
        success = generate_frontmatter_for_material(material)
        
        if success:
            stats['success'] += 1
        else:
            stats['failed'] += 1
            stats['errors'].append(material)
        
        # Progress indicator
        progress = (i / total) * 100
        print(f"Progress: {progress:.1f}% ({i}/{total})")
    
    # Calculate duration
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Print summary
    print(f"\n{'='*70}")
    print("BATCH GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"Total Materials:  {stats['total']}")
    print(f"✅ Successful:    {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"❌ Failed:        {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    print(f"⏱️  Duration:      {duration}")
    print(f"{'='*70}")
    
    if stats['errors']:
        print(f"\n❌ Failed Materials ({len(stats['errors'])}):")
        for material in stats['errors']:
            print(f"   - {material}")
    
    # Save summary report
    report_path = project_root / "BATCH_GENERATION_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(f"""# Batch Frontmatter Generation Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Property Research**: AI-enabled (fills missing data)  
**Text Generation**: Disabled (caption, subtitle, description)

## Summary

- **Total Materials**: {stats['total']}
- **Successful**: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)
- **Failed**: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)
- **Duration**: {duration}

## Configuration

This batch run:
- ✅ **Enables AI research** for missing property values in materialProperties
- ❌ **Disables AI generation** for text fields (caption, subtitle, description)
- Uses existing run.py infrastructure without --generate-caption or --generate-subtitle flags

## Results

### ✅ Successful Materials ({stats['success']})
""")
        
        # List successful materials
        for material in materials:
            if material not in stats['errors']:
                f.write(f"- {material}\n")
        
        if stats['errors']:
            f.write(f"\n### ❌ Failed Materials ({len(stats['errors'])})\n\n")
            for material in stats['errors']:
                f.write(f"- {material}\n")
    
    print(f"\n📝 Detailed report saved to: {report_path}")
    
    return 0 if stats['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
