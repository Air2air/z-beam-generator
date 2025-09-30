#!/usr/bin/env python3
"""
Standalone Validation Tool
Validate existing frontmatter, Materials.yaml, and Categories.yaml without regeneration.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse

from pipeline_integration import InvisiblePipelineRunner

class StandaloneValidator:
    """
    Validation-only tool for existing data without regeneration.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.pipeline_runner = InvisiblePipelineRunner(silent_mode=not verbose)
        self.validation_results = {
            'frontmatter_files': [],
            'materials_yaml': {},
            'categories_yaml': {},
            'summary': {
                'total_files_checked': 0,
                'passed_validation': 0,
                'failed_validation': 0,
                'issues_found': []
            }
        }
    
    def validate_all_frontmatter(self) -> Dict[str, Any]:
        """Validate all existing frontmatter files"""
        
        frontmatter_dir = Path("content/components/frontmatter")
        if not frontmatter_dir.exists():
            return {'error': 'Frontmatter directory not found'}
        
        frontmatter_files = list(frontmatter_dir.glob("*.yaml")) + list(frontmatter_dir.glob("*.md"))
        
        if self.verbose:
            print(f"🔍 Validating {len(frontmatter_files)} frontmatter files...")
        
        for file_path in frontmatter_files:
            material_name = self._extract_material_name(file_path.name)
            
            try:
                # Load frontmatter
                if file_path.suffix == '.yaml':
                    with open(file_path, 'r') as f:
                        frontmatter_data = yaml.safe_load(f)
                else:
                    # Extract YAML from markdown
                    with open(file_path, 'r') as f:
                        content = f.read()
                    frontmatter_data = self._extract_yaml_from_markdown(content)
                
                if frontmatter_data:
                    # Validate using pipeline
                    validation_result = self.pipeline_runner.run_invisible_validation(
                        material_name, frontmatter_data
                    )
                    
                    file_result = {
                        'file': str(file_path),
                        'material': material_name,
                        'validation_passed': validation_result['validation_passed'],
                        'quality_score': validation_result['quality_score'],
                        'issues': validation_result['issues_detected'],
                        'runtime_seconds': validation_result['runtime_seconds']
                    }
                    
                    self.validation_results['frontmatter_files'].append(file_result)
                    
                    if validation_result['validation_passed']:
                        self.validation_results['summary']['passed_validation'] += 1
                        if self.verbose:
                            print(f"✅ {file_path.name}: Quality {validation_result['quality_score']:.2f}")
                    else:
                        self.validation_results['summary']['failed_validation'] += 1
                        if self.verbose:
                            print(f"❌ {file_path.name}: {', '.join(validation_result['issues_detected'])}")
                        self.validation_results['summary']['issues_found'].extend(validation_result['issues_detected'])
                
                self.validation_results['summary']['total_files_checked'] += 1
                
            except Exception as e:
                if self.verbose:
                    print(f"🔥 Error validating {file_path.name}: {e}")
                self.validation_results['summary']['failed_validation'] += 1
                self.validation_results['summary']['issues_found'].append(f"Parse error in {file_path.name}: {e}")
        
        return self.validation_results
    
    def validate_materials_yaml(self) -> Dict[str, Any]:
        """Validate Materials.yaml structure and content"""
        
        materials_file = Path("data/Materials.yaml")
        if not materials_file.exists():
            return {'error': 'Materials.yaml not found'}
        
        if self.verbose:
            print("🔍 Validating Materials.yaml...")
        
        try:
            with open(materials_file, 'r') as f:
                materials_data = yaml.safe_load(f)
            
            validation_result = {
                'file': str(materials_file),
                'structure_valid': True,
                'material_count': 0,
                'categories_found': [],
                'missing_properties': [],
                'invalid_values': [],
                'issues': []
            }
            
            # Check basic structure
            if 'materials' not in materials_data:
                validation_result['structure_valid'] = False
                validation_result['issues'].append("Missing 'materials' key")
            
            if 'material_index' not in materials_data:
                validation_result['structure_valid'] = False
                validation_result['issues'].append("Missing 'material_index' key")
            
            # Validate materials
            materials = materials_data.get('materials', {})
            material_index = materials_data.get('material_index', {})
            
            for category, category_data in materials.items():
                validation_result['categories_found'].append(category)
                
                for item in category_data.get('items', []):
                    validation_result['material_count'] += 1
                    material_name = item.get('name', '')
                    
                    # Check material exists in index
                    if material_name not in material_index:
                        validation_result['issues'].append(f"Material {material_name} missing from material_index")
                    
                    # Validate material properties
                    properties = item.get('properties', {})
                    for prop_name, prop_data in properties.items():
                        if self._is_property_invalid(prop_name, prop_data):
                            validation_result['invalid_values'].append(f"{material_name}.{prop_name}")
            
            # Set overall validation status
            validation_result['validation_passed'] = validation_result['structure_valid'] and len(validation_result['issues']) == 0
            
            if self.verbose:
                if validation_result['validation_passed']:
                    print(f"✅ Materials.yaml: {validation_result['material_count']} materials in {len(validation_result['categories_found'])} categories")
                else:
                    print(f"❌ Materials.yaml: {len(validation_result['issues'])} issues found")
                    for issue in validation_result['issues'][:5]:  # Show first 5 issues
                        print(f"   • {issue}")
            
            self.validation_results['materials_yaml'] = validation_result
            return validation_result
            
        except Exception as e:
            error_result = {
                'error': f"Failed to load Materials.yaml: {e}",
                'validation_passed': False
            }
            self.validation_results['materials_yaml'] = error_result
            if self.verbose:
                print(f"🔥 Error loading Materials.yaml: {e}")
            return error_result
    
    def validate_categories_yaml(self) -> Dict[str, Any]:
        """Validate Categories.yaml structure and content"""
        
        categories_file = Path("data/Categories.yaml")
        if not categories_file.exists():
            return {'error': 'Categories.yaml not found'}
        
        if self.verbose:
            print("🔍 Validating Categories.yaml...")
        
        try:
            with open(categories_file, 'r') as f:
                categories_data = yaml.safe_load(f)
            
            validation_result = {
                'file': str(categories_file),
                'structure_valid': True,
                'category_count': 0,
                'categories_found': [],
                'missing_fields': [],
                'issues': []
            }
            
            # Check basic structure
            if 'categories' not in categories_data:
                validation_result['structure_valid'] = False
                validation_result['issues'].append("Missing 'categories' key")
                return validation_result
            
            # Validate categories
            categories = categories_data.get('categories', {})
            for category_name, category_info in categories.items():
                validation_result['category_count'] += 1
                validation_result['categories_found'].append(category_name)
                
                # Check required fields
                required_fields = ['name', 'description']
                for field in required_fields:
                    if field not in category_info:
                        validation_result['missing_fields'].append(f"{category_name}.{field}")
                        validation_result['issues'].append(f"Category {category_name} missing {field}")
            
            # Set overall validation status
            validation_result['validation_passed'] = validation_result['structure_valid'] and len(validation_result['issues']) == 0
            
            if self.verbose:
                if validation_result['validation_passed']:
                    print(f"✅ Categories.yaml: {validation_result['category_count']} categories")
                else:
                    print(f"❌ Categories.yaml: {len(validation_result['issues'])} issues found")
                    for issue in validation_result['issues']:
                        print(f"   • {issue}")
            
            self.validation_results['categories_yaml'] = validation_result
            return validation_result
            
        except Exception as e:
            error_result = {
                'error': f"Failed to load Categories.yaml: {e}",
                'validation_passed': False
            }
            self.validation_results['categories_yaml'] = error_result
            if self.verbose:
                print(f"🔥 Error loading Categories.yaml: {e}")
            return error_result
    
    def _extract_material_name(self, filename: str) -> str:
        """Extract material name from filename"""
        # Remove common suffixes
        base_name = filename.replace('-laser-cleaning.yaml', '').replace('-laser-cleaning.md', '').replace('.yaml', '').replace('.md', '')
        # Convert to title case
        return base_name.replace('-', ' ').replace('_', ' ').title()
    
    def _extract_yaml_from_markdown(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from markdown content"""
        try:
            yaml_start = content.find('---') + 3
            yaml_end = content.find('---', yaml_start)
            if yaml_start > 2:
                if yaml_end > yaml_start:
                    yaml_content = content[yaml_start:yaml_end].strip()
                else:
                    yaml_content = content[yaml_start:].strip()
                return yaml.safe_load(yaml_content)
        except:
            pass
        return None
    
    def _is_property_invalid(self, prop_name: str, prop_data: Any) -> bool:
        """Check if a property value is invalid"""
        if prop_data is None:
            return True
        
        if isinstance(prop_data, dict):
            value = prop_data.get('value')
            if value is None:
                return True
            
            try:
                num_value = float(value)
                # Basic sanity checks
                if prop_name == 'density' and not (0.1 <= num_value <= 25.0):
                    return True
                elif prop_name == 'meltingPoint' and not (-273 <= num_value <= 4000):
                    return True
                elif prop_name == 'thermalConductivity' and not (0.01 <= num_value <= 500):
                    return True
            except (ValueError, TypeError):
                return True
        
        return False
    
    def generate_validation_report(self) -> str:
        """Generate a comprehensive validation report"""
        
        report_lines = [
            "# Data Validation Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Total files checked: {self.validation_results['summary']['total_files_checked']}",
            f"- Passed validation: {self.validation_results['summary']['passed_validation']}",
            f"- Failed validation: {self.validation_results['summary']['failed_validation']}",
            ""
        ]
        
        # Materials.yaml results
        if self.validation_results['materials_yaml']:
            materials_result = self.validation_results['materials_yaml']
            status = "✅ PASSED" if materials_result.get('validation_passed', False) else "❌ FAILED"
            report_lines.extend([
                f"## Materials.yaml {status}",
                f"- Material count: {materials_result.get('material_count', 0)}",
                f"- Categories: {len(materials_result.get('categories_found', []))}",
                f"- Issues: {len(materials_result.get('issues', []))}",
                ""
            ])
        
        # Categories.yaml results
        if self.validation_results['categories_yaml']:
            categories_result = self.validation_results['categories_yaml']
            status = "✅ PASSED" if categories_result.get('validation_passed', False) else "❌ FAILED"
            report_lines.extend([
                f"## Categories.yaml {status}",
                f"- Category count: {categories_result.get('category_count', 0)}",
                f"- Issues: {len(categories_result.get('issues', []))}",
                ""
            ])
        
        # Frontmatter files summary
        passed_frontmatter = len([f for f in self.validation_results['frontmatter_files'] if f['validation_passed']])
        failed_frontmatter = len([f for f in self.validation_results['frontmatter_files'] if not f['validation_passed']])
        
        report_lines.extend([
            f"## Frontmatter Files",
            f"- Files validated: {len(self.validation_results['frontmatter_files'])}",
            f"- Passed: {passed_frontmatter}",
            f"- Failed: {failed_frontmatter}",
            ""
        ])
        
        # Failed files details
        if failed_frontmatter > 0:
            report_lines.extend(["### Failed Frontmatter Files"])
            for file_result in self.validation_results['frontmatter_files']:
                if not file_result['validation_passed']:
                    report_lines.append(f"- {file_result['file']}: {', '.join(file_result['issues'])}")
            report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """Main validation interface"""
    
    parser = argparse.ArgumentParser(description="Standalone Data Validation Tool")
    parser.add_argument("--frontmatter", action="store_true", help="Validate frontmatter files only")
    parser.add_argument("--materials", action="store_true", help="Validate Materials.yaml only")
    parser.add_argument("--categories", action="store_true", help="Validate Categories.yaml only")
    parser.add_argument("--all", action="store_true", help="Validate all data files")
    parser.add_argument("--report", help="Generate validation report to file")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    if not any([args.frontmatter, args.materials, args.categories, args.all]):
        args.all = True  # Default to validate all
    
    validator = StandaloneValidator(verbose=not args.quiet)
    
    print("🔍 Z-Beam Data Validation Tool")
    print("=" * 50)
    
    # Run requested validations
    if args.all or args.materials:
        validator.validate_materials_yaml()
    
    if args.all or args.categories:
        validator.validate_categories_yaml()
    
    if args.all or args.frontmatter:
        validator.validate_all_frontmatter()
    
    # Generate report if requested
    if args.report:
        report_content = validator.generate_validation_report()
        with open(args.report, 'w') as f:
            f.write(report_content)
        print(f"\n📄 Validation report saved to: {args.report}")
    
    # Print summary
    summary = validator.validation_results['summary']
    print(f"\n📊 Validation Summary:")
    print(f"   Total files: {summary['total_files_checked']}")
    print(f"   Passed: {summary['passed_validation']}")
    print(f"   Failed: {summary['failed_validation']}")
    
    if summary['failed_validation'] > 0:
        print(f"\n⚠️  Issues found: {len(summary['issues_found'])}")
        return False
    else:
        print(f"\n✅ All validations passed!")
        return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)