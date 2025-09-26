#!/usr/bin/env python3
"""
Frontmatter Data Issues Repair Script
Automatically fixes identified compliance issues in frontmatter files
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any

class FrontmatterRepairTool:
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.subcategory_fixes = {
            # Semiconductor fixes
            'semiconductor': {
                'elemental': 'intrinsic'
            },
            # Plastic fixes
            'plastic': {
                'general': 'thermoplastic'
            },
            # Glass fixes
            'glass': {
                'general': 'soda-lime',
                'silicate': 'soda-lime', 
                'crystal': 'lead',
                'specialty': 'specialty-glass',
                'treated': 'specialty-glass'
            },
            # Stone fixes
            'stone': {
                'mineral': 'metamorphic',
                'soft': 'sedimentary'
            },
            # Ceramic fixes
            'ceramic': {
                'general': 'oxide'
            },
            # Masonry fixes
            'masonry': {
                'cementitious': 'concrete',
                'surface': 'fired'
            },
            # Wood fixes
            'wood': {
                'flexible': 'softwood'
            },
            # Composite fixes
            'composite': {
                'structural': 'fiber-reinforced'
            }
        }
        
        self.wavelength_ranges = {
            # Common wavelength ranges based on laser type
            355: {'min': 320, 'max': 400},      # UV lasers
            532: {'min': 500, 'max': 570},      # Green lasers  
            1064: {'min': 1000, 'max': 1100},   # Nd:YAG
            10600: {'min': 10000, 'max': 11000} # CO2 lasers
        }
        
        self.repair_stats = {
            "files_processed": 0,
            "wavelength_fixes": 0,
            "subcategory_fixes": 0,
            "unit_fixes": 0,
            "errors": []
        }
    
    def load_frontmatter(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse frontmatter from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                yaml_start = content.find('---') + 3
                yaml_end = content.find('---', yaml_start)
                if yaml_end == -1:
                    yaml_content = content[yaml_start:].strip()
                else:
                    yaml_content = content[yaml_start:yaml_end].strip()
            else:
                raise ValueError("No YAML frontmatter found")
            
            return yaml.safe_load(yaml_content)
            
        except Exception as e:
            self.repair_stats["errors"].append(f"Error loading {file_path.name}: {e}")
            return None
    
    def save_frontmatter(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Save frontmatter data back to file"""
        try:
            yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
            content = f"---\n{yaml_content}---\n\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
        except Exception as e:
            self.repair_stats["errors"].append(f"Error saving {file_path.name}: {e}")
            return False
    
    def fix_wavelength_ranges(self, data: Dict[str, Any]) -> bool:
        """Add missing wavelengthMin and wavelengthMax fields"""
        if 'machineSettings' not in data:
            return False
        
        settings = data['machineSettings']
        if 'wavelength' not in settings:
            return False
        
        # Skip if already has ranges
        if 'wavelengthMin' in settings and 'wavelengthMax' in settings:
            return False
        
        wavelength = settings['wavelength']
        
        # Find closest match or calculate reasonable range
        if wavelength in self.wavelength_ranges:
            range_data = self.wavelength_ranges[wavelength]
        else:
            # Calculate 10% range around the value
            range_data = {
                'min': int(wavelength * 0.9),
                'max': int(wavelength * 1.1)
            }
        
        settings['wavelengthMin'] = float(range_data['min'])
        settings['wavelengthMax'] = float(range_data['max'])
        
        return True
    
    def fix_subcategory(self, data: Dict[str, Any]) -> bool:
        """Fix invalid subcategories"""
        if 'category' not in data or 'subcategory' not in data:
            return False
        
        category = data['category']
        subcategory = data['subcategory']
        
        if category in self.subcategory_fixes:
            fixes = self.subcategory_fixes[category]
            if subcategory in fixes:
                data['subcategory'] = fixes[subcategory]
                return True
        
        return False
    
    def fix_missing_units(self, data: Dict[str, Any]) -> bool:
        """Add missing unit fields"""
        fixed = False
        
        if 'properties' in data:
            props = data['properties']
            
            # Check for thermalConductivity without unit
            if 'thermalConductivity' in props and 'thermalConductivityUnit' not in props:
                props['thermalConductivityUnit'] = 'W/m·K'
                fixed = True
            
            # Check other common missing units
            unit_mappings = {
                'density': 'g/cm³',
                'tensileStrength': 'MPa',
                'youngsModulus': 'GPa',
                'meltingPoint': '°C'
            }
            
            for prop, unit in unit_mappings.items():
                if prop in props and f"{prop}Unit" not in props:
                    props[f"{prop}Unit"] = unit
                    fixed = True
        
        return fixed
    
    def repair_file(self, file_path: Path) -> Dict[str, bool]:
        """Repair a single frontmatter file"""
        result = {
            "wavelength_fixed": False,
            "subcategory_fixed": False,
            "units_fixed": False,
            "success": False
        }
        
        # Load frontmatter
        data = self.load_frontmatter(file_path)
        if data is None:
            return result
        
        # Apply fixes
        result["wavelength_fixed"] = self.fix_wavelength_ranges(data)
        result["subcategory_fixed"] = self.fix_subcategory(data)
        result["units_fixed"] = self.fix_missing_units(data)
        
        # Save if any fixes were applied
        if any([result["wavelength_fixed"], result["subcategory_fixed"], result["units_fixed"]]):
            result["success"] = self.save_frontmatter(file_path, data)
        else:
            result["success"] = True  # No fixes needed
        
        return result
    
    def repair_all_files(self) -> Dict[str, Any]:
        """Repair all frontmatter files"""
        if not self.frontmatter_dir.exists():
            return {"error": f"Directory not found: {self.frontmatter_dir}"}
        
        md_files = list(self.frontmatter_dir.glob("*.md"))
        print(f"🔧 Repairing {len(md_files)} frontmatter files...")
        
        for file_path in md_files:
            self.repair_stats["files_processed"] += 1
            result = self.repair_file(file_path)
            
            if result["success"]:
                if result["wavelength_fixed"]:
                    self.repair_stats["wavelength_fixes"] += 1
                if result["subcategory_fixed"]:
                    self.repair_stats["subcategory_fixes"] += 1
                if result["units_fixed"]:
                    self.repair_stats["unit_fixes"] += 1
            else:
                self.repair_stats["errors"].append(f"Failed to repair {file_path.name}")
        
        return self.repair_stats
    
    def generate_repair_report(self, stats: Dict[str, Any]) -> str:
        """Generate repair completion report"""
        report = []
        report.append("=" * 60)
        report.append("FRONTMATTER DATA REPAIR COMPLETION REPORT")
        report.append("=" * 60)
        report.append("")
        
        report.append("📊 REPAIR STATISTICS")
        report.append("-" * 30)
        report.append(f"Files processed: {stats['files_processed']}")
        report.append(f"Wavelength ranges added: {stats['wavelength_fixes']}")
        report.append(f"Subcategories fixed: {stats['subcategory_fixes']}")
        report.append(f"Unit fields added: {stats['unit_fixes']}")
        report.append("")
        
        if stats["errors"]:
            report.append("❌ ERRORS ENCOUNTERED")
            report.append("-" * 30)
            for error in stats["errors"]:
                report.append(f"  • {error}")
            report.append("")
        
        total_fixes = stats['wavelength_fixes'] + stats['subcategory_fixes'] + stats['unit_fixes']
        report.append(f"🎯 TOTAL REPAIRS COMPLETED: {total_fixes}")
        
        if total_fixes > 0:
            report.append("✅ SUCCESS: Data issues have been resolved!")
        else:
            report.append("ℹ️  INFO: No repairs were needed.")
        
        return "\n".join(report)


def main():
    """Main repair function"""
    print("🚀 Starting frontmatter data repair process...")
    
    repair_tool = FrontmatterRepairTool()
    stats = repair_tool.repair_all_files()
    
    if "error" in stats:
        print(f"❌ Repair failed: {stats['error']}")
        return False
    
    # Generate and display report
    report = repair_tool.generate_repair_report(stats)
    print(report)
    
    # Save repair log
    with open("frontmatter_repair_log.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    return len(stats["errors"]) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)