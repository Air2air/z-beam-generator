#!/usr/bin/env python3
"""
Metatags Component Generator

Generates HTML meta tags using frontmatter extraction.
Integrated with the modular component architecture.
"""

import sys
from pathlib import Path
from typing import Dict
import json
import re

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import after path setup
try:
    from generators.component_generators import FrontmatterComponentGenerator, ComponentResult
except ImportError:
    # Fallback if running standalone
    class FrontmatterComponentGenerator:
        def __init__(self, component_type): 
            self.component_type = component_type
        def generate(self, *args, **kwargs):
            raise NotImplementedError("Base class method")
    
    class ComponentResult:
        def __init__(self, component_type, content, success, error_message=None):
            self.component_type = component_type
            self.content = content
            self.success = success
            self.error_message = error_message


class MetatagsComponentGenerator(FrontmatterComponentGenerator):
    """Generator for meta tags components using frontmatter data"""
    
    def __init__(self):
        super().__init__("metatags")
    
    def _extract_from_frontmatter(self, material_name: str, frontmatter_data: Dict) -> str:
        """Generate HTML meta tags from frontmatter using schema and example"""
        
        # Load example file to understand the expected format
        try:
            example_path = Path(__file__).parent / "example_metatags.md"
            example_tags = {}
            if example_path.exists():
                with open(example_path, 'r', encoding='utf-8') as f:
                    example_content = f.read()
                    example_tags = self._parse_example_metatags(example_content)
        except Exception:
            example_tags = {}
        
        # Load schema to understand expected structure  
        try:
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "material.json"
            schema_fields = {}
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    # Extract relevant properties for meta tags
                    material_profile = schema.get('materialProfile', {}).get('profile', {})
                    schema_fields = {
                        'basic': material_profile.get('basicInfo', {}),
                        'chemical': material_profile.get('chemicalProperties', {}),
                        'physical': material_profile.get('physicalProperties', {}),
                    }
        except Exception:
            schema_fields = {}
        
        # Generate meta tags dynamically
        if example_tags:
            # Use example structure as template
            meta_tags = self._build_from_example(frontmatter_data, example_tags, material_name)
        elif schema_fields:
            # Use schema structure
            meta_tags = self._build_from_schema(frontmatter_data, schema_fields, material_name)
        else:
            # Fallback to hardcoded structure
            meta_tags = self._build_fallback_metatags(frontmatter_data, material_name)
        
        return '\n'.join(meta_tags)
    
    def _parse_example_metatags(self, example_content: str) -> Dict:
        """Parse example file to extract meta tag structure"""
        meta_tags = {}
        try:
            # Extract meta tags using regex
            meta_pattern = r'<meta\s+([^>]+)>'
            matches = re.findall(meta_pattern, example_content)
            
            for match in matches:
                # Parse attributes
                if 'name=' in match and 'content=' in match:
                    name_match = re.search(r'name="([^"]+)"', match)
                    content_match = re.search(r'content="([^"]+)"', match)
                    if name_match and content_match:
                        meta_tags[name_match.group(1)] = content_match.group(1)
                elif 'property=' in match and 'content=' in match:
                    prop_match = re.search(r'property="([^"]+)"', match)
                    content_match = re.search(r'content="([^"]+)"', match)
                    if prop_match and content_match:
                        meta_tags[prop_match.group(1)] = content_match.group(1)
        except Exception:
            pass
        return meta_tags
    
    def _build_from_example(self, frontmatter_data: Dict, example_tags: Dict, material_name: str) -> list:
        """Build meta tags using example structure as template"""
        meta_tags = []
        
        for tag_name, example_content in example_tags.items():
            content = self._generate_meta_content(frontmatter_data, tag_name, material_name, example_content)
            
            if tag_name.startswith('og:') or tag_name.startswith('twitter:'):
                meta_tags.append(f'<meta property="{tag_name}" content="{content}">')
            else:
                meta_tags.append(f'<meta name="{tag_name}" content="{content}">')
        
        return meta_tags
    
    def _build_from_schema(self, frontmatter_data: Dict, schema_fields: Dict, material_name: str) -> list:
        """Build meta tags using schema structure"""
        meta_tags = []
        
        # Basic meta tags
        title = self._get_field(frontmatter_data, ['title', 'name'], material_name)
        description = self._get_field(frontmatter_data, ['description'], f"Technical specifications and properties for {material_name}")
        category = self._get_field(frontmatter_data, ['category', 'type'], 'Material')
        
        meta_tags.append(f'<meta name="description" content="{description}">')
        
        # Generate keywords from schema
        keywords = self._generate_keywords_from_schema(frontmatter_data, schema_fields, material_name)
        meta_tags.append(f'<meta name="keywords" content="{", ".join(keywords)}">')
        
        meta_tags.append(f'<meta name="subject" content="{category}">')
        meta_tags.append(f'<meta name="classification" content="{category}">')
        
        # Open Graph tags
        meta_tags.append(f'<meta property="og:title" content="{title}">')
        meta_tags.append(f'<meta property="og:description" content="{description}">')
        meta_tags.append('<meta property="og:type" content="article">')
        
        # Twitter Card tags
        meta_tags.append('<meta name="twitter:card" content="summary">')
        meta_tags.append(f'<meta name="twitter:title" content="{title}">')
        meta_tags.append(f'<meta name="twitter:description" content="{description}">')
        
        return meta_tags
    
    def _build_fallback_metatags(self, frontmatter_data: Dict, material_name: str) -> list:
        """Build fallback meta tags structure"""
        # Extract basic information
        title = frontmatter_data.get('title', material_name)
        description = frontmatter_data.get('description', f"Technical specifications and properties for {material_name}")
        category = frontmatter_data.get('category', 'Material')
        
        # Extract additional metadata
        keywords = []
        keywords.append(material_name.lower())
        keywords.append(category.lower())
        
        # Add material type keywords
        chem_props = frontmatter_data.get('chemicalProperties', {})
        if 'materialType' in chem_props:
            keywords.append(chem_props['materialType'].lower())
        
        # Add properties keywords
        properties = frontmatter_data.get('properties', {})
        if properties:
            keywords.extend(['material properties', 'technical specifications'])
        
        # Build meta tags
        meta_tags = []
        meta_tags.append(f'<meta name="description" content="{description}">')
        meta_tags.append(f'<meta name="keywords" content="{", ".join(keywords)}">')
        meta_tags.append(f'<meta name="subject" content="{category}">')
        meta_tags.append(f'<meta name="classification" content="{category}">')
        
        # Open Graph tags
        meta_tags.append(f'<meta property="og:title" content="{title}">')
        meta_tags.append(f'<meta property="og:description" content="{description}">')
        meta_tags.append('<meta property="og:type" content="article">')
        
        # Twitter Card tags
        meta_tags.append('<meta name="twitter:card" content="summary">')
        meta_tags.append(f'<meta name="twitter:title" content="{title}">')
        meta_tags.append(f'<meta name="twitter:description" content="{description}">')
        
        return meta_tags
    
    def _generate_meta_content(self, frontmatter_data: Dict, tag_name: str, material_name: str, example_content: str) -> str:
        """Generate content for specific meta tag based on tag name"""
        
        if tag_name in ['description', 'og:description', 'twitter:description']:
            return self._get_field(frontmatter_data, ['description'], f"Technical specifications and properties for {material_name}")
        elif tag_name in ['title', 'og:title', 'twitter:title']:
            return self._get_field(frontmatter_data, ['title', 'name'], material_name)
        elif tag_name == 'keywords':
            keywords = [material_name.lower()]
            category = self._get_field(frontmatter_data, ['category', 'type'], '').lower()
            if category:
                keywords.append(category)
            return ", ".join(keywords)
        elif tag_name in ['subject', 'classification']:
            return self._get_field(frontmatter_data, ['category', 'type'], 'Material')
        elif tag_name == 'og:type':
            return 'article'
        elif tag_name == 'twitter:card':
            return 'summary'
        else:
            # Try to extract from frontmatter or use example
            extracted = self._get_field(frontmatter_data, [tag_name.replace(':', '.')], '')
            return extracted if extracted else example_content
    
    def _generate_keywords_from_schema(self, frontmatter_data: Dict, schema_fields: Dict, material_name: str) -> list:
        """Generate keywords from schema structure"""
        keywords = [material_name.lower()]
        
        # Add category/type
        category = self._get_field(frontmatter_data, ['category', 'type'], '').lower()
        if category:
            keywords.append(category)
        
        # Add properties from each schema section
        for section_name, section_data in schema_fields.items():
            if isinstance(section_data, dict) and 'properties' in section_data:
                section_props = section_data['properties']
                for prop_name in section_props.keys():
                    prop_value = self._get_field(frontmatter_data, [f'{section_name}Properties.{prop_name}', prop_name], '')
                    if prop_value and prop_value != 'N/A':
                        keywords.append(prop_name.lower().replace('_', ' '))
        
        # Add general keywords
        keywords.extend(['material properties', 'technical specifications'])
        
        return list(set(keywords))  # Remove duplicates
    
    def _get_field(self, data: Dict, paths: list, default: str = "") -> str:
        """Extract field using dot notation paths with fallback"""
        for path in paths:
            if '.' in path:
                # Handle nested path
                keys = path.split('.')
                current = data
                try:
                    for key in keys:
                        current = current[key]
                    if current is not None:
                        return str(current)
                except (KeyError, TypeError):
                    continue
            else:
                # Handle direct key
                value = data.get(path)
                if value is not None:
                    return str(value)
        return default
