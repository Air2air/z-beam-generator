#!/usr/bin/env python3
"""
Unique Values Validator

STRICT FAIL-FAST ARCHITECTURE PER GROK_INSTRUCTIONS.md
- ZERO TOLERANCE for duplicate values across materials
- IMMEDIATE failure if uniqueness violations found
- NO silent failures, NO skip logic, NO tolerance for duplicates
- ENFORCES scientific accuracy and material-specific values

Core Purpose: Validate that all material property values are unique within
their categories and prevent the 98.6% duplication problem identified in
MATERIALS_ANALYSIS_CRITICAL_FINDINGS.md
"""

import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict
from validation.errors import ConfigurationError

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Raised when uniqueness validation fails"""

class UniquenessValidator:
    """
    Validates material property uniqueness with strict fail-fast enforcement.
    
    GROK_INSTRUCTIONS.md Compliance:
    - ZERO tolerance for duplicate values
    - IMMEDIATE failure on violations
    - NO silent failures or warnings-only mode
    - STRICT enforcement of scientific accuracy
    """
    
    def __init__(self):
        """Initialize validator with strict requirements"""
        self.materials_file = project_root / "data" / "Materials.yaml"
        self.violation_threshold = 0  # ZERO tolerance per GROK_INSTRUCTIONS.md
        
        # FAIL-FAST: Validate required files exist
        self._validate_required_files()
        
        logger.info("✅ UniquenessValidator initialized with zero tolerance policy")
    
    def _validate_required_files(self):
        """FAIL-FAST validation of required files"""
        if not self.materials_file.exists():
            raise ConfigurationError(f"CRITICAL: Materials.yaml not found at {self.materials_file}")
        
        logger.info("✅ Required files validated")
    
    def validate_property_uniqueness(self) -> Dict[str, Any]:
        """
        Validate that property values are unique within material categories.
        
        FAIL-FAST: Raises ValidationError if ANY duplicates found
        ZERO TOLERANCE for duplicate values
        """
        logger.info("🔍 Starting uniqueness validation with ZERO tolerance policy")
        
        with open(self.materials_file, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        # Track values by category and property
        category_property_values = defaultdict(lambda: defaultdict(list))
        global_property_values = defaultdict(list)
        
        # Collect all property values
        total_materials = 0
        total_properties = 0
        
        for category, category_data in materials_data.get('materials', {}).items():
            for material_item in category_data.get('items', []):
                material_name = material_item.get('name')
                total_materials += 1
                
                properties = material_item.get('properties', {})
                for prop_name, prop_data in properties.items():
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        value = prop_data['value']
                        total_properties += 1
                        
                        # Track by category and property
                        category_property_values[category][prop_name].append({
                            'material': material_name,
                            'value': value,
                            'source': prop_data.get('source', 'unknown'),
                            'confidence': prop_data.get('confidence', 0)
                        })
                        
                        # Track globally
                        global_property_values[prop_name].append({
                            'material': material_name,
                            'category': category,
                            'value': value,
                            'source': prop_data.get('source', 'unknown'),
                            'confidence': prop_data.get('confidence', 0)
                        })
        
        logger.info(f"📊 Analyzed {total_materials} materials with {total_properties} properties")
        
        # Find duplicate values within categories
        category_duplicates = self._find_category_duplicates(category_property_values)
        
        # Find global duplicate values
        global_duplicates = self._find_global_duplicates(global_property_values)
        
        # Check for default sources (forbidden per GROK_INSTRUCTIONS.md)
        default_sources = self._find_default_sources(materials_data)
        
        # Calculate violation counts
        total_violations = (
            len(category_duplicates) + 
            len(global_duplicates) + 
            len(default_sources)
        )
        
        validation_result = {
            'total_materials': total_materials,
            'total_properties': total_properties,
            'category_duplicates': category_duplicates,
            'global_duplicates': global_duplicates,
            'default_sources': default_sources,
            'total_violations': total_violations,
            'validation_passed': total_violations == 0
        }
        
        # FAIL-FAST: Zero tolerance for violations
        if total_violations > 0:
            self._report_violations(validation_result)
            raise ValidationError(
                f"CRITICAL: Found {total_violations} uniqueness violations. "
                f"ZERO TOLERANCE policy violated. See detailed report above."
            )
        
        logger.info("✅ All materials pass uniqueness validation")
        return validation_result
    
    def _find_category_duplicates(
        self, 
        category_property_values: Dict[str, Dict[str, List[Dict[str, Any]]]]
    ) -> List[Dict[str, Any]]:
        """Find duplicate values within the same category"""
        duplicates = []
        
        for category, properties in category_property_values.items():
            for prop_name, value_list in properties.items():
                # Group by value
                value_groups = defaultdict(list)
                for entry in value_list:
                    value_groups[entry['value']].append(entry)
                
                # Find duplicates
                for value, entries in value_groups.items():
                    if len(entries) > 1:
                        duplicates.append({
                            'category': category,
                            'property': prop_name,
                            'duplicate_value': value,
                            'materials': [entry['material'] for entry in entries],
                            'count': len(entries),
                            'sources': [entry['source'] for entry in entries]
                        })
        
        return duplicates
    
    def _find_global_duplicates(
        self, 
        global_property_values: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Find duplicate values across all categories"""
        duplicates = []
        
        for prop_name, value_list in global_property_values.items():
            # Group by value
            value_groups = defaultdict(list)
            for entry in value_list:
                value_groups[entry['value']].append(entry)
            
            # Find duplicates across categories
            for value, entries in value_groups.items():
                if len(entries) > 1:
                    # Check if duplicates span multiple categories
                    categories = set(entry['category'] for entry in entries)
                    if len(categories) > 1:
                        duplicates.append({
                            'property': prop_name,
                            'duplicate_value': value,
                            'materials': [entry['material'] for entry in entries],
                            'categories': list(categories),
                            'count': len(entries),
                            'sources': [entry['source'] for entry in entries]
                        })
        
        return duplicates
    
    def _find_default_sources(self, materials_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find properties using forbidden default sources"""
        default_sources = []
        
        for category, category_data in materials_data.get('materials', {}).items():
            for material_item in category_data.get('items', []):
                material_name = material_item.get('name')
                
                properties = material_item.get('properties', {})
                for prop_name, prop_data in properties.items():
                    if isinstance(prop_data, dict):
                        source = prop_data.get('source', '')
                        confidence = prop_data.get('confidence', 0)
                        
                        # Check for forbidden default sources
                        if (source == 'default_from_category_range' or 
                            confidence < 0.9 or 
                            source != 'ai_research'):
                            default_sources.append({
                                'material': material_name,
                                'category': category,
                                'property': prop_name,
                                'source': source,
                                'confidence': confidence,
                                'value': prop_data.get('value')
                            })
        
        return default_sources
    
    def _report_violations(self, validation_result: Dict[str, Any]):
        """Report detailed validation violations"""
        print("\n🚨 UNIQUENESS VALIDATION FAILURES")
        print("=" * 60)
        print("Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DUPLICATES")
        print("=" * 60)
        
        # Report category duplicates
        category_duplicates = validation_result['category_duplicates']
        if category_duplicates:
            print(f"\n❌ CATEGORY DUPLICATES: {len(category_duplicates)} violations")
            for dup in category_duplicates[:10]:  # Show first 10
                materials = ', '.join(dup['materials'][:3])
                if len(dup['materials']) > 3:
                    materials += f" and {len(dup['materials'])-3} more"
                print(f"   • {dup['category']}.{dup['property']} = {dup['duplicate_value']}")
                print(f"     Materials: {materials}")
        
        # Report global duplicates
        global_duplicates = validation_result['global_duplicates']
        if global_duplicates:
            print(f"\n❌ GLOBAL DUPLICATES: {len(global_duplicates)} violations")
            for dup in global_duplicates[:10]:  # Show first 10
                materials = ', '.join(dup['materials'][:3])
                if len(dup['materials']) > 3:
                    materials += f" and {len(dup['materials'])-3} more"
                categories = ', '.join(dup['categories'])
                print(f"   • {dup['property']} = {dup['duplicate_value']}")
                print(f"     Materials: {materials}")
                print(f"     Categories: {categories}")
        
        # Report default sources
        default_sources = validation_result['default_sources']
        if default_sources:
            print(f"\n❌ FORBIDDEN DEFAULT SOURCES: {len(default_sources)} violations")
            for src in default_sources[:10]:  # Show first 10
                print(f"   • {src['material']}.{src['property']}")
                print(f"     Source: {src['source']} (confidence: {src['confidence']})")
        
        print(f"\n💥 TOTAL VIOLATIONS: {validation_result['total_violations']}")
        print("🚫 SYSTEM CANNOT OPERATE WITH DUPLICATE VALUES")
        print("🚫 REQUIRED: All property values must be unique and AI-researched")
        print("\nREQUIRED ACTIONS:")
        print("1. Replace ALL duplicate values with unique AI-researched values")
        print("2. Ensure ALL properties have source: ai_research")
        print("3. Ensure ALL confidence levels >= 0.9")
        print("4. Run ai_materials_researcher.py to fix violations")
    
    def validate_material_uniqueness(self, material_name: str) -> Dict[str, Any]:
        """Validate uniqueness for a specific material"""
        logger.info(f"🔍 Validating uniqueness for {material_name}")
        
        full_validation = self.validate_property_uniqueness()
        
        # Filter results for specific material
        material_violations = []
        
        for dup in full_validation['category_duplicates']:
            if material_name in dup['materials']:
                material_violations.append(dup)
        
        for dup in full_validation['global_duplicates']:
            if material_name in dup['materials']:
                material_violations.append(dup)
        
        for src in full_validation['default_sources']:
            if src['material'] == material_name:
                material_violations.append(src)
        
        return {
            'material_name': material_name,
            'violations': material_violations,
            'violation_count': len(material_violations),
            'validation_passed': len(material_violations) == 0
        }
    
    def get_duplicate_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about duplicate values"""
        try:
            validation_result = self.validate_property_uniqueness()
            return {
                'validation_successful': True,
                'statistics': {
                    'total_materials': validation_result['total_materials'],
                    'total_properties': validation_result['total_properties'],
                    'category_duplicate_count': len(validation_result['category_duplicates']),
                    'global_duplicate_count': len(validation_result['global_duplicates']),
                    'default_source_count': len(validation_result['default_sources']),
                    'total_violations': validation_result['total_violations']
                }
            }
        except ValidationError as e:
            # Return statistics even if validation fails
            return {
                'validation_successful': False,
                'error': str(e),
                'statistics': {
                    'validation_failed': True,
                    'zero_tolerance_violated': True
                }
            }

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unique Values Validator - ZERO TOLERANCE")
    parser.add_argument('--material', help='Validate specific material')
    parser.add_argument('--stats', action='store_true', help='Show duplicate statistics')
    parser.add_argument('--install-hooks', action='store_true', help='Install git pre-commit hooks')
    
    args = parser.parse_args()
    
    try:
        validator = UniquenessValidator()
        
        if args.install_hooks:
            print("Installing git pre-commit hooks...")
            # TODO: Implement git hook installation
            print("Git hooks installation not yet implemented")
            return
        
        if args.stats:
            stats = validator.get_duplicate_statistics()
            print("📊 UNIQUENESS STATISTICS:")
            print(f"   Validation Passed: {stats['validation_successful']}")
            if 'statistics' in stats:
                for key, value in stats['statistics'].items():
                    print(f"   {key}: {value}")
            return
        
        if args.material:
            result = validator.validate_material_uniqueness(args.material)
            print(f"Material: {result['material_name']}")
            print(f"Violations: {result['violation_count']}")
            print(f"Validation Passed: {result['validation_passed']}")
            return
        
        # Full validation
        result = validator.validate_property_uniqueness()
        print("✅ All materials pass uniqueness validation")
        
    except (ValidationError, ConfigurationError) as e:
        logger.error(f"💥 VALIDATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()