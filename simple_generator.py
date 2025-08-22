#!/usr/bin/env python3
"""
Z-Beam Content Generator - Simple Architecture

CORE PURPOSE:
- Load materials from lists/materials.yaml
- Generate components using prompts from components/*/prompt.yaml  
- Validate generated content against schemas/
- Save valid content to content/ folder

SIMPLE ARCHITECTURE:
1. MaterialLoader - loads materials list
2. ComponentGenerator - generates content using AI + prompts
3. ContentValidator - validates against schemas
4. ContentWriter - saves to content/ folder
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Import our standardized API client
from api_client import create_deepseek_client, APIResponse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Material:
    """Simple material data structure."""
    name: str
    category: str
    

@dataclass
class GeneratedComponent:
    """Structure for generated component content."""
    material: Material
    component_type: str
    content: str
    is_valid: bool = False


class MaterialLoader:
    """Loads materials from the materials list."""
    
    def __init__(self, materials_file: str = "lists/materials.yaml"):
        self.materials_file = Path(materials_file)
    
    def load_materials(self) -> List[Material]:
        """Load all materials from the YAML file."""
        logger.info(f"Loading materials from {self.materials_file}")
        
        with open(self.materials_file) as f:
            data = yaml.safe_load(f)
        
        materials = []
        for category, category_data in data["materials"].items():
            for material_name in category_data["items"]:
                materials.append(Material(name=material_name, category=category))
        
        logger.info(f"Loaded {len(materials)} materials across {len(data['materials'])} categories")
        return materials


class ComponentPromptLoader:
    """Loads component prompts from the legacy prompt files."""
    
    def __init__(self, components_dir: str = "components"):
        self.components_dir = Path(components_dir)
    
    def load_prompt(self, component_type: str) -> Optional[Dict]:
        """Load prompt for a specific component type."""
        prompt_file = self.components_dir / component_type / "prompt.yaml"
        
        if not prompt_file.exists():
            logger.warning(f"Prompt file not found: {prompt_file}")
            return None
        
        with open(prompt_file) as f:
            return yaml.safe_load(f)
    
    def list_available_components(self) -> List[str]:
        """List all available component types."""
        components = []
        for component_dir in self.components_dir.iterdir():
            if component_dir.is_dir() and (component_dir / "prompt.yaml").exists():
                components.append(component_dir.name)
        return components


class SchemaValidator:
    """Validates content against JSON schemas."""
    
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all schemas into memory."""
        for schema_file in self.schemas_dir.glob("*.json"):
            with open(schema_file) as f:
                self.schemas[schema_file.stem] = json.load(f)
        
        logger.info(f"Loaded {len(self.schemas)} schemas")
    
    def validate_frontmatter(self, frontmatter: Dict) -> bool:
        """Validate frontmatter against material schema."""
        # Simple validation - check required fields exist
        required_fields = ["name", "category", "description"]
        
        for field in required_fields:
            if field not in frontmatter:
                logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def validate_component(self, component: GeneratedComponent) -> bool:
        """Validate a generated component."""
        if component.component_type == "frontmatter":
            try:
                # Parse YAML frontmatter
                content = component.content.strip()
                if content.startswith("---") and content.count("---") >= 2:
                    yaml_content = content.split("---")[1]
                    frontmatter = yaml.safe_load(yaml_content)
                    return self.validate_frontmatter(frontmatter)
            except Exception as e:
                logger.error(f"Failed to parse frontmatter: {e}")
                return False
        
        # For other components, basic validation
        return len(component.content.strip()) > 10


class ContentWriter:
    """Writes validated content to the content folder."""
    
    def __init__(self, content_dir: str = "content"):
        self.content_dir = Path(content_dir)
        self.content_dir.mkdir(exist_ok=True)
    
    def write_component(self, component: GeneratedComponent) -> bool:
        """Write a validated component to disk with automatic post-processing and validation."""
        if not component.is_valid:
            logger.error(f"Cannot write invalid component: {component.material.name}/{component.component_type}")
            return False
        
        # Create material directory structure
        material_slug = component.material.name.lower().replace(" ", "-")
        component_dir = self.content_dir / "components" / component.component_type
        component_dir.mkdir(parents=True, exist_ok=True)
        
        # Write content file
        filename = f"{material_slug}-laser-cleaning.md"
        filepath = component_dir / filename
        
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
        
        logger.info(f"Wrote component: {filepath}")
        return True


class SimpleGenerator:
    """Simple, clean generator that ties everything together."""
    
    def __init__(self):
        # Setup environment
        load_dotenv()
        
        # Initialize components
        self.material_loader = MaterialLoader()
        self.prompt_loader = ComponentPromptLoader()
        self.validator = SchemaValidator()
        self.writer = ContentWriter()
        
        # Initialize API client
        self.api_client = create_deepseek_client()
        logger.info("✅ Initialized API client")
    
    def generate_for_material(self, material: Material, component_type: str) -> Optional[GeneratedComponent]:
        """Generate a single component for a material."""
        logger.info(f"Generating {component_type} for {material.name}")
        
        # Load prompt
        prompt_data = self.prompt_loader.load_prompt(component_type)
        if not prompt_data:
            return None
        
        # Generate content using API
        content = self._generate_content_with_api(material, component_type, prompt_data)
        if not content:
            return None
        
        # Create component
        component = GeneratedComponent(
            material=material,
            component_type=component_type,
            content=content
        )
        
        # Validate
        component.is_valid = self.validator.validate_component(component)
        
        return component
    
    def _generate_content_with_api(self, material: Material, component_type: str, prompt_data: dict) -> Optional[str]:
        """Generate content using the DeepSeek API."""
        try:
            # Extract template from prompt data
            template = prompt_data.get("template", "")
            if not template:
                logger.error(f"No template found in prompt for {component_type}")
                return None
            
            # Create a comprehensive substitution dictionary with safe defaults
            substitutions = {
                "subject": material.name,
                "category": material.category,
                "article_type": "material",
                "material_formula": f"{material.name} formula",
                "material_symbol": material.name[:2].upper(),
                "material_type": "compound",
                "subject_slug": material.name.lower().replace(" ", "-"),
                "min_words": 800,
                "max_words": 1200,
                "schema": "Material schema context",
                # Additional common variables
                "formatted_title": f"Laser Cleaning {material.name} - Technical Guide",
                "formatted_headline": f"Comprehensive technical guide for laser cleaning {material.name}",
                "formatted_description": f"Technical overview of {material.name} for laser cleaning applications",
                "formatted_keywords": f"{material.name.lower()}, laser cleaning, {material.category}",
                "formatted_technical_specs": "Technical specifications context",
                "formatted_environmental_impact": "Environmental impact context",
                "min_tags": 5,
                "count": "---"  # For template compatibility
            }
            
            # Safely substitute variables, ignoring missing ones
            try:
                formatted_prompt = template.format(**substitutions)
            except KeyError as e:
                # If there are still missing variables, try partial formatting
                logger.warning(f"Missing template variable {e} for {component_type}, attempting partial substitution")
                import string
                formatter = string.Formatter()
                formatted_prompt = formatter.vformat(template, (), substitutions)
            
            # System prompt for technical accuracy
            system_prompt = (
                "You are a technical expert in laser cleaning and materials science. "
                "Generate accurate, professional content for industrial laser cleaning applications. "
                "Focus on technical precision and real-world applications. "
                "Output clean markdown content without any markdown code block wrapping."
            )
            
            # Make API call
            response = self.api_client.generate(formatted_prompt, system_prompt)
            
            if response.success:
                logger.info(f"✅ Generated {len(response.content)} chars in {response.response_time:.2f}s")
                return response.content
            else:
                logger.error(f"❌ API generation failed: {response.error_message}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating content: {e}")
            return None
    
    def _create_mock_content(self, material: Material, component_type: str, prompt_data: dict) -> str:
        """Create mock content for testing (fallback only)."""
        logger.warning(f"Using mock content for {material.name}/{component_type}")
        
        if component_type == "frontmatter":
            return f"""---
name: {material.name}
category: {material.category}
description: Technical overview of {material.name} for laser cleaning applications
author: Dr. Technical Expert
keywords: [{material.name.lower()}, laser cleaning, {material.category}]
---"""
        else:
            return f"# {material.name} {component_type.title()}\n\nMock content for {material.name} {component_type}."
    
    def generate_all_for_material(self, material: Material) -> Dict[str, GeneratedComponent]:
        """Generate all components for a material."""
        components = {}
        available_types = self.prompt_loader.list_available_components()
        
        for component_type in available_types:
            component = self.generate_for_material(material, component_type)
            if component:
                components[component_type] = component
        
        return components
    
    def run(self, limit: Optional[int] = None):
        """Run the generator for all materials."""
        logger.info("Starting Z-Beam content generation")
        
        # Load materials
        materials = self.material_loader.load_materials()
        
        if limit:
            materials = materials[:limit]
            logger.info(f"Limited to first {limit} materials")
        
        # Generate content
        for material in materials:
            logger.info(f"Processing material: {material.name} ({material.category})")
            
            components = self.generate_all_for_material(material)
            
            # Write valid components
            for component in components.values():
                if component.is_valid:
                    self.writer.write_component(component)
                else:
                    logger.warning(f"Invalid component: {material.name}/{component.component_type}")


if __name__ == "__main__":
    # Simple test run
    generator = SimpleGenerator()
    
    # Test API connection first
    test_result = generator.api_client.test_connection()
    if not test_result.success:
        logger.error(f"❌ API connection failed: {test_result.error_message}")
        exit(1)
    
    logger.info("✅ API connection verified, starting generation...")
    generator.run(limit=1)  # Test with 1 material first
