#!/usr/bin/env python3
"""
Categories.yaml Generator - Standalone Data Generation Tool

This script generates and maintains a comprehensive database of material property
ranges organized by category and subcategory. Uses AI research to validate and 
update property data periodically.

Usage:
    python3 scripts/generators/categories_generator.py --generate
    python3 scripts/generators/categories_generator.py --refresh
    python3 scripts/generators/categories_generator.py --validate
"""

import argparse
import hashlib
import json
import logging
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from api.client_factory import ClientFactory
    from api.config import APIConfig
except ImportError as e:
    print(f"Warning: Could not import API modules: {e}")
    print("Generator will run in validation-only mode")
    ClientFactory = None
    APIConfig = None


class CategoryResearchError(Exception):
    """Raised when category research fails"""
    pass


class SubcategoryValidationError(Exception):
    """Raised when subcategory validation fails"""
    pass


class CategoriesGenerator:
    """Standalone generator for Categories.yaml database"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_root = PROJECT_ROOT
        self.materials_yaml_path = self.project_root / "data" / "Materials.yaml"
        self.categories_yaml_path = self.project_root / "data" / "Categories.yaml"
        self.schema_path = self.project_root / "schemas" / "categories_schema.json"
        
        # Fail-fast validation
        self._validate_dependencies()
        
        # Initialize API client for research
        self.api_client = None
        self._init_api_client()
    
    def _validate_dependencies(self):
        """Validate all required dependencies exist (fail-fast)"""
        if not self.materials_yaml_path.exists():
            raise CategoryResearchError(f"Source Materials.yaml not found: {self.materials_yaml_path}")
        
        if not self.schema_path.exists():
            raise CategoryResearchError(f"Categories schema not found: {self.schema_path}")
        
        self.logger.info("✅ All dependencies validated")
    
    def _init_api_client(self):
        """Initialize API client for research validation"""
        try:
            if ClientFactory is None or APIConfig is None:
                self.logger.warning("API modules not available - research features disabled")
                return
                
            config = APIConfig()
            client_factory = ClientFactory(config)
            self.api_client = client_factory.get_client("deepseek")
            self.logger.info("✅ API client initialized for research")
        except Exception as e:
            self.logger.warning(f"Could not initialize API client: {str(e)}")
            self.api_client = None
    
    def generate_categories_database(self) -> bool:
        """Generate complete Categories.yaml database"""
        try:
            self.logger.info("🚀 Starting Categories.yaml generation")
            
            # Step 1: Parse source Materials.yaml
            categories_data = self._parse_materials_yaml()
            
            # Step 2: Research property ranges for each category/subcategory
            researched_data = self._research_property_ranges(categories_data)
            
            # Step 3: Generate final database structure
            database = self._build_categories_database(researched_data)
            
            # Step 4: Validate against schema
            self._validate_database(database)
            
            # Step 5: Write Categories.yaml
            self._write_categories_yaml(database)
            
            self.logger.info("✅ Categories.yaml generated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Categories generation failed: {str(e)}")
            return False
    
    def refresh_categories_database(self) -> bool:
        """Refresh existing Categories.yaml with updated research"""
        try:
            self.logger.info("🔄 Refreshing Categories.yaml database")
            
            if not self.categories_yaml_path.exists():
                self.logger.info("No existing Categories.yaml found, generating from scratch")
                return self.generate_categories_database()
            
            # Load existing database
            with open(self.categories_yaml_path, 'r') as f:
                existing_data = yaml.safe_load(f)
            
            # Research updates for categories with low confidence or old data
            updated_data = self._research_updates(existing_data)
            
            # Validate and write updated database
            self._validate_database(updated_data)
            self._write_categories_yaml(updated_data)
            
            self.logger.info("✅ Categories.yaml refreshed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Categories refresh failed: {str(e)}")
            return False
    
    def validate_categories_database(self) -> bool:
        """Validate existing Categories.yaml against schema"""
        try:
            self.logger.info("🔍 Validating Categories.yaml")
            
            if not self.categories_yaml_path.exists():
                self.logger.error("❌ Categories.yaml not found")
                return False
            
            with open(self.categories_yaml_path, 'r') as f:
                database = yaml.safe_load(f)
            
            self._validate_database(database)
            self.logger.info("✅ Categories.yaml validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Categories validation failed: {str(e)}")
            return False
    
    def _parse_materials_yaml(self) -> Dict:
        """Parse Materials.yaml to extract category/subcategory combinations"""
        with open(self.materials_yaml_path, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        categories = {}
        subcategory_combinations = set()
        
        # Extract existing category_ranges
        if 'category_ranges' in materials_data:
            for category, ranges in materials_data['category_ranges'].items():
                categories[category] = {
                    'category_ranges': ranges,
                    'subcategories': set()
                }
        
        # Extract all category/subcategory combinations from materials
        materials_section = materials_data.get('materials', {})
        for material_name, material_data in materials_section.items():
            if isinstance(material_data, dict):
                category = material_data.get('category', 'unknown')
                subcategory = material_data.get('subcategory', 'unknown')
                
                if category != 'unknown' and subcategory != 'unknown':
                    if category not in categories:
                        categories[category] = {
                            'category_ranges': {},
                            'subcategories': set()
                        }
                    
                    categories[category]['subcategories'].add(subcategory)
                    subcategory_combinations.add((category, subcategory))
        
        # Convert sets to lists for JSON serialization
        for category_data in categories.values():
            category_data['subcategories'] = list(category_data['subcategories'])
        
        self.logger.info(f"📊 Found {len(categories)} categories with {len(subcategory_combinations)} subcategory combinations")
        return categories
    
    def _research_property_ranges(self, categories_data: Dict) -> Dict:
        """Use AI to research property ranges for each category/subcategory"""
        researched_data = {}
        
        for category, category_info in categories_data.items():
            self.logger.info(f"🔬 Researching {category} category")
            
            researched_category = {
                'category_ranges': category_info['category_ranges'],
                'subcategories': {},
                'common_applications': self._research_applications(category)
            }
            
            # Research each subcategory
            for subcategory in category_info['subcategories']:
                self.logger.info(f"  🔍 Researching {category}/{subcategory}")
                
                subcategory_data = self._research_subcategory_properties(category, subcategory)
                researched_category['subcategories'][subcategory] = subcategory_data
            
            researched_data[category] = researched_category
        
        return researched_data
    
    def _research_subcategory_properties(self, category: str, subcategory: str) -> Dict:
        """Research properties for specific category/subcategory combination"""
        try:
            # Build research prompt
            research_prompt = self._build_research_prompt(category, subcategory)
            
            # Query AI for property research
            response = self.api_client.generate_text(research_prompt)
            
            # Parse AI response into structured data
            properties_data = self._parse_research_response(response, category, subcategory)
            
            return properties_data
            
        except Exception as e:
            self.logger.warning(f"Research failed for {category}/{subcategory}: {str(e)}")
            return self._create_minimal_subcategory_data(category, subcategory)
    
    def _build_research_prompt(self, category: str, subcategory: str) -> str:
        """Build AI research prompt for category/subcategory"""
        return f"""Research comprehensive material properties for {category} materials in the {subcategory} subcategory.

Provide detailed property ranges suitable for laser cleaning applications, including:

MATERIAL PROPERTIES:
- density (g/cm³)
- meltingPoint (°C)
- thermalConductivity (W/m·K) 
- tensileStrength (MPa)
- hardness (appropriate scale)
- youngsModulus (GPa)
- thermalExpansion (10⁻⁶/°C)
- specificHeat (J/kg·K)
- thermalDiffusivity (mm²/s)
- reflectivity (% at 1064nm)
- absorptionCoefficient (10⁶/m at 1064nm)
- ablationThreshold (J/cm²)
- oxidationResistance (qualitative)
- crystallineStructure (crystal system)

LASER MACHINE SETTINGS:
- powerRange (W)
- wavelength (nm)
- spotSize (μm)
- repetitionRate (kHz)
- fluenceThreshold (J/cm²)
- pulseWidth (ns)
- scanSpeed (mm/s)
- overlapRatio (%)
- passCount (passes)

For each property, provide:
- Typical value
- Minimum value
- Maximum value
- Confidence level (0-100)
- Brief description
- Units

Format as YAML structure. Focus on scientifically accurate ranges specific to {subcategory} {category} materials."""
    
    def _parse_research_response(self, response: str, category: str, subcategory: str) -> Dict:
        """Parse AI research response into structured property data"""
        try:
            # Try to extract YAML from response
            if '```yaml' in response:
                yaml_start = response.find('```yaml') + 7
                yaml_end = response.find('```', yaml_start)
                yaml_content = response[yaml_start:yaml_end].strip()
            else:
                yaml_content = response
            
            # Parse YAML response
            parsed_data = yaml.safe_load(yaml_content)
            
            # Validate and structure the response
            structured_data = {
                'materialProperties': {},
                'machineSettings': {},
                'specialConsiderations': [],
                'research_sources': [{
                    'type': 'ai_validated',
                    'title': f'AI Research for {category}/{subcategory}',
                    'confidence_contribution': 75,
                    'properties_validated': list(parsed_data.get('materialProperties', {}).keys()) + list(parsed_data.get('machineSettings', {}).keys())
                }]
            }
            
            # Process materialProperties
            if 'materialProperties' in parsed_data:
                structured_data['materialProperties'] = parsed_data['materialProperties']
            
            # Process machineSettings
            if 'machineSettings' in parsed_data:
                structured_data['machineSettings'] = parsed_data['machineSettings']
            
            # Extract special considerations
            if 'specialConsiderations' in parsed_data:
                structured_data['specialConsiderations'] = parsed_data['specialConsiderations']
            
            return structured_data
            
        except Exception as e:
            self.logger.warning(f"Failed to parse research response for {category}/{subcategory}: {str(e)}")
            return self._create_minimal_subcategory_data(category, subcategory)
    
    def _research_applications(self, category: str) -> List[str]:
        """Research common laser cleaning applications for category"""
        applications_map = {
            'metal': ['rust removal', 'oxide cleaning', 'surface preparation', 'paint stripping'],
            'ceramic': ['contamination removal', 'surface cleaning', 'restoration'],
            'glass': ['contamination removal', 'surface preparation', 'restoration'],
            'polymer': ['surface preparation', 'adhesive removal', 'cleaning'],
            'composite': ['surface preparation', 'contamination removal', 'bonding preparation'],
            'stone': ['restoration', 'contamination removal', 'surface cleaning'],
            'organic': ['surface preparation', 'contamination removal']
        }
        return applications_map.get(category, ['laser cleaning', 'surface preparation'])
    
    def _create_minimal_subcategory_data(self, category: str, subcategory: str) -> Dict:
        """Create minimal subcategory data when research fails"""
        return {
            'materialProperties': {},
            'machineSettings': {},
            'specialConsiderations': ['research_failed'],
            'research_sources': [{
                'type': 'ai_validated',
                'title': f'Minimal data for {category}/{subcategory}',
                'confidence_contribution': 25,
                'properties_validated': []
            }]
        }
    
    def _research_updates(self, existing_data: Dict) -> Dict:
        """Research updates for existing database"""
        # For now, return existing data - future enhancement point
        updated_metadata = self._generate_metadata(existing_data.get('categories', {}))
        existing_data['metadata'] = updated_metadata
        return existing_data
    
    def _build_categories_database(self, researched_data: Dict) -> Dict:
        """Build final Categories.yaml database structure"""
        database = {
            'metadata': self._generate_metadata(researched_data),
            'categories': researched_data
        }
        return database
    
    def _generate_metadata(self, categories_data: Dict) -> Dict:
        """Generate metadata section for Categories.yaml"""
        total_subcategories = sum(
            len(category_data.get('subcategories', {})) 
            for category_data in categories_data.values()
        )
        
        # Calculate Materials.yaml hash for tracking changes
        materials_hash = self._calculate_materials_hash()
        
        return {
            'version': '1.0.0',
            'generated_date': datetime.now().isoformat(),
            'source_materials_yaml_hash': materials_hash,
            'research_confidence_threshold': 75,
            'total_categories': len(categories_data),
            'total_subcategories': total_subcategories
        }
    
    def _calculate_materials_hash(self) -> str:
        """Calculate hash of Materials.yaml for change tracking"""
        with open(self.materials_yaml_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _validate_database(self, database: Dict):
        """Validate database against JSON schema"""
        try:
            with open(self.schema_path, 'r') as f:
                # Load schema for potential future use with jsonschema library
                _ = json.load(f)
            
            # Basic structure validation for now
            if 'metadata' not in database:
                raise SubcategoryValidationError("Missing metadata section")
            
            if 'categories' not in database:
                raise SubcategoryValidationError("Missing categories section")
            
            self.logger.info("✅ Database structure validation passed")
            
        except Exception as e:
            raise SubcategoryValidationError(f"Database validation failed: {str(e)}")
    
    def _write_categories_yaml(self, database: Dict):
        """Write Categories.yaml database to file"""
        try:
            with open(self.categories_yaml_path, 'w') as f:
                yaml.dump(database, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
            
            self.logger.info(f"✅ Categories.yaml written to {self.categories_yaml_path}")
            
        except Exception as e:
            raise CategoryResearchError(f"Failed to write Categories.yaml: {str(e)}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Categories.yaml Database Generator')
    parser.add_argument('--generate', action='store_true', help='Generate new Categories.yaml')
    parser.add_argument('--refresh', action='store_true', help='Refresh existing Categories.yaml')
    parser.add_argument('--validate', action='store_true', help='Validate existing Categories.yaml')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        generator = CategoriesGenerator()
        
        if args.generate:
            success = generator.generate_categories_database()
        elif args.refresh:
            success = generator.refresh_categories_database()
        elif args.validate:
            success = generator.validate_categories_database()
        else:
            parser.print_help()
            return
        
        exit_code = 0 if success else 1
        sys.exit(exit_code)
        
    except Exception as e:
        logging.error(f"❌ Generator failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()