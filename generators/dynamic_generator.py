#!/usr/bin/env python3
"""
Dynamic Schema-Driven Generator for Z-Beam

This module provides dynamic content generation based on JSON schemas,
allowing for flexible field-driven content creation with component selection.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple slug generation functions
def create_material_slug(name: str) -> str:
    return name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')

def create_filename_slug(name: str, suffix: str = "laser-cleaning") -> str:
    slug = create_material_slug(name)
    return f"{slug}-{suffix}" if suffix else slug

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
    
    def get_available_components(self) -> List[str]:
        """Get list of available component types"""
        # Scan components directory for available components
        components = []
        if self.components_dir.exists():
            for component_dir in self.components_dir.iterdir():
                if component_dir.is_dir() and component_dir.name != "__pycache__":
                    components.append(component_dir.name)
        return components
    
    def get_prompt(self, component_type: str) -> Optional[Dict]:
        """Get prompt configuration for a component type"""
        return None

class MaterialLoader:
    """Loads materials from YAML configuration"""
    
    def __init__(self, materials_file: str = "data/materials.yaml"):
        self.materials_file = Path(materials_file)
        self.materials = {}
        self.load_materials()
    
    def load_materials(self):
        """Load materials from YAML file"""
        try:
            import yaml
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'materials' not in data:
                logger.warning(f"No materials found in {self.materials_file}")
                return
            
            # Flatten the nested structure into a simple name->data mapping
            for category, category_data in data['materials'].items():
                if 'items' in category_data:
                    for item in category_data['items']:
                        material_name = item['name']
                        # Add category to the material data
                        item['category'] = category
                        self.materials[material_name] = item
            
            logger.info(f"Loaded {len(self.materials)} materials from {self.materials_file}")
            
        except Exception as e:
            logger.error(f"Error loading materials from {self.materials_file}: {e}")
            self.materials = {}
    
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
    
    def __init__(self, api_config=None, api_client=None):
        """Initialize DynamicGenerator - API-only, no mock support"""
        self.schema_manager = SchemaManager()
        self.component_manager = ComponentManager()
        self.material_loader = MaterialLoader()
        self.api_client = api_client  # Accept api_client parameter for backwards compatibility
        self.api_config = api_config
        self.author_info = None  # Store author information
        
        logger.info("Dynamic Generator initialized - API-only mode")
    
    def get_available_components(self) -> List[str]:
        """Get list of available component types"""
        try:
            from generators.component_generators import ComponentGeneratorFactory
            return ComponentGeneratorFactory.get_available_components()
        except ImportError:
            raise Exception("generators.component_generators not available - no fallback to component manager permitted in fail-fast architecture")
    
    def get_available_materials(self) -> List[str]:
        """Get list of available materials"""
        return self.material_loader.get_all_materials()
    
    def set_author(self, author_info: Dict):
        """Set author information for content generation."""
        self.author_info = author_info
    
    def set_api_client(self, api_client):
        """Set API client for component generation"""
        self.api_client = api_client
    
    def _extract_frontmatter_data(self, material_name: str) -> Optional[Dict]:
        """Extract frontmatter data from existing frontmatter file - simplified"""
        return None

    def generate_component(self, material_name: str, component_type: str, 
                          schema_fields: Optional[Dict] = None,
                          ai_detection_service=None) -> ComponentResult:
        """Generate a single component using the new component generator system"""
        
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
            
            # Import the component generator factory
            from generators.component_generators import ComponentGeneratorFactory
            
            # Create component generator
            generator = ComponentGeneratorFactory.create_generator(component_type, ai_detection_service)
            if not generator:
                return ComponentResult(
                    component_type=component_type,
                    content="",
                    success=False,
                    error_message=f"No generator available for component type: {component_type}"
                )
            
            # Get dynamic fields from schema for this material
            article_type = material.get('article_type', 'material')
            dynamic_fields = self.schema_manager.get_dynamic_fields(article_type)
            
            # Extract frontmatter data if needed
            frontmatter_data = self._extract_frontmatter_data(material_name)
            
            # Extract author information from material data
            author_info = self.author_info  # Use globally set author if available
            if not author_info:
                # Check if author_id is in the top level material
                if 'author_id' in material:
                    author_info = {'id': material['author_id']}
                # Check if author_id is in the material.data nested structure  
                elif 'data' in material and 'author_id' in material['data']:
                    author_info = {'id': material['data']['author_id']}
            
            # Generate using the specific component generator with schema fields
            result = generator.generate(
                material_name=material_name,
                material_data=material,
                api_client=self.api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data,
                schema_fields=dynamic_fields  # Pass dynamic schema fields
            )
            
            return result
            
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
        """Build a simple prompt - deprecated method"""
        return f"Generate content for {material.get('name', 'material')}"
    
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
                schema_fields,
                None  # No AI detection service in batch mode
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
        # Handle legacy "content" component type - should save to "text" directory
        if component_type == "content":
            component_type = "text"
        
        # Create proper component directory structure: content/components/{component_type}/
        output_dir = Path(request.output_dir) / "components" / component_type
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename using clean slug generation
        filename = create_filename_slug(request.material) + ".md"
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
    parser.add_argument('--test-api', action='store_true', help='Test API connection')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize generator
    generator = DynamicGenerator()
    
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
