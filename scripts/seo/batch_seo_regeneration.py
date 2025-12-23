#!/usr/bin/env python3
"""
Batch SEO Metadata Generation

Regenerates page_title and meta_description for all materials using AI pipeline.
Replaces failed code-generated SEO with spec-compliant AI-generated content.

Usage:
    # Generate for all materials
    python3 scripts/seo/batch_seo_regeneration.py

    # Generate for specific materials
    python3 scripts/seo/batch_seo_regeneration.py --materials "aluminum-laser-cleaning,steel-laser-cleaning"
    
    # Dry run (show what would be generated)
    python3 scripts/seo/batch_seo_regeneration.py --dry-run
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from shared.api.client_factory import create_api_client
from generation.seo.minimal_generator import MinimalSEOGenerator


def load_materials():
    """Load all material identifiers from Materials.yaml."""
    materials_path = project_root / 'data' / 'materials' / 'Materials.yaml'
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return list(data['materials'].keys())


def delete_existing_seo(material_id: str, dry_run: bool = False):
    """Delete existing page_title and meta_description from material."""
    materials_path = project_root / 'data' / 'materials' / 'Materials.yaml'
    
    if dry_run:
        print(f"   [DRY RUN] Would delete existing SEO for {material_id}")
        return
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    material = data['materials'].get(material_id, {})
    deleted = []
    
    if 'page_title' in material:
        del material['page_title']
        deleted.append('page_title')
    
    if 'meta_description' in material:
        del material['meta_description']
        deleted.append('meta_description')
    
    if deleted:
        with open(materials_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"   🗑️  Deleted: {', '.join(deleted)}")


def generate_seo_for_material(generator: MinimalSEOGenerator, material_id: str, dry_run: bool = False):
    """Generate both page_title and meta_description for a material."""
    print(f"\n{'='*80}")
    print(f"📝 MATERIAL: {material_id}")
    print(f"{'='*80}")
    
    if dry_run:
        print("   [DRY RUN] Would generate page_title and meta_description")
        return True, True
    
    # Delete existing failed content first
    delete_existing_seo(material_id, dry_run)
    
    # Generate both SEO fields
    print("\n🔍 Generating SEO metadata...")
    title_success, desc_success = generator.generate(material_id)
    
    if title_success and desc_success:
        print("   ✅ Both fields generated successfully")
    elif title_success or desc_success:
        print("   ⚠️  Partial success")
    else:
        print("   ❌ Generation failed")
    
    return title_success, desc_success


def main():
    """Main batch generation process."""
    parser = argparse.ArgumentParser(description='Batch regenerate SEO metadata for materials')
    parser.add_argument('--materials', help='Comma-separated list of material IDs')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--limit', type=int, help='Limit number of materials to process')
    args = parser.parse_args()
    
    print("="*80)
    print("🚀 BATCH SEO METADATA REGENERATION")
    print("="*80)
    
    # Initialize API client and generator
    print("\n🔧 Initializing API client...")
    api_client = create_api_client('grok')
    generator = MinimalSEOGenerator(api_client)
    print("✅ Ready to generate\n")
    
    # Get materials to process
    if args.materials:
        materials = [m.strip() for m in args.materials.split(',')]
        print(f"📋 Processing {len(materials)} specified materials")
    else:
        materials = load_materials()
        print(f"📋 Found {len(materials)} materials in Materials.yaml")
        
        if args.limit:
            materials = materials[:args.limit]
            print(f"   ⚠️  Limited to first {args.limit} materials")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    
    # Process each material
    results = {
        'success': [],
        'partial': [],
        'failed': []
    }
    
    for i, material_id in enumerate(materials, 1):
        print(f"\n[{i}/{len(materials)}]")
        
        try:
            title_ok, desc_ok = generate_seo_for_material(generator, material_id, args.dry_run)
            
            if title_ok and desc_ok:
                results['success'].append(material_id)
            elif title_ok or desc_ok:
                results['partial'].append(material_id)
            else:
                results['failed'].append(material_id)
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results['failed'].append(material_id)
    
    # Summary
    print("\n" + "="*80)
    print("📊 BATCH GENERATION SUMMARY")
    print("="*80)
    print(f"✅ Success (both generated): {len(results['success'])}")
    print(f"⚠️  Partial (one generated): {len(results['partial'])}")
    print(f"❌ Failed (none generated): {len(results['failed'])}")
    print(f"\n📈 Total materials processed: {len(materials)}")
    print(f"📈 Success rate: {(len(results['success']) / len(materials) * 100):.1f}%")
    
    if results['partial']:
        print(f"\n⚠️  Partial failures ({len(results['partial'])}):")
        for mat in results['partial'][:10]:
            print(f"   - {mat}")
        if len(results['partial']) > 10:
            print(f"   ... and {len(results['partial']) - 10} more")
    
    if results['failed']:
        print(f"\n❌ Complete failures ({len(results['failed'])}):")
        for mat in results['failed'][:10]:
            print(f"   - {mat}")
        if len(results['failed']) > 10:
            print(f"   ... and {len(results['failed']) - 10} more")
    
    print("="*80)
    
    return 0 if len(results['success']) == len(materials) else 1


if __name__ == '__main__':
    sys.exit(main())
