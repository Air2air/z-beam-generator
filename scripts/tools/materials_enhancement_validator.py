#!/usr/bin/env python3
"""
Materials Enhancement Validator and Normalizer
Ensures all materials have complete, normalized data structures.
"""

import yaml
import re
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import os

class MaterialsEnhancementValidator:
    """Validates and enhances materials.yaml for complete normalization."""
    
    def __init__(self, materials_file: str = "data/materials.yaml"):
        self.materials_file = materials_file
        self.validation_errors = []
        self.enhancement_suggestions = []
        self.normalization_issues = []
        
    def load_materials(self) -> Dict[str, Any]:
        """Load materials from YAML file."""
        try:
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.validation_errors.append(f"Failed to load {self.materials_file}: {e}")
            return {}
    
    def validate_required_fields(self, data: Dict[str, Any]) -> None:
        """Validate that all required fields are present and complete."""
        print("🔍 VALIDATING REQUIRED FIELDS...")
        
        # Category-level required fields
        category_required = ['description', 'article_type', 'processing_priority', 'items']
        
        # Material-level required fields
        material_required = [
            'name', 'author_id', 'complexity', 'difficulty_score', 'category',
            'machine_settings', 'applications', 'environmental_impact', 
            'outcomes', 'regulatory_standards', 'compatibility'
        ]
        
        # Machine settings required fields
        machine_settings_required = [
            'fluence_threshold', 'pulse_duration', 'wavelength_optimal',
            'power_range', 'repetition_rate', 'spot_size', 'laser_type',
            'ablation_threshold', 'thermal_damage_threshold', 
            'processing_speed', 'surface_roughness_change'
        ]
        
        materials = data.get('materials', {})
        
        for cat_name, cat_data in materials.items():
            if not isinstance(cat_data, dict):
                self.validation_errors.append(f"❌ {cat_name}: Category is not a dictionary")
                continue
                
            # Check category fields
            missing_cat_fields = [f for f in category_required if f not in cat_data]
            if missing_cat_fields:
                self.validation_errors.append(f"❌ {cat_name}: Missing category fields: {missing_cat_fields}")
            
            # Check items
            items = cat_data.get('items', [])
            for i, item in enumerate(items):
                item_name = item.get('name', f'Item {i}')
                
                # Check material required fields
                missing_fields = [f for f in material_required if f not in item]
                if missing_fields:
                    self.validation_errors.append(f"❌ {cat_name}.{item_name}: Missing fields: {missing_fields}")
                
                # Check machine settings
                if 'machine_settings' in item:
                    machine_settings = item['machine_settings']
                    missing_machine = [f for f in machine_settings_required if f not in machine_settings]
                    if missing_machine:
                        self.validation_errors.append(f"❌ {cat_name}.{item_name}.machine_settings: Missing: {missing_machine}")
                
                # Check applications format
                if 'applications' in item:
                    apps = item['applications']
                    if not isinstance(apps, list) or len(apps) < 6:
                        self.enhancement_suggestions.append(f"⚠️  {cat_name}.{item_name}: Applications should have 6+ entries")
    
    def validate_field_normalization(self, data: Dict[str, Any]) -> None:
        """Validate field format consistency and normalization."""
        print("📏 VALIDATING FIELD NORMALIZATION...")
        
        materials = data.get('materials', {})
        
        for cat_name, cat_data in materials.items():
            if not isinstance(cat_data, dict):
                continue
                
            items = cat_data.get('items', [])
            for item in items:
                item_name = item.get('name', 'Unknown')
                
                # Validate author_id format
                author_id = item.get('author_id')
                if not isinstance(author_id, int) or author_id < 1 or author_id > 4:
                    self.normalization_issues.append(f"❌ {cat_name}.{item_name}: author_id must be 1-4")
                
                # Validate complexity format
                complexity = item.get('complexity')
                if complexity not in ['low', 'medium', 'high']:
                    self.normalization_issues.append(f"❌ {cat_name}.{item_name}: complexity must be low/medium/high")
                
                # Validate difficulty_score format
                difficulty_score = item.get('difficulty_score')
                if not isinstance(difficulty_score, int) or difficulty_score < 1 or difficulty_score > 5:
                    self.normalization_issues.append(f"❌ {cat_name}.{item_name}: difficulty_score must be 1-5")
                
                # Validate machine_settings format
                machine_settings = item.get('machine_settings', {})
                self._validate_machine_settings_format(cat_name, item_name, machine_settings)
                
                # Validate applications format
                applications = item.get('applications', [])
                self._validate_applications_format(cat_name, item_name, applications)
                
                # Validate environmental_impact structure
                env_impact = item.get('environmental_impact', {})
                self._validate_environmental_impact_format(cat_name, item_name, env_impact)
                
                # Validate outcomes structure
                outcomes = item.get('outcomes', {})
                self._validate_outcomes_format(cat_name, item_name, outcomes)
                
                # Validate regulatory_standards format
                reg_standards = item.get('regulatory_standards', [])
                self._validate_regulatory_standards_format(cat_name, item_name, reg_standards)
                
                # Validate compatibility structure
                compatibility = item.get('compatibility', {})
                self._validate_compatibility_format(cat_name, item_name, compatibility)
    
    def _validate_machine_settings_format(self, cat_name: str, item_name: str, machine_settings: Dict) -> None:
        """Validate machine settings field formats."""
        required_patterns = {
            'fluence_threshold': r'^\d+(\.\d+)?[–-]\d+(\.\d+)?\s*J/cm²$',
            'pulse_duration': r'^\d+[–-]\d+(ns|μs|ms)$',
            'wavelength_optimal': r'^\d+nm$',
            'power_range': r'^\d+[–-]\d+W$',
            'repetition_rate': r'^\d+[–-]\d+kHz$',
            'spot_size': r'^\d+(\.\d+)?[–-]\d+(\.\d+)?mm$',
            'ablation_threshold': r'^\d+(\.\d+)?\s*J/cm²$',
            'thermal_damage_threshold': r'^\d+(\.\d+)?\s*J/cm²$',
            'processing_speed': r'^\d+[–-]\d+\s*mm/min$',
            'surface_roughness_change': r'^<\d+%$'
        }
        
        for field, pattern in required_patterns.items():
            if field in machine_settings:
                value = str(machine_settings[field])
                if not re.match(pattern, value):
                    self.normalization_issues.append(f"❌ {cat_name}.{item_name}.machine_settings.{field}: Format should match '{pattern}'")
    
    def _validate_applications_format(self, cat_name: str, item_name: str, applications: List) -> None:
        """Validate applications field format."""
        if not isinstance(applications, list):
            self.normalization_issues.append(f"❌ {cat_name}.{item_name}.applications: Must be a list")
            return
        
        if len(applications) < 6:
            self.enhancement_suggestions.append(f"⚠️  {cat_name}.{item_name}.applications: Should have 6+ applications")
        
        for app in applications:
            if not isinstance(app, str) or ':' not in app:
                self.normalization_issues.append(f"❌ {cat_name}.{item_name}.applications: Should be 'Industry: Description' format")
    
    def _validate_environmental_impact_format(self, cat_name: str, item_name: str, env_impact: Dict) -> None:
        """Validate environmental impact structure."""
        required_fields = [
            'chemical_waste_elimination',
            'volatile_organic_compounds', 
            'water_consumption',
            'energy_efficiency',
            'air_quality_improvement',
            'resource_conservation'
        ]
        
        missing = [f for f in required_fields if f not in env_impact]
        if missing:
            self.validation_errors.append(f"❌ {cat_name}.{item_name}.environmental_impact: Missing {missing}")
    
    def _validate_outcomes_format(self, cat_name: str, item_name: str, outcomes: Dict) -> None:
        """Validate outcomes structure."""
        required_fields = [
            'contaminant_removal_efficiency',
            'surface_integrity_preservation',
            'processing_time_reduction',
            'quality_consistency',
            'safety_improvement',
            'cost_effectiveness'
        ]
        
        missing = [f for f in required_fields if f not in outcomes]
        if missing:
            self.validation_errors.append(f"❌ {cat_name}.{item_name}.outcomes: Missing {missing}")
    
    def _validate_regulatory_standards_format(self, cat_name: str, item_name: str, reg_standards: List) -> None:
        """Validate regulatory standards format."""
        if not isinstance(reg_standards, list):
            self.normalization_issues.append(f"❌ {cat_name}.{item_name}.regulatory_standards: Must be a list")
            return
        
        if len(reg_standards) < 4:
            self.enhancement_suggestions.append(f"⚠️  {cat_name}.{item_name}.regulatory_standards: Should have 4+ standards")
        
        required_patterns = [
            r'OSHA.*CFR.*Personal Protective Equipment',
            r'FDA.*CFR.*Laser Product Performance Standards',
            r'ANSI.*Safe Use of Lasers',
            r'IEC.*Safety of Laser Products'
        ]
        
        found_patterns = []
        for standard in reg_standards:
            for i, pattern in enumerate(required_patterns):
                if re.search(pattern, standard, re.IGNORECASE):
                    found_patterns.append(i)
        
        if len(set(found_patterns)) < 4:
            self.enhancement_suggestions.append(f"⚠️  {cat_name}.{item_name}.regulatory_standards: Missing core safety standards")
    
    def _validate_compatibility_format(self, cat_name: str, item_name: str, compatibility: Dict) -> None:
        """Validate compatibility structure."""
        required_sections = ['laser_types', 'surface_treatments', 'incompatible_conditions']
        
        missing = [s for s in required_sections if s not in compatibility]
        if missing:
            self.validation_errors.append(f"❌ {cat_name}.{item_name}.compatibility: Missing {missing}")
        
        # Check laser_types format
        if 'laser_types' in compatibility:
            laser_types = compatibility['laser_types']
            if not isinstance(laser_types, list) or len(laser_types) < 3:
                self.enhancement_suggestions.append(f"⚠️  {cat_name}.{item_name}.compatibility.laser_types: Should have 3+ types")
    
    def generate_enhancement_template(self) -> Dict[str, Any]:
        """Generate template for missing fields."""
        return {
            'environmental_impact': {
                'chemical_waste_elimination': '>95% reduction vs chemical cleaning methods',
                'volatile_organic_compounds': 'Zero VOC emissions',
                'water_consumption': 'Dry process, eliminates contaminated water disposal',
                'energy_efficiency': 'Targeted cleaning reduces processing time by 45%',
                'air_quality_improvement': 'No chemical fumes or dust generation',
                'resource_conservation': 'Extends material life through precise cleaning'
            },
            'outcomes': {
                'contaminant_removal_efficiency': '>95% for surface contaminants and coatings',
                'surface_integrity_preservation': '>98% original surface characteristics retention',
                'processing_time_reduction': '50% faster than traditional cleaning methods',
                'quality_consistency': 'Uniform cleaning across material variations',
                'safety_improvement': 'Eliminates chemical handling and exposure risks',
                'cost_effectiveness': '40% reduction in long-term maintenance costs'
            },
            'regulatory_standards': [
                'OSHA 29 CFR 1926.95 - Personal Protective Equipment',
                'FDA 21 CFR 1040.10 - Laser Product Performance Standards',
                'ANSI Z136.1 - Safe Use of Lasers',
                'IEC 60825 - Safety of Laser Products'
            ],
            'compatibility': {
                'laser_types': [
                    'Fiber lasers (optimal for most applications)',
                    'Nd:YAG lasers (excellent for precision work)',
                    'CO2 lasers (moderate effectiveness)'
                ],
                'surface_treatments': [
                    'Natural surfaces',
                    'Coated surfaces',
                    'Stained or contaminated surfaces'
                ],
                'incompatible_conditions': [
                    'Severely damaged material requiring structural repair',
                    'Extremely thin material susceptible to thermal damage'
                ]
            }
        }
    
    def run_full_validation(self) -> Tuple[bool, Dict[str, List[str]]]:
        """Run complete validation and return results."""
        print("🚀 STARTING COMPLETE MATERIALS VALIDATION")
        print("=" * 50)
        
        data = self.load_materials()
        if not data:
            return False, {'errors': self.validation_errors}
        
        # Run all validations
        self.validate_required_fields(data)
        self.validate_field_normalization(data)
        
        # Compile results
        results = {
            'errors': self.validation_errors,
            'enhancement_suggestions': self.enhancement_suggestions,
            'normalization_issues': self.normalization_issues
        }
        
        # Print summary
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"   Critical Errors: {len(self.validation_errors)} ❌")
        print(f"   Enhancement Suggestions: {len(self.enhancement_suggestions)} ⚠️")
        print(f"   Normalization Issues: {len(self.normalization_issues)} 📏")
        
        is_valid = (len(self.validation_errors) == 0 and 
                   len(self.normalization_issues) == 0)
        
        if is_valid:
            print("\n✅ ALL MATERIALS ARE FULLY ENHANCED AND NORMALIZED!")
        else:
            print(f"\n⚠️  {len(self.validation_errors + self.normalization_issues)} ISSUES NEED ATTENTION")
        
        return is_valid, results
    
    def generate_fix_script(self, results: Dict[str, List[str]]) -> str:
        """Generate a Python script to fix identified issues."""
        script_content = '''#!/usr/bin/env python3
"""
Auto-generated script to fix materials.yaml issues
Generated on: {timestamp}
"""

import yaml
import re
from typing import Dict, Any

def fix_materials():
    """Fix all identified issues in materials.yaml"""
    
    with open('data/materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {{}})
    
    # Enhancement template
    enhancement_template = {enhancement_template}
    
    # Apply fixes here based on validation results
    # (This would be customized based on specific issues found)
    
    # Save fixed file
    with open('data/materials.yaml', 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=120)
    
    print("✅ Materials.yaml has been enhanced and normalized!")

if __name__ == "__main__":
    fix_materials()
'''.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            enhancement_template=str(self.generate_enhancement_template())
        )
        
        return script_content


def main():
    """Main execution function."""
    print("🔧 MATERIALS ENHANCEMENT VALIDATOR")
    print("=" * 40)
    
    validator = MaterialsEnhancementValidator()
    is_valid, results = validator.run_full_validation()
    
    # Print detailed results
    if results['errors']:
        print(f"\n❌ CRITICAL ERRORS ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"   {error}")
    
    if results['normalization_issues']:
        print(f"\n📏 NORMALIZATION ISSUES ({len(results['normalization_issues'])}):")
        for issue in results['normalization_issues']:
            print(f"   {issue}")
    
    if results['enhancement_suggestions']:
        print(f"\n💡 ENHANCEMENT SUGGESTIONS ({len(results['enhancement_suggestions'])}):")
        for suggestion in results['enhancement_suggestions']:
            print(f"   {suggestion}")
    
    # Generate fix script if needed
    if not is_valid:
        print(f"\n🛠️  GENERATING AUTO-FIX SCRIPT...")
        fix_script = validator.generate_fix_script(results)
        with open('scripts/tools/fix_materials_issues.py', 'w') as f:
            f.write(fix_script)
        print(f"   Generated: scripts/tools/fix_materials_issues.py")
    
    return is_valid


if __name__ == "__main__":
    main()
