#!/usr/bin/env python3
"""
Normalize Frontmatter Organization

Ensures all frontmatter files have consistent field ordering and removes deprecated fields.
Applies the FieldOrderingService standard order to all files.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from components.frontmatter.ordering.field_ordering_service import FieldOrderingService

BASE_PATH = Path(__file__).resolve().parents[2]
FRONTMATTER_DIR = BASE_PATH / "content/components/frontmatter"

# Fields to remove (deprecated per GROK_INSTRUCTIONS.md)
DEPRECATED_FIELDS = ["applicationTypes", "metadata"]

# Expected field order (from FieldOrderingService)
EXPECTED_ORDER = [
    "name", "category", "subcategory",
    "title", "headline", "description", "keywords",
    "chemicalProperties",
    "materialProperties",
    "composition", "applications",
    "machineSettings",
    "compatibility", "regulatoryStandards",
    "author", "images",
    "environmentalImpact", "outcomes", "outcomeMetrics",
    "caption",
    "tags"
]

def normalize_file(file_path: Path) -> Dict[str, any]:
    """
    Normalize a single frontmatter file.
    
    Returns:
        dict with normalization results
    """
    material_name = file_path.stem.replace('-laser-cleaning', '')
    
    try:
        # Load YAML
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return {"status": "error", "message": "Empty file"}
        
        changes = []
        
        # Remove deprecated fields
        for field in DEPRECATED_FIELDS:
            if field in data:
                del data[field]
                changes.append(f"Removed {field}")
        
        # Apply field ordering
        ordered_data = FieldOrderingService.apply_field_ordering(data)
        
        # Check if order changed
        original_keys = list(data.keys())
        ordered_keys = list(ordered_data.keys())
        
        if original_keys != ordered_keys:
            changes.append("Reordered fields")
        
        # Save normalized file
        if changes:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(ordered_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
            
            return {
                "status": "updated",
                "material": material_name,
                "changes": changes
            }
        else:
            return {
                "status": "ok",
                "material": material_name
            }
            
    except Exception as e:
        return {
            "status": "error",
            "material": material_name,
            "message": str(e)
        }

def main():
    print("🔧 Normalizing Frontmatter Organization")
    print("=" * 70)
    
    # Find all frontmatter files
    frontmatter_files = list(FRONTMATTER_DIR.glob("*-laser-cleaning.yaml"))
    
    if not frontmatter_files:
        print("❌ No frontmatter files found")
        return
    
    print(f"📁 Found {len(frontmatter_files)} frontmatter files")
    print()
    
    results = {
        "updated": [],
        "ok": [],
        "errors": []
    }
    
    # Process each file
    for file_path in sorted(frontmatter_files):
        result = normalize_file(file_path)
        
        if result["status"] == "updated":
            results["updated"].append(result)
            print(f"✅ {result['material']}: {', '.join(result['changes'])}")
        elif result["status"] == "ok":
            results["ok"].append(result)
        elif result["status"] == "error":
            results["errors"].append(result)
            print(f"❌ {result['material']}: {result['message']}")
    
    # Summary
    print()
    print("=" * 70)
    print(f"📊 Summary:")
    print(f"  ✅ Updated: {len(results['updated'])} files")
    print(f"  ✓  Already OK: {len(results['ok'])} files")
    print(f"  ❌ Errors: {len(results['errors'])} files")
    
    if results["updated"]:
        print()
        print("📝 Updated files:")
        for result in results["updated"][:10]:
            print(f"  • {result['material']}: {', '.join(result['changes'])}")
        if len(results["updated"]) > 10:
            print(f"  ... and {len(results['updated']) - 10} more")
    
    if results["errors"]:
        print()
        print("⚠️  Errors:")
        for result in results["errors"]:
            print(f"  • {result['material']}: {result['message']}")

if __name__ == '__main__':
    main()
