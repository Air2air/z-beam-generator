#!/usr/bin/env python3
"""
Material Value Range Analysis Tool

This script evaluates numeric values in materialProperties and machineSettings 
from frontmatter files against the expected ranges defined in Categories.yaml 
to identify values that fall outside their proper bounds.
"""

import yaml
import os
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import re

class ValueRangeAnalyzer:
    def __init__(self):
        self.categories_data = {}
        self.machine_settings_ranges = {}
        self.issues_found = []
        self.stats = {
            'files_processed': 0,
            'total_values_checked': 0,
            'out_of_range_values': 0,
            'missing_range_definitions': 0
        }
        
    def load_categories_data(self, categories_file: str) -> None:
        """Load the Categories.yaml file to get expected ranges."""
        try:
            with open(categories_file, 'r') as f:
                self.categories_data = yaml.safe_load(f)
            print(f"✓ Loaded categories data with {len(self.categories_data.get('categories', {}))} categories")
        except Exception as e:
            print(f"❌ Error loading categories file: {e}")
            raise
            
    def load_machine_settings_ranges(self, materials_file: str) -> None:
        """Load machine settings ranges from Materials.yaml."""
        try:
            with open(materials_file, 'r') as f:
                materials_data = yaml.safe_load(f)
                self.machine_settings_ranges = materials_data.get('machineSettingsRanges', {})
            print(f"✓ Loaded machine settings ranges for {len(self.machine_settings_ranges)} parameters")
        except Exception as e:
            print(f"❌ Error loading materials file: {e}")
            raise
    
    def parse_numeric_value(self, value: Any) -> Optional[float]:
        """Parse a numeric value from various formats."""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common units and multipliers
            cleaned = value.replace(',', '')
            
            # Handle scientific notation markers like ×10⁻⁶
            if '×10⁻' in cleaned:
                parts = cleaned.split('×10⁻')
                if len(parts) == 2:
                    try:
                        base = float(parts[0])
                        exp = int(parts[1].split('/')[0])  # Handle cases like ×10⁻⁶/K
                        return base * (10 ** -exp)
                    except ValueError:
                        pass
            
            # Handle regular scientific notation
            if 'e-' in cleaned.lower() or 'e+' in cleaned.lower():
                try:
                    return float(cleaned.split()[0])
                except ValueError:
                    pass
            
            # Extract first number from string
            number_match = re.search(r'-?\d+\.?\d*', cleaned)
            if number_match:
                try:
                    return float(number_match.group())
                except ValueError:
                    pass
        
        return None
    
    def get_property_range(self, category: str, property_name: str) -> Optional[Dict]:
        """Get the expected range for a property in a given category."""
        if category not in self.categories_data.get('categories', {}):
            return None
            
        category_data = self.categories_data['categories'][category]
        
        # Check in category_ranges first
        if 'category_ranges' in category_data and property_name in category_data['category_ranges']:
            range_data = category_data['category_ranges'][property_name]
            return {
                'min': range_data.get('min'),
                'max': range_data.get('max'),
                'unit': range_data.get('unit'),
                'source': 'category_ranges'
            }
        
        # Check in other property sections
        for section in ['electricalProperties', 'processingParameters', 'chemicalProperties', 'mechanicalProperties']:
            if section in category_data and property_name in category_data[section]:
                range_data = category_data[section][property_name]
                return {
                    'min': range_data.get('min'),
                    'max': range_data.get('max'),
                    'unit': range_data.get('unit'),
                    'source': section
                }
        
        return None
    
    def get_machine_setting_range(self, setting_name: str) -> Optional[Dict]:
        """Get the expected range for a machine setting."""
        if setting_name in self.machine_settings_ranges:
            range_data = self.machine_settings_ranges[setting_name]
            return {
                'min': range_data.get('min'),
                'max': range_data.get('max'),
                'unit': range_data.get('unit'),
                'source': 'machineSettingsRanges'
            }
        return None
    
    def check_value_against_range(self, value: float, range_info: Dict, 
                                material_name: str, property_name: str, 
                                category: str, property_type: str) -> None:
        """Check if a value falls within its expected range."""
        min_val = range_info.get('min')
        max_val = range_info.get('max')
        
        if min_val is None and max_val is None:
            return  # No range defined
        
        self.stats['total_values_checked'] += 1
        
        out_of_range = False
        issue_details = {
            'material': material_name,
            'category': category,
            'property_type': property_type,
            'property_name': property_name,
            'actual_value': value,
            'expected_min': min_val,
            'expected_max': max_val,
            'unit': range_info.get('unit'),
            'source': range_info.get('source'),
            'severity': 'info'
        }
        
        if min_val is not None and value < min_val:
            out_of_range = True
            issue_details['issue'] = f"Value {value} is below minimum {min_val}"
            issue_details['deviation'] = value - min_val
            issue_details['deviation_percent'] = ((value - min_val) / min_val) * 100 if min_val != 0 else float('inf')
            issue_details['severity'] = 'high' if abs(issue_details['deviation_percent']) > 50 else 'medium'
        
        elif max_val is not None and value > max_val:
            out_of_range = True
            issue_details['issue'] = f"Value {value} is above maximum {max_val}"
            issue_details['deviation'] = value - max_val
            issue_details['deviation_percent'] = ((value - max_val) / max_val) * 100 if max_val != 0 else float('inf')
            issue_details['severity'] = 'high' if abs(issue_details['deviation_percent']) > 50 else 'medium'
        
        if out_of_range:
            self.stats['out_of_range_values'] += 1
            self.issues_found.append(issue_details)
    
    def analyze_frontmatter_file(self, file_path: str) -> None:
        """Analyze a single frontmatter file for out-of-range values."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            material_name = data.get('name', 'Unknown')
            category = data.get('category', '').lower()
            
            self.stats['files_processed'] += 1
            
            # Analyze materialProperties
            if 'materialProperties' in data:
                for prop_name, prop_data in data['materialProperties'].items():
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        value = self.parse_numeric_value(prop_data['value'])
                        if value is not None:
                            range_info = self.get_property_range(category, prop_name)
                            if range_info:
                                self.check_value_against_range(
                                    value, range_info, material_name, 
                                    prop_name, category, 'materialProperty'
                                )
                            else:
                                self.stats['missing_range_definitions'] += 1
            
            # Analyze machineSettings
            if 'machineSettings' in data:
                for setting_name, setting_data in data['machineSettings'].items():
                    if isinstance(setting_data, dict) and 'value' in setting_data:
                        value = self.parse_numeric_value(setting_data['value'])
                        if value is not None:
                            range_info = self.get_machine_setting_range(setting_name)
                            if range_info:
                                self.check_value_against_range(
                                    value, range_info, material_name,
                                    setting_name, category, 'machineSetting'
                                )
                            else:
                                self.stats['missing_range_definitions'] += 1
                                
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
    
    def generate_report(self) -> str:
        """Generate a comprehensive analysis report."""
        report = []
        
        # Header
        report.append("=" * 80)
        report.append("MATERIAL VALUE RANGE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {os.popen('date').read().strip()}")
        report.append("")
        
        # Summary statistics
        report.append("📊 ANALYSIS SUMMARY")
        report.append("-" * 40)
        report.append(f"Files processed: {self.stats['files_processed']}")
        report.append(f"Total values checked: {self.stats['total_values_checked']}")
        report.append(f"Out-of-range values found: {self.stats['out_of_range_values']}")
        report.append(f"Missing range definitions: {self.stats['missing_range_definitions']}")
        if self.stats['total_values_checked'] > 0:
            error_rate = (self.stats['out_of_range_values'] / self.stats['total_values_checked']) * 100
            report.append(f"Error rate: {error_rate:.1f}%")
        report.append("")
        
        if not self.issues_found:
            report.append("✅ NO RANGE VIOLATIONS FOUND")
            report.append("All material property and machine setting values are within their expected ranges.")
            return "\n".join(report)
        
        # Group issues by severity
        high_severity = [issue for issue in self.issues_found if issue['severity'] == 'high']
        medium_severity = [issue for issue in self.issues_found if issue['severity'] == 'medium']
        
        # High severity issues
        if high_severity:
            report.append("🚨 HIGH SEVERITY VIOLATIONS (>50% deviation)")
            report.append("-" * 50)
            for issue in high_severity:
                report.append(f"Material: {issue['material']} ({issue['category']})")
                report.append(f"Property: {issue['property_name']} ({issue['property_type']})")
                report.append(f"Issue: {issue['issue']}")
                report.append(f"Expected range: {issue['expected_min']} - {issue['expected_max']} {issue.get('unit', '')}")
                report.append(f"Deviation: {issue['deviation']:.2f} ({issue['deviation_percent']:.1f}%)")
                report.append(f"Source: {issue['source']}")
                report.append("")
        
        # Medium severity issues
        if medium_severity:
            report.append("⚠️  MEDIUM SEVERITY VIOLATIONS (<50% deviation)")
            report.append("-" * 50)
            for issue in medium_severity:
                report.append(f"Material: {issue['material']} ({issue['category']})")
                report.append(f"Property: {issue['property_name']} ({issue['property_type']})")
                report.append(f"Issue: {issue['issue']}")
                report.append(f"Expected range: {issue['expected_min']} - {issue['expected_max']} {issue.get('unit', '')}")
                report.append(f"Deviation: {issue['deviation']:.2f} ({issue['deviation_percent']:.1f}%)")
                report.append(f"Source: {issue['source']}")
                report.append("")
        
        # Summary by category
        report.append("📋 ISSUES BY CATEGORY")
        report.append("-" * 30)
        categories = {}
        for issue in self.issues_found:
            cat = issue['category']
            if cat not in categories:
                categories[cat] = {'count': 0, 'materials': set()}
            categories[cat]['count'] += 1
            categories[cat]['materials'].add(issue['material'])
        
        for cat, info in sorted(categories.items()):
            report.append(f"{cat}: {info['count']} violations in {len(info['materials'])} materials")
        
        # Summary by property type
        report.append("")
        report.append("📋 ISSUES BY PROPERTY TYPE")
        report.append("-" * 35)
        prop_types = {}
        for issue in self.issues_found:
            ptype = issue['property_type']
            if ptype not in prop_types:
                prop_types[ptype] = 0
            prop_types[ptype] += 1
        
        for ptype, count in sorted(prop_types.items()):
            report.append(f"{ptype}: {count} violations")
        
        # Most common violations
        report.append("")
        report.append("📋 MOST COMMON VIOLATIONS")
        report.append("-" * 35)
        prop_names = {}
        for issue in self.issues_found:
            pname = issue['property_name']
            if pname not in prop_names:
                prop_names[pname] = 0
            prop_names[pname] += 1
        
        for pname, count in sorted(prop_names.items(), key=lambda x: x[1], reverse=True)[:10]:
            report.append(f"{pname}: {count} violations")
        
        return "\n".join(report)

def main():
    analyzer = ValueRangeAnalyzer()
    
    print("🔍 Material Value Range Analysis")
    print("=" * 40)
    
    # Load reference data
    categories_file = "data/Categories.yaml"
    materials_file = "data/Materials.yaml"
    
    print("Loading reference data...")
    analyzer.load_categories_data(categories_file)
    analyzer.load_machine_settings_ranges(materials_file)
    
    # Find and analyze frontmatter files
    frontmatter_pattern = "content/components/frontmatter/*.yaml"
    frontmatter_files = glob.glob(frontmatter_pattern)
    
    print(f"\nAnalyzing {len(frontmatter_files)} frontmatter files...")
    
    for i, file_path in enumerate(frontmatter_files, 1):
        if i % 20 == 0:
            print(f"  Processed {i}/{len(frontmatter_files)} files...")
        analyzer.analyze_frontmatter_file(file_path)
    
    print("✅ Analysis complete!")
    
    # Generate and save report
    report = analyzer.generate_report()
    
    # Save to file
    report_file = "MATERIAL_VALUE_RANGE_ANALYSIS_REPORT.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_file}")
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("QUICK SUMMARY")
    print("=" * 60)
    print(f"Files analyzed: {analyzer.stats['files_processed']}")
    print(f"Total values checked: {analyzer.stats['total_values_checked']}")
    print(f"Range violations found: {analyzer.stats['out_of_range_values']}")
    
    if analyzer.stats['out_of_range_values'] > 0:
        error_rate = (analyzer.stats['out_of_range_values'] / analyzer.stats['total_values_checked']) * 100
        print(f"Error rate: {error_rate:.1f}%")
        print(f"\n🔍 See {report_file} for detailed analysis")
    else:
        print("✅ All values are within expected ranges!")

if __name__ == "__main__":
    main()