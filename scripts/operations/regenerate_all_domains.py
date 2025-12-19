#!/usr/bin/env python3
"""
Regenerate All Domains - Complete frontmatter export

Regenerates frontmatter for all 4 domains:
- Materials (153 files)
- Contaminants (98 files)
- Compounds (19 files)
- Settings (153 files)

Total: 424 files
"""

import sys
from pathlib import Path
import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from export.core.universal_exporter import UniversalFrontmatterExporter


def regenerate_domain(config_file: str, domain_name: str):
    """Regenerate single domain"""
    print(f"\n{'='*80}")
    print(f"📦 REGENERATING {domain_name.upper()} DOMAIN")
    print(f"{'='*80}\n")
    
    # Load config from YAML
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    exporter = UniversalFrontmatterExporter(config)
    results = exporter.export_all()
    
    # Count successes and failures
    success_count = sum(1 for v in results.values() if v)
    error_count = sum(1 for v in results.values() if not v)
    
    print(f"\n📊 {domain_name.upper()} SUMMARY:")
    print(f"   ✅ Successfully exported: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📁 Output directory: {config.get('output_path', 'N/A')}")
    
    return {'success': success_count, 'errors': error_count}


def main():
    """Regenerate all domains"""
    print("\n" + "="*80)
    print("🚀 REGENERATE ALL FRONTMATTER - ALL 4 DOMAINS")
    print("="*80)
    
    domains = [
        ('export/config/materials.yaml', 'Materials'),
        ('export/config/contaminants.yaml', 'Contaminants'),
        ('export/config/compounds.yaml', 'Compounds'),
        ('export/config/settings.yaml', 'Settings'),
    ]
    
    total_success = 0
    total_errors = 0
    
    for config_file, domain_name in domains:
        try:
            stats = regenerate_domain(config_file, domain_name)
            total_success += stats['success']
            total_errors += stats['errors']
        except Exception as e:
            print(f"❌ ERROR regenerating {domain_name}: {e}")
            total_errors += 1
    
    # Final summary
    print(f"\n{'='*80}")
    print("📊 FINAL SUMMARY - ALL DOMAINS")
    print(f"{'='*80}")
    print(f"   ✅ Total files generated: {total_success}")
    print(f"   ❌ Total errors: {total_errors}")
    print(f"   📁 Output: /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/")
    print(f"{'='*80}\n")
    
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
