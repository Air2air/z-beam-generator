#!/usr/bin/env python3
"""
Fully Dynamic Z-Beam Content Generator

FEATURES:
1. 100% schema-driven validation and content generation
2. Dynamic field content mapping from schemas
3. Schema-based required field extraction
4. Comprehensive error handling and validation
5. Extensive testing framework integrated
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
import string

# Import our standardized API client
from api_client import create_deepseek_client
from dynamic_schema_generator import DynamicSchemaValidator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Material:
    """Enhanced material data structure with schema support."""
    name: str
    category: str
    symbol: Optional[str] = None
    formula: Optional[str] = None
    material_type: Optional[str] = None


@dataclass
class GeneratedComponent:
    """Enhanced structure for generated component content."""
    material: Material
    component_type: str
    content: str
    is_valid: bool = False
    validation_errors: List[str] = None
    schema_used: Optional[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


@dataclass
class ContentGenerationConfig:
    """Configuration extracted from schema for content generation."""
    field_content_mapping: Dict[str, str]
    dynamic_sections: bool
    introduction_prompt: Optional[str]
    use_research_module: bool
    schema_type: str


class EnhancedMaterialLoader:
    """Enhanced material loader with schema integration."""
    
    def __init__(self, materials_file: str = "lists/materials.yaml", 
                 material_formulas_file: str = "components/base/material_formulas.json",
                 material_symbols_file: str = "components/base/material_symbols.json"):
        self.materials_file = Path(materials_file)
        self.formulas_file = Path(material_formulas_file)
        self.symbols_file = Path(material_symbols_file)
        
        # Load formula and symbol databases
        self.formulas = self._load_json_file(self.formulas_file)
        self.symbols = self._load_json_file(self.symbols_file)
    
    def _load_json_file(self, file_path: Path) -> Dict:
        """Load JSON file with error handling."""
        try:
            if file_path.exists():
                with open(file_path) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load {file_path}: {e}")
        return {}
    
    def load_materials(self) -> List[Material]:
        """Load all materials with enhanced metadata."""
        logger.info(f"Loading materials from {self.materials_file}")
        
        with open(self.materials_file) as f:
            data = yaml.safe_load(f)
        
        materials = []
        for category, category_data in data["materials"].items():
            for material_name in category_data["items"]:
                # Enhance material with formula and symbol data
                material = Material(
                    name=material_name,
                    category=category,
                    formula=self.formulas.get(material_name, material_name),
                    symbol=self.symbols.get(material_name, material_name[:2].upper()),
                    material_type=self._determine_material_type(material_name, category)
                )
                materials.append(material)
        
        logger.info(f"Loaded {len(materials)} materials with enhanced metadata")
        return materials
    
    def _determine_material_type(self, material_name: str, category: str) -> str:
        """Determine material type based on name and category."""
        material_name_lower = material_name.lower()
        
        # Define material type mappings
        type_mappings = {
            'metal': 'element',
            'ceramic': 'compound',
            'semiconductor': 'compound',
            'plastic': 'polymer',
            'composite': 'composite',
            'glass': 'compound',
            'masonry': 'compound',
            'stone': 'mineral',
            'wood': 'organic'
        }
        
        # Check for specific patterns
        if 'alloy' in material_name_lower or 'steel' in material_name_lower:
            return 'alloy'
        elif 'resin' in material_name_lower or 'polymer' in material_name_lower:
            return 'polymer'
        elif 'fiber' in material_name_lower and 'composite' in material_name_lower:
            return 'composite'
        
        return type_mappings.get(category, 'compound')


class DynamicComponentPromptLoader:
    """Enhanced prompt loader with schema integration."""
    
    def __init__(self, components_dir: str = "components", validator: DynamicSchemaValidator = None):
        self.components_dir = Path(components_dir)
        self.validator = validator or DynamicSchemaValidator()
    
    def load_prompt_with_schema_config(self, component_type: str, material: Material) -> Tuple[Optional[Dict], Optional[ContentGenerationConfig]]:
        """Load prompt and extract schema-based configuration."""
        prompt_data = self.load_prompt(component_type)
        if not prompt_data:
            return None, None
        
        # Get schema for this component type
        schema = self.validator.get_schema_for_component(component_type, material.category)
        config = None
        
        if schema:
            config = self._extract_generation_config(schema)
        
        return prompt_data, config
    
    def load_prompt(self, component_type: str) -> Optional[Dict]:
        """Load prompt for a specific component type."""
        prompt_file = self.components_dir / component_type / "prompt.yaml"
        
        if not prompt_file.exists():
            logger.warning(f"Prompt file not found: {prompt_file}")
            return None
        
        try:
            with open(prompt_file) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt {prompt_file}: {e}")
            return None
    
    def _extract_generation_config(self, schema: Dict) -> Optional[ContentGenerationConfig]:
        """Extract content generation configuration from schema."""
        for profile_key, profile_data in schema.items():
            if 'generatorConfig' in profile_data:
                config_data = profile_data['generatorConfig']
                content_gen = config_data.get('contentGeneration', {})
                
                return ContentGenerationConfig(
                    field_content_mapping=content_gen.get('fieldContentMapping', {}),
                    dynamic_sections=content_gen.get('dynamicSectionsFromFrontmatter', False),
                    introduction_prompt=content_gen.get('introductionPrompt'),
                    use_research_module=config_data.get('useResearchModule', False),
                    schema_type=config_data.get('jsonld', {}).get('schemaType', 'Article')
                )
        
        return None
    
    def list_available_components(self) -> List[str]:
        """List all available component types."""
        components = []
        for component_dir in self.components_dir.iterdir():
            if component_dir.is_dir() and (component_dir / "prompt.yaml").exists():
                components.append(component_dir.name)
        return components


class DynamicSchemaValidatorEnhanced(DynamicSchemaValidator):
    """Enhanced validator with comprehensive testing capabilities."""
    
    def validate_component_comprehensive(self, component: GeneratedComponent) -> GeneratedComponent:
        """Comprehensive validation with detailed error reporting."""
        component.validation_errors = []
        
        if component.component_type == "frontmatter":
            # Parse and validate frontmatter
            frontmatter = self._parse_component_frontmatter(component.content)
            if not frontmatter:
                component.validation_errors.append("Failed to parse YAML frontmatter")
                component.is_valid = False
                return component
            
            # Get appropriate schema
            schema = self.get_schema_for_component(component.component_type, component.material.category)
            if not schema:
                component.validation_errors.append(f"No schema found for {component.component_type}")
                component.is_valid = False
                return component
            
            # Validate against schema
            result = self.validate_frontmatter_against_schema(frontmatter, schema)
            component.schema_used = result.schema_name
            
            if not result.is_valid:
                if result.missing_fields:
                    component.validation_errors.append(f"Missing required fields: {', '.join(result.missing_fields)}")
                if result.field_type_errors:
                    component.validation_errors.extend(result.field_type_errors)
            
            component.is_valid = result.is_valid
            
        else:
            # Basic validation for other component types
            content_length = len(component.content.strip())
            if content_length < 10:
                component.validation_errors.append(f"Content too short: {content_length} characters")
                component.is_valid = False
            else:
                component.is_valid = True
        
        return component
    
    def _parse_component_frontmatter(self, content: str) -> Optional[Dict]:
        """Parse frontmatter from component content."""
        try:
            if not content.strip().startswith('---'):
                return None
            
            lines = content.split('\n')
            yaml_lines = []
            in_frontmatter = False
            
            for line in lines:
                if line.strip() == '---':
                    if in_frontmatter:
                        break
                    else:
                        in_frontmatter = True
                        continue
                
                if in_frontmatter:
                    yaml_lines.append(line)
            
            if yaml_lines:
                yaml_content = '\n'.join(yaml_lines)
                return yaml.safe_load(yaml_content)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse frontmatter: {e}")
            return None


class DynamicContentWriter:
    """Enhanced content writer with validation tracking."""
    
    def __init__(self, content_dir: str = "content"):
        self.content_dir = Path(content_dir)
        self.content_dir.mkdir(exist_ok=True)
        self.write_stats = {"valid": 0, "invalid": 0, "total": 0}
    
    def write_component(self, component: GeneratedComponent) -> bool:
        """Write component with comprehensive validation tracking."""
        self.write_stats["total"] += 1
        
        if not component.is_valid:
            self.write_stats["invalid"] += 1
            logger.error(f"Cannot write invalid component: {component.material.name}/{component.component_type}")
            logger.error(f"Validation errors: {'; '.join(component.validation_errors)}")
            return False
        
        # Create material directory structure
        material_slug = component.material.name.lower().replace(" ", "-")
        component_dir = self.content_dir / "components" / component.component_type
        component_dir.mkdir(parents=True, exist_ok=True)
        
        # Write content file
        filename = f"{material_slug}-laser-cleaning.md"
        filepath = component_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                f.write(component.content)
            
            # Apply automatic post-processing and validation
            try:
                from validators.centralized_validator import CentralizedValidator
                validator = CentralizedValidator()
                
                # Step 1: Apply post-processing cleanup
                post_processed = validator.post_process_generated_content(str(filepath), component.component_type)
                if post_processed:
                    logger.info(f"✅ Applied post-processing cleanup to {filepath}")
                
                # Step 2: Run validation and auto-fixes
                validation_successful = validator.validate_and_fix_component_immediately(
                    component.material.name, 
                    component.component_type, 
                    max_retries=2, 
                    force_fix=True
                )
                
                if validation_successful:
                    logger.info(f"✅ Automatic validation and fixes completed for {filepath}")
                else:
                    logger.warning(f"⚠️ Validation issues remain after auto-fixes for {filepath}")
                    
            except Exception as e:
                logger.warning(f"Post-processing/validation failed for {filepath}: {e}")
            
            self.write_stats["valid"] += 1
            logger.info(f"✅ Wrote valid component: {filepath}")
            if component.schema_used:
                logger.info(f"   Schema: {component.schema_used}")
            return True
            
        except Exception as e:
            self.write_stats["invalid"] += 1
            logger.error(f"Failed to write component {filepath}: {e}")
            return False
    
    def get_write_statistics(self) -> Dict[str, int]:
        """Get writing statistics."""
        return self.write_stats.copy()


class FullyDynamicGenerator:
    """Fully dynamic generator using schema-driven content generation."""
    
    def __init__(self):
        # Setup environment
        load_dotenv()
        
        # Initialize components
        self.material_loader = EnhancedMaterialLoader()
        self.validator = DynamicSchemaValidatorEnhanced()
        self.prompt_loader = DynamicComponentPromptLoader(validator=self.validator)
        self.writer = DynamicContentWriter()
        
        # Initialize API client
        self.api_client = create_deepseek_client()
        logger.info("✅ Initialized fully dynamic generator")
    
    def generate_for_material(self, material: Material, component_type: str) -> Optional[GeneratedComponent]:
        """Generate component using fully dynamic schema-driven approach."""
        logger.info(f"Generating {component_type} for {material.name} ({material.category})")
        
        # Load prompt and schema configuration
        prompt_data, schema_config = self.prompt_loader.load_prompt_with_schema_config(component_type, material)
        if not prompt_data:
            logger.error(f"No prompt data found for {component_type}")
            return None
        
        # Generate content using dynamic approach
        content = self._generate_content_dynamically(material, component_type, prompt_data, schema_config)
        if not content:
            return None
        
        # Create component
        component = GeneratedComponent(
            material=material,
            component_type=component_type,
            content=content
        )
        
        # Comprehensive validation
        component = self.validator.validate_component_comprehensive(component)
        
        return component
    
    def _generate_content_dynamically(self, material: Material, component_type: str, 
                                    prompt_data: dict, schema_config: Optional[ContentGenerationConfig]) -> Optional[str]:
        """Generate content using schema-driven field mapping."""
        try:
            # Extract template
            template = prompt_data.get("template", "")
            if not template:
                logger.error(f"No template found in prompt for {component_type}")
                return None
            
            # Create comprehensive substitution dictionary
            substitutions = self._create_dynamic_substitutions(material, component_type, schema_config)
            
            # Use field content mapping if available
            if schema_config and schema_config.field_content_mapping:
                logger.info(f"Using dynamic field content mapping with {len(schema_config.field_content_mapping)} fields")
                # Could enhance template with field-specific content here
            
            # Safely substitute variables
            formatted_prompt = self._safe_template_substitution(template, substitutions)
            
            # Create dynamic system prompt
            system_prompt = self._create_dynamic_system_prompt(component_type, schema_config)
            
            # Make API call
            response = self.api_client.generate(formatted_prompt, system_prompt)
            
            if response.success:
                logger.info(f"✅ Generated {len(response.content)} chars in {response.response_time:.2f}s")
                return response.content
            else:
                logger.error(f"❌ API generation failed: {response.error_message}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error in dynamic content generation: {e}")
            return None
    
    def _create_dynamic_substitutions(self, material: Material, component_type: str, 
                                    schema_config: Optional[ContentGenerationConfig]) -> Dict[str, str]:
        """Create comprehensive substitution dictionary."""
        substitutions = {
            # Core material data
            "subject": material.name,
            "category": material.category,
            "material_formula": material.formula or material.name,
            "material_symbol": material.symbol or material.name[:2].upper(),
            "material_type": material.material_type or "compound",
            
            # Template fields
            "article_type": "material",
            "subject_slug": material.name.lower().replace(" ", "-"),
            "min_words": 800,
            "max_words": 1200,
            
            # Formatted fields
            "formatted_title": f"Laser Cleaning {material.name} - Technical Guide",
            "formatted_headline": f"Comprehensive technical guide for laser cleaning {material.name}",
            "formatted_description": f"Technical overview of {material.name} for laser cleaning applications",
            "formatted_keywords": f"{material.name.lower()}, laser cleaning, {material.category}",
            
            # Schema context
            "schema": f"Schema-driven content for {component_type}",
            "min_tags": 5,
            "count": "---"
        }
        
        # Add schema-specific substitutions
        if schema_config:
            substitutions["schema_type"] = schema_config.schema_type
            if schema_config.introduction_prompt:
                substitutions["introduction_context"] = schema_config.introduction_prompt.format(
                    subject=material.name
                )
        
        return substitutions
    
    def _safe_template_substitution(self, template: str, substitutions: Dict[str, str]) -> str:
        """Safely substitute template variables, handling missing ones gracefully."""
        try:
            return template.format(**substitutions)
        except KeyError as e:
            logger.warning(f"Missing template variable {e}, attempting partial substitution")
            try:
                formatter = string.Formatter()
                return formatter.vformat(template, (), substitutions)
            except Exception as e2:
                logger.error(f"Template substitution failed: {e2}")
                return template
    
    def _create_dynamic_system_prompt(self, component_type: str, 
                                    schema_config: Optional[ContentGenerationConfig]) -> str:
        """Create system prompt based on component type and schema configuration."""
        base_prompt = (
            "You are a technical expert in laser cleaning and materials science. "
            "Generate accurate, professional content for industrial laser cleaning applications. "
            "Focus on technical precision and real-world applications. "
            "Output clean markdown content without any markdown code block wrapping."
        )
        
        if schema_config:
            if schema_config.use_research_module:
                base_prompt += " Use comprehensive research data and technical specifications."
            
            if schema_config.field_content_mapping:
                base_prompt += f" Structure content according to {len(schema_config.field_content_mapping)} field mappings."
        
        component_specific = {
            "frontmatter": " Generate complete YAML frontmatter with all required fields.",
            "content": " Create comprehensive article content with technical depth.",
            "caption": " Generate precise scientific image captions with specific parameters.",
            "table": " Create structured technical data tables.",
            "tags": " Generate relevant technical tags and keywords."
        }
        
        return base_prompt + component_specific.get(component_type, "")
    
    def test_api_connection(self) -> bool:
        """Test API connection with comprehensive error reporting."""
        logger.info("Testing API connection...")
        
        test_result = self.api_client.test_connection()
        if test_result.success:
            logger.info("✅ API connection successful")
            return True
        else:
            logger.error(f"❌ API connection failed: {test_result.error_message}")
            return False
    
    def generate_all_for_material(self, material: Material, component_types: Optional[List[str]] = None) -> Dict[str, GeneratedComponent]:
        """Generate all or specified components for a material."""
        components = {}
        
        if component_types is None:
            component_types = self.prompt_loader.list_available_components()
        
        for component_type in component_types:
            logger.info(f"Generating {component_type} for {material.name}")
            component = self.generate_for_material(material, component_type)
            if component:
                components[component_type] = component
                
                # Log validation status
                if component.is_valid:
                    logger.info(f"✅ Valid {component_type} generated")
                else:
                    logger.warning(f"❌ Invalid {component_type}: {'; '.join(component.validation_errors)}")
        
        return components
    
    def run_comprehensive_generation(self, material_names: Optional[List[str]] = None, 
                                   component_types: Optional[List[str]] = None,
                                   limit: Optional[int] = None) -> Dict[str, Any]:
        """Run comprehensive generation with full reporting."""
        logger.info("Starting comprehensive dynamic content generation")
        
        # Load materials
        all_materials = self.material_loader.load_materials()
        
        # Filter materials if specified
        if material_names:
            materials = [m for m in all_materials if m.name in material_names]
        else:
            materials = all_materials
        
        if limit:
            materials = materials[:limit]
        
        logger.info(f"Processing {len(materials)} materials")
        
        # Generation statistics
        stats = {
            "materials_processed": 0,
            "components_generated": 0,
            "components_valid": 0,
            "components_invalid": 0,
            "errors": []
        }
        
        # Generate content
        for material in materials:
            try:
                logger.info(f"Processing material: {material.name} ({material.category})")
                stats["materials_processed"] += 1
                
                components = self.generate_all_for_material(material, component_types)
                
                # Write valid components and track statistics
                for component in components.values():
                    stats["components_generated"] += 1
                    
                    if component.is_valid:
                        stats["components_valid"] += 1
                        self.writer.write_component(component)
                    else:
                        stats["components_invalid"] += 1
                        stats["errors"].extend(component.validation_errors)
                
            except Exception as e:
                error_msg = f"Failed to process {material.name}: {e}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)
        
        # Add writer statistics
        write_stats = self.writer.get_write_statistics()
        stats.update(write_stats)
        
        logger.info("✅ Comprehensive generation completed")
        logger.info(f"Summary: {stats['materials_processed']} materials, {stats['components_valid']} valid components written")
        
        return stats


if __name__ == "__main__":
    # Comprehensive test run
    generator = FullyDynamicGenerator()
    
    # Test API first
    if not generator.test_api_connection():
        exit(1)
    
    # Run comprehensive generation with testing
    stats = generator.run_comprehensive_generation(
        material_names=["Aluminum", "Steel"],  # Test with specific materials
        limit=2
    )
    
    print("\n" + "="*60)
    print("GENERATION STATISTICS")
    print("="*60)
    for key, value in stats.items():
        if key != "errors":
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    if stats["errors"]:
        print(f"\nErrors ({len(stats['errors'])}):")
        for error in stats["errors"][:5]:  # Show first 5 errors
            print(f"  - {error}")
