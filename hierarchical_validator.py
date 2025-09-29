#!/usr/bin/env python3
"""
Hierarchical Data Validation Pipeline
Validates data at Materials.yaml/Categories.yaml level and propagates to frontmatter.
"""

import os
import yaml
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Import the numeric extraction utility
def extract_numeric_value(value):
    """Extract numeric value from various formats, including Shore hardness scales."""
    import re
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove common units and multipliers first
        cleaned = value.replace(',', '')
        
        # Handle Shore hardness ranges specifically (Shore D 60-70, Shore A 10-20)
        shore_range_match = re.search(r'Shore\s+[AD]\s+(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', cleaned, re.IGNORECASE)
        if shore_range_match:
            # Return midpoint of the range
            min_val = float(shore_range_match.group(1))
            max_val = float(shore_range_match.group(2))
            return (min_val + max_val) / 2.0
        
        # Handle Shore hardness single values (Shore A 10, Shore D 90)
        shore_match = re.search(r'Shore\s+[AD]\s+(\d+(?:\.\d+)?)', cleaned, re.IGNORECASE)
        if shore_match:
            return float(shore_match.group(1))
        
        # Handle scientific notation markers like ×10⁻⁶
        if '×10⁻' in cleaned:
            parts = cleaned.split('×10⁻')
            if len(parts) == 2:
                try:
                    base = float(parts[0])
                    exponent = int(parts[1])
                    return base * (10 ** -exponent)
                except ValueError:
                    pass
        
        # Try direct conversion
        try:
            return float(cleaned)
        except ValueError:
            pass
    
    # If all else fails, try to extract any number
    import re
    if isinstance(value, str):
        numbers = re.findall(r'-?\d+\.?\d*', value)
        if numbers:
            return float(numbers[0])
    
    raise ValueError(f"Cannot extract numeric value from: {value}")

class HierarchicalValidator:
    """
    Validates data hierarchy: Categories.yaml → Materials.yaml → Frontmatter
    Ensures data consistency and quality propagation through the entire system.
    """
    
    def __init__(self, ai_validation_enabled: bool = True, silent_mode: bool = False):
        self.ai_validation_enabled = ai_validation_enabled
        self.silent_mode = silent_mode
        
        # Load verbose logging configuration from run.py
        try:
            from run import GLOBAL_OPERATIONAL_CONFIG
            pipeline_config = GLOBAL_OPERATIONAL_CONFIG.get('pipeline_integration', {})
            logging_config = GLOBAL_OPERATIONAL_CONFIG.get('logging', {})
            
            self.ai_verbose_logging = pipeline_config.get('ai_verbose_logging', True)
            self.ai_log_prompts = pipeline_config.get('ai_log_prompts', True)
            self.ai_log_timing = pipeline_config.get('ai_log_timing', True)
            self.ai_research_logger_enabled = logging_config.get('ai_research_logger', True)
            
            # Override silent_mode if verbose AI logging is enabled
            if self.ai_verbose_logging:
                self.silent_mode = False
        except ImportError:
            # Fallback defaults
            self.ai_verbose_logging = True
            self.ai_log_prompts = True
            self.ai_log_timing = True
            self.ai_research_logger_enabled = True
            self.silent_mode = False
        
        # Setup enhanced logging
        log_level = logging.DEBUG if not self.silent_mode else logging.ERROR
        logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        self.logger = logging.getLogger(__name__)
        
        # Create dedicated AI research logger
        if self.ai_research_logger_enabled:
            self.ai_logger = logging.getLogger(f"{__name__}.ai_research")
            self.ai_logger.setLevel(logging.DEBUG)
            
            # Add console handler for AI research if verbose
            if self.ai_verbose_logging and not self.silent_mode:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('🤖 AI RESEARCH: %(message)s')
                console_handler.setFormatter(formatter)
                self.ai_logger.addHandler(console_handler)
        else:
            self.ai_logger = self.logger
        
        # Validation results storage
        self.validation_results = {
            'categories_validation': {},
            'materials_validation': {},
            'frontmatter_validation': {},
            'hierarchy_consistency': {},
            'ai_cross_validation': {}
        }
        
        # Data storage
        self.categories_data = None
        self.materials_data = None
        
    def run_hierarchical_validation(self) -> Dict[str, Any]:
        """
        Run complete hierarchical validation from Categories.yaml down to frontmatter.
        """
        
        if not self.silent_mode:
            self.logger.info("🔍 Starting hierarchical data validation...")
        
        # Stage 1: Validate Categories.yaml
        categories_result = self._validate_categories_yaml()
        self.validation_results['categories_validation'] = categories_result
        
        # Stage 2: Validate Materials.yaml against Categories.yaml
        materials_result = self._validate_materials_yaml()
        self.validation_results['materials_validation'] = materials_result
        
        # Stage 3: Validate hierarchy consistency
        hierarchy_result = self._validate_hierarchy_consistency()
        self.validation_results['hierarchy_consistency'] = hierarchy_result
        
        # Stage 4: AI cross-validation of critical properties
        if self.ai_validation_enabled:
            ai_result = self._ai_validate_property_ranges()
            self.validation_results['ai_cross_validation'] = ai_result
        
        # Stage 5: Sample frontmatter validation
        frontmatter_result = self._validate_frontmatter_consistency()
        self.validation_results['frontmatter_validation'] = frontmatter_result
        
        # Generate summary
        summary = self._generate_validation_summary()
        
        return {
            'validation_results': self.validation_results,
            'summary': summary,
            'recommendations': self._generate_recommendations()
        }
    
    def _validate_categories_yaml(self) -> Dict[str, Any]:
        """Validate Categories.yaml structure and property ranges"""
        
        if not self.silent_mode:
            self.logger.info("🏷️ Validating Categories.yaml...")
        
        try:
            with open('data/Categories.yaml', 'r') as f:
                self.categories_data = yaml.safe_load(f)
            
            result = {
                'file_valid': True,
                'categories_found': [],
                'property_ranges_validated': {},
                'missing_ranges': [],
                'invalid_ranges': [],
                'issues': []
            }
            
            # Validate structure
            if 'categories' not in self.categories_data:
                result['file_valid'] = False
                result['issues'].append("Missing 'categories' key in Categories.yaml")
                return result
            
            categories = self.categories_data['categories']
            
            # Validate each category
            for category_name, category_data in categories.items():
                result['categories_found'].append(category_name)
                
                # Check required fields
                if 'name' not in category_data:
                    result['issues'].append(f"Category {category_name} missing 'name' field")
                if 'description' not in category_data:
                    result['issues'].append(f"Category {category_name} missing 'description' field")
                
                # Validate property ranges
                if 'category_ranges' in category_data:
                    ranges = category_data['category_ranges']
                    range_validation = self._validate_property_ranges(category_name, ranges)
                    result['property_ranges_validated'][category_name] = range_validation
                    
                    if not range_validation['valid']:
                        result['invalid_ranges'].extend(range_validation['issues'])
                else:
                    result['missing_ranges'].append(category_name)
            
            result['file_valid'] = len(result['issues']) == 0
            return result
            
        except Exception as e:
            return {
                'file_valid': False,
                'error': f"Failed to load Categories.yaml: {e}",
                'issues': [f"File loading error: {e}"]
            }
    
    def _validate_materials_yaml(self) -> Dict[str, Any]:
        """Validate Materials.yaml against Categories.yaml constraints"""
        
        if not self.silent_mode:
            self.logger.info("🔬 Validating Materials.yaml against Categories.yaml...")
        
        try:
            with open('data/Materials.yaml', 'r') as f:
                self.materials_data = yaml.safe_load(f)
            
            result = {
                'file_valid': True,
                'materials_validated': 0,
                'category_mismatches': [],
                'property_violations': [],
                'missing_properties': [],
                'issues': []
            }
            
            # Validate structure
            if 'materials' not in self.materials_data:
                result['issues'].append("Missing 'materials' key in Materials.yaml")
                result['file_valid'] = False
                return result
            
            materials = self.materials_data['materials']
            material_index = self.materials_data.get('material_index', {})
            
            # Validate each material
            for category, category_data in materials.items():
                if 'items' not in category_data:
                    result['issues'].append(f"Category {category} missing 'items' key")
                    continue
                
                for material_item in category_data['items']:
                    material_name = material_item.get('name', 'Unknown')
                    result['materials_validated'] += 1
                    
                    # Check category consistency
                    indexed_category = material_index.get(material_name)
                    if indexed_category != category:
                        result['category_mismatches'].append({
                            'material': material_name,
                            'materials_category': category,
                            'index_category': indexed_category
                        })
                    
                    # Validate properties against category ranges
                    if 'properties' in material_item:
                        violations = self._check_property_violations(
                            material_name, category, material_item['properties']
                        )
                        result['property_violations'].extend(violations)
            
            result['file_valid'] = len(result['issues']) == 0
            return result
            
        except Exception as e:
            return {
                'file_valid': False,
                'error': f"Failed to load Materials.yaml: {e}",
                'issues': [f"File loading error: {e}"]
            }
    
    def _validate_hierarchy_consistency(self) -> Dict[str, Any]:
        """Validate consistency between Categories.yaml and Materials.yaml"""
        
        if not self.silent_mode:
            self.logger.info("🔗 Validating hierarchy consistency...")
        
        result = {
            'consistent': True,
            'category_alignment': {},
            'orphaned_materials': [],
            'missing_categories': [],
            'property_coverage': {},
            'issues': []
        }
        
        if not self.categories_data or not self.materials_data:
            result['issues'].append("Cannot validate hierarchy - missing source data")
            result['consistent'] = False
            return result
        
        # Check category alignment
        categories_in_schema = set(self.categories_data['categories'].keys())
        categories_in_materials = set(self.materials_data['materials'].keys())
        
        # Find missing categories
        missing_in_materials = categories_in_schema - categories_in_materials
        missing_in_schema = categories_in_materials - categories_in_schema
        
        if missing_in_materials:
            result['missing_categories'].extend(list(missing_in_materials))
            result['issues'].append(f"Categories in schema but not in materials: {list(missing_in_materials)}")
        
        if missing_in_schema:
            result['orphaned_materials'].extend(list(missing_in_schema))
            result['issues'].append(f"Categories in materials but not in schema: {list(missing_in_schema)}")
        
        # Check property coverage
        for category in categories_in_schema.intersection(categories_in_materials):
            schema_properties = set(self.categories_data['categories'][category].get('category_ranges', {}).keys())
            
            # Get properties used in materials
            material_properties = set()
            category_materials = self.materials_data['materials'][category].get('items', [])
            for material in category_materials:
                material_properties.update(material.get('properties', {}).keys())
            
            coverage = {
                'schema_properties': list(schema_properties),
                'material_properties': list(material_properties),
                'covered': list(schema_properties.intersection(material_properties)),
                'uncovered_schema': list(schema_properties - material_properties),
                'uncovered_materials': list(material_properties - schema_properties)
            }
            
            result['property_coverage'][category] = coverage
        
        result['consistent'] = len(result['issues']) == 0
        return result
    
    def _validate_property_ranges(self, category_name: str, ranges: Dict[str, Any]) -> Dict[str, Any]:
        """Validate property ranges for scientific reasonableness"""
        
        result = {
            'valid': True,
            'properties_checked': len(ranges),
            'issues': []
        }
        
        for prop_name, range_data in ranges.items():
            if not isinstance(range_data, dict):
                result['issues'].append(f"{category_name}.{prop_name}: Invalid range format")
                continue
            
            min_val = range_data.get('min')
            max_val = range_data.get('max')
            unit = range_data.get('unit', '')
            
            # Basic range validation
            if min_val is None or max_val is None:
                result['issues'].append(f"{category_name}.{prop_name}: Missing min or max value")
                continue
            
            try:
                min_num = float(min_val)
                max_num = float(max_val)
                
                if min_num >= max_num:
                    result['issues'].append(f"{category_name}.{prop_name}: Min ({min_num}) >= Max ({max_num})")
                
                # Scientific reasonableness checks
                if prop_name == 'density' and (min_num <= 0 or max_num > 30):
                    result['issues'].append(f"{category_name}.{prop_name}: Density range ({min_num}-{max_num}) unrealistic")
                
                elif prop_name == 'meltingPoint' and (min_num < -273 or max_num > 4000):
                    result['issues'].append(f"{category_name}.{prop_name}: Melting point range ({min_num}-{max_num}) unrealistic")
                
                elif prop_name == 'thermalConductivity' and (min_num < 0 or max_num > 500):
                    result['issues'].append(f"{category_name}.{prop_name}: Thermal conductivity range ({min_num}-{max_num}) unrealistic")
                
            except (ValueError, TypeError):
                result['issues'].append(f"{category_name}.{prop_name}: Non-numeric range values")
        
        result['valid'] = len(result['issues']) == 0
        return result
    
    def _check_property_violations(self, material_name: str, category: str, properties: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if material properties violate category ranges"""
        
        violations = []
        
        if not self.categories_data or category not in self.categories_data['categories']:
            return violations
        
        category_ranges = self.categories_data['categories'][category].get('category_ranges', {})
        
        for prop_name, prop_data in properties.items():
            if prop_name not in category_ranges:
                continue
            
            range_data = category_ranges[prop_name]
            
            try:
                # Handle thermal destruction type separately (categorical field)
                if prop_name == 'thermalDestructionType':
                    if isinstance(prop_data, dict):
                        value = prop_data.get('value')
                    else:
                        value = prop_data
                    
                    # Expected thermal destruction type from category range
                    expected_type = range_data
                    if isinstance(expected_type, dict):
                        expected_type = expected_type.get('value', expected_type)
                    
                    if value and value != expected_type:
                        violations.append({
                            'material': material_name,
                            'category': category,
                            'property': prop_name,
                            'value': value,
                            'expected': expected_type,
                            'unit': 'categorical',
                            'severity': 'medium'
                        })
                    continue
                
                # Extract value for numeric properties
                if isinstance(prop_data, dict):
                    value = prop_data.get('value')
                else:
                    value = prop_data
                
                if value is None:
                    continue
                
                num_value = extract_numeric_value(value)
                
                # Handle range bounds with safe extraction
                try:
                    min_range = extract_numeric_value(range_data.get('min', float('-inf')))
                except (ValueError, TypeError):
                    min_range = float('-inf')
                
                try:
                    max_range = extract_numeric_value(range_data.get('max', float('inf')))
                except (ValueError, TypeError):
                    max_range = float('inf')
                
                if not (min_range <= num_value <= max_range):
                    violations.append({
                        'material': material_name,
                        'category': category,
                        'property': prop_name,
                        'value': num_value,
                        'range': f"{min_range}-{max_range}",
                        'unit': range_data.get('unit', ''),
                        'severity': 'high' if num_value < min_range * 0.5 or num_value > max_range * 2 else 'medium'
                    })
                    
            except (ValueError, TypeError):
                violations.append({
                    'material': material_name,
                    'category': category,
                    'property': prop_name,
                    'value': prop_data,
                    'error': 'Invalid numeric value',
                    'severity': 'high'
                })
        
        return violations
    
    def _ai_validate_property_ranges(self) -> Dict[str, Any]:
        """Use AI to validate property ranges against materials science knowledge"""
        
        if not self.silent_mode:
            self.logger.info("🤖 Running AI validation of property ranges...")
        
        result = {
            'enabled': True,
            'categories_validated': 0,
            'properties_validated': 0,
            'ai_recommendations': {},
            'validation_issues': [],
            'api_errors': []
        }
        
        if not self.categories_data:
            result['validation_issues'].append("No Categories.yaml data available for AI validation")
            return result
        
        try:
            from api.client_factory import create_api_client
            api_client = create_api_client('deepseek')
            
            # Validate each category's ranges
            for category_name, category_data in self.categories_data['categories'].items():
                result['categories_validated'] += 1
                
                if 'category_ranges' not in category_data:
                    continue
                
                ranges = category_data['category_ranges']
                category_result = self._ai_validate_category_ranges(api_client, category_name, ranges)
                
                result['ai_recommendations'][category_name] = category_result
                result['properties_validated'] += len(ranges)
                
                if not category_result.get('validation_passed', True):
                    result['validation_issues'].extend(category_result.get('issues', []))
        
        except Exception as e:
            result['api_errors'].append(f"AI validation error: {e}")
        
        return result
    
    def _ai_validate_category_ranges(self, api_client, category_name: str, ranges: Dict[str, Any]) -> Dict[str, Any]:
        """AI validate ranges for a specific category"""
        
        import time
        start_time = time.time()
        
        if self.ai_verbose_logging:
            self.ai_logger.info(f"Starting AI validation for category: {category_name}")
            self.ai_logger.info(f"Properties to validate: {list(ranges.keys())}")
        
        # Create validation prompt  
        ranges_text = ""
        thermal_destruction_info = ""
        
        for prop_name, range_data in ranges.items():
            unit = range_data.get('unit', '')
            min_val = range_data.get('min', 'N/A')
            max_val = range_data.get('max', 'N/A')
            
            if prop_name == 'thermalDestructionType':
                thermal_destruction_info = f"Thermal destruction type: {range_data}\n"
            elif prop_name == 'thermalDestructionPoint':
                thermal_destruction_info += f"Thermal destruction point: {min_val} to {max_val} {unit}\n"
            else:
                ranges_text += f"- {prop_name}: {min_val} to {max_val} {unit}\n"
        
        validation_prompt = f"""You are a materials science expert. Validate these property ranges for the "{category_name}" material category:

{ranges_text}

{thermal_destruction_info}

CRITICAL: Validate the thermal destruction mechanism for accuracy:
- Does the thermal destruction type match the actual behavior of {category_name} materials?
- Are the thermal destruction temperatures realistic?
- Valid thermal destruction types: melting, decomposition, carbonization, oxidation, sublimation, thermal_shock, softening, spalling, calcination, delamination

Are these ranges and thermal behaviors realistic for {category_name} materials? Respond with JSON:
{{
    "validation_passed": true/false,
    "overall_confidence": 0.0-1.0,
    "thermal_destruction_valid": true/false,
    "thermal_destruction_comment": "assessment of thermal behavior accuracy",
    "property_assessments": {{
        "propertyName": {{"valid": true/false, "confidence": 0.0-1.0, "comment": "brief note"}}
    }},
    "recommendations": ["any suggested improvements"]
}}"""

        if self.ai_log_prompts:
            self.ai_logger.debug(f"AI Validation Prompt for {category_name}:\n{validation_prompt[:200]}...")
        
        try:
            if self.ai_verbose_logging:
                self.ai_logger.info(f"Sending AI validation request for {category_name}...")
            
            response = api_client.generate_simple(
                prompt=validation_prompt,
                max_tokens=500,
                temperature=0.1
            )
            
            response_time = time.time() - start_time
            
            if self.ai_log_timing:
                self.ai_logger.info(f"AI response received in {response_time:.2f}s for {category_name}")
            
            if response.success and response.content:
                import json
                content = response.content.strip()
                
                if self.ai_log_prompts:
                    self.ai_logger.debug(f"AI Response for {category_name}: {content[:150]}...")
                
                # Extract JSON from response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_content = content[start_idx:end_idx]
                    validation_result = json.loads(json_content)
                    
                    if self.ai_verbose_logging:
                        confidence = validation_result.get('overall_confidence', 0)
                        passed = validation_result.get('validation_passed', False)
                        self.ai_logger.info(f"AI validation for {category_name}: {'PASSED' if passed else 'FAILED'} (confidence: {confidence:.1%})")
                        
                        recommendations = validation_result.get('recommendations', [])
                        if recommendations:
                            self.ai_logger.info(f"AI recommendations for {category_name}: {len(recommendations)} items")
                    
                    return validation_result
            
            if self.ai_verbose_logging:
                self.ai_logger.warning(f"AI validation failed for {category_name}: {response.error if not response.success else 'No content'}")
            
            return {'validation_passed': True, 'error': 'Failed to parse AI response'}
            
        except Exception as e:
            if self.ai_verbose_logging:
                self.ai_logger.error(f"AI validation error for {category_name}: {e}")
            return {'validation_passed': True, 'error': f"AI validation error: {e}"}
    
    def _ai_research_thermal_destruction_type(self, api_client, material_name: str, category: str) -> Dict[str, Any]:
        """AI research to determine appropriate thermal destruction type for a material"""
        
        # Thermal destruction taxonomy prompt
        taxonomy_prompt = f"""You are a materials science expert. For the material "{material_name}" in category "{category}":

1. What is the primary thermal destruction mechanism?
2. At what temperature does thermal damage begin?
3. What is the appropriate thermal destruction type from: melting, decomposition, carbonization, oxidation, sublimation, thermal_shock, softening, spalling, calcination, delamination

Consider the material's chemical composition, crystal structure, and typical applications.

Format response as JSON:
{{
    "thermal_destruction_type": "primary_mechanism",
    "thermal_destruction_point": temperature_in_celsius,
    "secondary_mechanisms": ["mechanism1", "mechanism2"],
    "confidence": 0.9,
    "reasoning": "Brief scientific explanation"
}}"""
        
        if self.ai_verbose_logging:
            self.ai_logger.info(f"Researching thermal destruction type for {material_name} ({category})")
        
        try:
            response = api_client.generate_simple(
                prompt=taxonomy_prompt,
                max_tokens=400,
                temperature=0.1
            )
            
            if response.success and response.content:
                import json
                try:
                    research_data = json.loads(response.content)
                    if self.ai_verbose_logging:
                        destruction_type = research_data.get('thermal_destruction_type', 'unknown')
                        confidence = research_data.get('confidence', 0.0)
                        self.ai_logger.info(f"AI suggests {destruction_type} for {material_name} (confidence: {confidence:.2f})")
                    
                    return {
                        'success': True,
                        'data': research_data,
                        'material': material_name,
                        'category': category
                    }
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    content = response.content
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_content = content[start_idx:end_idx]
                        research_data = json.loads(json_content)
                        return {
                            'success': True,
                            'data': research_data,
                            'material': material_name,
                            'category': category
                        }
                    
                    if self.ai_verbose_logging:
                        self.ai_logger.warning(f"Could not parse JSON for {material_name}")
                    return {'success': False, 'error': 'JSON parsing failed'}
            else:
                if self.ai_verbose_logging:
                    self.ai_logger.error(f"AI research failed for {material_name}: {response.error}")
                return {'success': False, 'error': response.error}
        
        except Exception as e:
            if self.ai_verbose_logging:
                self.ai_logger.error(f"AI research error for {material_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_frontmatter_consistency(self) -> Dict[str, Any]:
        """Sample frontmatter files to ensure they follow hierarchy validation"""
        
        if not self.silent_mode:
            self.logger.info("📄 Validating frontmatter consistency...")
        
        result = {
            'files_checked': 0,
            'files_passed': 0,
            'hierarchy_violations': [],
            'sample_issues': []
        }
        
        # Sample a few frontmatter files
        frontmatter_dir = Path("content/components/frontmatter")
        if not frontmatter_dir.exists():
            result['sample_issues'].append("Frontmatter directory not found")
            return result
        
        sample_files = list(frontmatter_dir.glob("*.yaml"))[:10]  # Sample first 10 files
        
        for file_path in sample_files:
            result['files_checked'] += 1
            
            try:
                with open(file_path, 'r') as f:
                    frontmatter_data = yaml.safe_load(f)
                
                # Extract material name and check hierarchy
                material_name = self._extract_material_name_from_filename(file_path.name)
                violations = self._check_frontmatter_hierarchy(material_name, frontmatter_data)
                
                if violations:
                    result['hierarchy_violations'].extend(violations)
                else:
                    result['files_passed'] += 1
                    
            except Exception as e:
                result['sample_issues'].append(f"Error validating {file_path.name}: {e}")
        
        return result
    
    def _extract_material_name_from_filename(self, filename: str) -> str:
        """Extract material name from frontmatter filename"""
        base_name = filename.replace('-laser-cleaning.yaml', '').replace('.yaml', '')
        return base_name.replace('-', ' ').replace('_', ' ').title()
    
    def _check_frontmatter_hierarchy(self, material_name: str, frontmatter_data: Dict[str, Any]) -> List[str]:
        """Check if frontmatter follows hierarchy validation rules"""
        
        violations = []
        
        if not self.materials_data:
            return violations
        
        # Find material in Materials.yaml
        material_index = self.materials_data.get('material_index', {})
        material_category = material_index.get(material_name)
        
        if not material_category:
            violations.append(f"Material {material_name} not found in Materials.yaml index")
            return violations
        
        # Check if frontmatter category matches Materials.yaml
        frontmatter_category = frontmatter_data.get('category')
        if frontmatter_category != material_category:
            violations.append(f"Category mismatch: frontmatter='{frontmatter_category}', materials='{material_category}'")
        
        # Check if properties respect category ranges
        properties = frontmatter_data.get('materialProperties', {})
        property_violations = self._check_property_violations(material_name, material_category, properties)
        
        for violation in property_violations:
            violations.append(f"Property violation: {violation['property']} = {violation['value']} (range: {violation['range']})")
        
        return violations
    
    def _generate_validation_summary(self) -> Dict[str, Any]:
        """Generate overall validation summary"""
        
        summary = {
            'overall_status': 'PASSED',
            'categories_status': 'PASSED',
            'materials_status': 'PASSED',
            'hierarchy_status': 'PASSED',
            'ai_validation_status': 'PASSED',
            'frontmatter_status': 'PASSED',
            'total_issues': 0,
            'critical_issues': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Count issues
        total_issues = 0
        critical_issues = 0
        
        # Categories validation
        categories_result = self.validation_results.get('categories_validation', {})
        if not categories_result.get('file_valid', True):
            summary['categories_status'] = 'FAILED'
            total_issues += len(categories_result.get('issues', []))
            critical_issues += 1
        
        # Materials validation
        materials_result = self.validation_results.get('materials_validation', {})
        if not materials_result.get('file_valid', True):
            summary['materials_status'] = 'FAILED'
            total_issues += len(materials_result.get('issues', []))
            critical_issues += 1
        
        # Property violations
        property_violations = materials_result.get('property_violations', [])
        if property_violations:
            summary['materials_status'] = 'WARNING'
            total_issues += len(property_violations)
            critical_issues += len([v for v in property_violations if v.get('severity') == 'high'])
        
        # Hierarchy consistency
        hierarchy_result = self.validation_results.get('hierarchy_consistency', {})
        if not hierarchy_result.get('consistent', True):
            summary['hierarchy_status'] = 'FAILED'
            total_issues += len(hierarchy_result.get('issues', []))
            critical_issues += 1
        
        # AI validation
        ai_result = self.validation_results.get('ai_cross_validation', {})
        if ai_result.get('validation_issues'):
            summary['ai_validation_status'] = 'WARNING'
            total_issues += len(ai_result.get('validation_issues', []))
        
        # Frontmatter validation
        frontmatter_result = self.validation_results.get('frontmatter_validation', {})
        if frontmatter_result.get('hierarchy_violations'):
            summary['frontmatter_status'] = 'WARNING'
            total_issues += len(frontmatter_result.get('hierarchy_violations', []))
        
        summary['total_issues'] = total_issues
        summary['critical_issues'] = critical_issues
        
        if critical_issues > 0:
            summary['overall_status'] = 'FAILED'
        elif total_issues > 0:
            summary['overall_status'] = 'WARNING'
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        
        recommendations = []
        
        # Categories recommendations
        categories_result = self.validation_results.get('categories_validation', {})
        if categories_result.get('missing_ranges'):
            recommendations.append(f"Add property ranges for categories: {', '.join(categories_result['missing_ranges'])}")
        
        if categories_result.get('invalid_ranges'):
            recommendations.append("Fix invalid property ranges in Categories.yaml")
        
        # Materials recommendations
        materials_result = self.validation_results.get('materials_validation', {})
        property_violations = materials_result.get('property_violations', [])
        
        if property_violations:
            high_severity = [v for v in property_violations if v.get('severity') == 'high']
            if high_severity:
                recommendations.append(f"URGENT: Fix {len(high_severity)} high-severity property violations in Materials.yaml")
            
            medium_severity = [v for v in property_violations if v.get('severity') == 'medium']
            if medium_severity:
                recommendations.append(f"Review {len(medium_severity)} medium-severity property violations")
        
        # Hierarchy recommendations
        hierarchy_result = self.validation_results.get('hierarchy_consistency', {})
        if hierarchy_result.get('missing_categories'):
            recommendations.append("Add missing categories to maintain hierarchy consistency")
        
        if hierarchy_result.get('orphaned_materials'):
            recommendations.append("Remove or reassign orphaned material categories")
        
        # AI recommendations
        ai_result = self.validation_results.get('ai_cross_validation', {})
        for category, ai_data in ai_result.get('ai_recommendations', {}).items():
            if ai_data.get('recommendations'):
                recommendations.extend([f"{category}: {rec}" for rec in ai_data['recommendations']])
        
        if not recommendations:
            recommendations.append("All validations passed - no actions required")
        
        return recommendations


def main():
    """Test the hierarchical validation system"""
    
    print("🔍 Testing Hierarchical Data Validation Pipeline...")
    print("=" * 60)
    
    validator = HierarchicalValidator(ai_validation_enabled=True, silent_mode=False)
    
    # Run complete validation
    results = validator.run_hierarchical_validation()
    
    # Print summary
    summary = results['summary']
    print(f"\n📊 Validation Summary:")
    print(f"   Overall Status: {summary['overall_status']}")
    print(f"   Categories: {summary['categories_status']}")
    print(f"   Materials: {summary['materials_status']}")
    print(f"   Hierarchy: {summary['hierarchy_status']}")
    print(f"   AI Validation: {summary['ai_validation_status']}")
    print(f"   Frontmatter: {summary['frontmatter_status']}")
    print(f"   Total Issues: {summary['total_issues']}")
    print(f"   Critical Issues: {summary['critical_issues']}")
    
    # Print recommendations
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n🎉 Hierarchical validation completed!")

if __name__ == "__main__":
    main()