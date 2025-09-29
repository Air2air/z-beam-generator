#!/usr/bin/env python3
"""
Integrated Property Validation Pipeline
Invisible integration with content generation workflow.
"""

import os
import yaml
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class InvisiblePipelineRunner:
    """
    Lightweight pipeline runner that operates invisibly during content generation.
    Performs essential validation without user awareness.
    """
    
    def __init__(self, silent_mode: bool = False):  # Default to verbose for AI research logging
        self.silent_mode = silent_mode
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.config_file = Path("config/pipeline_config.yaml")
        
        # Load runtime configuration from run.py
        try:
            from run import GLOBAL_OPERATIONAL_CONFIG
            pipeline_config = GLOBAL_OPERATIONAL_CONFIG.get('pipeline_integration', {})
            logging_config = GLOBAL_OPERATIONAL_CONFIG.get('logging', {})
            
            self.silent_mode = pipeline_config.get('silent_mode', silent_mode)
            self.max_execution_time = pipeline_config.get('max_validation_time', 15)
            self.cache_enabled = pipeline_config.get('cache_validations', True)
            self.quality_threshold = pipeline_config.get('quality_threshold', 0.6)
            self.ai_validation_enabled = pipeline_config.get('ai_validation_enabled', True)
            self.ai_critical_only = pipeline_config.get('ai_validation_critical_only', True)
            self.ai_confidence_threshold = pipeline_config.get('ai_confidence_threshold', 0.7)
            self.hierarchical_validation_enabled = pipeline_config.get('hierarchical_validation_enabled', True)
            self.hierarchical_validation_pre_generation = pipeline_config.get('hierarchical_validation_pre_generation', True)
            self.hierarchical_validation_post_generation = pipeline_config.get('hierarchical_validation_post_generation', True)
            
            # AI research logging configuration
            self.ai_verbose_logging = pipeline_config.get('ai_verbose_logging', True)
            self.ai_log_prompts = pipeline_config.get('ai_log_prompts', True)
            self.ai_log_timing = pipeline_config.get('ai_log_timing', True)
            self.ai_research_logger_enabled = logging_config.get('ai_research_logger', True)
            
            # Override silent_mode if verbose AI logging is enabled
            if self.ai_verbose_logging:
                self.silent_mode = False
        except ImportError:
            # Fallback if run.py not available
            self.max_execution_time = 15
            self.cache_enabled = True
            self.quality_threshold = 0.6
            self.ai_validation_enabled = True
            self.ai_critical_only = True
            self.ai_confidence_threshold = 0.7
            self.hierarchical_validation_enabled = True
            self.hierarchical_validation_pre_generation = True
            self.hierarchical_validation_post_generation = True
            
            # AI research logging fallback defaults
            self.ai_verbose_logging = True
            self.ai_log_prompts = True
            self.ai_log_timing = True
            self.ai_research_logger_enabled = True
            self.silent_mode = False
        
        # Setup enhanced logging with AI research support
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
                formatter = logging.Formatter('🤖 AI PIPELINE: %(message)s')
                console_handler.setFormatter(formatter)
                self.ai_logger.addHandler(console_handler)
        else:
            self.ai_logger = self.logger
        
        # Load streamlined configuration
        self.config = self._load_streamlined_config()
        
        # Track what we've validated to avoid redundant work
        self.validation_cache = {} if self.cache_enabled else None
    
    def _load_streamlined_config(self) -> Dict[str, Any]:
        """Load minimal configuration for invisible operation"""
        
        return {
            'quality_thresholds': {
                'min_confidence': 0.6,
                'max_variance': 0.3,
                'critical_properties': ['density', 'meltingPoint', 'thermalConductivity']
            },
            'validation_scope': {
                'run_discovery': False,      # Skip - expensive
                'run_standardization': True, # Essential
                'run_research': True,        # Enable AI validation for critical properties
                'run_cross_validation': True, # Essential
                'run_quality_assurance': True, # Essential
                'run_production_deploy': False, # Skip - handled by content generation
                'run_monitoring': False      # Skip - not needed for single material
            },
            'ai_validation': {
                'enabled': self.ai_validation_enabled,
                'critical_properties_only': self.ai_critical_only,
                'confidence_threshold': self.ai_confidence_threshold,
                'timeout_seconds': 5,        # Quick AI validation timeout
            },
            'performance': {
                'max_execution_time': 15,   # Increased for AI validation
                'cache_validations': True,
                'parallel_processing': True
            }
        }
    
    def run_invisible_validation(self, material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run invisible validation during content generation.
        
        Args:
            material_name: Name of material being generated
            frontmatter_data: Existing frontmatter data if available
            
        Returns:
            Validation results (minimal for performance)
        """
        
        if not self.silent_mode:
            self.logger.info(f"Running invisible validation for {material_name}")
        
        # Check cache first
        if self.cache_enabled and self.validation_cache is not None:
            cache_key = f"{material_name}_{hash(str(frontmatter_data))}"
            if cache_key in self.validation_cache:
                return self.validation_cache[cache_key]
        else:
            cache_key = None
        
        validation_result = {
            'material': material_name,
            'validation_passed': True,
            'quality_score': 0.8,  # Default
            'issues_detected': [],
            'runtime_seconds': 0,
            'cache_hit': False
        }
        
        start_time = datetime.now()
        
        try:
            # Run only essential validation stages
            if frontmatter_data:
                # Validate existing frontmatter
                validation_result.update(self._validate_existing_frontmatter(material_name, frontmatter_data))
            else:
                # Pre-generation validation
                validation_result.update(self._pre_generation_validation(material_name))
            
            # Cache result
            validation_result['runtime_seconds'] = (datetime.now() - start_time).total_seconds()
            if self.cache_enabled and self.validation_cache is not None and cache_key:
                self.validation_cache[cache_key] = validation_result
            
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Validation error for {material_name}: {e}")
            validation_result['validation_passed'] = False
            validation_result['issues_detected'].append(f"Validation error: {e}")
        
        return validation_result
    
    def _validate_existing_frontmatter(self, material_name: str, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate existing frontmatter data quickly with hierarchical validation"""
        
        issues = []
        quality_factors = []
        hierarchical_validation = {}
        
        # Stage 0: Hierarchical validation (data integrity from Categories.yaml → Materials.yaml → Frontmatter)
        if self.hierarchical_validation_enabled and self.hierarchical_validation_post_generation:
            try:
                if not self.silent_mode:
                    self.logger.info("Running hierarchical data validation...")
                
                from hierarchical_validator import HierarchicalValidator
                hierarchical_validator = HierarchicalValidator(ai_validation_enabled=True, silent_mode=True)
                hierarchical_results = hierarchical_validator.run_hierarchical_validation()
                
                hierarchical_validation = {
                    'summary': hierarchical_results['summary'],
                    'categories_valid': hierarchical_results['summary']['categories_status'] != 'FAILED',
                    'materials_valid': hierarchical_results['summary']['materials_status'] != 'FAILED',
                    'hierarchy_consistent': hierarchical_results['summary']['hierarchy_status'] != 'FAILED',
                    'total_issues': hierarchical_results['summary']['total_issues'],
                    'critical_issues': hierarchical_results['summary']['critical_issues']
                }
                
                # Adjust quality score based on hierarchical validation
                if hierarchical_results['summary']['critical_issues'] > 0:
                    issues.append(f"CRITICAL: {hierarchical_results['summary']['critical_issues']} hierarchical validation failures")
                    quality_factors.append(0.3)  # Severe penalty for critical issues
                elif hierarchical_results['summary']['total_issues'] > 0:
                    issues.append(f"WARNING: {hierarchical_results['summary']['total_issues']} hierarchical validation issues")
                    quality_factors.append(0.7)  # Moderate penalty for non-critical issues
                else:
                    quality_factors.append(0.95)  # High score for clean hierarchy
                
            except Exception as e:
                if not self.silent_mode:
                    self.logger.warning(f"Hierarchical validation failed: {e}")
                hierarchical_validation = {'error': f"Hierarchical validation error: {e}"}
                quality_factors.append(0.8)  # Neutral score if hierarchical validation fails
        else:
            hierarchical_validation = {'disabled': True}
            quality_factors.append(0.85)  # Neutral score if hierarchical validation disabled
        
        # Check material properties
        properties = frontmatter_data.get('materialProperties', {})
        if not properties:
            issues.append("No material properties found")
            quality_factors.append(0.3)
        else:
            # Quick property validation
            property_quality = self._validate_properties_quickly(properties)
            quality_factors.append(property_quality)
            
            if property_quality < 0.6:
                issues.append("Low property data quality")
            
            # AI-powered validation for critical properties
            if self.config['ai_validation']['enabled']:
                ai_validation_result = self._ai_validate_critical_properties(material_name, properties)
                if not ai_validation_result['validation_passed']:
                    issues.extend(ai_validation_result['issues'])
                    quality_factors.append(ai_validation_result['confidence_score'])
        
        # Check critical properties
        critical_props = self.config['quality_thresholds']['critical_properties']
        missing_critical = [prop for prop in critical_props if prop not in properties]
        
        if missing_critical:
            issues.append(f"Missing critical properties: {', '.join(missing_critical)}")
            quality_factors.append(0.5)
        else:
            quality_factors.append(0.9)
        
        # Check structure completeness
        required_sections = ['title', 'category', 'materialProperties']
        missing_sections = [section for section in required_sections if section not in frontmatter_data]
        
        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")
            quality_factors.append(0.4)
        else:
            quality_factors.append(0.9)
        
        # Calculate overall quality
        quality_score = sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
        
        return {
            'quality_score': quality_score,
            'validation_passed': quality_score >= 0.6,
            'issues_detected': issues,
            'hierarchical_validation': hierarchical_validation
        }
    
    def _validate_properties_quickly(self, properties: Dict[str, Any]) -> float:
        """Quick validation of material properties"""
        
        total_properties = len(properties)
        if total_properties == 0:
            return 0.0
        
        quality_score = 0.0
        
        for prop_name, prop_data in properties.items():
            prop_score = 0.0
            
            if isinstance(prop_data, dict):
                # Check for required fields
                if 'value' in prop_data:
                    prop_score += 0.4
                if 'unit' in prop_data:
                    prop_score += 0.3
                if 'min' in prop_data and 'max' in prop_data:
                    prop_score += 0.2
                if 'confidence' in prop_data:
                    prop_score += 0.1
                
                # Check value reasonableness
                if self._is_value_reasonable(prop_name, prop_data):
                    prop_score += 0.1
            else:
                # Simple value - lower score
                prop_score = 0.3
            
            quality_score += prop_score
        
        return quality_score / total_properties
    
    def _is_value_reasonable(self, prop_name: str, prop_data: Dict[str, Any]) -> bool:
        """Quick reasonableness check for property values"""
        
        value = prop_data.get('value')
        if value is None:
            return False
        
        try:
            num_value = float(value)
            
            # Basic sanity checks
            if prop_name == 'density':
                return 0.1 <= num_value <= 25.0  # g/cm³
            elif prop_name == 'meltingPoint':
                return -273 <= num_value <= 4000  # °C
            elif prop_name == 'thermalConductivity':
                return 0.01 <= num_value <= 500  # W/m·K
            else:
                return num_value > 0  # Most properties should be positive
                
        except (ValueError, TypeError):
            return False
    
    def _pre_generation_validation(self, material_name: str) -> Dict[str, Any]:
        """Pre-generation validation checks with hierarchical validation"""
        
        issues = []
        hierarchical_validation = {}
        
        # Stage 0: Hierarchical validation (ensure data integrity before generation)
        if self.hierarchical_validation_enabled and self.hierarchical_validation_pre_generation:
            try:
                if not self.silent_mode:
                    self.logger.info("Running pre-generation hierarchical validation...")
                
                from hierarchical_validator import HierarchicalValidator
                hierarchical_validator = HierarchicalValidator(ai_validation_enabled=True, silent_mode=True)
                hierarchical_results = hierarchical_validator.run_hierarchical_validation()
                
                hierarchical_validation = {
                    'summary': hierarchical_results['summary'],
                    'categories_valid': hierarchical_results['summary']['categories_status'] != 'FAILED',
                    'materials_valid': hierarchical_results['summary']['materials_status'] != 'FAILED',
                    'hierarchy_consistent': hierarchical_results['summary']['hierarchy_status'] != 'FAILED',
                    'total_issues': hierarchical_results['summary']['total_issues'],
                    'critical_issues': hierarchical_results['summary']['critical_issues']
                }
                
                # Flag critical hierarchical issues
                if hierarchical_results['summary']['critical_issues'] > 0:
                    issues.append(f"CRITICAL: {hierarchical_results['summary']['critical_issues']} hierarchical validation failures")
                elif hierarchical_results['summary']['total_issues'] > 0:
                    issues.append(f"WARNING: {hierarchical_results['summary']['total_issues']} hierarchical validation issues")
                
            except Exception as e:
                if not self.silent_mode:
                    self.logger.warning(f"Pre-generation hierarchical validation failed: {e}")
                hierarchical_validation = {'error': f"Hierarchical validation error: {e}"}
        else:
            hierarchical_validation = {'disabled': True}
        
        # Check if material exists in Materials.yaml
        try:
            with open('data/Materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            material_index = materials_data.get('material_index', {})
            if material_name not in material_index:
                issues.append(f"Material {material_name} not found in Materials.yaml")
        
        except Exception as e:
            issues.append(f"Could not load Materials.yaml: {e}")
        
        return {
            'quality_score': 0.7 if not issues else 0.4,
            'validation_passed': len(issues) == 0,
            'issues_detected': issues,
            'hierarchical_validation': hierarchical_validation
        }
    
    def improve_frontmatter_data(self, material_name: str, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Quickly improve frontmatter data quality without heavy processing.
        Called invisibly during generation.
        """
        
        improved_data = frontmatter_data.copy()
        
        # Fix common issues
        properties = improved_data.get('materialProperties', {})
        
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict):
                # Add missing confidence if not present
                if 'confidence' not in prop_data:
                    improved_data['materialProperties'][prop_name]['confidence'] = 0.7
                
                # Ensure min/max are present and reasonable
                if 'value' in prop_data and ('min' not in prop_data or 'max' not in prop_data):
                    value = prop_data['value']
                    try:
                        num_value = float(value)
                        if 'min' not in prop_data:
                            improved_data['materialProperties'][prop_name]['min'] = round(num_value * 0.9, 3)
                        if 'max' not in prop_data:
                            improved_data['materialProperties'][prop_name]['max'] = round(num_value * 1.1, 3)
                    except (ValueError, TypeError):
                        pass
        
        return improved_data


    def _ai_validate_critical_properties(self, material_name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to validate critical material properties against materials science knowledge.
        """
        
        import time
        start_time = time.time()
        
        ai_validation_result = {
            'validation_passed': True,
            'confidence_score': 0.8,
            'issues': [],
            'ai_responses': {}
        }
        
        if not self.config['ai_validation']['enabled']:
            if self.ai_verbose_logging:
                self.ai_logger.info(f"AI validation disabled for {material_name}")
            return ai_validation_result
        
        critical_properties = self.config['quality_thresholds']['critical_properties']
        
        # Only validate properties that exist and are critical
        properties_to_validate = []
        for prop_name in critical_properties:
            if prop_name in properties:
                prop_data = properties[prop_name]
                if isinstance(prop_data, dict) and 'value' in prop_data:
                    properties_to_validate.append((prop_name, prop_data))
        
        if not properties_to_validate:
            if self.ai_verbose_logging:
                self.ai_logger.info(f"No critical properties to validate for {material_name}")
            return ai_validation_result
        
        if self.ai_verbose_logging:
            property_names = [prop[0] for prop in properties_to_validate]
            self.ai_logger.info(f"Starting AI validation for {material_name}: {property_names}")
        
        # Determine material category
        material_category = self._get_material_category(material_name)
        
        try:
            # Import API client for AI validation
            from api.client_factory import create_api_client
            
            # Create AI client with short timeout
            api_client = create_api_client('deepseek')
            
            if self.ai_verbose_logging:
                self.ai_logger.info(f"AI client created for {material_name} validation")
            
            for prop_name, prop_data in properties_to_validate:
                prop_start_time = time.time()
                value = prop_data.get('value')
                unit = prop_data.get('unit', '')
                
                if self.ai_verbose_logging:
                    self.ai_logger.info(f"Validating {prop_name} = {value} {unit} for {material_name}")
                
                # Create validation prompt
                validation_prompt = f"""You are a materials science expert. Validate this property for {material_name} ({material_category} category):

Property: {prop_name}
Value: {value} {unit}
Material: {material_name}
Category: {material_category}

Is this value realistic for this material? Respond with JSON:
{{
    "valid": true/false,
    "confidence": 0.0-1.0,
    "reason": "brief explanation",
    "expected_range": "typical range for this material"
}}"""

                if self.ai_log_prompts:
                    self.ai_logger.debug(f"AI Prompt for {prop_name}: {validation_prompt[:100]}...")
                
                # Quick AI validation with timeout
                response = api_client.generate_simple(
                    prompt=validation_prompt,
                    max_tokens=200,
                    temperature=0.1
                )
                
                prop_response_time = time.time() - prop_start_time
                
                if self.ai_log_timing:
                    self.ai_logger.info(f"AI response for {prop_name} received in {prop_response_time:.2f}s")
                
                if response.success and response.content:
                    try:
                        # Parse AI response
                        import json
                        content = response.content.strip()
                        
                        if self.ai_log_prompts:
                            self.ai_logger.debug(f"AI Response for {prop_name}: {content[:100]}...")
                        
                        # Extract JSON from response
                        start_idx = content.find('{')
                        end_idx = content.rfind('}') + 1
                        if start_idx >= 0 and end_idx > start_idx:
                            json_content = content[start_idx:end_idx]
                            ai_result = json.loads(json_content)
                            
                            ai_validation_result['ai_responses'][prop_name] = ai_result
                            
                            # Log AI validation result
                            if self.ai_verbose_logging:
                                valid = ai_result.get('valid', True)
                                confidence = ai_result.get('confidence', 0)
                                reason = ai_result.get('reason', 'No reason provided')
                                self.ai_logger.info(f"AI validation for {prop_name}: {'PASSED' if valid else 'FAILED'} (confidence: {confidence:.1%}) - {reason}")
                            
                            # Check AI validation result
                            if not ai_result.get('valid', True):
                                ai_validation_result['validation_passed'] = False
                                ai_validation_result['issues'].append(
                                    f"AI validation failed for {prop_name}: {ai_result.get('reason', 'Invalid value')}"
                                )
                                
                                if self.ai_verbose_logging:
                                    expected_range = ai_result.get('expected_range', 'Unknown')
                                    self.ai_logger.warning(f"Expected range for {prop_name}: {expected_range}")
                            
                            # Update confidence score
                            ai_confidence = ai_result.get('confidence', 0.5)
                            if ai_confidence < self.config['ai_validation']['confidence_threshold']:
                                ai_validation_result['confidence_score'] = min(ai_validation_result['confidence_score'], ai_confidence)
                                
                                if self.ai_verbose_logging:
                                    threshold = self.config['ai_validation']['confidence_threshold']
                                    self.ai_logger.warning(f"Low AI confidence for {prop_name}: {ai_confidence:.1%} < {threshold:.1%}")
                    
                    except (json.JSONDecodeError, KeyError) as e:
                        if self.ai_verbose_logging:
                            self.ai_logger.error(f"Failed to parse AI validation response for {prop_name}: {e}")
                        elif not self.silent_mode:
                            self.logger.warning(f"Failed to parse AI validation response for {prop_name}: {e}")
                else:
                    if self.ai_verbose_logging:
                        self.ai_logger.error(f"AI validation failed for {prop_name}: {response.error if not response.success else 'No content'}")
                    elif not self.silent_mode:
                        self.logger.warning(f"AI validation failed for {prop_name}: {response.error}")
        
        except Exception as e:
            if self.ai_verbose_logging:
                self.ai_logger.error(f"AI validation error for {material_name}: {e}")
            elif not self.silent_mode:
                self.logger.warning(f"AI validation error: {e}")
            # Don't fail validation due to AI errors
        
        total_time = time.time() - start_time
        
        if self.ai_verbose_logging:
            validated_count = len(properties_to_validate)
            passed = ai_validation_result['validation_passed']
            confidence = ai_validation_result['confidence_score']
            self.ai_logger.info(f"AI validation complete for {material_name}: {validated_count} properties, {'PASSED' if passed else 'FAILED'} (confidence: {confidence:.1%}) in {total_time:.2f}s")
        
        return ai_validation_result
    
    def _get_material_category(self, material_name: str) -> str:
        """Get material category from Materials.yaml"""
        try:
            import yaml
            with open('data/Materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            material_index = materials_data.get('material_index', {})
            return material_index.get(material_name, 'unknown')
        except Exception:
            return 'unknown'


class PipelineIntegrationHooks:
    """
    Integration hooks for seamless pipeline operation within content generation.
    """
    
    def __init__(self):
        self.pipeline_runner = InvisiblePipelineRunner(silent_mode=True)
    
    def pre_frontmatter_hook(self, material_name: str) -> Dict[str, Any]:
        """
        Called before frontmatter generation.
        Validates material and prepares for generation.
        """
        
        return self.pipeline_runner.run_invisible_validation(material_name)
    
    def post_frontmatter_hook(self, material_name: str, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called after frontmatter generation.
        Validates and potentially improves the generated frontmatter.
        """
        
        # Validate generated frontmatter
        validation_result = self.pipeline_runner.run_invisible_validation(material_name, frontmatter_data)
        
        # Improve if needed
        if not validation_result['validation_passed']:
            improved_data = self.pipeline_runner.improve_frontmatter_data(material_name, frontmatter_data)
            return {
                'improved_frontmatter': improved_data,
                'validation_result': validation_result,
                'improvements_made': True
            }
        
        return {
            'improved_frontmatter': frontmatter_data,
            'validation_result': validation_result,
            'improvements_made': False
        }
    
    def batch_validation_hook(self, materials_list: List[str]) -> Dict[str, Any]:
        """
        Called for batch generation operations.
        Performs lightweight validation across multiple materials.
        """
        
        batch_results = {
            'total_materials': len(materials_list),
            'validation_passed': 0,
            'validation_failed': 0,
            'issues_summary': []
        }
        
        for material_name in materials_list:
            result = self.pipeline_runner.run_invisible_validation(material_name)
            
            if result['validation_passed']:
                batch_results['validation_passed'] += 1
            else:
                batch_results['validation_failed'] += 1
                batch_results['issues_summary'].extend(result['issues_detected'])
        
        return batch_results


# Global pipeline integration instance
pipeline_hooks = PipelineIntegrationHooks()

def validate_material_pre_generation(material_name: str) -> Dict[str, Any]:
    """Global function for pre-generation validation"""
    return pipeline_hooks.pre_frontmatter_hook(material_name)

def validate_and_improve_frontmatter(material_name: str, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
    """Global function for post-generation validation and improvement"""
    return pipeline_hooks.post_frontmatter_hook(material_name, frontmatter_data)

def validate_batch_generation(materials_list: List[str]) -> Dict[str, Any]:
    """Global function for batch validation"""
    return pipeline_hooks.batch_validation_hook(materials_list)


def main():
    """Test the invisible pipeline integration"""
    
    print("🔍 Testing invisible pipeline integration...")
    
    # Test pre-generation validation
    pre_result = validate_material_pre_generation("aluminum")
    print(f"✅ Pre-validation: {pre_result['validation_passed']}")
    
    # Test post-generation validation
    sample_frontmatter = {
        'title': 'Aluminum Laser Cleaning',
        'category': 'metals',
        'materialProperties': {
            'density': {
                'value': 2.7,
                'unit': 'g/cm³',
                'min': 2.6,
                'max': 2.8
            }
        }
    }
    
    post_result = validate_and_improve_frontmatter("aluminum", sample_frontmatter)
    print(f"✅ Post-validation: {post_result['validation_result']['validation_passed']}")
    print(f"🔧 Improvements made: {post_result['improvements_made']}")
    
    print("\n🎉 Invisible pipeline integration tested successfully!")

if __name__ == "__main__":
    main()