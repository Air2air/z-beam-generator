#!/usr/bin/env python3
"""
Thermal Behavior Migration Script

Converts materials from inconsistent thermal behavior structure to standardized 
thermal behavior types (melting vs decomposition).

This script:
1. Identifies materials that decompose vs melt
2. Updates frontmatter files with proper thermal behavior structure
3. Converts inconsistent meltingPoint formats to standardized structure
4. Adds thermalBehaviorType property to all materials

Usage:
    python3 scripts/migrate_thermal_behavior.py [--dry-run] [--material MATERIAL_NAME]
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from typing import Dict, Tuple, Optional

class ThermalBehaviorMigrator:
    """Migrates materials to standardized thermal behavior structure"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.frontmatter_dir = self.workspace_root / "content" / "components" / "frontmatter"
        self.materials_yaml = self.workspace_root / "data" / "materials.yaml"
        
        # Materials that decompose instead of melting
        self.decomposing_categories = {"wood", "composite"}
        self.decomposing_materials = {
            # Wood materials
            "ash", "birch", "cedar", "cherry", "fir", "hickory", "mahogany", 
            "maple", "oak", "pine", "plywood", "redwood", "rosewood", "teak",
            "walnut", "mdf", "bamboo", "balsa",
            # Composite materials that decompose
            "epoxy", "fiberglass", "carbon-fiber", "kevlar"
        }
        
        self.stats = {
            "processed": 0,
            "converted_to_decomposition": 0,
            "standardized_melting": 0,
            "errors": 0,
            "skipped": 0
        }
    
    def load_materials_data(self) -> Dict:
        """Load materials.yaml data"""
        try:
            with open(self.materials_yaml) as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading materials.yaml: {e}")
            return {}
    
    def get_material_category(self, material_name: str, materials_data: Dict) -> Optional[str]:
        """Get category for a material"""
        material_index = materials_data.get("material_index", {})
        
        # Try exact match first
        material_info = material_index.get(material_name, {})
        if material_info:
            return material_info.get("category")
        
        # Try capitalized version
        capitalized_name = material_name.capitalize()
        material_info = material_index.get(capitalized_name, {})
        if material_info:
            return material_info.get("category")
        
        # Try title case for multi-word materials
        title_name = material_name.replace("-", " ").title()
        material_info = material_index.get(title_name, {})
        if material_info:
            return material_info.get("category")
        
        return None
    
    def should_decompose(self, material_name: str, category: str) -> bool:
        """Determine if material should use decomposition instead of melting"""
        return (
            category in self.decomposing_categories or 
            material_name.lower() in self.decomposing_materials
        )
    
    def parse_thermal_value(self, thermal_str: str) -> Tuple[Optional[float], str, str]:
        """
        Parse thermal value string and extract numeric value, unit, and behavior type
        
        Returns: (numeric_value, unit, behavior_type)
        """
        if not thermal_str or thermal_str == "N/A":
            return None, "°C", "melting"
        
        # Check for decomposition indicators
        decomp_patterns = [
            r"decomposes?\s+at\s+(\d+(?:\.\d+)?)\s*°?([CF])",
            r"decomposition\s+(?:at\s+)?(\d+(?:\.\d+)?)\s*°?([CF])",
            r"pyrolysis\s+(?:at\s+)?(\d+(?:\.\d+)?)\s*°?([CF])"
        ]
        
        for pattern in decomp_patterns:
            match = re.search(pattern, thermal_str, re.IGNORECASE)
            if match:
                temp = float(match.group(1))
                unit = "°C" if match.group(2).upper() == "C" else "°F"
                return temp, unit, "decomposition"
        
        # Standard melting point pattern
        melting_match = re.search(r"(\d+(?:\.\d+)?)\s*°?([CF])", thermal_str)
        if melting_match:
            temp = float(melting_match.group(1))
            unit = "°C" if melting_match.group(2).upper() == "C" else "°F"
            return temp, unit, "melting"
        
        return None, "°C", "melting"
    
    def convert_frontmatter_thermal(self, frontmatter: Dict, material_name: str, category: str) -> Tuple[Dict, bool]:
        """Convert frontmatter thermal properties to new structure
        
        Returns: (updated_frontmatter, changes_made)
        """
        updated = frontmatter.copy()
        
        # Determine thermal behavior type
        should_decompose = self.should_decompose(material_name, category)
        current_melting_point = frontmatter.get("properties", {}).get("meltingPoint")
        
        if not current_melting_point:
            return updated, False
        
        # Parse current thermal data
        numeric_value, unit, detected_behavior = self.parse_thermal_value(current_melting_point)
        
        # Override detected behavior if material should decompose
        if should_decompose:
            behavior_type = "decomposition"
        else:
            behavior_type = detected_behavior
        
        # Ensure properties section exists
        if "properties" not in updated:
            updated["properties"] = {}
        
        # Track if we made changes
        changes_made = False
        
        # Add thermal behavior type if missing or different
        if updated["properties"].get("thermalBehaviorType") != behavior_type:
            updated["properties"]["thermalBehaviorType"] = behavior_type
            changes_made = True
        
        if behavior_type == "decomposition":
            # Convert to decomposition structure
            if numeric_value is not None:
                new_decomp_point = f"{int(numeric_value)}{unit}"
                if updated["properties"].get("decompositionPoint") != new_decomp_point:
                    updated["properties"]["decompositionPoint"] = new_decomp_point
                    updated["properties"]["decompositionPointNumeric"] = int(numeric_value)
                    updated["properties"]["decompositionPointUnit"] = unit
                    changes_made = True
            
            # Clean up old melting point data for decomposing materials
            props = updated["properties"]
            for old_key in ["meltingPoint", "meltingPointNumeric", "meltingPointUnit"]:
                if old_key in props:
                    del props[old_key]
                    changes_made = True
        
        else:
            # Standardize melting point structure
            if numeric_value is not None:
                new_melting_point = f"{int(numeric_value)}{unit}"
                if updated["properties"].get("meltingPoint") != new_melting_point:
                    updated["properties"]["meltingPoint"] = new_melting_point
                    updated["properties"]["meltingPointNumeric"] = int(numeric_value)
                    updated["properties"]["meltingPointUnit"] = unit
                    changes_made = True
            
            # Clean up any inconsistent meltingPointUnit values
            if updated["properties"].get("meltingPointUnit") == "Decomposes":
                updated["properties"]["meltingPointUnit"] = unit
                changes_made = True
        
        return updated, changes_made
    
    def process_frontmatter_file(self, file_path: Path, materials_data: Dict, dry_run: bool = False) -> bool:
        """Process a single frontmatter file"""
        try:
            # Extract material name from filename
            material_name = file_path.stem.replace("-laser-cleaning", "")
            category = self.get_material_category(material_name, materials_data)
            
            if not category:
                print(f"⚠️  Unknown category for {material_name}, skipping")
                self.stats["skipped"] += 1
                return False
            
            # Read current frontmatter
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Split frontmatter and content
            parts = content.split('---', 2)
            if len(parts) < 3:
                print(f"⚠️  Invalid frontmatter format in {file_path}")
                self.stats["errors"] += 1
                return False
            
            frontmatter_str = parts[1]
            body_content = parts[2]
            
            # Parse frontmatter
            frontmatter = yaml.safe_load(frontmatter_str)
            
            # Convert thermal properties
            updated_frontmatter, changes_made = self.convert_frontmatter_thermal(frontmatter, material_name, category)
            
            # Check if changes were made
            if not changes_made:
                print(f"✅ No changes needed for {material_name}")
                return True
            
            # Update stats based on what changed
            thermal_behavior = updated_frontmatter['properties'].get('thermalBehaviorType', 'unknown')
            if thermal_behavior == "decomposition":
                self.stats["converted_to_decomposition"] += 1
            else:
                self.stats["standardized_melting"] += 1
            
            if dry_run:
                print(f"🔍 Would update {material_name} ({category}) - thermal behavior: {thermal_behavior}")
                return True
            
            # Write updated file
            updated_yaml = yaml.dump(updated_frontmatter, default_flow_style=False, sort_keys=False)
            updated_content = f"---\n{updated_yaml}---{body_content}"
            
            with open(file_path, 'w') as f:
                f.write(updated_content)
            
            thermal_behavior = updated_frontmatter['properties'].get('thermalBehaviorType', 'unknown')
            print(f"✅ Updated {material_name} ({category}) - thermal behavior: {thermal_behavior}")
            self.stats["processed"] += 1
            return True
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            self.stats["errors"] += 1
            return False
    
    def migrate_all_materials(self, dry_run: bool = False, specific_material: str = None):
        """Migrate all frontmatter files or a specific material"""
        print("🚀 Starting thermal behavior migration...")
        print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
        
        materials_data = self.load_materials_data()
        if not materials_data:
            print("❌ Could not load materials data")
            return
        
        # Find frontmatter files
        if specific_material:
            files_to_process = [self.frontmatter_dir / f"{specific_material}-laser-cleaning.md"]
            files_to_process = [f for f in files_to_process if f.exists()]
        else:
            files_to_process = list(self.frontmatter_dir.glob("*-laser-cleaning.md"))
        
        if not files_to_process:
            print("❌ No frontmatter files found")
            return
        
        print(f"📂 Found {len(files_to_process)} frontmatter files to process")
        print()
        
        # Process files
        for file_path in sorted(files_to_process):
            self.process_frontmatter_file(file_path, materials_data, dry_run)
        
        # Print summary
        print()
        print("📊 Migration Summary:")
        print(f"   Total processed: {self.stats['processed']}")
        print(f"   Converted to decomposition: {self.stats['converted_to_decomposition']}")
        print(f"   Standardized melting: {self.stats['standardized_melting']}")
        print(f"   Errors: {self.stats['errors']}")
        print(f"   Skipped: {self.stats['skipped']}")
        
        if dry_run:
            print("\n🔍 This was a dry run. Use --live to apply changes.")

def main():
    parser = argparse.ArgumentParser(description="Migrate thermal behavior structure")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be changed without making changes")
    parser.add_argument("--live", action="store_true",
                       help="Apply changes to files")
    parser.add_argument("--material", type=str,
                       help="Process only specific material")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.live:
        print("❌ Must specify either --dry-run or --live")
        return
    
    workspace_root = os.getcwd()
    migrator = ThermalBehaviorMigrator(workspace_root)
    
    migrator.migrate_all_materials(
        dry_run=args.dry_run,
        specific_material=args.material
    )

if __name__ == "__main__":
    main()
