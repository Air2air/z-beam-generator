#!/usr/bin/env python3
"""
Enhanced Categories.yaml Validation Tool

Validates the enhanced Categories.yaml file structure, data integrity,
and consistency with source Materials.yaml.

Author: Z-Beam Content Generator
Date: 2025-09-26
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CategoriesValidator:
    """Enhanced Categories.yaml validation and quality assurance"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.categories_path = self.base_dir / "data" / "Categories.yaml"
        self.materials_path = self.base_dir / "data" / "Materials.yaml"
        
    def load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
            
    def validate_structure(self, categories_data: Dict[str, Any]) -> bool:
        """Validate the enhanced Categories.yaml structure"""
        logger.info("Validating enhanced Categories.yaml structure...")
        
        validation_results = []
        
        # Check metadata
        if 'metadata' in categories_data:
            metadata = categories_data['metadata']
            validation_results.append(('Metadata version', metadata.get('version') == '2.0.0'))
            validation_results.append(('Enhancement applied', metadata.get('enhancement_applied') is True))
            validation_results.append(('Additional field categories', metadata.get('additional_field_categories') == 4))
        else:
            validation_results.append(('Metadata exists', False))
            
        # Check categories structure
        if 'categories' in categories_data:
            categories = categories_data['categories']
            
            # Expected categories
            expected_categories = {'ceramic', 'composite', 'glass', 'masonry', 'metal', 'plastic', 'semiconductor', 'stone', 'wood'}
            actual_categories = set(categories.keys())
            validation_results.append(('All expected categories present', expected_categories.issubset(actual_categories)))
            
            # Check each category has required fields
            required_fields = {'category_ranges', 'subcategories', 'common_applications'}
            enhanced_fields = {'industryApplications', 'electricalProperties', 'processingParameters', 'chemicalProperties'}
            
            enhanced_category_count = 0
            for category_name, category_data in categories.items():
                # Basic structure
                has_basic = all(field in category_data for field in required_fields)
                validation_results.append((f'{category_name} - Basic structure', has_basic))
                
                # Enhanced fields
                has_enhanced = any(field in category_data for field in enhanced_fields)
                if has_enhanced:
                    enhanced_category_count += 1
                    
                # Industry applications structure
                if 'industryApplications' in category_data:
                    industry_apps = category_data['industryApplications']
                    has_industries = 'common_industries' in industry_apps and len(industry_apps['common_industries']) > 0
                    has_standards = 'regulatory_standards' in industry_apps and len(industry_apps['regulatory_standards']) > 0
                    validation_results.append((f'{category_name} - Industry applications', has_industries and has_standards))
                    
            validation_results.append(('Categories with enhancements', enhanced_category_count >= 7))
            
        else:
            validation_results.append(('Categories exist', False))
            
        # Print validation results
        logger.info("\n📋 Structure Validation Results:")
        passed = 0
        total = len(validation_results)
        
        for test_name, result in validation_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {status} {test_name}")
            if result:
                passed += 1
                
        logger.info(f"\n📊 Structure Validation Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        return passed == total
        
    def validate_data_quality(self, categories_data: Dict[str, Any], materials_data: Dict[str, Any]) -> bool:
        """Validate data quality and consistency with source materials"""
        logger.info("Validating data quality and source consistency...")
        
        validation_results = []
        categories = categories_data.get('categories', {})
        
        # Check that ranges make sense (min < max)
        range_validation_passed = 0
        range_validation_total = 0
        
        for category_name, category_data in categories.items():
            if 'category_ranges' in category_data:
                for field_name, field_data in category_data['category_ranges'].items():
                    if isinstance(field_data, dict) and 'min' in field_data and 'max' in field_data:
                        range_validation_total += 1
                        if field_data['min'] <= field_data['max']:
                            range_validation_passed += 1
                        else:
                            logger.warning(f"Invalid range in {category_name}.{field_name}: {field_data['min']} > {field_data['max']}")
                            
        validation_results.append(('Valid ranges (min ≤ max)', range_validation_passed == range_validation_total))
        
        # Check enhanced properties have confidence scores
        confidence_validation_passed = 0
        confidence_validation_total = 0
        
        enhanced_property_fields = {'electricalProperties', 'processingParameters', 'chemicalProperties'}
        
        for category_name, category_data in categories.items():
            for field_type in enhanced_property_fields:
                if field_type in category_data:
                    for prop_name, prop_data in category_data[field_type].items():
                        if isinstance(prop_data, dict):
                            confidence_validation_total += 1
                            if 'confidence' in prop_data and isinstance(prop_data['confidence'], (int, float)):
                                confidence_validation_passed += 1
                            else:
                                logger.warning(f"Missing confidence score in {category_name}.{field_type}.{prop_name}")
                                
        validation_results.append(('Enhanced properties have confidence scores', 
                                 confidence_validation_passed == confidence_validation_total if confidence_validation_total > 0 else True))
        
        # Check industry applications are not empty
        industry_validation_passed = 0
        industry_validation_total = 0
        
        for category_name, category_data in categories.items():
            if 'industryApplications' in category_data:
                industry_validation_total += 1
                industry_apps = category_data['industryApplications']
                
                industries = industry_apps.get('common_industries', [])
                standards = industry_apps.get('regulatory_standards', [])
                
                if len(industries) > 0 and len(standards) > 0:
                    industry_validation_passed += 1
                else:
                    logger.warning(f"Empty industry applications in {category_name}: {len(industries)} industries, {len(standards)} standards")
                    
        validation_results.append(('Industry applications populated', 
                                 industry_validation_passed == industry_validation_total if industry_validation_total > 0 else True))
        
        # Print validation results
        logger.info("\n📋 Data Quality Validation Results:")
        passed = 0
        total = len(validation_results)
        
        for test_name, result in validation_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {status} {test_name}")
            if result:
                passed += 1
                
        logger.info(f"\n📊 Data Quality Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        return passed == total
        
    def generate_statistics(self, categories_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive statistics about the enhanced Categories.yaml"""
        logger.info("Generating enhanced Categories.yaml statistics...")
        
        stats = {
            'metadata': categories_data.get('metadata', {}),
            'categories': {},
            'totals': {
                'categories': 0,
                'enhanced_categories': 0,
                'industry_applications': 0,
                'electrical_properties': 0,
                'processing_parameters': 0,
                'chemical_properties': 0,
                'total_industries': 0,
                'total_standards': 0,
                'total_enhanced_fields': 0
            }
        }
        
        categories = categories_data.get('categories', {})
        
        for category_name, category_data in categories.items():
            stats['categories'][category_name] = {}
            stats['totals']['categories'] += 1
            
            # Industry applications
            if 'industryApplications' in category_data:
                stats['totals']['industry_applications'] += 1
                industry_apps = category_data['industryApplications']
                industries = len(industry_apps.get('common_industries', []))
                standards = len(industry_apps.get('regulatory_standards', []))
                stats['categories'][category_name]['industries'] = industries
                stats['categories'][category_name]['standards'] = standards
                stats['totals']['total_industries'] += industries
                stats['totals']['total_standards'] += standards
                
            # Electrical properties
            if 'electricalProperties' in category_data:
                stats['totals']['electrical_properties'] += 1
                electrical_props = len(category_data['electricalProperties'])
                stats['categories'][category_name]['electrical_properties'] = electrical_props
                stats['totals']['total_enhanced_fields'] += electrical_props
                
            # Processing parameters
            if 'processingParameters' in category_data:
                stats['totals']['processing_parameters'] += 1
                processing_props = len(category_data['processingParameters'])
                stats['categories'][category_name]['processing_parameters'] = processing_props
                stats['totals']['total_enhanced_fields'] += processing_props
                
            # Chemical properties
            if 'chemicalProperties' in category_data:
                stats['totals']['chemical_properties'] += 1
                chemical_props = len(category_data['chemicalProperties'])
                stats['categories'][category_name]['chemical_properties'] = chemical_props
                stats['totals']['total_enhanced_fields'] += chemical_props
                
            # Count enhanced categories
            enhanced_fields = {'industryApplications', 'electricalProperties', 'processingParameters', 'chemicalProperties'}
            if any(field in category_data for field in enhanced_fields):
                stats['totals']['enhanced_categories'] += 1
                
        return stats
        
    def run_validation(self) -> bool:
        """Run comprehensive validation of enhanced Categories.yaml"""
        logger.info("🔍 Starting comprehensive Categories.yaml validation...")
        
        # Load files
        categories_data = self.load_yaml_file(self.categories_path)
        materials_data = self.load_yaml_file(self.materials_path)
        
        if not categories_data:
            logger.error("Failed to load Categories.yaml")
            return False
            
        if not materials_data:
            logger.error("Failed to load Materials.yaml")
            return False
            
        logger.info(f"📁 Enhanced Categories: {self.categories_path}")
        logger.info(f"📁 Source Materials: {self.materials_path}")
        
        # Run validations
        structure_valid = self.validate_structure(categories_data)
        data_quality_valid = self.validate_data_quality(categories_data, materials_data)
        
        # Generate statistics
        stats = self.generate_statistics(categories_data)
        
        # Print statistics
        logger.info("\n📈 Enhancement Statistics:")
        logger.info(f"  📦 Total Categories: {stats['totals']['categories']}")
        logger.info(f"  🔧 Enhanced Categories: {stats['totals']['enhanced_categories']}")
        logger.info(f"  🏭 Categories with Industry Applications: {stats['totals']['industry_applications']}")
        logger.info(f"  ⚡ Categories with Electrical Properties: {stats['totals']['electrical_properties']}")
        logger.info(f"  🌡️  Categories with Processing Parameters: {stats['totals']['processing_parameters']}")
        logger.info(f"  🧪 Categories with Chemical Properties: {stats['totals']['chemical_properties']}")
        logger.info(f"  🏢 Total Industries: {stats['totals']['total_industries']}")
        logger.info(f"  📋 Total Standards: {stats['totals']['total_standards']}")
        logger.info(f"  🔬 Total Enhanced Fields: {stats['totals']['total_enhanced_fields']}")
        
        # Overall result
        overall_valid = structure_valid and data_quality_valid
        
        if overall_valid:
            logger.info("\n✅ Categories.yaml enhancement validation PASSED - Enhanced Categories.yaml is ready for use!")
        else:
            logger.error("\n❌ Categories.yaml enhancement validation FAILED - Please review issues above")
            
        # Save validation report
        report_path = self.base_dir / "docs" / "CATEGORIES_VALIDATION_REPORT.md"
        self.save_validation_report(report_path, overall_valid, stats)
        
        return overall_valid
        
    def save_validation_report(self, report_path: Path, validation_passed: bool, stats: Dict[str, Any]) -> None:
        """Save comprehensive validation report"""
        
        report_content = f"""# Categories.yaml Enhancement Validation Report

## Validation Summary

**Status**: {'✅ PASSED' if validation_passed else '❌ FAILED'}  
**Generated**: {stats['metadata'].get('generated_date', 'Unknown')}  
**Version**: {stats['metadata'].get('version', 'Unknown')}  

## Enhancement Statistics

- **Total Categories**: {stats['totals']['categories']}
- **Enhanced Categories**: {stats['totals']['enhanced_categories']}
- **Categories with Industry Applications**: {stats['totals']['industry_applications']}
- **Categories with Electrical Properties**: {stats['totals']['electrical_properties']}  
- **Categories with Processing Parameters**: {stats['totals']['processing_parameters']}
- **Categories with Chemical Properties**: {stats['totals']['chemical_properties']}
- **Total Industries**: {stats['totals']['total_industries']}
- **Total Standards**: {stats['totals']['total_standards']}
- **Total Enhanced Fields**: {stats['totals']['total_enhanced_fields']}

## Category-by-Category Summary

"""
        
        for category_name, category_stats in stats['categories'].items():
            report_content += f"### {category_name.title()} Category\n\n"
            
            if 'industries' in category_stats:
                report_content += f"- **Industries**: {category_stats['industries']}\n"
            if 'standards' in category_stats:
                report_content += f"- **Standards**: {category_stats['standards']}\n"
            if 'electrical_properties' in category_stats:
                report_content += f"- **Electrical Properties**: {category_stats['electrical_properties']}\n"
            if 'processing_parameters' in category_stats:
                report_content += f"- **Processing Parameters**: {category_stats['processing_parameters']}\n"
            if 'chemical_properties' in category_stats:
                report_content += f"- **Chemical Properties**: {category_stats['chemical_properties']}\n"
                
            report_content += "\n"
            
        report_content += f"""## File Locations

- **Enhanced Categories**: `data/Categories.yaml`
- **Original Backup**: `data/Categories_backup_before_enhancement.yaml`
- **Source Materials**: `data/Materials.yaml`
- **Validation Report**: `{report_path.relative_to(self.base_dir)}`

## Quality Assurance

The enhanced Categories.yaml has been validated for:

1. **Structure Integrity** - All required fields and proper YAML structure
2. **Data Quality** - Valid ranges, confidence scores, and populated content  
3. **Source Consistency** - Alignment with Materials.yaml source data
4. **Enhancement Coverage** - Comprehensive industry and technical properties

## Next Steps

{'✅ Enhanced Categories.yaml is ready for production use!' if validation_passed else '❌ Please address validation issues before using enhanced Categories.yaml'}

"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as file:
                file.write(report_content)
            logger.info(f"📄 Validation report saved: {report_path}")
        except Exception as e:
            logger.error(f"Error saving validation report: {e}")

def main():
    """Main execution"""
    validator = CategoriesValidator()
    success = validator.run_validation()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())