#!/usr/bin/env python3
"""
Comprehensive Materials.yaml Data Consistency Checker

Checks for various types of data inconsistencies beyond author fields:
1. Missing required fields
2. Data type inconsistencies  
3. Value range violations
4. Duplicate/conflicting data
5. Schema compliance issues
6. Cross-reference integrity
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict, Counter
from datetime import datetime

class MaterialsDataConsistencyChecker:
    
    def __init__(self, materials_file: str = "data/Materials.yaml"):
        self.materials_file = Path(materials_file)
        self.issues = []
        self.stats = {}
        
        # Expected author IDs mapping
        self.author_ids = {
            'Alessandro Moretti': 2,
            'Todd Dunning': 4, 
            'Yi-Chun Lin': 1,
            'Ikmanda Roswati': 3
        }
        
        # Required fields for different sections
        self.required_fields = {
            'material': ['category', 'applications', 'author'],
            'author': ['name', 'country', 'expertise', 'id', 'image', 'sex', 'title'],
            'captions': ['before_text', 'after_text', 'author', 'generated'],
            'materialProperties': [],  # Variable based on category
            'machineSettings': []      # Variable based on material type
        }
    
    def load_materials(self) -> Dict[str, Any]:
        """Load Materials.yaml safely"""
        try:
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.add_issue('CRITICAL', 'FILE_LOAD', f"Failed to load {self.materials_file}: {e}")
            return {}
    
    def add_issue(self, severity: str, category: str, description: str, material: str = None):
        """Add a consistency issue"""
        self.issues.append({
            'severity': severity,
            'category': category,
            'description': description,
            'material': material
        })
    
    def check_missing_fields(self, data: Dict[str, Any]):
        """Check for missing required fields"""
        materials = data.get('materials', {})
        missing_count = 0
        
        for material_name, material_data in materials.items():
            # Check top-level required fields
            for field in self.required_fields['material']:
                if field not in material_data or not material_data[field]:
                    self.add_issue('HIGH', 'MISSING_FIELD', 
                                 f"Missing required field '{field}'", material_name)
                    missing_count += 1
            
            # Check author fields if author exists
            if 'author' in material_data and isinstance(material_data['author'], dict):
                for field in self.required_fields['author']:
                    if field not in material_data['author']:
                        self.add_issue('MEDIUM', 'MISSING_AUTHOR_FIELD',
                                     f"Missing author field '{field}'", material_name)
                        missing_count += 1
            
            # Check captions fields if captions exist
            if 'captions' in material_data and isinstance(material_data['captions'], dict):
                for field in self.required_fields['captions']:
                    if field not in material_data['captions']:
                        self.add_issue('MEDIUM', 'MISSING_CAPTION_FIELD',
                                     f"Missing caption field '{field}'", material_name)
                        missing_count += 1
        
        self.stats['missing_fields'] = missing_count
    
    def check_data_types(self, data: Dict[str, Any]):
        """Check for data type inconsistencies"""
        materials = data.get('materials', {})
        type_issues = 0
        
        for material_name, material_data in materials.items():
            # Check applications is a list
            if 'applications' in material_data:
                if not isinstance(material_data['applications'], list):
                    self.add_issue('HIGH', 'TYPE_ERROR',
                                 f"'applications' should be a list, got {type(material_data['applications']).__name__}",
                                 material_name)
                    type_issues += 1
            
            # Check author is a dict
            if 'author' in material_data:
                if not isinstance(material_data['author'], dict):
                    self.add_issue('HIGH', 'TYPE_ERROR',
                                 f"'author' should be a dict, got {type(material_data['author']).__name__}",
                                 material_name)
                    type_issues += 1
                else:
                    # Check author ID is integer
                    if 'id' in material_data['author']:
                        if not isinstance(material_data['author']['id'], int):
                            self.add_issue('MEDIUM', 'TYPE_ERROR',
                                         f"author.id should be integer, got {type(material_data['author']['id']).__name__}",
                                         material_name)
                            type_issues += 1
            
            # Check materialProperties structure
            if 'materialProperties' in material_data:
                if not isinstance(material_data['materialProperties'], dict):
                    self.add_issue('HIGH', 'TYPE_ERROR',
                                 f"'materialProperties' should be a dict, got {type(material_data['materialProperties']).__name__}",
                                 material_name)
                    type_issues += 1
        
        self.stats['type_issues'] = type_issues
    
    def check_author_consistency(self, data: Dict[str, Any]):
        """Check author data consistency"""
        materials = data.get('materials', {})
        author_issues = 0
        
        for material_name, material_data in materials.items():
            if 'author' in material_data and isinstance(material_data['author'], dict):
                author = material_data['author']
                author_name = author.get('name', '')
                author_id = author.get('id', None)
                
                # Check if author ID matches expected mapping
                if author_name in self.author_ids:
                    expected_id = self.author_ids[author_name]
                    if author_id != expected_id:
                        self.add_issue('MEDIUM', 'AUTHOR_ID_MISMATCH',
                                     f"Author '{author_name}' has ID {author_id}, expected {expected_id}",
                                     material_name)
                        author_issues += 1
                
                # Check for unknown authors
                elif author_name and author_name not in self.author_ids:
                    self.add_issue('LOW', 'UNKNOWN_AUTHOR',
                                 f"Unknown author '{author_name}' not in author mapping",
                                 material_name)
                    author_issues += 1
        
        self.stats['author_issues'] = author_issues
    
    def check_duplicate_values(self, data: Dict[str, Any]):
        """Check for unexpected duplicate values that might indicate copy-paste errors"""
        materials = data.get('materials', {})
        
        # Track values that should typically be unique per material
        value_trackers = {
            'descriptions': defaultdict(list),
            'captions_before': defaultdict(list),
            'captions_after': defaultdict(list)
        }
        
        for material_name, material_data in materials.items():
            # Track descriptions
            if 'description' in material_data:
                desc = material_data['description']
                if isinstance(desc, str) and len(desc) > 20:  # Only check substantial descriptions
                    value_trackers['descriptions'][desc].append(material_name)
            
            # Track caption content
            if 'captions' in material_data and isinstance(material_data['captions'], dict):
                captions = material_data['captions']
                
                if 'before_text' in captions:
                    before = captions['before_text']
                    if isinstance(before, str) and len(before) > 50:  # Only check substantial content
                        value_trackers['captions_before'][before].append(material_name)
                
                if 'after_text' in captions:
                    after = captions['after_text']
                    if isinstance(after, str) and len(after) > 50:  # Only check substantial content
                        value_trackers['captions_after'][after].append(material_name)
        
        # Report duplicates
        duplicate_count = 0
        for content_type, tracker in value_trackers.items():
            for value, materials in tracker.items():
                if len(materials) > 1:
                    self.add_issue('MEDIUM', 'DUPLICATE_CONTENT',
                                 f"Identical {content_type} found in materials: {', '.join(materials)}")
                    duplicate_count += 1
        
        self.stats['duplicate_content'] = duplicate_count
    
    def check_category_consistency(self, data: Dict[str, Any]):
        """Check category-related consistency"""
        materials = data.get('materials', {})
        material_index = data.get('material_index', {})
        category_issues = 0
        
        for material_name, material_data in materials.items():
            material_category = material_data.get('category', '')
            index_category = material_index.get(material_name, '')
            
            # Check if material category matches index
            if material_category and index_category and material_category != index_category:
                self.add_issue('HIGH', 'CATEGORY_MISMATCH',
                             f"Category mismatch: material='{material_category}' vs index='{index_category}'",
                             material_name)
                category_issues += 1
            
            # Check if material exists in index
            if material_name not in material_index:
                self.add_issue('MEDIUM', 'MISSING_INDEX',
                             "Material not found in material_index",
                             material_name)
                category_issues += 1
        
        # Check if index materials exist in materials section
        for index_material in material_index.keys():
            if index_material not in materials:
                self.add_issue('MEDIUM', 'ORPHANED_INDEX',
                             f"Material '{index_material}' in index but not in materials section")
                category_issues += 1
        
        self.stats['category_issues'] = category_issues
    
    def check_property_completeness(self, data: Dict[str, Any]):
        """Check for property completeness issues"""
        materials = data.get('materials', {})
        completeness_issues = 0
        
        # Track property coverage by category
        category_properties = defaultdict(set)
        
        for material_name, material_data in materials.items():
            category = material_data.get('category', 'unknown')
            
            # Collect all properties for this material
            if 'materialProperties' in material_data:
                mat_props = material_data['materialProperties']
                if isinstance(mat_props, dict):
                    for prop_group, props in mat_props.items():
                        if isinstance(props, dict) and 'properties' in props:
                            category_properties[category].update(props['properties'].keys())
            
            # Check for extremely sparse property data
            total_props = sum(
                len(group.get('properties', {})) 
                for group in material_data.get('materialProperties', {}).values()
                if isinstance(group, dict)
            )
            
            if total_props < 5:  # Arbitrary threshold for "too few properties"
                self.add_issue('LOW', 'SPARSE_PROPERTIES',
                             f"Only {total_props} properties defined (might need more research)",
                             material_name)
                completeness_issues += 1
        
        self.stats['completeness_issues'] = completeness_issues
        self.stats['category_property_coverage'] = {
            cat: len(props) for cat, props in category_properties.items()
        }
    
    def check_value_ranges(self, data: Dict[str, Any]):
        """Check for obviously invalid property values"""
        materials = data.get('materials', {})
        range_issues = 0
        
        # Define reasonable ranges for common properties
        property_ranges = {
            'density': {'min': 0.1, 'max': 25.0, 'unit': 'g/cm³'},
            'meltingPoint': {'min': -100, 'max': 4000, 'unit': '°C'},
            'thermalConductivity': {'min': 0.01, 'max': 500, 'unit': 'W/(m·K)'},
            'hardness': {'min': 0.01, 'max': 100, 'unit': 'GPa'},
            'tensileStrength': {'min': 0.1, 'max': 10000, 'unit': 'MPa'}
        }
        
        for material_name, material_data in materials.items():
            if 'materialProperties' in material_data:
                mat_props = material_data['materialProperties']
                if isinstance(mat_props, dict):
                    for prop_group, group_data in mat_props.items():
                        if isinstance(group_data, dict) and 'properties' in group_data:
                            properties = group_data['properties']
                            
                            for prop_name, prop_data in properties.items():
                                if isinstance(prop_data, dict) and 'value' in prop_data:
                                    value = prop_data['value']
                                    
                                    # Check against known ranges
                                    if prop_name in property_ranges:
                                        range_def = property_ranges[prop_name]
                                        if isinstance(value, (int, float)):
                                            if value < range_def['min'] or value > range_def['max']:
                                                self.add_issue('MEDIUM', 'VALUE_RANGE',
                                                             f"Property '{prop_name}' value {value} outside expected range "
                                                             f"[{range_def['min']}-{range_def['max']}] {range_def['unit']}",
                                                             material_name)
                                                range_issues += 1
        
        self.stats['range_issues'] = range_issues
    
    def generate_report(self):
        """Generate comprehensive consistency report"""
        # Sort issues by severity and category
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        self.issues.sort(key=lambda x: (severity_order.get(x['severity'], 4), x['category'], x['material'] or ''))
        
        # Count issues by severity
        severity_counts = Counter(issue['severity'] for issue in self.issues)
        
        report = f"""# Materials.yaml Comprehensive Data Consistency Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 📊 Summary
- **Total Issues Found**: {len(self.issues)}
- **Critical**: {severity_counts.get('CRITICAL', 0)}
- **High Priority**: {severity_counts.get('HIGH', 0)}
- **Medium Priority**: {severity_counts.get('MEDIUM', 0)}
- **Low Priority**: {severity_counts.get('LOW', 0)}

## 📈 Statistics
"""
        
        for stat_name, stat_value in self.stats.items():
            if isinstance(stat_value, dict):
                report += f"- **{stat_name.replace('_', ' ').title()}**:\n"
                for key, value in stat_value.items():
                    report += f"  - {key}: {value}\n"
            else:
                report += f"- **{stat_name.replace('_', ' ').title()}**: {stat_value}\n"
        
        if self.issues:
            report += "\n## 🚨 Issues Found\n\n"
            
            current_severity = None
            for issue in self.issues:
                if issue['severity'] != current_severity:
                    current_severity = issue['severity']
                    icon = {'CRITICAL': '🔥', 'HIGH': '⚠️', 'MEDIUM': '⚡', 'LOW': '💡'}.get(current_severity, '❓')
                    report += f"\n### {icon} {current_severity} Priority Issues\n\n"
                
                material_info = f" ({issue['material']})" if issue['material'] else ""
                report += f"- **{issue['category']}**{material_info}: {issue['description']}\n"
        else:
            report += "\n## ✅ No Issues Found\nAll data consistency checks passed!\n"
        
        return report
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all consistency checks"""
        print("🔍 Materials.yaml Comprehensive Data Consistency Checker")
        print("=" * 60)
        
        # Load data
        print("📖 Loading Materials.yaml...")
        data = self.load_materials()
        
        if not data:
            return {'success': False, 'report': 'Failed to load Materials.yaml'}
        
        # Run all checks
        print("🔍 Checking missing fields...")
        self.check_missing_fields(data)
        
        print("🔍 Checking data types...")
        self.check_data_types(data)
        
        print("🔍 Checking author consistency...")
        self.check_author_consistency(data)
        
        print("🔍 Checking for duplicate content...")
        self.check_duplicate_values(data)
        
        print("🔍 Checking category consistency...")
        self.check_category_consistency(data)
        
        print("🔍 Checking property completeness...")
        self.check_property_completeness(data)
        
        print("🔍 Checking value ranges...")
        self.check_value_ranges(data)
        
        # Generate report
        print("📄 Generating report...")
        report = self.generate_report()
        
        # Save report
        report_file = Path("MATERIALS_COMPREHENSIVE_CONSISTENCY_REPORT.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Report saved: {report_file}")
        print(f"📊 Total issues found: {len(self.issues)}")
        
        # Print summary
        if self.issues:
            severity_counts = Counter(issue['severity'] for issue in self.issues)
            print(f"🔥 Critical: {severity_counts.get('CRITICAL', 0)}")
            print(f"⚠️  High: {severity_counts.get('HIGH', 0)}")
            print(f"⚡ Medium: {severity_counts.get('MEDIUM', 0)}")
            print(f"💡 Low: {severity_counts.get('LOW', 0)}")
        else:
            print("✅ No consistency issues found!")
        
        return {
            'success': True,
            'issues': self.issues,
            'stats': self.stats,
            'report': report
        }

def main():
    checker = MaterialsDataConsistencyChecker()
    result = checker.run_all_checks()
    
    if result['success']:
        print("\n🎉 Consistency check completed!")
        if result['issues']:
            print("⚠️  Issues found - see report for details")
        else:
            print("✅ All checks passed!")
    else:
        print("❌ Consistency check failed!")
        exit(1)

if __name__ == "__main__":
    main()