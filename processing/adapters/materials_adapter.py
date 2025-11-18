"""
Materials.yaml Data Source Adapter

Implements DataSourceAdapter interface for Materials.yaml structure.
Handles material-specific data access, context building, and content extraction.
"""

import json
import logging
import re
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any

from processing.adapters.base import DataSourceAdapter

logger = logging.getLogger(__name__)


class MaterialsAdapter(DataSourceAdapter):
    """
    Adapter for Materials.yaml data source.
    
    Implements all data access patterns specific to material frontmatter generation.
    """
    
    def __init__(self, materials_path: Path = None):
        """
        Initialize materials adapter.
        
        Args:
            materials_path: Path to Materials.yaml (default: data/materials/Materials.yaml)
        """
        if materials_path is None:
            materials_path = Path("data/materials/Materials.yaml")
        
        self.materials_path = Path(materials_path)
        self._data_cache = None
        logger.debug(f"MaterialsAdapter initialized with path: {self.materials_path}")
    
    def get_data_path(self) -> Path:
        """Get path to Materials.yaml"""
        return self.materials_path
    
    def load_all_data(self) -> Dict[str, Any]:
        """Load complete Materials.yaml structure"""
        if self._data_cache is None:
            try:
                with open(self.materials_path, 'r', encoding='utf-8') as f:
                    self._data_cache = yaml.safe_load(f)
                logger.debug(f"Loaded {len(self._data_cache.get('materials', {}))} materials")
            except Exception as e:
                logger.error(f"Failed to load Materials.yaml: {e}")
                raise ValueError(f"Cannot load Materials.yaml: {e}")
        
        return self._data_cache
    
    def get_item_data(self, identifier: str) -> Dict[str, Any]:
        """
        Get data for specific material.
        
        Args:
            identifier: Material name
            
        Returns:
            Material data dict
            
        Raises:
            ValueError: If material not found
        """
        all_data = self.load_all_data()
        materials = all_data.get('materials', {})
        
        if identifier not in materials:
            raise ValueError(f"Material '{identifier}' not found in Materials.yaml")
        
        return materials[identifier]
    
    def build_context(self, item_data: Dict[str, Any]) -> str:
        """
        Build context string from material data.
        
        Includes category, subcategory, description snippet, and key properties.
        
        Args:
            item_data: Material data dict
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        if 'category' in item_data:
            context_parts.append(f"Category: {item_data['category']}")
        
        if 'subcategory' in item_data:
            context_parts.append(f"Subcategory: {item_data['subcategory']}")
        
        if 'description' in item_data:
            desc = item_data['description']
            # Truncate long descriptions
            if len(desc) > 300:
                desc = desc[:300] + "..."
            context_parts.append(f"Description: {desc}")
        
        # Extract key properties
        properties = item_data.get('materialProperties', {})
        key_props = []
        for prop in ['hardness', 'thermalConductivity', 'density', 'meltingPoint']:
            if prop in properties:
                key_props.append(f"{prop}: {properties[prop]}")
        
        if key_props:
            context_parts.append("Properties: " + ", ".join(key_props[:5]))
        
        return "\n".join(context_parts)
    
    def get_author_id(self, item_data: Dict[str, Any]) -> int:
        """
        Extract author ID from material data with rotation for variety.
        
        If author is not specified in data, rotates through all 4 authors
        based on material name hash to ensure distribution and consistency.
        
        Args:
            item_data: Material data dict
            
        Returns:
            Author ID (1-4)
        """
        author_data = item_data.get('author', {})
        if isinstance(author_data, dict) and 'id' in author_data:
            return author_data['id']
        elif isinstance(author_data, int):
            return author_data
        
        # If no author specified, rotate based on material name for consistency
        # This ensures each material consistently gets the same author
        # but distributes all 4 authors across materials
        material_name = item_data.get('name', '')
        if not material_name:
            # Try to infer from data structure
            all_data = self.load_all_data()
            materials = all_data.get('materials', {})
            # Find this material in the list
            for name, data in materials.items():
                if data is item_data:
                    material_name = name
                    break
        
        # Use hash of material name for consistent rotation (1-4)
        if material_name:
            name_hash = hash(material_name)
            author_id = (abs(name_hash) % 4) + 1  # Maps to 1, 2, 3, or 4
            return author_id
        
        # Fallback to author 2 (Italy - Alessandro) if can't determine
        return 2
    
    def write_component(
        self,
        identifier: str,
        component_type: str,
        content_data: Any
    ) -> None:
        """
        Write component content to Materials.yaml atomically.
        
        Uses atomic write pattern (write to temp → rename) to prevent corruption.
        
        Args:
            identifier: Material name
            component_type: Component type (subtitle, caption, faq, description)
            content_data: Content to write
            
        Raises:
            ValueError: If material not found
            IOError: If write fails
        """
        # Load current data
        materials_data = self.load_all_data()
        
        if identifier not in materials_data['materials']:
            raise ValueError(f"Material '{identifier}' not found in Materials.yaml")
        
        # Update component
        materials_data['materials'][identifier][component_type] = content_data
        
        # Atomic write: temp file → rename
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=self.materials_path.parent,
                delete=False,
                suffix='.yaml'
            ) as temp_f:
                yaml.dump(
                    materials_data,
                    temp_f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False
                )
                temp_path = temp_f.name
            
            # Replace original file
            Path(temp_path).replace(self.materials_path)
            
            # Invalidate cache
            self._data_cache = None
            
            logger.info(f"✅ {component_type} written to Materials.yaml → materials.{identifier}.{component_type}")
            
        except Exception as e:
            logger.error(f"Failed to write to Materials.yaml: {e}")
            raise IOError(f"Write failed: {e}")
    
    def get_enrichment_data(self, identifier: str) -> Dict[str, Any]:
        """
        Get enrichment data for material (properties, applications, etc.)
        
        Args:
            identifier: Material name
            
        Returns:
            Dict with enrichment data
        """
        item_data = self.get_item_data(identifier)
        
        facts = {
            'category': item_data.get('category', ''),
            'subcategory': item_data.get('subcategory', ''),
            'properties': {},
            'applications': item_data.get('applications', ''),
            'machine_settings': {},
            'key_challenges': ''
        }
        
        # Extract property values from nested structure
        material_props = item_data.get('materialProperties', {})
        material_chars = material_props.get('material_characteristics', {})
        for prop_name, prop_data in material_chars.items():
            if isinstance(prop_data, dict) and 'value' in prop_data:
                value = prop_data.get('value')
                unit = prop_data.get('unit', '')
                if value is not None:
                    facts['properties'][prop_name] = f"{value} {unit}".strip()
        
        # Extract machine settings from nested structure
        settings_section = item_data.get('machineSettings', {})
        laser_settings = settings_section.get('laser_settings', {})
        settings = laser_settings if laser_settings else settings_section
        for setting_name, setting_data in settings.items():
            if isinstance(setting_data, dict):
                value = setting_data.get('value')
                unit = setting_data.get('unit', '')
                if value:
                    facts['machine_settings'][setting_name] = f"{value} {unit}".strip()
        
        return facts
    
    def extract_component_content(
        self,
        text: str,
        component_type: str
    ) -> Any:
        """
        Extract component-specific content from generated text.
        
        Args:
            text: Generated text
            component_type: Component type
            
        Returns:
            Extracted content in appropriate format
        """
        if component_type == 'caption':
            return self._extract_caption(text)
        elif component_type == 'faq':
            return self._extract_faq(text)
        elif component_type == 'subtitle':
            return text.strip()
        elif component_type == 'description':
            return text.strip()
        else:
            # Default: return as-is
            return text.strip()
    
    def _extract_before_after(self, text: str) -> Dict[str, str]:
        """
        Extract before/after sections from text (used by caption component).
        
        Looks for **BEFORE_TEXT:** and **AFTER_TEXT:** markers,
        falls back to paragraph splitting if markers not found.
        
        Args:
            text: Generated caption text
            
        Returns:
            Dict with 'before' and 'after' keys
            
        Raises:
            ValueError: If extraction fails
        """
        # Try to find marked sections
        before_match = re.search(
            r'\*\*BEFORE_TEXT:\*\*\s*(.+?)(?=\*\*AFTER_TEXT:|\Z)',
            text,
            re.DOTALL
        )
        after_match = re.search(
            r'\*\*AFTER_TEXT:\*\*\s*(.+)',
            text,
            re.DOTALL
        )
        
        if not before_match or not after_match:
            # Fallback: split by paragraphs
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            if len(paragraphs) < 2:
                raise ValueError(f"Could not extract before/after sections: {text[:200]}")
            before_text = paragraphs[0]
            after_text = paragraphs[1]
        else:
            before_text = before_match.group(1).strip()
            after_text = after_match.group(1).strip()
        
        # Clean up any remaining markers
        before_text = re.sub(
            r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*',
            '',
            before_text
        ).strip()
        after_text = re.sub(
            r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*',
            '',
            after_text
        ).strip()
        
        return {
            'before': before_text,
            'after': after_text
        }
    
    def _extract_json_list(self, text: str) -> list:
        """
        Extract list items from JSON structure in text (used by faq component).
        
        Args:
            text: Generated FAQ text (should contain JSON)
            
        Returns:
            List of FAQ items (dicts with 'question' and 'answer')
            
        Raises:
            ValueError: If JSON extraction fails
        """
        # Find JSON structure
        faq_pattern = r'\{\s*"faq"\s*:\s*\[(.*?)\]\s*\}'
        matches = list(re.finditer(faq_pattern, text, re.DOTALL))
        
        if not matches:
            raise ValueError("Could not find FAQ JSON in response")
        
        # Use last match (in case of multiple)
        json_str = matches[-1].group(0)
        
        try:
            data = json.loads(json_str)
            faq_list = data.get('faq', [])
            
            if not faq_list:
                raise ValueError("FAQ list is empty")
            
            return faq_list
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid FAQ JSON: {e}")
