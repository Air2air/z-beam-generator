#!/usr/bin/env python3
"""
Schema Loader - Loads from actual YAML files
"""
import logging
import yaml
import re
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SchemaLoader:
    """Loads schemas from YAML files"""
    
    def __init__(self, article_type: str):
        self.article_type = article_type
        self.schema_file = Path(f"schemas/{article_type}_schema_prompt.md")
        self._schema_cache = None
    
    def get_schema(self) -> Dict[str, Any]:
        """Get schema data from file"""
        if self._schema_cache is None:
            self._schema_cache = self._load_schema()
        return self._schema_cache
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load schema from markdown file"""
        if not self.schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_file}")
        
        with open(self.schema_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML from markdown
        yaml_content = self._extract_yaml(content)
        
        if not yaml_content:
            raise ValueError(f"No YAML content found in {self.schema_file}")
        
        return yaml.safe_load(yaml_content)
    
    def _extract_yaml(self, content: str) -> str:
        """Extract YAML from markdown content"""
        # Look for ```yaml blocks
        yaml_match = re.search(r'```yaml\s*\n(.*?)\n```', content, re.DOTALL)
        if yaml_match:
            return yaml_match.group(1)
        
        # Look for yaml: sections
        yaml_match = re.search(r'yaml:\s*\n(.*?)(?=\n[^\s]|\Z)', content, re.DOTALL)
        if yaml_match:
            return yaml_match.group(1)
        
        return ""
    
    def get_metadata_schema(self) -> Dict[str, Any]:
        """Get metadata schema"""
        return self.get_schema().get("metadata", {})
    
    def get_tag_schema(self) -> Dict[str, Any]:
        """Get tag schema"""
        return self.get_schema().get("tags", {})
    
    def get_jsonld_schema(self) -> Dict[str, Any]:
        """Get JSON-LD schema"""
        return self.get_schema().get("jsonld", {})
    
    def get_prompt_template(self) -> str:
        """Get prompt template"""
        return self.get_schema().get("prompt", "")