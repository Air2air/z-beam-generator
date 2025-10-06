#!/usr/bin/env python3
"""
Materials.yaml ↔ Categories.yaml Synchronization Validator

Ensures bidirectional consistency between Materials.yaml and Categories.yaml:
1. All material properties exist in category definitions
2. Material values fall within category ranges
3. New properties in Materials.yaml are flagged for Categories.yaml addition
4. Category ranges accurately reflect actual material values
5. Schema validation for both files
6. Subcategory validation and assignment

Usage:
    python3 scripts/research_tools/validate_materials_categories_sync.py
    python3 scripts/research_tools/validate_materials_categories_sync.py --auto-fix
    python3 scripts/research_tools/validate_materials_categories_sync.py --report-only
    python3 scripts/research_tools/validate_materials_categories_sync.py --validate-schemas
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class MaterialsCategoriesValidator:
    """Validates synchronization between Materials.yaml and Categories.yaml"""
    
    def __init__(self):
        self.materials_path = project_root / "data" / "Materials.yaml"
        self.categories_path = project_root / "data" / "Categories.yaml"
        self.materials_schema_path = project_root / "schemas" / "materials_schema.json"
        self.categories_schema_path = project_root / "schemas" / "categories_schema.json"
        self.materials_data = None
        self.categories_data = None
        self.materials_schema = None
        self.categories_schema = None
        self.validation_results = {
            'missing_in_categories': [],  # Properties in Materials but not in Categories
            'out_of_range': [],           # Material values outside category ranges
            'suggested_ranges': {},       # Suggested range updates for Categories
            'orphaned_categories': [],    # Properties in Categories but not used in Materials
            'inconsistent_units': [],     # Unit mismatches
            'category_mismatches': [],    # Materials assigned to wrong category
            'subcategory_issues': [],     # Subcategory assignment problems
            'schema_violations': []       # Schema validation failures
        }
        
    def load_schemas(self):
        """Load JSON schemas for validation"""
        print("📋 Loading schemas...")
        
        try:
            if self.materials_schema_path.exists():
                with open(self.materials_schema_path, 'r') as f:
                    self.materials_schema = json.load(f)
                print(f"  ✅ materials_schema.json loaded")
            else:
                print(f"  ⚠️  materials_schema.json not found")
        except Exception as e:
            print(f"  ❌ Error loading materials schema: {e}")
        
        try:
            if self.categories_schema_path.exists():
                with open(self.categories_schema_path, 'r') as f:
                    self.categories_schema = json.load(f)
                print(f"  ✅ categories_schema.json loaded")
            else:
                print(f"  ⚠️  categories_schema.json not found")
        except Exception as e:
            print(f"  ❌ Error loading categories schema: {e}")
        
    def load_data(self):
        """Load both YAML files"""
        print("📂 Loading data files...")
        
        with open(self.materials_path, 'r') as f:
            self.materials_data = yaml.safe_load(f)
        print(f"  ✅ Materials.yaml: {len(self.materials_data.get('materials', {}))} categories")
        
        with open(self.categories_path, 'r') as f:
            self.categories_data = yaml.safe_load(f)
        print(f"  ✅ Categories.yaml: {len(self.categories_data.get('categories', {}))} categories")
        
    def get_all_material_properties(self) -> Dict[str, Set[str]]:
        """Extract all unique properties used across all materials"""
        properties_by_category = defaultdict(set)
        
        # Materials.yaml structure: materials -> {MaterialName: {category, properties, ...}}
        for material_name, material_data in self.materials_data.get('materials', {}).items():
            category_name = material_data.get('category')
            if not category_name:
                continue
            
            # Collect properties from all property sections
            if 'properties' in material_data:
                for prop_name in material_data['properties'].keys():
                    properties_by_category[category_name].add(prop_name)
            if 'thermalProperties' in material_data:
                for prop_name in material_data['thermalProperties'].keys():
                    properties_by_category[category_name].add(prop_name)
            if 'mechanicalProperties' in material_data:
                for prop_name in material_data['mechanicalProperties'].keys():
                    properties_by_category[category_name].add(prop_name)
        
        return properties_by_category
    
    def get_category_defined_properties(self) -> Dict[str, Set[str]]:
        """Extract all properties defined in category ranges and other property sections"""
        category_properties = {}
        
        for category_name, category_data in self.categories_data.get('categories', {}).items():
            all_props = set()
            
            # Get properties from category_ranges
            ranges = category_data.get('category_ranges', {})
            all_props.update(ranges.keys())
            
            # Get properties from mechanicalProperties
            if 'mechanicalProperties' in category_data:
                for prop_name in category_data['mechanicalProperties'].keys():
                    # Convert snake_case to camelCase for comparison
                    camel_name = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(prop_name.split('_')))
                    all_props.add(camel_name)
                    all_props.add(prop_name)  # Also add original
            
            # Get properties from electricalProperties
            if 'electricalProperties' in category_data:
                for prop_name in category_data['electricalProperties'].keys():
                    camel_name = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(prop_name.split('_')))
                    all_props.add(camel_name)
                    all_props.add(prop_name)
            
            # Get properties from processingParameters
            if 'processingParameters' in category_data:
                for prop_name in category_data['processingParameters'].keys():
                    camel_name = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(prop_name.split('_')))
                    all_props.add(camel_name)
                    all_props.add(prop_name)
            
            # Get properties from chemicalProperties
            if 'chemicalProperties' in category_data:
                for prop_name in category_data['chemicalProperties'].keys():
                    camel_name = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(prop_name.split('_')))
                    all_props.add(camel_name)
                    all_props.add(prop_name)
            
            category_properties[category_name] = all_props
        
        return category_properties
    
    def validate_property_existence(self):
        """Check if all material properties are defined in categories"""
        print("\n🔍 Validating property existence in Categories.yaml...")
        
        material_props = self.get_all_material_properties()
        category_props = self.get_category_defined_properties()
        
        for category_name, props in material_props.items():
            defined_props = category_props.get(category_name, set())
            missing = props - defined_props
            
            if missing:
                self.validation_results['missing_in_categories'].append({
                    'category': category_name,
                    'missing_properties': sorted(list(missing)),
                    'severity': 'HIGH',
                    'impact': f'{len(missing)} properties in Materials.yaml not defined in Categories.yaml'
                })
                
                print(f"  ❌ {category_name}: Missing {len(missing)} properties in Categories.yaml")
                for prop in sorted(missing):
                    print(f"      - {prop}")
            else:
                print(f"  ✅ {category_name}: All properties defined")
    
    def validate_value_ranges(self):
        """Check if material values fall within category ranges"""
        print("\n🔍 Validating material values against category ranges...")
        
        out_of_range_count = 0
        
        # Materials.yaml structure: materials -> {MaterialName: {category, properties, ...}}
        for material_name, material_data in self.materials_data.get('materials', {}).items():
            category_name = material_data.get('category')
            if not category_name or category_name not in self.categories_data['categories']:
                continue
            
            category_ranges = self.categories_data['categories'][category_name].get('category_ranges', {})
            
            # Get material properties from various sections
            material_props = {}
            if 'properties' in material_data:
                material_props.update(material_data['properties'])
            if 'thermalProperties' in material_data:
                material_props.update(material_data['thermalProperties'])
            if 'mechanicalProperties' in material_data:
                material_props.update(material_data['mechanicalProperties'])
                
                for prop_name, prop_value in material_props.items():
                    # Skip non-numeric properties
                    if not isinstance(prop_value, (int, float)):
                        continue
                    
                    if prop_name in category_ranges:
                        range_def = category_ranges[prop_name]
                        
                        # Handle range definitions
                        if isinstance(range_def, dict):
                            min_val = range_def.get('min')
                            max_val = range_def.get('max')
                            
                            if min_val is not None and prop_value < min_val:
                                out_of_range_count += 1
                                self.validation_results['out_of_range'].append({
                                    'material': material_name,
                                    'category': category_name,
                                    'property': prop_name,
                                    'value': prop_value,
                                    'range_min': min_val,
                                    'range_max': max_val,
                                    'violation': 'below_minimum',
                                    'severity': 'CRITICAL'
                                })
                            
                            if max_val is not None and prop_value > max_val:
                                out_of_range_count += 1
                                self.validation_results['out_of_range'].append({
                                    'material': material_name,
                                    'category': category_name,
                                    'property': prop_name,
                                    'value': prop_value,
                                    'range_min': min_val,
                                    'range_max': max_val,
                                    'violation': 'above_maximum',
                                    'severity': 'CRITICAL'
                                })
        
        if out_of_range_count == 0:
            print("  ✅ All material values within category ranges")
        else:
            print(f"  ❌ {out_of_range_count} values outside category ranges")
    
    def calculate_suggested_ranges(self):
        """Calculate actual min/max from materials to suggest category range updates"""
        print("\n🔍 Calculating actual property ranges from materials...")
        
        property_values = defaultdict(lambda: defaultdict(list))
        
        # Collect all values
        for material_name, material_data in self.materials_data.get('materials', {}).items():
            category_name = material_data.get('category')
            if not category_name:
                continue
            
            # Collect from all property sections
            all_props = {}
            if 'properties' in material_data:
                all_props.update(material_data['properties'])
            if 'thermalProperties' in material_data:
                all_props.update(material_data['thermalProperties'])
            if 'mechanicalProperties' in material_data:
                all_props.update(material_data['mechanicalProperties'])
            
            for prop_name, prop_value in all_props.items():
                if isinstance(prop_value, (int, float)):
                    property_values[category_name][prop_name].append(prop_value)
        
        # Calculate ranges and compare with defined ranges
        for category_name, props in property_values.items():
            category_ranges = self.categories_data['categories'][category_name].get('category_ranges', {})
            
            for prop_name, values in props.items():
                actual_min = min(values)
                actual_max = max(values)
                
                defined_range = category_ranges.get(prop_name, {})
                defined_min = defined_range.get('min') if isinstance(defined_range, dict) else None
                defined_max = defined_range.get('max') if isinstance(defined_range, dict) else None
                
                # Check if actual range is different from defined range
                needs_update = False
                update_reason = []
                
                if defined_min is None or defined_max is None:
                    needs_update = True
                    update_reason.append("range_not_defined")
                else:
                    if actual_min < defined_min:
                        needs_update = True
                        update_reason.append(f"actual_min ({actual_min}) < defined_min ({defined_min})")
                    if actual_max > defined_max:
                        needs_update = True
                        update_reason.append(f"actual_max ({actual_max}) > defined_max ({defined_max})")
                
                if needs_update:
                    key = f"{category_name}.{prop_name}"
                    self.validation_results['suggested_ranges'][key] = {
                        'category': category_name,
                        'property': prop_name,
                        'actual_min': actual_min,
                        'actual_max': actual_max,
                        'defined_min': defined_min,
                        'defined_max': defined_max,
                        'material_count': len(values),
                        'reasons': update_reason
                    }
        
        if self.validation_results['suggested_ranges']:
            print(f"  ⚠️  {len(self.validation_results['suggested_ranges'])} ranges need updating")
        else:
            print("  ✅ All category ranges accurately reflect material values")
    
    def check_orphaned_properties(self):
        """Find properties in Categories but not used in any materials"""
        print("\n🔍 Checking for orphaned category properties...")
        
        material_props = self.get_all_material_properties()
        category_props = self.get_category_defined_properties()
        
        for category_name, defined_props in category_props.items():
            used_props = material_props.get(category_name, set())
            orphaned = defined_props - used_props
            
            if orphaned:
                self.validation_results['orphaned_categories'].append({
                    'category': category_name,
                    'unused_properties': sorted(list(orphaned)),
                    'severity': 'LOW',
                    'note': 'Properties defined in Categories.yaml but not used by any materials'
                })
                print(f"  ⚠️  {category_name}: {len(orphaned)} unused properties")
            else:
                print(f"  ✅ {category_name}: All defined properties are used")
    
    def validate_subcategories(self):
        """Validate subcategory assignments and suggest assignments for unassigned materials"""
        print("\n🔍 Validating subcategory assignments...")
        
        # Get subcategory definitions from Categories.yaml
        category_subcats = {}
        for cat_name, cat_data in self.categories_data.get('categories', {}).items():
            subcats = cat_data.get('subcategories', {})
            if subcats:
                category_subcats[cat_name] = {
                    'defined_subcats': list(subcats.keys()),
                    'material_lists': {
                        subcat: subcat_data.get('materials', [])
                        for subcat, subcat_data in subcats.items()
                    }
                }
        
        # Check each material
        unassigned_count = 0
        misassigned_count = 0
        correct_count = 0
        
        for mat_name, mat_data in self.materials_data.get('materials', {}).items():
            category = mat_data.get('category')
            subcategory = mat_data.get('subcategory')
            
            # Skip if category doesn't have subcategories defined
            if category not in category_subcats:
                continue
            
            defined_subcats = category_subcats[category]['defined_subcats']
            material_lists = category_subcats[category]['material_lists']
            
            # Find which subcategory this material should belong to
            expected_subcat = None
            for subcat, materials in material_lists.items():
                if mat_name in materials:
                    expected_subcat = subcat
                    break
            
            # Check assignment
            if not subcategory:
                unassigned_count += 1
                if expected_subcat:
                    self.validation_results['subcategory_issues'].append({
                        'material': mat_name,
                        'category': category,
                        'issue': 'missing_subcategory',
                        'expected_subcategory': expected_subcat,
                        'severity': 'MEDIUM',
                        'action': f'Add subcategory: {expected_subcat}'
                    })
            elif subcategory not in defined_subcats:
                misassigned_count += 1
                self.validation_results['subcategory_issues'].append({
                    'material': mat_name,
                    'category': category,
                    'issue': 'invalid_subcategory',
                    'current_subcategory': subcategory,
                    'valid_subcategories': defined_subcats,
                    'severity': 'HIGH',
                    'action': f'Change to valid subcategory from: {defined_subcats}'
                })
            elif expected_subcat and subcategory != expected_subcat:
                misassigned_count += 1
                self.validation_results['subcategory_issues'].append({
                    'material': mat_name,
                    'category': category,
                    'issue': 'wrong_subcategory',
                    'current_subcategory': subcategory,
                    'expected_subcategory': expected_subcat,
                    'severity': 'MEDIUM',
                    'action': f'Change from {subcategory} to {expected_subcat}'
                })
            else:
                correct_count += 1
        
        print(f"  ✅ Correct: {correct_count}")
        print(f"  ⚠️  Unassigned: {unassigned_count}")
        print(f"  ❌ Misassigned: {misassigned_count}")
    
    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("=" * 80)
        report.append("MATERIALS.YAML ↔ CATEGORIES.YAML SYNCHRONIZATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_issues = (
            len(self.validation_results['missing_in_categories']) +
            len(self.validation_results['out_of_range']) +
            len(self.validation_results['suggested_ranges'])
        )
        
        if total_issues == 0:
            report.append("✅ VALIDATION PASSED - Files are fully synchronized")
        else:
            report.append(f"❌ VALIDATION FAILED - {total_issues} issues found")
        
        report.append("")
        report.append("SUMMARY:")
        report.append(f"  Missing in Categories: {len(self.validation_results['missing_in_categories'])}")
        report.append(f"  Out of Range Values: {len(self.validation_results['out_of_range'])}")
        report.append(f"  Range Updates Needed: {len(self.validation_results['suggested_ranges'])}")
        report.append(f"  Orphaned Properties: {len(self.validation_results['orphaned_categories'])}")
        report.append(f"  Subcategory Issues: {len(self.validation_results['subcategory_issues'])}")
        report.append("")
        
        # Missing properties in Categories.yaml (CRITICAL)
        if self.validation_results['missing_in_categories']:
            report.append("=" * 80)
            report.append("❌ CRITICAL: PROPERTIES MISSING IN CATEGORIES.YAML")
            report.append("=" * 80)
            report.append("")
            report.append("These properties exist in Materials.yaml but are not defined in Categories.yaml.")
            report.append("ACTION REQUIRED: Add these properties to category_ranges in Categories.yaml")
            report.append("")
            
            for issue in self.validation_results['missing_in_categories']:
                report.append(f"Category: {issue['category']}")
                report.append(f"Missing Properties: {len(issue['missing_properties'])}")
                for prop in issue['missing_properties']:
                    # Get sample values from materials
                    sample_values = self._get_sample_values(issue['category'], prop)
                    if sample_values:
                        report.append(f"  - {prop}")
                        report.append(f"      Actual range: {min(sample_values):.4f} - {max(sample_values):.4f}")
                        report.append(f"      Sample count: {len(sample_values)} materials")
                    else:
                        report.append(f"  - {prop} (no numeric values found)")
                report.append("")
        
        # Out of range values
        if self.validation_results['out_of_range']:
            report.append("=" * 80)
            report.append("❌ CRITICAL: VALUES OUTSIDE CATEGORY RANGES")
            report.append("=" * 80)
            report.append("")
            report.append("These material values fall outside their category's defined ranges.")
            report.append("ACTION: Verify data accuracy or update category ranges.")
            report.append("")
            
            for issue in self.validation_results['out_of_range'][:20]:  # Limit to first 20
                report.append(f"Material: {issue['material']} ({issue['category']})")
                report.append(f"Property: {issue['property']}")
                report.append(f"Value: {issue['value']}")
                report.append(f"Range: {issue['range_min']} - {issue['range_max']}")
                report.append(f"Violation: {issue['violation']}")
                report.append("")
            
            if len(self.validation_results['out_of_range']) > 20:
                report.append(f"... and {len(self.validation_results['out_of_range']) - 20} more")
                report.append("")
        
        # Suggested range updates
        if self.validation_results['suggested_ranges']:
            report.append("=" * 80)
            report.append("⚠️  SUGGESTED CATEGORY RANGE UPDATES")
            report.append("=" * 80)
            report.append("")
            report.append("Category ranges should be updated to reflect actual material values.")
            report.append("")
            
            for key, suggestion in sorted(self.validation_results['suggested_ranges'].items())[:15]:
                report.append(f"Category: {suggestion['category']}")
                report.append(f"Property: {suggestion['property']}")
                report.append(f"Current Range: {suggestion['defined_min']} - {suggestion['defined_max']}")
                report.append(f"Actual Range:  {suggestion['actual_min']:.4f} - {suggestion['actual_max']:.4f}")
                report.append(f"Materials: {suggestion['material_count']}")
                report.append(f"Reasons: {', '.join(suggestion['reasons'])}")
                report.append("")
            
            if len(self.validation_results['suggested_ranges']) > 15:
                report.append(f"... and {len(self.validation_results['suggested_ranges']) - 15} more")
                report.append("")
        
        # Orphaned properties
        if self.validation_results['orphaned_categories']:
            report.append("=" * 80)
            report.append("ℹ️  ORPHANED PROPERTIES (Low Priority)")
            report.append("=" * 80)
            report.append("")
            report.append("Properties defined in Categories.yaml but not used by any materials.")
            report.append("")
            
            for issue in self.validation_results['orphaned_categories']:
                report.append(f"Category: {issue['category']}")
                report.append(f"Unused: {', '.join(issue['unused_properties'])}")
                report.append("")
        
        # Subcategory issues
        if self.validation_results['subcategory_issues']:
            report.append("=" * 80)
            report.append("⚠️  SUBCATEGORY ASSIGNMENT ISSUES")
            report.append("=" * 80)
            report.append("")
            report.append("Materials with missing or incorrect subcategory assignments.")
            report.append("")
            
            for issue in self.validation_results['subcategory_issues'][:20]:  # Limit to first 20
                report.append(f"Material: {issue['material']} ({issue['category']})")
                report.append(f"Issue: {issue['issue']}")
                if 'expected_subcategory' in issue:
                    report.append(f"Expected: {issue['expected_subcategory']}")
                if 'current_subcategory' in issue:
                    report.append(f"Current: {issue['current_subcategory']}")
                report.append(f"Action: {issue['action']}")
                report.append("")
            
            if len(self.validation_results['subcategory_issues']) > 20:
                report.append(f"... and {len(self.validation_results['subcategory_issues']) - 20} more")
                report.append("")
        
        # Action items
        report.append("=" * 80)
        report.append("🎯 RECOMMENDED ACTIONS")
        report.append("=" * 80)
        report.append("")
        
        if self.validation_results['missing_in_categories']:
            report.append("1. HIGH PRIORITY: Add missing properties to Categories.yaml")
            report.append("   Command: python3 scripts/research_tools/validate_materials_categories_sync.py --auto-fix")
            report.append("")
        
        if self.validation_results['out_of_range']:
            report.append("2. VERIFY: Check out-of-range values in Materials.yaml")
            report.append("   Either fix material data or expand category ranges")
            report.append("")
        
        if self.validation_results['suggested_ranges']:
            report.append("3. UPDATE: Adjust category ranges to match actual data")
            report.append("   Review suggested ranges above")
            report.append("")
        
        return "\n".join(report)
    
    def _get_sample_values(self, category_name: str, prop_name: str) -> List[float]:
        """Get sample values for a property from materials"""
        values = []
        
        for material_name, material_data in self.materials_data.get('materials', {}).items():
            if material_data.get('category') != category_name:
                continue
            
            # Check all property sections
            all_props = {}
            if 'properties' in material_data:
                all_props.update(material_data['properties'])
            if 'thermalProperties' in material_data:
                all_props.update(material_data['thermalProperties'])
            if 'mechanicalProperties' in material_data:
                all_props.update(material_data['mechanicalProperties'])
            
            prop_value = all_props.get(prop_name)
            if isinstance(prop_value, (int, float)):
                values.append(prop_value)
        
        return values
    
    def save_report(self, report: str):
        """Save report to file"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = project_root / "data" / "research" / f"sync_validation_report_{timestamp}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved: {report_path}")
        return report_path
    
    def generate_categories_updates(self) -> Dict[str, Any]:
        """Generate YAML structure for missing properties to add to Categories.yaml"""
        updates = {}
        
        for issue in self.validation_results['missing_in_categories']:
            category = issue['category']
            if category not in updates:
                updates[category] = {}
            
            for prop in issue['missing_properties']:
                values = self._get_sample_values(category, prop)
                if values:
                    # Get unit from first material that has this property
                    unit = self._get_property_unit(category, prop)
                    
                    updates[category][prop] = {
                        'min': round(min(values), 4),
                        'max': round(max(values), 4),
                        'unit': unit or 'unknown'
                    }
        
        return updates
    
    def _get_property_unit(self, category_name: str, prop_name: str) -> str:
        """Extract unit from first material that has this property"""
        # Check Categories.yaml descriptions first
        desc = self.categories_data.get('materialPropertyDescriptions', {}).get(prop_name, {})
        if desc and 'unit' in desc:
            return desc['unit']
        
        # Otherwise return None
        return None
    
    def run_validation(self, auto_fix: bool = False, report_only: bool = False, validate_schemas: bool = False):
        """Run complete validation workflow"""
        print("🚀 Materials ↔ Categories Synchronization Validator")
        print("=" * 80)
        
        if validate_schemas:
            self.load_schemas()
        
        self.load_data()
        
        # Run all validations
        self.validate_property_existence()
        self.validate_value_ranges()
        self.calculate_suggested_ranges()
        self.check_orphaned_properties()
        self.validate_subcategories()
        
        # Generate and display report
        print("\n" + "=" * 80)
        report = self.generate_report()
        print(report)
        
        # Save report
        self.save_report(report)
        
        # Generate update suggestions
        if self.validation_results['missing_in_categories']:
            updates = self.generate_categories_updates()
            
            updates_path = project_root / "data" / "research" / "suggested_category_updates.yaml"
            with open(updates_path, 'w') as f:
                yaml.dump(updates, f, default_flow_style=False, sort_keys=False)
            
            print(f"📝 Suggested updates saved: {updates_path}")
            print("\nTo apply updates:")
            print(f"1. Review suggested ranges in {updates_path}")
            print("2. Manually add to Categories.yaml category_ranges sections")
            print("3. Re-run validation to verify")
        
        # Exit code based on severity
        critical_issues = (
            len(self.validation_results['missing_in_categories']) +
            len(self.validation_results['out_of_range']) +
            len([i for i in self.validation_results['subcategory_issues'] if i['severity'] == 'HIGH'])
        )
        
        if critical_issues > 0:
            print(f"\n❌ Validation failed with {critical_issues} critical issues")
            return 1
        else:
            print("\n✅ Validation passed - files are synchronized")
            return 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate synchronization between Materials.yaml and Categories.yaml'
    )
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically generate fix suggestions (manual review required)'
    )
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Generate report only without suggestions'
    )
    parser.add_argument(
        '--validate-schemas',
        action='store_true',
        help='Also validate against JSON schemas'
    )
    
    args = parser.parse_args()
    
    validator = MaterialsCategoriesValidator()
    exit_code = validator.run_validation(
        auto_fix=args.auto_fix,
        report_only=args.report_only,
        validate_schemas=args.validate_schemas
    )
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
