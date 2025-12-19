#!/usr/bin/env python3
"""
Material Normalization Validator

Ensures material and contaminant names are consistent across ALL data files.
Materials.yaml is the SINGLE SOURCE OF TRUTH.

Usage:
    python3 scripts/tools/material_normalization_validator.py --check
    python3 scripts/tools/material_normalization_validator.py --fix
    python3 scripts/tools/material_normalization_validator.py --report

Author: AI Assistant
Date: November 28, 2025
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Use centralized YAML utilities
from shared.utils.yaml_utils import load_yaml

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data files that reference materials
DATA_FILES = {
    # Primary source of truth
    "Materials.yaml": PROJECT_ROOT / "data" / "materials" / "Materials.yaml",
    
    # Files that must match Materials.yaml
    "Settings.yaml": PROJECT_ROOT / "data" / "settings" / "Settings.yaml",
    "MachineSettings.yaml": PROJECT_ROOT / "data" / "materials" / "MachineSettings.yaml",
    "MaterialProperties.yaml": PROJECT_ROOT / "data" / "materials" / "MaterialProperties.yaml",
    "contaminants.yaml": PROJECT_ROOT / "data" / "contaminants" / "contaminants.yaml",
    "IndustryApplications.yaml": PROJECT_ROOT / "data" / "materials" / "IndustryApplications.yaml",
}

# Code files with hardcoded material mappings
CODE_FILES = {
    "category_contamination_researcher.py": PROJECT_ROOT / "domains" / "materials" / "image" / "research" / "category_contamination_researcher.py",
    "shape_researcher.py": PROJECT_ROOT / "domains" / "materials" / "image" / "research" / "shape_researcher.py",
}


def get_materials_from_source() -> Tuple[Set[str], Dict[str, str]]:
    """
    Get canonical material list from Materials.yaml (source of truth).
    
    Returns:
        Tuple of (material_names set, material_to_category dict)
    """    if not DATA_FILES["Materials.yaml"].exists():
        print(f"⚠️  File not found: {DATA_FILES['Materials.yaml']}")
        return set(), {}
        data = load_yaml(DATA_FILES["Materials.yaml"])
    materials_section = data.get("materials", {})
    
    material_names = set()
    material_to_category = {}
    
    for name, value in materials_section.items():
        material_names.add(name)
        # Value is a dict with 'category' key
        if isinstance(value, dict):
            material_to_category[name] = value.get("category", "unknown")
        elif isinstance(value, str):
            # Simple format: Material: category
            material_to_category[name] = value
    
    return material_names, material_to_category


def get_materials_from_file(path: Path, file_type: str) -> Set[str]:
    """Extract material names from a data file."""
    data = load_yaml(path)
    materials = set()
    
    if file_type in ["Settings.yaml"]:
        # Settings.yaml has materials as top-level keys
        for key in data:
            if isinstance(key, str) and key[0].isupper() and not key.startswith("_") and key not in ["schema_version", "last_updated", "description"]:
                # Check if it looks like a material entry (has settings-like content)
                if isinstance(data[key], dict):
                    materials.add(key)
    
    elif file_type in ["MachineSettings.yaml", "MaterialProperties.yaml"]:
        # These have materials section
        materials_section = data.get("materials", data)
        for key in materials_section:
            if isinstance(key, str) and key[0].isupper() and key not in ["schema_version", "last_updated", "description"]:
                materials.add(key)
    
    elif file_type == "contaminants.yaml":
        # Contaminants have valid_materials and prohibited_materials lists
        patterns = data.get("contamination_patterns", {})
        for pattern_data in patterns.values():
            if isinstance(pattern_data, dict):
                for mat in pattern_data.get("valid_materials", []):
                    materials.add(mat)
                for mat in pattern_data.get("prohibited_materials", []):
                    materials.add(mat)
    
    elif file_type == "IndustryApplications.yaml":
        # Industry applications may have different structure
        for key in data:
            if isinstance(key, str) and key[0].isupper() and key not in ["schema_version", "last_updated", "description", "metadata"]:
                materials.add(key)
    
    return materials


def check_category_map_sync(canonical_materials: Set[str], material_categories: Dict[str, str]) -> List[str]:
    """Check if CATEGORY_MAP in category_contamination_researcher.py is in sync."""
    issues = []
    
    code_path = CODE_FILES["category_contamination_researcher.py"]
    if not code_path.exists():
        return [f"File not found: {code_path}"]
    
    content = code_path.read_text()
    
    # Find materials in CATEGORY_MAP
    import re
    map_materials = set(re.findall(r'"([A-Z][a-zA-Z0-9 ]+)":\s*"[a-z_]+"', content))
    
    # Check for materials in YAML but not in code
    missing_in_code = canonical_materials - map_materials
    if missing_in_code:
        # Filter to just important plastics/metals that should be mapped
        important_missing = {m for m in missing_in_code if any(
            cat in material_categories.get(m, "").lower() 
            for cat in ["plastic", "metal", "polymer", "ceramic", "glass", "wood"]
        )}
        if important_missing:
            issues.append(f"Materials in YAML but not in CATEGORY_MAP: {sorted(important_missing)[:10]}...")
    
    return issues


def generate_report(canonical: Set[str], material_categories: Dict[str, str]) -> str:
    """Generate comprehensive normalization report."""
    report = []
    report.append("=" * 70)
    report.append("MATERIAL NORMALIZATION REPORT")
    report.append("=" * 70)
    report.append(f"\n📋 Source of Truth: Materials.yaml ({len(canonical)} materials)\n")
    
    all_issues = []
    
    # Check each data file
    for file_name, file_path in DATA_FILES.items():
        if file_name == "Materials.yaml":
            continue
        
        if not file_path.exists():
            report.append(f"⚠️  {file_name}: FILE NOT FOUND")
            continue
        
        file_materials = get_materials_from_file(file_path, file_name)
        
        missing = canonical - file_materials
        extra = file_materials - canonical
        
        status = "✅" if not missing and not extra else "❌"
        report.append(f"\n{status} {file_name}:")
        report.append(f"   Materials found: {len(file_materials)}")
        
        if missing:
            report.append(f"   ⚠️  Missing from source: {len(missing)}")
            if len(missing) <= 10:
                report.append(f"      {sorted(missing)}")
            else:
                report.append(f"      {sorted(missing)[:10]}... (+{len(missing)-10} more)")
            all_issues.extend([f"{file_name} missing: {m}" for m in missing])
        
        if extra:
            report.append(f"   ⚠️  Not in Materials.yaml: {len(extra)}")
            if len(extra) <= 10:
                report.append(f"      {sorted(extra)}")
            else:
                report.append(f"      {sorted(extra)[:10]}... (+{len(extra)-10} more)")
            all_issues.extend([f"{file_name} has unknown: {m}" for m in extra])
    
    # Check code files
    report.append("\n" + "-" * 70)
    report.append("CODE FILE SYNC STATUS:")
    
    code_issues = check_category_map_sync(canonical, material_categories)
    if code_issues:
        report.append("❌ category_contamination_researcher.py:")
        for issue in code_issues:
            report.append(f"   {issue}")
        all_issues.extend(code_issues)
    else:
        report.append("✅ category_contamination_researcher.py: In sync")
    
    # Summary
    report.append("\n" + "=" * 70)
    if all_issues:
        report.append(f"❌ NORMALIZATION ISSUES FOUND: {len(all_issues)}")
        report.append("\nRun with --fix to attempt automatic fixes")
    else:
        report.append("✅ ALL FILES NORMALIZED - No issues found")
    report.append("=" * 70)
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Material normalization validator")
    parser.add_argument("--check", action="store_true", help="Check for normalization issues")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues (not implemented)")
    args = parser.parse_args()
    
    if not any([args.check, args.report, args.fix]):
        args.report = True  # Default to report
    
    # Load source of truth
    canonical_materials, material_categories = get_materials_from_source()
    print(f"📋 Loaded {len(canonical_materials)} materials from Materials.yaml")
    
    if args.report or args.check:
        report = generate_report(canonical_materials, material_categories)
        print(report)
    
    if args.fix:
        print("\n⚠️  --fix not yet implemented. Please fix issues manually.")
        print("   See report above for specific issues to address.")


if __name__ == "__main__":
    main()
