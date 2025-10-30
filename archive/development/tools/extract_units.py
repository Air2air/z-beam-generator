#!/usr/bin/env python3
"""
Units Extraction Tool for Categories.yaml

This script separates units from values in Categories.yaml, creating a cleaner
structure where units are stored in separate keys.

Usage:
    python3 scripts/tools/extract_units.py
"""

import re
import yaml
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_unit_from_value(value_str):
    """Extract unit from a value string like '15.7 g/cm³' -> (15.7, 'g/cm³')"""
    if not isinstance(value_str, str):
        return value_str, None
    
    # Handle special cases
    if value_str in ['melting', 'decomposition', 'sublimation']:
        return value_str, None
    
    # Regular expression to separate number from unit
    # Matches: optional negative, number (int or float), space, unit
    pattern = r'^(-?\d+(?:\.\d+)?)\s*(.+)$'
    match = re.match(pattern, str(value_str).strip())
    
    if match:
        number_str, unit = match.groups()
        try:
            # Try to convert to float, then to int if it's a whole number
            number = float(number_str)
            if number.is_integer():
                number = int(number)
            return number, unit.strip()
        except ValueError:
            # If conversion fails, return original
            return value_str, None
    
    # If no match, return original
    return value_str, None

def process_property_range(prop_data):
    """Process a property range dictionary to extract units"""
    if not isinstance(prop_data, dict):
        return prop_data
    
    processed = {}
    units_found = set()
    
    for key, value in prop_data.items():
        if key in ['max', 'min', 'typical', 'value']:
            number, unit = extract_unit_from_value(value)
            processed[key] = number
            if unit:
                units_found.add(unit)
        else:
            processed[key] = value
    
    # Add unit key if we found consistent units
    if len(units_found) == 1:
        processed['unit'] = list(units_found)[0]
    elif len(units_found) > 1:
        logger.warning(f"Inconsistent units found: {units_found}")
        # Keep the first unit found
        processed['unit'] = list(units_found)[0]
    
    return processed

def process_category_ranges(category_ranges):
    """Process all property ranges in a category"""
    if not isinstance(category_ranges, dict):
        return category_ranges
    
    processed = {}
    for prop_name, prop_data in category_ranges.items():
        processed[prop_name] = process_property_range(prop_data)
    
    return processed

def process_categories_yaml(data):
    """Process the entire Categories.yaml structure"""
    if 'categories' not in data:
        logger.error("No 'categories' section found in data")
        return data
    
    processed_data = data.copy()
    
    for category_name, category_data in data['categories'].items():
        logger.info(f"Processing category: {category_name}")
        
        processed_category = category_data.copy()
        
        # Process category_ranges
        if 'category_ranges' in category_data:
            processed_category['category_ranges'] = process_category_ranges(
                category_data['category_ranges']
            )
        
        # Process subcategories if they exist
        if 'subcategories' in category_data and isinstance(category_data['subcategories'], dict):
            processed_subcategories = {}
            
            for subcat_name, subcat_data in category_data['subcategories'].items():
                processed_subcat = subcat_data.copy()
                
                # Process materialProperties
                if 'materialProperties' in subcat_data:
                    processed_subcat['materialProperties'] = process_category_ranges(
                        subcat_data['materialProperties']
                    )
                
                # Process machineSettings
                if 'machineSettings' in subcat_data:
                    processed_subcat['machineSettings'] = process_category_ranges(
                        subcat_data['machineSettings']
                    )
                
                processed_subcategories[subcat_name] = processed_subcat
            
            processed_category['subcategories'] = processed_subcategories
        
        processed_data['categories'][category_name] = processed_category
    
    return processed_data

def main():
    """Main function to process Categories.yaml"""
    project_root = Path(__file__).parent.parent.parent
    categories_path = project_root / "data" / "Categories.yaml"
    backup_path = project_root / "data" / "Categories_backup.yaml"
    
    if not categories_path.exists():
        logger.error(f"Categories.yaml not found at {categories_path}")
        return False
    
    try:
        # Load current Categories.yaml
        logger.info(f"Loading Categories.yaml from {categories_path}")
        with open(categories_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Create backup
        logger.info(f"Creating backup at {backup_path}")
        with open(backup_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        
        # Process the data
        logger.info("Processing Categories.yaml to extract units")
        processed_data = process_categories_yaml(data)
        
        # Write processed data back
        logger.info("Writing processed Categories.yaml")
        with open(categories_path, 'w') as f:
            yaml.dump(processed_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        
        logger.info("✅ Units extraction completed successfully")
        logger.info(f"📁 Original backed up to: {backup_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Units extraction failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)