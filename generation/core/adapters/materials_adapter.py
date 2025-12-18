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

from generation.core.adapters.base import DataSourceAdapter

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
        
        # NO DESCRIPTION - it acts as an example template that LLM copies
        # Only provide category/subcategory for classification context
        
        # Extract key properties
        properties = item_data.get('properties', {})
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
        
        # FAIL-FAST: Material must have author.id - no hash fallback
        if not item_data:
            raise ValueError("item_data is required - cannot determine author without material data")
        
        from data.authors.registry import resolve_author_for_generation
        author_info = resolve_author_for_generation(item_data)
        return author_info['id']
    
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
            component_type: Component type (micro, faq, description)
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
        material_props = item_data.get('properties', {})
        material_chars = material_props.get('material_characteristics', {})
        for prop_name, prop_data in material_chars.items():
            if isinstance(prop_data, dict) and 'value' in prop_data:
                value = prop_data.get('value')
                unit = prop_data.get('unit', '')
                if value is not None:
                    facts['properties'][prop_name] = f"{value} {unit}".strip()
        
        # Extract machine settings from nested structure
        settings_section = item_data.get('machine_settings', {})
        laser_settings = settings_section.get('laser_settings', {})
        settings = laser_settings if laser_settings else settings_section
        for setting_name, setting_data in settings.items():
            if isinstance(setting_data, dict):
                value = setting_data.get('value')
                unit = setting_data.get('unit', '')
                if value:
                    facts['machine_settings'][setting_name] = f"{value} {unit}".strip()
        
        return facts
    
    def extract_content(
        self,
        text: str,
        component_type: str
    ) -> Any:
        """
        Extract content using strategy pattern based on component type.
        
        Strategy is determined by ComponentRegistry.get_spec(component_type).extraction_strategy
        
        Args:
            text: Generated text
            component_type: Component type
            
        Returns:
            Extracted content in appropriate format
            
        Raises:
            ValueError: If extraction fails or unknown strategy
        """
        from shared.text.utils.component_specs import ComponentRegistry
        
        # Get extraction strategy for this component
        try:
            spec = ComponentRegistry.get_spec(component_type)
            strategy = spec.extraction_strategy
        except KeyError:
            # Fallback to 'raw' for unknown components
            strategy = 'raw'
        
        # Apply strategy
        if strategy == 'raw':
            return text.strip()
        elif strategy == 'before_after':
            return self._extract_before_after(text)
        elif strategy == 'json_list':
            return self._extract_json_list(text)
        elif strategy == 'yaml':
            return self._extract_yaml(text)
        else:
            raise ValueError(f"Unknown extraction strategy: {strategy}")
    
    def extract_component_content(
        self,
        text: str,
        component_type: str
    ) -> Any:
        """
        DEPRECATED: Use extract_content() instead.
        Extract component-specific content from generated text.
        
        Args:
            text: Generated text
            component_type: Component type
            
        Returns:
            Extracted content in appropriate format
        """
        # Delegate to new strategy-based method
        return self.extract_content(text, component_type)
    
    def _extract_before_after(self, text: str) -> Dict[str, str]:
        """
        Extract before/after sections from text (used by micro component).
        
        Looks for **BEFORE_TEXT:** and **AFTER_TEXT:** markers,
        falls back to paragraph splitting if markers not found.
        
        Args:
            text: Generated micro text
            
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
                # Only one paragraph - treat as "before" micro only
                before_text = paragraphs[0] if paragraphs else text.strip()
                after_text = ''
            else:
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
            text: Generated FAQ text (should contain JSON or markdown list)
            
        Returns:
            List of FAQ items (dicts with 'question' and 'answer')
            
        Raises:
            ValueError: If extraction fails
        """
        # Try Strategy 1: JSON structure
        faq_pattern = r'\{\s*"faq"\s*:\s*\[(.*?)\]\s*\}'
        matches = list(re.finditer(faq_pattern, text, re.DOTALL))
        
        if matches:
            # Use last match (in case of multiple)
            json_str = matches[-1].group(0)
            
            try:
                data = json.loads(json_str)
                faq_list = data.get('faq', [])
                
                if faq_list:
                    return faq_list
            except json.JSONDecodeError:
                pass  # Fall through to markdown parsing
        
        # Try Strategy 2: Markdown Q&A format with **question** markers (Grok pattern)
        # Grok generates: **[question text]** \n [answer]
        # Questions can end with ? or . (sometimes statements like "Tell me about...")
        nested_pattern = r'\*\*([^*]+?[.?])\*\*\s*\n(.+?)(?=\n\*\*|$)'
        nested_matches = re.findall(nested_pattern, text, re.DOTALL)
        
        if nested_matches and len(nested_matches) >= 1:  # Accept even single Q&A if in bold format
            faq_list = []
            for question, answer in nested_matches:
                faq_list.append({
                    'question': question.strip(),
                    'answer': answer.strip()
                })
            return faq_list
        
        # Try Strategy 3: Top-level **Q1:** markers  
        # Look for "**Q1:**" or "**Q:**" followed by answer text
        qa_pattern = r'\*\*Q\d+:?\*\*\s*(.+?)\n\n(.+?)(?=\*\*Q\d+:?\*\*|$)'
        qa_matches = re.findall(qa_pattern, text, re.DOTALL)
        
        if qa_matches:
            faq_list = []
            for question, answer in qa_matches:
                faq_list.append({
                    'question': question.strip(),
                    'answer': answer.strip()
                })
            return faq_list
        
        # Try Strategy 4: Plain Q: / A: format (fallback)
        qa_pattern2 = r'(?:Q\d*|Question\d*):\s*(.+?)\s*(?:A\d*|Answer\d*):\s*(.+?)(?=(?:Q\d*|Question\d*|$))'
        qa_matches2 = re.findall(qa_pattern2, text, re.DOTALL | re.IGNORECASE)
        
        if qa_matches2:
            faq_list = []
            for question, answer in qa_matches2:
                faq_list.append({
                    'question': question.strip(),
                    'answer': answer.strip()
                })
            return faq_list
        
        # Try Strategy 3: Markdown with header format (### Title)
        # Split by headers and look for Q&A pairs
        header_pattern = r'###\s*(.+?)\n\n(.+?)(?=###|$)'
        header_matches = re.findall(header_pattern, text, re.DOTALL)
        
        if header_matches:
            faq_list = []
            for question, answer in header_matches:
                faq_list.append({
                    'question': question.strip(),
                    'answer': answer.strip()
                })
            return faq_list
        
        raise ValueError("Could not extract FAQ Q&A pairs from response")

    def _extract_yaml(self, text: str) -> Dict:
        """
        Extract YAML structure from text (used by component_summaries).
        
        Handles:
        - Code blocks with ```yaml ... ``` markers
        - Raw YAML without code block markers
        
        Args:
            text: Generated text containing YAML structure
            
        Returns:
            Parsed YAML as dict
            
        Raises:
            ValueError: If extraction fails
        """
        import yaml
        
        # Strategy 1: Extract from ```yaml code block
        yaml_block_pattern = r'```(?:yaml)?\s*\n?(.*?)```'
        matches = re.findall(yaml_block_pattern, text, re.DOTALL)
        
        if matches:
            # Use the last match (most complete)
            yaml_text = matches[-1].strip()
            try:
                return yaml.safe_load(yaml_text)
            except yaml.YAMLError:
                pass  # Fall through to raw parsing
        
        # Strategy 2: Try to parse raw text as YAML
        # Look for YAML-like structure (key: value patterns)
        if ':' in text:
            try:
                # Remove any leading/trailing non-YAML content
                lines = text.split('\n')
                yaml_lines = []
                in_yaml = False
                
                for line in lines:
                    # Start capturing at first key: line
                    if not in_yaml and re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*:', line):
                        in_yaml = True
                    if in_yaml:
                        yaml_lines.append(line)
                
                if yaml_lines:
                    yaml_text = '\n'.join(yaml_lines)
                    return yaml.safe_load(yaml_text)
            except yaml.YAMLError:
                pass
        
        raise ValueError("Could not extract YAML structure from response")
