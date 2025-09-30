#!/usr/bin/env python3
"""
Materials Field Analyzer - Comprehensive field extraction from Materials.yaml

This script analyzes Materials.yaml to identify all category/subcategory-applicable 
fields beyond materialProperties and machineSettings.

Usage:
    python3 scripts/tools/analyze_material_fields.py
"""

import yaml
from pathlib import Path
from collections import defaultdict, Counter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_materials_yaml(materials_path: Path) -> dict:
    """Analyze Materials.yaml to extract all field categories"""
    
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    
    analysis = {
        'category_level_fields': set(),
        'material_item_fields': set(),
        'fields_by_category': defaultdict(lambda: defaultdict(set)),
        'field_frequency': Counter(),
        'field_types': defaultdict(set),
        'categories_found': set(),
        'subcategories_found': set(),
        'total_materials_analyzed': 0
    }
    
    # Analyze category_ranges section
    if 'category_ranges' in data:
        logger.info("Analyzing category_ranges section...")
        for category, ranges in data['category_ranges'].items():
            analysis['categories_found'].add(category)
            analysis['category_level_fields'].update(ranges.keys())
            
            for field_name, field_data in ranges.items():
                analysis['field_frequency'][field_name] += 1
                analysis['fields_by_category'][category]['category_ranges'].add(field_name)
                
                if isinstance(field_data, dict):
                    analysis['field_types'][field_name].add('dict')
                elif isinstance(field_data, str):
                    analysis['field_types'][field_name].add('string')
                else:
                    analysis['field_types'][field_name].add(str(type(field_data).__name__))
    
    # Analyze materials section
    if 'materials' in data:
        logger.info("Analyzing materials section...")
        materials_section = data['materials']
        
        for category_name, category_data in materials_section.items():
            analysis['categories_found'].add(category_name)
            
            if isinstance(category_data, dict) and 'items' in category_data:
                # Category-level fields
                for key, value in category_data.items():
                    if key != 'items':
                        analysis['field_frequency'][key] += 1
                        analysis['fields_by_category'][category_name]['category_meta'].add(key)
                        analysis['field_types'][key].add(str(type(value).__name__))
                
                # Item-level fields
                for item in category_data['items']:
                    analysis['total_materials_analyzed'] += 1
                    
                    for field_name, field_value in item.items():
                        analysis['material_item_fields'].add(field_name)
                        analysis['field_frequency'][field_name] += 1
                        analysis['fields_by_category'][category_name]['item_fields'].add(field_name)
                        
                        if field_name == 'category':
                            analysis['categories_found'].add(field_value)
                        elif field_name == 'subcategory':
                            analysis['subcategories_found'].add(field_value)
                        
                        # Track field types
                        if isinstance(field_value, list):
                            analysis['field_types'][field_name].add('list')
                        elif isinstance(field_value, dict):
                            analysis['field_types'][field_name].add('dict')
                        else:
                            analysis['field_types'][field_name].add(str(type(field_value).__name__))
    
    # Convert sets to lists for JSON serialization
    for key, value in analysis.items():
        if isinstance(value, set):
            analysis[key] = sorted(list(value))
        elif isinstance(value, defaultdict):
            analysis[key] = dict(value)
            for sub_key, sub_value in analysis[key].items():
                if isinstance(sub_value, defaultdict):
                    analysis[key][sub_key] = dict(sub_value)
                    for sub_sub_key, sub_sub_value in analysis[key][sub_key].items():
                        if isinstance(sub_sub_value, set):
                            analysis[key][sub_key][sub_sub_key] = sorted(list(sub_sub_value))
        elif hasattr(value, '__iter__') and not isinstance(value, str):
            try:
                analysis[key] = dict(value) if hasattr(value, 'items') else list(value)
            except Exception:
                pass
    
    return analysis

def categorize_fields(analysis: dict) -> dict:
    """Categorize fields by their potential use in Categories.yaml"""
    
    categorization = {
        'materialProperties_candidates': [],
        'machineSettings_candidates': [],
        'metadata_fields': [],
        'taxonomic_fields': [],
        'industry_regulatory_fields': [],
        'processing_fields': [],
        'physical_test_fields': [],
        'electrical_fields': [],
        'optical_fields': [],
        'uncategorized_fields': []
    }
    
    # Known material property fields
    material_props = {
        'density', 'thermalConductivity', 'meltingPoint', 'melting_point',
        'tensileStrength', 'compressive_strength', 'flexural_strength',
        'youngsModulus', 'hardness', 'thermalExpansion', 'thermalDiffusivity',
        'specificHeat', 'fracture_toughness', 'chemical_resistance',
        'porosity', 'firing_temperature', 'ionic_conductivity'
    }
    
    # Known machine setting fields  
    machine_settings = {
        'laserAbsorption', 'laserReflectivity', 'ablationThreshold',
        'powerRange', 'wavelength', 'spotSize', 'repetitionRate',
        'fluenceThreshold', 'pulseWidth', 'scanSpeed', 'overlapRatio',
        'passCount'
    }
    
    # Other categorizations
    metadata_fields = {
        'author_id', 'article_type', 'description', 'processing_priority',
        'complexity', 'index'
    }
    
    taxonomic_fields = {
        'category', 'subcategory', 'name', 'title'
    }
    
    industry_regulatory = {
        'industryTags', 'regulatoryStandards'
    }
    
    electrical_fields = {
        'dielectric_constant', 'electricalResistivity', 'ionic_conductivity'
    }
    
    optical_fields = {
        'laserAbsorption', 'laserReflectivity', 'reflectivity', 'absorptionCoefficient'
    }
    
    # Categorize each field
    all_fields = analysis['material_item_fields'] + analysis['category_level_fields']
    
    for field in set(all_fields):
        if field in material_props:
            categorization['materialProperties_candidates'].append(field)
        elif field in machine_settings:
            categorization['machineSettings_candidates'].append(field)
        elif field in metadata_fields:
            categorization['metadata_fields'].append(field)
        elif field in taxonomic_fields:
            categorization['taxonomic_fields'].append(field)
        elif field in industry_regulatory:
            categorization['industry_regulatory_fields'].append(field)
        elif field in electrical_fields:
            categorization['electrical_fields'].append(field)
        elif field in optical_fields:
            categorization['optical_fields'].append(field)
        elif 'temperature' in field.lower() or 'thermal' in field.lower():
            categorization['processing_fields'].append(field)
        elif 'strength' in field.lower() or 'modulus' in field.lower():
            categorization['physical_test_fields'].append(field)
        else:
            categorization['uncategorized_fields'].append(field)
    
    # Sort all lists
    for key in categorization:
        categorization[key].sort()
    
    return categorization

def main():
    """Main analysis function"""
    project_root = Path(__file__).parent.parent.parent
    materials_path = project_root / "data" / "Materials.yaml"
    output_path = project_root / "docs" / "MATERIAL_FIELDS_ANALYSIS.md"
    
    if not materials_path.exists():
        logger.error(f"Materials.yaml not found at {materials_path}")
        return False
    
    try:
        # Analyze Materials.yaml
        logger.info("Starting comprehensive field analysis...")
        analysis = analyze_materials_yaml(materials_path)
        
        # Categorize fields
        logger.info("Categorizing fields by potential use...")
        categorization = categorize_fields(analysis)
        
        # Generate report
        logger.info("Generating analysis report...")
        report = generate_report(analysis, categorization)
        
        # Write report
        with open(output_path, 'w') as f:
            f.write(report)
        
        logger.info(f"✅ Analysis complete: {output_path}")
        
        # Print summary
        print_summary(analysis, categorization)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        return False

def generate_report(analysis: dict, categorization: dict) -> str:
    """Generate comprehensive markdown report"""
    
    report = f"""# Materials.yaml Field Analysis Report

## Overview

Comprehensive analysis of all fields in Materials.yaml to identify category/subcategory-applicable fields beyond materialProperties and machineSettings.

### Analysis Summary
- **Total Categories Found**: {len(analysis['categories_found'])}
- **Total Subcategories Found**: {len(analysis['subcategories_found'])} 
- **Total Materials Analyzed**: {analysis['total_materials_analyzed']}
- **Unique Fields Found**: {len(analysis['material_item_fields']) + len(analysis['category_level_fields'])}

## Categories and Subcategories Found

### Categories ({len(analysis['categories_found'])})
{format_list(analysis['categories_found'])}

### Subcategories ({len(analysis['subcategories_found'])})
{format_list(analysis['subcategories_found'])}

## Field Categorization for Categories.yaml

### 🔧 Material Properties Candidates ({len(categorization['materialProperties_candidates'])})
*Fields suitable for materialProperties section*
{format_list_with_frequency(categorization['materialProperties_candidates'], analysis['field_frequency'])}

### ⚙️ Machine Settings Candidates ({len(categorization['machineSettings_candidates'])})
*Fields suitable for machineSettings section*
{format_list_with_frequency(categorization['machineSettings_candidates'], analysis['field_frequency'])}

### 🏭 Industry & Regulatory Fields ({len(categorization['industry_regulatory_fields'])})
*Fields for industry tags and regulatory standards*
{format_list_with_frequency(categorization['industry_regulatory_fields'], analysis['field_frequency'])}

### ⚡ Electrical Properties ({len(categorization['electrical_fields'])})
*Fields for electrical characteristics*
{format_list_with_frequency(categorization['electrical_fields'], analysis['field_frequency'])}

### 💡 Optical Properties ({len(categorization['optical_fields'])})
*Fields for optical/laser interaction properties*
{format_list_with_frequency(categorization['optical_fields'], analysis['field_frequency'])}

### 🔥 Processing Fields ({len(categorization['processing_fields'])})
*Fields for processing conditions and thermal properties*
{format_list_with_frequency(categorization['processing_fields'], analysis['field_frequency'])}

### 🧪 Physical Test Fields ({len(categorization['physical_test_fields'])})
*Fields for mechanical testing results*
{format_list_with_frequency(categorization['physical_test_fields'], analysis['field_frequency'])}

### 📋 Metadata Fields ({len(categorization['metadata_fields'])})
*Fields for content management and organization*
{format_list_with_frequency(categorization['metadata_fields'], analysis['field_frequency'])}

### 🏷️ Taxonomic Fields ({len(categorization['taxonomic_fields'])})
*Fields for material classification*
{format_list_with_frequency(categorization['taxonomic_fields'], analysis['field_frequency'])}

### ❓ Uncategorized Fields ({len(categorization['uncategorized_fields'])})
*Fields requiring further analysis*
{format_list_with_frequency(categorization['uncategorized_fields'], analysis['field_frequency'])}

## Recommended Categories.yaml Extensions

Based on this analysis, the Categories.yaml structure should be extended to include:

### 1. Industry & Applications Section
```yaml
categories:
  metal:
    industry_applications:
      common_industries: [Automotive, Aerospace, Medical, Electronics]
      regulatory_standards: 
        - OSHA 29 CFR 1926.95
        - FDA 21 CFR 1040.10
        - ANSI Z136.1
```

### 2. Electrical Properties Section  
```yaml
categories:
  ceramic:
    electricalProperties:
      dielectric_constant:
        min: 2.0
        max: 25.0
        unit: ""
      electricalResistivity:
        min: 1e10
        max: 1e16
        unit: Ω·cm
```

### 3. Processing Parameters Section
```yaml  
categories:
  ceramic:
    processingParameters:
      firing_temperature:
        min: 1000
        max: 1700
        unit: °C
      porosity:
        min: 0
        max: 15
        unit: '%'
```

## Most Frequent Fields by Category

{generate_category_frequency_table(analysis)}

## Field Type Distribution

{generate_field_type_distribution(analysis)}

## Recommendations

1. **Extend Categories.yaml Schema**: Add sections for industry applications, electrical properties, and processing parameters
2. **Standardize Units**: Many fields have inconsistent unit formats that should be normalized
3. **Add Validation**: Implement validation for field ranges and data types
4. **Consider Subcategory Specificity**: Some fields may benefit from subcategory-specific ranges
5. **Include Regulatory Data**: Industry tags and regulatory standards are valuable for practical applications

## Next Steps

1. Update Categories.yaml schema to include new field categories
2. Research appropriate ranges for electrical and processing properties
3. Create validation rules for new field types
4. Consider AI research for subcategory-specific property refinements
"""

    return report

def format_list(items):
    """Format list for markdown"""
    if not items:
        return "None found"
    return '\n'.join(f"- {item}" for item in sorted(items))

def format_list_with_frequency(items, frequency_dict):
    """Format list with frequency information"""
    if not items:
        return "None found"
    
    items_with_freq = [(item, frequency_dict.get(item, 0)) for item in sorted(items)]
    return '\n'.join(f"- `{item}` (used {freq}x)" for item, freq in items_with_freq)

def generate_category_frequency_table(analysis):
    """Generate frequency table by category"""
    table = "| Category | Unique Fields | Most Common Fields |\n"
    table += "|----------|---------------|--------------------|\n"
    
    for category in sorted(analysis['categories_found']):
        if category in analysis['fields_by_category']:
            fields = analysis['fields_by_category'][category]
            item_fields = fields.get('item_fields', set())
            total_fields = len(item_fields)
            
            # Get top 3 most common fields for this category
            common_fields = []
            for field in sorted(item_fields)[:3]:
                freq = analysis['field_frequency'].get(field, 0)
                common_fields.append(f"{field} ({freq})")
            
            table += f"| {category} | {total_fields} | {', '.join(common_fields)} |\n"
    
    return table

def generate_field_type_distribution(analysis):
    """Generate field type distribution summary"""
    type_summary = "| Field | Types Found | Examples |\n"
    type_summary += "|-------|-------------|----------|\n"
    
    for field, types in sorted(analysis['field_types'].items())[:10]:  # Top 10
        type_list = ', '.join(sorted(types))
        freq = analysis['field_frequency'].get(field, 0)
        type_summary += f"| {field} | {type_list} | Used {freq}x |\n"
    
    return type_summary

def print_summary(analysis, categorization):
    """Print summary to console"""
    print("\\n" + "="*60)
    print("MATERIALS.YAML FIELD ANALYSIS SUMMARY")
    print("="*60)
    print(f"📊 Total Categories: {len(analysis['categories_found'])}")
    print(f"📊 Total Subcategories: {len(analysis['subcategories_found'])}")  
    print(f"📊 Total Materials: {analysis['total_materials_analyzed']}")
    print(f"📊 Unique Fields: {len(set(analysis['material_item_fields'] + analysis['category_level_fields']))}")
    print("\\n🎯 NEW FIELDS FOR CATEGORIES.YAML:")
    print(f"   • Industry/Regulatory: {len(categorization['industry_regulatory_fields'])} fields")
    print(f"   • Electrical Properties: {len(categorization['electrical_fields'])} fields")
    print(f"   • Processing Parameters: {len(categorization['processing_fields'])} fields")
    print(f"   • Physical Test Data: {len(categorization['physical_test_fields'])} fields")
    print("="*60)

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)