#!/usr/bin/env python3
"""
Dynamic Schema-Driven Generator for Z-Beam

This module provides dynamic content generation based on JSON schemas,
allowing for flexible field-driven content creation with component selection.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GenerationRequest:
    """Request for content generation"""
    material: str
    components: List[str]
    article_type: str = "material"
    output_dir: Optional[str] = None

@dataclass
class ComponentResult:
    """Result of component generation"""
    component_type: str
    content: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class GenerationResult:
    """Complete generation result"""
    material: str
    results: Dict[str, ComponentResult]
    success: bool
    total_components: int
    successful_components: int

class SchemaManager:
    """Manages JSON schemas and their dynamic field extraction"""
    
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.schemas = {}
        self.load_schemas()
    
    def load_schemas(self):
        """Load all JSON schemas from the schemas directory"""
        if not self.schemas_dir.exists():
            logger.warning(f"Schemas directory {self.schemas_dir} not found")
            return
        
        for schema_file in self.schemas_dir.glob("*.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    self.schemas[schema_file.stem] = schema_data
                    logger.info(f"Loaded schema: {schema_file.stem}")
            except Exception as e:
                logger.error(f"Error loading schema {schema_file}: {e}")
    
    def get_schema(self, schema_type: str) -> Optional[Dict]:
        """Get schema by type"""
        return self.schemas.get(schema_type)
    
    def get_dynamic_fields(self, schema_type: str) -> Dict[str, Any]:
        """Extract dynamic fields from schema for content generation"""
        schema = self.get_schema(schema_type)
        if not schema:
            return {}
        
        # Extract field mappings from schema
        field_mappings = {}
        
        # Look for generator config with field content mapping
        for root_key, root_value in schema.items():
            if isinstance(root_value, dict):
                generator_config = root_value.get('generatorConfig', {})
                content_generation = generator_config.get('contentGeneration', {})
                field_content_mapping = content_generation.get('fieldContentMapping', {})
                
                if field_content_mapping:
                    field_mappings.update(field_content_mapping)
                
                # Also extract profile fields for additional context
                profile = root_value.get('profile', {})
                if profile:
                    field_mappings['profile_fields'] = list(profile.keys())
        
        return field_mappings
    
    def get_required_fields(self, schema_type: str) -> List[str]:
        """Get required fields from schema validation rules"""
        schema = self.get_schema(schema_type)
        if not schema:
            return []
        
        required_fields = []
        for root_key, root_value in schema.items():
            if isinstance(root_value, dict):
                validation = root_value.get('validation', {})
                frontmatter = validation.get('frontmatter', {})
                required = frontmatter.get('requiredFields', [])
                if required:
                    required_fields.extend(required)
        
        return required_fields

class ComponentManager:
    """Manages component prompts and generation"""
    
    def __init__(self, components_dir: str = "components"):
        self.components_dir = Path(components_dir)
        self.prompts = {}
        self.load_prompts()
    
    def load_prompts(self):
        """Load all component prompt.yaml files"""
        if not self.components_dir.exists():
            logger.warning(f"Components directory {self.components_dir} not found")
            return
        
        for component_dir in self.components_dir.iterdir():
            if component_dir.is_dir():
                prompt_file = component_dir / "prompt.yaml"
                if prompt_file.exists():
                    try:
                        with open(prompt_file, 'r', encoding='utf-8') as f:
                            prompt_data = yaml.safe_load(f)
                            self.prompts[component_dir.name] = prompt_data
                            logger.info(f"Loaded prompt: {component_dir.name}")
                    except Exception as e:
                        logger.error(f"Error loading prompt {prompt_file}: {e}")
    
    def get_available_components(self) -> List[str]:
        """Get list of available component types"""
        return list(self.prompts.keys())
    
    def get_prompt(self, component_type: str) -> Optional[Dict]:
        """Get prompt configuration for a component type"""
        return self.prompts.get(component_type)

class MaterialLoader:
    """Loads materials from YAML configuration"""
    
    def __init__(self, materials_file: str = "lists/materials.yaml"):
        self.materials_file = Path(materials_file)
        self.materials = {}
        self.load_materials()
    
    def load_materials(self):
        """Load materials from YAML file"""
        if not self.materials_file.exists():
            logger.warning(f"Materials file {self.materials_file} not found")
            return
        
        try:
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                materials_data = data.get('materials', {})
                
                # Flatten materials by category
                for category, category_data in materials_data.items():
                    items = category_data.get('items', [])
                    for item in items:
                        self.materials[item] = {
                            'name': item,
                            'category': category,
                            'article_type': category_data.get('article_type', 'material')
                        }
                
                logger.info(f"Loaded {len(self.materials)} materials")
        except Exception as e:
            logger.error(f"Error loading materials: {e}")
    
    def get_material(self, name: str) -> Optional[Dict]:
        """Get material by name"""
        return self.materials.get(name)
    
    def get_all_materials(self) -> List[str]:
        """Get list of all material names"""
        return list(self.materials.keys())
    
    def get_materials_by_category(self, category: str) -> List[str]:
        """Get materials by category"""
        return [name for name, data in self.materials.items() 
                if data.get('category') == category]

class DynamicGenerator:
    """Main dynamic content generator with schema-driven field generation"""
    
    def __init__(self, api_client=None, use_mock=False):
        self.schema_manager = SchemaManager()
        self.component_manager = ComponentManager()
        self.material_loader = MaterialLoader()
        self.api_client = api_client
        self.author_info = None  # Store author information
        
        # Import and initialize API client if not provided
        if not self.api_client and not use_mock:
            try:
                from api.deepseek import create_deepseek_client
                self.api_client = create_deepseek_client()
                logger.info("Initialized standardized DeepSeek API client")
            except ImportError:
                logger.warning("DeepSeek client not available, falling back to basic API client")
                try:
                    from api.client import APIClient
                    self.api_client = APIClient()
                except ImportError:
                    logger.warning("No API client available - will use mock generation")
                    use_mock = True
        
        # Use mock client if requested or if real client unavailable
        if use_mock or not self.api_client:
            try:
                from api.client import MockAPIClient
                self.api_client = MockAPIClient()
                logger.info("Using mock API client for testing")
            except ImportError:
                logger.error("Mock API client not available")
                self.api_client = None
    
    def get_available_components(self) -> List[str]:
        """Get list of available component types"""
        return self.component_manager.get_available_components()
    
    def get_available_materials(self) -> List[str]:
        """Get list of available materials"""
        return self.material_loader.get_all_materials()
    
    def set_author(self, author_info: Dict):
        """Set author information for content generation."""
        self.author_info = author_info
    
    def _extract_frontmatter_data(self, material_name: str) -> Optional[Dict]:
        """Extract frontmatter data from existing frontmatter file"""
        try:
            # Create proper file path for frontmatter
            material_slug = material_name.lower().replace(' ', '-').replace('_', '-')
            frontmatter_path = Path("content/components/frontmatter") / f"{material_slug}-laser-cleaning.md"
            
            if not frontmatter_path.exists():
                logger.warning(f"Frontmatter file not found: {frontmatter_path}")
                return None
            
            with open(frontmatter_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle files wrapped in code blocks
            if content.startswith('```yaml\n'):
                # Remove the code block wrapper
                content = content[8:]  # Remove ```yaml\n
                if content.endswith('\n```'):
                    content = content[:-4]  # Remove \n```
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter_yaml = parts[1].strip()
                    return yaml.safe_load(frontmatter_yaml)
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting frontmatter for {material_name}: {e}")
            return None

    def generate_component(self, material_name: str, component_type: str, 
                          schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate a single component with dynamic schema-driven content"""
        
        try:
            # Get material info
            material = self.material_loader.get_material(material_name)
            if not material:
                return ComponentResult(
                    component_type=component_type,
                    content="",
                    success=False,
                    error_message=f"Material {material_name} not found"
                )
            
            # Get component prompt
            prompt_config = self.component_manager.get_prompt(component_type)
            if not prompt_config:
                return ComponentResult(
                    component_type=component_type,
                    content="",
                    success=False,
                    error_message=f"Component {component_type} not found"
                )
            
            # Get dynamic fields from schema
            article_type = material.get('article_type', 'material')
            dynamic_fields = self.schema_manager.get_dynamic_fields(article_type)
            
            # Extract frontmatter data for propertiestable component
            frontmatter_data = None
            if component_type == 'propertiestable':
                frontmatter_data = self._extract_frontmatter_data(material_name)
            
            # Build dynamic prompt with schema fields and frontmatter data
            prompt = self._build_dynamic_prompt(
                prompt_config, material, dynamic_fields, schema_fields, frontmatter_data
            )
            
            # Generate content using standardized API client
            if self.api_client:
                # Check if we have a DeepSeek-specific client for optimized generation
                if hasattr(self.api_client, 'generate_for_component'):
                    response = self.api_client.generate_for_component(
                        component_type=component_type,
                        material=material_name,
                        prompt_template=prompt
                    )
                else:
                    # Use standard generation with proper request structure
                    if hasattr(self.api_client, 'generate_simple'):
                        response = self.api_client.generate_simple(prompt)
                    else:
                        # Fallback for basic clients
                        response = self.api_client.generate(prompt)
                
                if response.success:
                    content = response.content
                    logger.info(f"Generated {component_type} for {material_name} ({response.token_count} tokens)")
                else:
                    return ComponentResult(
                        component_type=component_type,
                        content="",
                        success=False,
                        error_message=f"API generation failed: {response.error}"
                    )
            else:
                # Mock generation for testing
                content = f"# {component_type.title()} for {material_name}\n\n"
                content += "Generated content based on dynamic schema fields:\n"
                for field, description in dynamic_fields.items():
                    if field != 'profile_fields':
                        content += f"- {field}: {description}\n"
            
            return ComponentResult(
                component_type=component_type,
                content=content,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating {component_type} for {material_name}: {e}")
            return ComponentResult(
                component_type=component_type,
                content="",
                success=False,
                error_message=str(e)
            )
    
    def _build_dynamic_prompt(self, prompt_config: Dict, material: Dict, 
                             dynamic_fields: Dict, schema_fields: Optional[Dict] = None,
                             frontmatter_data: Optional[Dict] = None) -> str:
        """Build a dynamic prompt incorporating schema fields and template variables"""
        
        # Start with base prompt - use 'template' from YAML files
        base_prompt = prompt_config.get('template', prompt_config.get('prompt', ''))
        system_prompt = prompt_config.get('system', '')
        
        # Extract material information
        material_name = material['name']
        category = material['category']
        article_type = material.get('article_type', 'material')
        
        # Create comprehensive template variables
        template_vars = {
            'subject': material_name,
            'material': material_name,
            'material_name': material_name,  # Add explicit material_name mapping
            'category': category,
            'article_type': article_type,
            'subject_lowercase': material_name.lower(),
            'subject_slug': material_name.lower().replace(' ', '-').replace('_', '-'),
            
            # Material properties (fallback values)
            'material_formula': material.get('formula', material_name),
            'material_symbol': material.get('symbol', material_name[:2].upper()),
            'material_type': material.get('material_type', category),
            'material_description': material.get('description', f"{material_name} is a {category} material used in laser cleaning applications."),
            
            # Bullet-specific variables
            'bullet_count': "2 to 6",  # Randomized bullet count
            
            # Formatted technical specs (placeholders)
            'formatted_technical_specs': f"Technical specifications for {material_name} laser cleaning",
            'formatted_environmental_impact': f"Environmental benefits of {material_name} laser processing",
            'formatted_regulatory_standards': f"Industry standards for {material_name} treatment"
        }
        
        # Add author information if available
        if self.author_info:
            country = self.author_info.get('country', 'International')
            author_id = self.author_info.get('id', 0)
            template_vars['country'] = country
            template_vars['author_name'] = self.author_info.get('name', 'Expert Author')
            template_vars['author_title'] = self.author_info.get('title', 'Technical Expert')
            template_vars['author_expertise'] = self.author_info.get('expertise', 'Laser Processing')
            template_vars['author_id'] = str(author_id)
            
            # Create country context for bullets and other components
            if country != 'International':
                template_vars['country_context'] = f"Write from the perspective of a technical expert in {country}, incorporating relevant regional standards and industry practices."
            else:
                template_vars['country_context'] = "Write from an international technical perspective with global industry standards."
                
            # Create author-specific formatting rules for bullets
            if author_id == 1:  # Taiwan - Yi-Chun Lin
                template_vars['bullet_format_rules'] = """
TAIWAN AUTHOR REQUIREMENTS:
- Generate EXACTLY 4 bullets
- Each bullet must have EXACTLY 1 sentence
- Use numbered list format (1., 2., 3., 4.)
- Start each bullet with **Technical Focus:** followed by the topic
- Order: Parameters → Applications → Safety → Environmental Benefits
- Write in English only, incorporate Taiwan semiconductor/electronics industry context
- Include metric measurements and specific wavelengths"""
                
            elif author_id == 2:  # Italy - Alessandro Moretti
                template_vars['bullet_format_rules'] = """
ITALIAN AUTHOR REQUIREMENTS:
- Generate EXACTLY 5 bullets
- Each bullet must have EXACTLY 2 sentences
- Use traditional bullet format with - prefix
- Start each bullet with **[TOPIC]** in ALL CAPS brackets
- Order: Applications → Parameters → Environmental → Safety → Challenges
- Write in English only, incorporate European/Italian manufacturing industry context
- Include European standards and industrial applications"""
                
            elif author_id == 3:  # Indonesia - Ikmanda Roswati
                template_vars['bullet_format_rules'] = """
INDONESIAN AUTHOR REQUIREMENTS:
- Generate EXACTLY 6 bullets
- Each bullet must have EXACTLY 1 sentence
- Use bullet format with • prefix
- Start each bullet with **Aspect [Topic]:** (use English "Aspect" for all content)
- Order: Environmental → Safety → Applications → Parameters → Challenges → Benefits
- CRITICAL: Write ONLY in English for all content including headers
- Incorporate Indonesian tropical/humid environment and industrial context in English
- Emphasize sustainability and regional manufacturing considerations"""
                
            elif author_id == 4:  # USA - Todd Dunning
                template_vars['bullet_format_rules'] = """
USA AUTHOR REQUIREMENTS:
- Generate EXACTLY 3 bullets
- Each bullet must have EXACTLY 3 sentences
- Use bullet format with * prefix
- Start each bullet with **Key Point:** followed by the topic
- Order: Safety → Parameters → Applications
- Write in English only, incorporate US high-tech industry and regulatory context
- Include OSHA standards, FDA considerations, and Silicon Valley tech applications"""
            else:
                template_vars['bullet_format_rules'] = """
DEFAULT INTERNATIONAL REQUIREMENTS:
- Generate EXACTLY 4 bullets
- Each bullet must have EXACTLY 1 sentence
- Use bullet format with * prefix
- Start each bullet with **[Topic]:** followed by technical details
- Standard order: Parameters → Applications → Safety → Environmental
- Write in English only with international technical perspective"""
        else:
            template_vars['country'] = 'International'
            template_vars['author_name'] = 'Expert Author'
            template_vars['author_title'] = 'Technical Expert'
            template_vars['author_expertise'] = 'Laser Processing'
            template_vars['author_id'] = '0'
            template_vars['country_context'] = "Write from an international technical perspective with global industry standards."
            template_vars['bullet_format_rules'] = """
DEFAULT INTERNATIONAL REQUIREMENTS:
- Generate EXACTLY 4 bullets
- Each bullet must have EXACTLY 1 sentence
- Use bullet format with * prefix
- Start each bullet with **[Topic]:** followed by technical details
- Standard order: Parameters → Applications → Safety → Environmental
- Write in English only with international technical perspective"""
        
        # Replace all template variables in the prompt
        prompt = base_prompt
        for var, value in template_vars.items():
            prompt = prompt.replace(f'{{{var}}}', str(value))
        
        # Add frontmatter data for propertiestable component
        if frontmatter_data:
            prompt += "\n\nFRONTMATTER DATA AVAILABLE:\n"
            
            # Chemical properties
            chem_props = frontmatter_data.get('chemicalProperties', {})
            if chem_props:
                prompt += f"Chemical Formula: {chem_props.get('formula', 'N/A')}\n"
                prompt += f"Material Symbol: {chem_props.get('symbol', 'N/A')}\n"
                prompt += f"Material Type: {chem_props.get('materialType', 'N/A')}\n"
            
            # Physical properties
            properties = frontmatter_data.get('properties', {})
            if properties:
                prompt += f"Density: {properties.get('density', 'N/A')}\n"
                prompt += f"Thermal Conductivity: {properties.get('thermalConductivity', 'N/A')}\n"
                prompt += f"Melting Point: {properties.get('meltingPoint', 'N/A')}\n"
            
            # Category from frontmatter
            fm_category = frontmatter_data.get('category', '')
            if fm_category:
                prompt += f"Category: {fm_category.title()}\n"
            
            # Technical specifications for tensile strength
            tech_specs = frontmatter_data.get('technicalSpecifications', {})
            if tech_specs and hasattr(tech_specs, 'get'):
                tensile = tech_specs.get('tensileStrength', '')
                if tensile:
                    prompt += f"Tensile Strength: {tensile}\n"
        
        # Add dynamic schema field instructions if available
        if dynamic_fields:
            prompt += "\n\nGenerate content incorporating these dynamic fields:\n"
            for field, instruction in dynamic_fields.items():
                if field != 'profile_fields':
                    formatted_instruction = instruction.replace('{subject}', material_name)
                    prompt += f"- {field}: {formatted_instruction}\n"
        
        # Add schema fields if provided
        if schema_fields:
            prompt += "\n\nAdditional context from schema:\n"
            for field, value in schema_fields.items():
                prompt += f"- {field}: {value}\n"
        
        # Combine with system prompt if available
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        else:
            full_prompt = prompt
        
        return full_prompt
    
    def generate_multiple(self, request: GenerationRequest) -> GenerationResult:
        """Generate multiple components for a material"""
        
        results = {}
        successful = 0
        
        # Get schema fields for the material
        material = self.material_loader.get_material(request.material)
        if not material:
            return GenerationResult(
                material=request.material,
                results={},
                success=False,
                total_components=0,
                successful_components=0
            )
        
        article_type = material.get('article_type', 'material')
        schema_fields = self.schema_manager.get_dynamic_fields(article_type)
        
        # Generate each requested component
        for component_type in request.components:
            logger.info(f"Generating {component_type} for {request.material}")
            
            result = self.generate_component(
                request.material, 
                component_type, 
                schema_fields
            )
            
            results[component_type] = result
            if result.success:
                successful += 1
                
                # Save to file if output directory specified
                if request.output_dir:
                    self._save_component(request, component_type, result.content)
        
        return GenerationResult(
            material=request.material,
            results=results,
            success=successful > 0,
            total_components=len(request.components),
            successful_components=successful
        )
    
    def _save_component(self, request: GenerationRequest, component_type: str, content: str):
        """Save generated component to file"""
        # Create proper component directory structure: content/components/{component_type}/
        output_dir = Path(request.output_dir) / "components" / component_type
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename: {material}-laser-cleaning.md
        material_slug = request.material.lower().replace(' ', '-').replace('_', '-')
        filename = f"{material_slug}-laser-cleaning.md"
        filepath = output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved {component_type} to {filepath}")
        except Exception as e:
            logger.error(f"Error saving {component_type}: {e}")

def main():
    """CLI interface for dynamic generation with enhanced component selection"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Z-Beam Dynamic Schema Generator with Component Selection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 -m generators.dynamic_generator --material "Copper" --components "frontmatter,content"
  python3 -m generators.dynamic_generator --list-materials
  python3 -m generators.dynamic_generator --list-components
  python3 -m generators.dynamic_generator --material "Steel" --components all
  python3 -m generators.dynamic_generator --material "Aluminum" --interactive
        """
    )
    
    parser.add_argument('--material', help='Material name to generate content for')
    parser.add_argument('--components', help='Components to generate: comma-separated list or "all"')
    parser.add_argument('--output-dir', default='content', help='Output directory for generated content')
    parser.add_argument('--list-materials', action='store_true', help='List available materials')
    parser.add_argument('--list-components', action='store_true', help='List available components')
    parser.add_argument('--interactive', action='store_true', help='Interactive component selection')
    parser.add_argument('--mock', action='store_true', help='Use mock API client for testing')
    parser.add_argument('--test-api', action='store_true', help='Test API connection')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize generator
    generator = DynamicGenerator(use_mock=args.mock)
    
    # Test API connection if requested
    if args.test_api:
        if hasattr(generator.api_client, 'test_connection'):
            if generator.api_client.test_connection():
                print("✅ API connection successful!")
                return
            else:
                print("❌ API connection failed!")
                return
        else:
            print("⚠️  API connection test not available for this client")
            return
    
    # List operations
    if args.list_materials:
        materials = generator.get_available_materials()
        print(f"📋 Available materials ({len(materials)}):")
        for i, material in enumerate(sorted(materials), 1):
            print(f"   {i:3d}. {material}")
        return
    
    if args.list_components:
        components = generator.get_available_components()
        print(f"🔧 Available components ({len(components)}):")
        for i, component in enumerate(sorted(components), 1):
            print(f"   {i}. {component}")
        return
    
    # Require material for generation
    if not args.material:
        print("❌ Material name is required for generation")
        print("   Use --list-materials to see available materials")
        return
    
    # Interactive component selection
    if args.interactive:
        components_list = interactive_component_selection(generator)
        if not components_list:
            print("No components selected. Exiting.")
            return
    else:
        # Parse components list
        if not args.components:
            print("❌ Components list is required")
            print("   Use --list-components to see available components")
            print("   Use --components all to generate all components")
            return
        
        available_components = generator.get_available_components()
        
        if args.components.lower() == 'all':
            components_list = available_components
        else:
            components_list = [c.strip() for c in args.components.split(',')]
            
            # Validate components
            invalid_components = [c for c in components_list if c not in available_components]
            if invalid_components:
                print(f"❌ Invalid components: {', '.join(invalid_components)}")
                print(f"   Available components: {', '.join(available_components)}")
                return
    
    # Create generation request
    request = GenerationRequest(
        material=args.material,
        components=components_list,
        output_dir=args.output_dir
    )
    
    # Generate content
    print(f"🚀 Generating {len(components_list)} components for {args.material}...")
    print(f"📁 Output directory: {args.output_dir}")
    print("=" * 50)
    
    result = generator.generate_multiple(request)
    
    # Report results
    print(f"\n📊 Generation Results for {result.material}:")
    print(f"   Success: {'✅' if result.success else '❌'}")
    print(f"   Components: {result.successful_components}/{result.total_components}")
    print("=" * 50)
    
    for component_type, component_result in result.results.items():
        if component_result.success:
            print(f"   ✅ {component_type}")
        else:
            print(f"   ❌ {component_type}: {component_result.error_message}")
    
    # Show API statistics if available
    if hasattr(generator.api_client, 'get_statistics'):
        stats = generator.api_client.get_statistics()
        print("\n📈 API Statistics:")
        print(f"   Requests: {stats.get('total_requests', 0)}")
        print(f"   Success rate: {stats.get('success_rate', 0):.1f}%")
        print(f"   Total tokens: {stats.get('total_tokens', 0)}")
        print(f"   Avg response time: {stats.get('average_response_time', 0):.2f}s")

def interactive_component_selection(generator) -> list:
    """Interactive component selection interface"""
    
    available_components = generator.get_available_components()
    
    print(f"\n🔧 Available components ({len(available_components)}):")
    for i, component in enumerate(available_components, 1):
        print(f"   {i}. {component}")
    
    print("\nComponent selection options:")
    print("  - Enter numbers (e.g., 1,3,5)")
    print("  - Enter names (e.g., frontmatter,content)")
    print("  - Enter 'all' for all components")
    print("  - Enter 'quit' to exit")
    
    while True:
        try:
            selection = input("\nSelect components: ").strip()
            
            if selection.lower() == 'quit':
                return []
            
            if selection.lower() == 'all':
                return available_components
            
            # Parse numeric selection
            if selection.replace(',', '').replace(' ', '').isdigit():
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_components = []
                for idx in indices:
                    if 0 <= idx < len(available_components):
                        selected_components.append(available_components[idx])
                    else:
                        print(f"❌ Invalid number: {idx + 1}")
                        continue
                return selected_components
            
            # Parse name selection
            else:
                components_list = [c.strip() for c in selection.split(',')]
                invalid = [c for c in components_list if c not in available_components]
                if invalid:
                    print(f"❌ Invalid components: {', '.join(invalid)}")
                    continue
                return components_list
                
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid selection. Please try again.")
            continue

if __name__ == "__main__":
    main()
