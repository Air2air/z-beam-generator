#!/usr/bin/env python3
"""
YAML Parser for Component Migration
Handles YAML files with multiple documents (--- separators) and provides 
utilities for loading and transforming component data.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class YAMLParser:
    """YAML parser for handling multi-document component files."""
    
    def __init__(self):
        self.component_dirs = {
            "micro": Path("content/components/caption"),
            "jsonld": Path("content/components/jsonld"),
            "metatags": Path("content/components/metatags"),
            "table": Path("content/components/table"),
            "author": Path("content/components/author"),
            "badgesymbol": Path("content/components/badgesymbol")
        }
    
    def load_component_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load a component file that may contain multiple YAML documents.
        
        Args:
            file_path: Path to the component file
            
        Returns:
            Dict containing the parsed component data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Component file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has multiple documents (contains ---)
            if '---' in content:
                return self._load_multi_document_yaml(content, file_path)
            else:
                # Single document YAML
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
                    
        except Exception as e:
            logger.error(f"Failed to load component file {file_path}: {e}")
            return {}
    
    def _load_multi_document_yaml(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Load YAML content with multiple documents."""
        
        try:
            # Split content by document separators and parse each
            documents = list(yaml.safe_load_all(content))
            
            if len(documents) == 1:
                return documents[0] or {}
            
            # Merge multiple documents intelligently
            merged_data = {}
            
            for doc in documents:
                if doc and isinstance(doc, dict):
                    # Skip metadata-only documents (common pattern in component files)
                    if self._is_metadata_document(doc):
                        continue
                    
                    # Merge content documents
                    merged_data.update(doc)
            
            return merged_data
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {file_path}: {e}")
            # Fallback: try to extract content from first non-metadata section
            return self._fallback_parse(content, file_path)
    
    def _is_metadata_document(self, doc: Dict[str, Any]) -> bool:
        """Check if a document is just metadata (skip these)."""
        
        # Common metadata-only patterns
        metadata_keys = {'Material', 'Component', 'Generated', 'Generator', 'Version'}
        doc_keys = set(doc.keys())
        
        # If document only contains metadata keys, skip it
        if doc_keys.issubset(metadata_keys):
            return True
        
        # If document is very small and only has metadata-like fields
        if len(doc) <= 3 and any(key in metadata_keys for key in doc_keys):
            return True
        
        return False
    
    def _fallback_parse(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Fallback parser for problematic YAML files."""
        
        try:
            # Split by document separators and try to parse the main content section
            sections = content.split('---')
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                try:
                    parsed = yaml.safe_load(section)
                    if parsed and isinstance(parsed, dict) and len(parsed) > 3:
                        # This looks like the main content section
                        return parsed
                except Exception:
                    continue
            
            logger.warning(f"Could not parse any section from {file_path}")
            return {}
            
        except Exception as e:
            logger.error(f"Fallback parsing failed for {file_path}: {e}")
            return {}
    
    def load_json_component(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load JSON component files (like JSON-LD)."""
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"JSON component file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON component file {file_path}: {e}")
            return {}
    
    def get_component_file_path(self, material_name: str, component_type: str) -> Optional[Path]:
        """Get the file path for a specific component."""
        
        if component_type not in self.component_dirs:
            logger.warning(f"Unknown component type: {component_type}")
            return None
        
        component_dir = self.component_dirs[component_type]
        
        # Try different file extensions
        possible_files = [
            component_dir / f"{material_name}-laser-cleaning.yaml",
            component_dir / f"{material_name}-laser-cleaning.json",
            component_dir / f"{material_name}-laser-cleaning.md",
            component_dir / f"{material_name}.yaml",
            component_dir / f"{material_name}.json",
            component_dir / f"{material_name}.md"
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                return file_path
        
        return None
    
    def load_all_components_for_material(self, material_name: str) -> Dict[str, Dict[str, Any]]:
        """Load all available component files for a material."""
        
        components_data = {}
        
        for component_type in self.component_dirs.keys():
            file_path = self.get_component_file_path(material_name, component_type)
            
            if file_path:
                if file_path.suffix == '.json':
                    component_data = self.load_json_component(file_path)
                else:
                    component_data = self.load_component_file(file_path)
                
                if component_data:
                    components_data[component_type] = component_data
                    logger.info(f"Loaded {component_type} component for {material_name}")
        
        return components_data
    
    def validate_component_data(self, component_type: str, data: Dict[str, Any]) -> bool:
        """Validate component data structure."""
        
        if not data:
            return False
        
        # Basic validation rules for each component type
        validation_rules = {
            'micro': lambda d: 'before' in d or 'after' in d,
            'jsonld': lambda d: '@context' in d or 'structuredData' in d or 'content' in d,
            'metatags': lambda d: 'title' in d or 'meta' in d or 'htmlMeta' in d,
            'tags': lambda d: isinstance(d, list) or 'tags' in d or 'contentTags' in d,
            'table': lambda d: 'properties_table' in d or 'propertiesTable' in d,
            'author': lambda d: 'authorInfo' in d or 'name' in d,
            'badgesymbol': lambda d: 'symbol' in d or 'badge' in d
        }
        
        rule = validation_rules.get(component_type)
        if rule:
            return rule(data)
        
        # Default: any non-empty dict is valid
        return isinstance(data, dict) and len(data) > 0

def test_yaml_parser():
    """Test the YAML parser with sample files."""
    
    parser = YAMLParser()
    
    print("🧪 Testing YAML Parser")
    print("=" * 50)
    
    # Test with aluminum components
    material_name = "aluminum"
    
    print(f"📁 Loading all components for {material_name}:")
    components = parser.load_all_components_for_material(material_name)
    
    for component_type, data in components.items():
        size = len(str(data))
        valid = parser.validate_component_data(component_type, data)
        status = "✅" if valid else "❌"
        print(f"  {status} {component_type}: {size} chars, valid: {valid}")
    
    print("\n📊 Summary:")
    print(f"  Components loaded: {len(components)}")
    print(f"  Total data size: {sum(len(str(data)) for data in components.values())} chars")
    
    return components

if __name__ == "__main__":
    test_yaml_parser()