#!/usr/bin/env python3
"""
Enhanced Categories.yaml Population Tool

This script enhances the existing Categories.yaml with additional field categories
discovered in the comprehensive field analysis:
- Industry Applications
- Electrical Properties  
- Processing Parameters
- Chemical Properties

Usage:
    python3 scripts/tools/populate_enhanced_categories.py
"""

import yaml
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_value_and_unit(value_str):
    """Extract numerical value and unit from strings like '2000-4000 MPa' or '9.8'"""
    if not isinstance(value_str, str):
        return None, None, None, None
    
    # Handle range values like "2000-4000 MPa"
    range_pattern = r'^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)\s*(.*)$'
    range_match = re.match(range_pattern, value_str.strip())
    
    if range_match:
        min_val, max_val, unit = range_match.groups()
        return float(min_val), float(max_val), unit.strip() or None, (float(min_val) + float(max_val)) / 2
    
    # Handle single values like "9.8" or "35 W/(m·K)"
    single_pattern = r'^(\d+(?:\.\d+)?)\s*(.*)$'
    single_match = re.match(single_pattern, value_str.strip())
    
    if single_match:
        value, unit = single_match.groups()
        return float(value), float(value), unit.strip() or None, float(value)
    
    return None, None, None, None

def analyze_materials_for_enhancement(materials_data):
    """Analyze materials data to extract additional field categories"""
    
    enhancement_data = {
        'industry_applications': defaultdict(lambda: defaultdict(set)),
        'electrical_properties': defaultdict(lambda: defaultdict(list)),
        'processing_parameters': defaultdict(lambda: defaultdict(list)),
        'chemical_properties': defaultdict(lambda: defaultdict(list)),
        'category_stats': defaultdict(int)
    }
    
    if 'materials' not in materials_data:
        return enhancement_data
    
    materials_section = materials_data['materials']
    
    for category_name, category_data in materials_section.items():
        if not isinstance(category_data, dict) or 'items' not in category_data:
            continue
            
        logger.info(f"Analyzing {category_name} category for enhancements...")
        enhancement_data['category_stats'][category_name] = len(category_data['items'])
        
        # Analyze each material item
        for item in category_data['items']:
            # Industry Applications
            if 'industryTags' in item:
                for tag in item['industryTags']:
                    enhancement_data['industry_applications'][category_name]['industries'].add(tag)
            
            if 'regulatoryStandards' in item:
                for standard in item['regulatoryStandards']:
                    enhancement_data['industry_applications'][category_name]['regulatory_standards'].add(standard)
            
            # Electrical Properties
            electrical_fields = ['dielectric_constant', 'electricalResistivity']
            for field in electrical_fields:
                if field in item:
                    min_val, max_val, unit, typical = extract_value_and_unit(str(item[field]))
                    if min_val is not None:
                        enhancement_data['electrical_properties'][category_name][field].append({
                            'min': min_val,
                            'max': max_val,
                            'unit': unit,
                            'typical': typical
                        })
            
            # Processing Parameters
            processing_fields = ['operating_temperature', 'melting_point', 'curie_temperature']
            for field in processing_fields:
                if field in item:
                    min_val, max_val, unit, typical = extract_value_and_unit(str(item[field]))
                    if min_val is not None:
                        enhancement_data['processing_parameters'][category_name][field].append({
                            'min': min_val,
                            'max': max_val, 
                            'unit': unit,
                            'typical': typical
                        })
            
            # Chemical Properties
            chemical_fields = ['moisture_content', 'resin_content', 'mineral_composition', 'porosity']
            for field in chemical_fields:
                if field in item:
                    if field in ['moisture_content', 'resin_content', 'porosity']:
                        min_val, max_val, unit, typical = extract_value_and_unit(str(item[field]))
                        if min_val is not None:
                            enhancement_data['chemical_properties'][category_name][field].append({
                                'min': min_val,
                                'max': max_val,
                                'unit': unit,
                                'typical': typical
                            })
                    else:
                        # For composition fields, just track presence
                        enhancement_data['chemical_properties'][category_name][field].append(str(item[field]))
    
    return enhancement_data

def calculate_field_ranges(field_data_list):
    """Calculate min/max ranges and typical values from field data"""
    if not field_data_list:
        return None
    
    # For numeric data
    if isinstance(field_data_list[0], dict) and 'min' in field_data_list[0]:
        all_mins = [item['min'] for item in field_data_list]
        all_maxs = [item['max'] for item in field_data_list]
        all_typicals = [item['typical'] for item in field_data_list if item['typical']]
        
        # Get most common unit
        units = [item['unit'] for item in field_data_list if item['unit']]
        most_common_unit = Counter(units).most_common(1)[0][0] if units else None
        
        return {
            'min': min(all_mins),
            'max': max(all_maxs),
            'typical': sum(all_typicals) / len(all_typicals) if all_typicals else None,
            'unit': most_common_unit,
            'confidence': min(95, 60 + len(field_data_list) * 5)  # Confidence based on data points
        }
    
    # For text data, return most common values
    return {
        'common_values': Counter(field_data_list).most_common(5),
        'total_samples': len(field_data_list)
    }

def enhance_categories_yaml(current_data, materials_data):
    """Enhance current Categories.yaml with additional field categories"""
    
    # Analyze materials for enhancement data
    enhancement_data = analyze_materials_for_enhancement(materials_data)
    
    enhanced_data = current_data.copy()
    
    # Update metadata
    enhanced_data['metadata']['version'] = '2.0.0'
    enhanced_data['metadata']['generated_date'] = datetime.now().isoformat()
    enhanced_data['metadata']['enhancement_applied'] = True
    enhanced_data['metadata']['additional_field_categories'] = 4
    
    # Enhance each category
    for category_name, category_data in enhanced_data['categories'].items():
        logger.info(f"Enhancing {category_name} category...")
        
        # Add Industry Applications
        if category_name in enhancement_data['industry_applications']:
            industry_data = enhancement_data['industry_applications'][category_name]
            category_data['industryApplications'] = {
                'common_industries': sorted(list(industry_data.get('industries', set()))),
                'regulatory_standards': sorted(list(industry_data.get('regulatory_standards', set())))
            }
        
        # Add Electrical Properties
        if category_name in enhancement_data['electrical_properties']:
            electrical_data = enhancement_data['electrical_properties'][category_name]
            category_data['electricalProperties'] = {}
            
            for field_name, field_data_list in electrical_data.items():
                range_data = calculate_field_ranges(field_data_list)
                if range_data and 'min' in range_data:
                    category_data['electricalProperties'][field_name] = {
                        'min': range_data['min'],
                        'max': range_data['max'],
                        'unit': range_data['unit'],
                        'confidence': range_data['confidence']
                    }
                    if range_data['typical']:
                        category_data['electricalProperties'][field_name]['typical'] = range_data['typical']
        
        # Add Processing Parameters
        if category_name in enhancement_data['processing_parameters']:
            processing_data = enhancement_data['processing_parameters'][category_name]
            category_data['processingParameters'] = {}
            
            for field_name, field_data_list in processing_data.items():
                range_data = calculate_field_ranges(field_data_list)
                if range_data and 'min' in range_data:
                    category_data['processingParameters'][field_name] = {
                        'min': range_data['min'],
                        'max': range_data['max'], 
                        'unit': range_data['unit'],
                        'confidence': range_data['confidence']
                    }
                    if range_data['typical']:
                        category_data['processingParameters'][field_name]['typical'] = range_data['typical']
        
        # Add Chemical Properties
        if category_name in enhancement_data['chemical_properties']:
            chemical_data = enhancement_data['chemical_properties'][category_name]
            category_data['chemicalProperties'] = {}
            
            for field_name, field_data_list in chemical_data.items():
                range_data = calculate_field_ranges(field_data_list)
                if range_data:
                    if 'min' in range_data:  # Numeric data
                        category_data['chemicalProperties'][field_name] = {
                            'min': range_data['min'],
                            'max': range_data['max'],
                            'unit': range_data['unit'],
                            'confidence': range_data['confidence']
                        }
                        if range_data['typical']:
                            category_data['chemicalProperties'][field_name]['typical'] = range_data['typical']
                    else:  # Text data
                        category_data['chemicalProperties'][field_name] = {
                            'common_values': [item[0] for item in range_data['common_values']],
                            'total_samples': range_data['total_samples']
                        }
    
    return enhanced_data

def main():
    """Main enhancement function"""
    project_root = Path(__file__).parent.parent.parent
    categories_path = project_root / "data" / "Categories.yaml" 
    materials_path = project_root / "data" / "Materials.yaml"
    enhanced_path = project_root / "data" / "Categories.yaml"
    backup_path = project_root / "data" / "Categories_backup_before_enhancement.yaml"
    
    if not categories_path.exists():
        logger.error(f"Categories.yaml not found at {categories_path}")
        return False
    
    if not materials_path.exists():
        logger.error(f"Materials.yaml not found at {materials_path}")
        return False
    
    try:
        # Load existing Categories.yaml
        logger.info("Loading existing Categories.yaml...")
        with open(categories_path, 'r') as f:
            current_data = yaml.safe_load(f)
        
        # Load Materials.yaml for enhancement data
        logger.info("Loading Materials.yaml for enhancement data...")
        with open(materials_path, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        # Create backup
        logger.info(f"Creating backup at {backup_path}")
        with open(backup_path, 'w') as f:
            yaml.dump(current_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        
        # Enhance Categories.yaml
        logger.info("Enhancing Categories.yaml with additional field categories...")
        enhanced_data = enhance_categories_yaml(current_data, materials_data)
        
        # Write enhanced version
        logger.info(f"Writing enhanced Categories.yaml to {enhanced_path}")
        with open(enhanced_path, 'w') as f:
            yaml.dump(enhanced_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        
        # Generate summary
        logger.info("Generating enhancement summary...")
        summary = generate_enhancement_summary(enhanced_data, current_data)
        
        summary_path = project_root / "docs" / "CATEGORIES_ENHANCEMENT_SUMMARY.md"
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        logger.info("✅ Categories.yaml enhancement completed successfully")
        logger.info(f"📁 Enhanced version: {enhanced_path}")
        logger.info(f"📁 Original backed up: {backup_path}")
        logger.info(f"📁 Enhancement summary: {summary_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhancement failed: {str(e)}")
        return False

def generate_enhancement_summary(enhanced_data, original_data):
    """Generate summary of enhancements applied"""
    
    summary = f"""# Categories.yaml Enhancement Summary

## Enhancement Overview

Enhanced Categories.yaml from version 1.0.0 to 2.0.0 with additional field categories discovered through comprehensive Materials.yaml analysis.

### Enhancement Date
{enhanced_data['metadata']['generated_date']}

### New Field Categories Added
- **Industry Applications** - Industry tags and regulatory standards
- **Electrical Properties** - Electrical characteristics and insulation properties  
- **Processing Parameters** - Operating temperatures and thermal processing data
- **Chemical Properties** - Material composition and chemical characteristics

## Category-by-Category Enhancements

"""

    for category_name, category_data in enhanced_data['categories'].items():
        summary += f"### {category_name.title()} Category\n\n"
        
        # Count enhancements
        enhancements = []
        if 'industryApplications' in category_data:
            industries = len(category_data['industryApplications'].get('common_industries', []))
            standards = len(category_data['industryApplications'].get('regulatory_standards', []))
            enhancements.append(f"Industry Applications: {industries} industries, {standards} standards")
        
        if 'electricalProperties' in category_data:
            props = len(category_data['electricalProperties'])
            enhancements.append(f"Electrical Properties: {props} properties")
        
        if 'processingParameters' in category_data:
            params = len(category_data['processingParameters'])
            enhancements.append(f"Processing Parameters: {params} parameters")
        
        if 'chemicalProperties' in category_data:
            chem_props = len(category_data['chemicalProperties'])
            enhancements.append(f"Chemical Properties: {chem_props} properties")
        
        if enhancements:
            for enhancement in enhancements:
                summary += f"- {enhancement}\n"
        else:
            summary += "- No additional data available for enhancement\n"
        
        summary += "\n"
    
    summary += """## Usage

The enhanced Categories.yaml provides comprehensive material characterization data for:

1. **Industry Guidance** - Direct application recommendations and compliance standards
2. **Electrical Safety** - Insulation and conductivity properties for laser safety
3. **Processing Optimization** - Temperature limits and thermal processing parameters  
4. **Material Selection** - Chemical composition and property-based selection criteria

## File Locations

- **Enhanced Version**: `data/Categories.yaml`
- **Original Backup**: `data/Categories_backup_before_enhancement.yaml`  
- **Source Data**: `data/Materials.yaml`

## Next Steps

1. Validate enhanced data against Materials.yaml source
2. Consider replacing original Categories.yaml with enhanced version
3. Update schema validation to include new field categories
4. Test integration with existing components
"""

    return summary

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)