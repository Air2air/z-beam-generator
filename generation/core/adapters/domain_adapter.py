"""
Generic Domain Adapter

Config-driven adapter that works with ANY domain by reading from domains/*/config.yaml.
No domain-specific code - all behavior determined by configuration.

Usage:
    from generation.core.adapters.domain_adapter import DomainAdapter
    
    # For materials domain
    adapter = DomainAdapter('materials')
    
    # For settings domain  
    adapter = DomainAdapter('settings')
    
    # Uses domains/{domain}/config.yaml for all configuration
"""

import logging
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from generation.core.adapters.base import DataSourceAdapter

logger = logging.getLogger(__name__)


class DomainAdapter(DataSourceAdapter):
    """
    Generic adapter that configures itself from domain config.yaml.
    
    All domain-specific behavior comes from configuration, not code.
    
    Required config keys in domains/{domain}/config.yaml:
        data_path: Path to data YAML (e.g., "data/materials/Materials.yaml")
        data_root_key: Root key in YAML (e.g., "materials" or "settings")
        prompts: Dict of prompt templates by component type
    
    Optional config keys:
        author_key: Path to author ID in item data (default: "author.id")
        context_keys: List of keys to include in context (default: ["category"])
    """
    
    def __init__(self, domain: str, config_override: Optional[Dict] = None):
        """
        Initialize adapter for specified domain.
        
        Args:
            domain: Domain name (e.g., 'materials', 'settings')
            config_override: Optional config dict to override file loading
        """
        self.domain = domain
        self.domain_path = Path(f"domains/{domain}")
        self.config_path = self.domain_path / "config.yaml"
        
        # Load domain configuration
        if config_override:
            self.config = config_override
        else:
            self.config = self._load_domain_config()
        
        # Extract required paths from config
        self.data_path = Path(self.config.get('data_path', f"data/{domain}/{domain.title()}.yaml"))
        self.data_root_key = self.config.get('data_root_key', domain)
        
        # Optional configuration with defaults
        self.author_key = self.config.get('author_key', 'author.id')
        self.context_keys = self.config.get('context_keys', ['category'])
        
        # Cache for loaded data
        self._data_cache = None
        
        logger.info(f"DomainAdapter initialized for '{domain}' domain")
        logger.debug(f"  Data path: {self.data_path}")
        logger.debug(f"  Root key: {self.data_root_key}")
    
    def _load_domain_config(self) -> Dict[str, Any]:
        """Load configuration from domains/{domain}/config.yaml"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Domain config not found: {self.config_path}\n"
                f"Create domains/{self.domain}/config.yaml with required keys."
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.debug(f"Loaded domain config from {self.config_path}")
        return config
    
    def get_data_path(self) -> Path:
        """Get path to domain data YAML"""
        return self.data_path
    
    def load_all_data(self) -> Dict[str, Any]:
        """Load complete data structure from domain YAML"""
        if self._data_cache is None:
            if not self.data_path.exists():
                raise FileNotFoundError(f"Data file not found: {self.data_path}")
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self._data_cache = yaml.safe_load(f)
            
            item_count = len(self._data_cache.get(self.data_root_key, {}))
            logger.debug(f"Loaded {item_count} items from {self.data_path}")
        
        return self._data_cache
    
    def invalidate_cache(self):
        """Clear data cache to force reload on next access"""
        self._data_cache = None
    
    def get_item_data(self, identifier: str) -> Dict[str, Any]:
        """
        Get data for specific item.
        
        Args:
            identifier: Item name/ID
            
        Returns:
            Item data dict
            
        Raises:
            ValueError: If item not found
        """
        all_data = self.load_all_data()
        items = all_data.get(self.data_root_key, {})
        
        if identifier not in items:
            raise ValueError(
                f"'{identifier}' not found in {self.data_path} "
                f"(root key: {self.data_root_key})"
            )
        
        return items[identifier]
    
    def build_context(self, item_data: Dict[str, Any]) -> str:
        """
        Build context string from item data using configured keys.
        
        Args:
            item_data: Data for specific item
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for key in self.context_keys:
            if '.' in key:
                # Handle nested keys like "properties.density"
                value = item_data
                for part in key.split('.'):
                    value = value.get(part, {}) if isinstance(value, dict) else None
                    if value is None:
                        break
            else:
                value = item_data.get(key)
            
            if value:
                # Clean up key name for display
                display_key = key.split('.')[-1].replace('_', ' ').title()
                context_parts.append(f"{display_key}: {value}")
        
        return "\n".join(context_parts)
    
    def get_author_id(self, item_data: Dict[str, Any]) -> int:
        """
        Extract author ID from item data using configured path.
        
        For settings domain: Falls back to Materials.yaml to get material's author.
        This maintains voice consistency - settings use same author as the material.
        
        Args:
            item_data: Data for specific item
            
        Returns:
            Author ID (1-4), defaults to 1 if not found
        """
        # Navigate nested path (e.g., "author.id")
        value = item_data
        for part in self.author_key.split('.'):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        
        # If not found and domain is settings, check Materials.yaml
        if value is None and self.domain == 'settings':
            material_name = item_data.get('material')
            if material_name:
                try:
                    # Load material data to get author
                    materials_path = Path('data/materials/Materials.yaml')
                    if materials_path.exists():
                        import yaml
                        with open(materials_path, 'r') as f:
                            materials_data = yaml.safe_load(f)
                        
                        material = materials_data.get('materials', {}).get(material_name, {})
                        author_data = material.get('author', {})
                        author_id = author_data.get('id')
                        
                        if author_id:
                            logger.info(f"Using author {author_id} from Materials.yaml for {material_name}")
                            return int(author_id)
                except Exception as e:
                    logger.debug(f"Could not load author from Materials.yaml: {e}")
        
        # Fail fast - author assignment is mandatory
        if value is None:
            raise ValueError(
                f"Author ID not found at '{self.author_key}'. "
                "All items must have author.id assigned. "
                "See Author Assignment Immutability Policy in copilot-instructions.md"
            )
        
        return int(value)
    
    def get_prompt_template(self, component_type: str) -> Optional[str]:
        """
        Get prompt template for component type from domain config.
        
        Args:
            component_type: Component type (e.g., 'caption', 'component_summary')
            
        Returns:
            Prompt template string or None if not found
        """
        prompts = self.config.get('prompts', {})
        return prompts.get(component_type)
    
    def write_component(
        self,
        identifier: str,
        component_type: str,
        content_data: Any
    ) -> None:
        """
        Write generated content to domain data YAML atomically.
        
        Args:
            identifier: Item name/ID
            component_type: Component type
            content_data: Content to write
        """
        # Reload fresh data
        self.invalidate_cache()
        all_data = self.load_all_data()
        
        # Verify item exists
        items = all_data.get(self.data_root_key, {})
        if identifier not in items:
            raise ValueError(f"'{identifier}' not found in {self.data_path}")
        
        # Write content to item
        items[identifier][component_type] = content_data
        
        # Atomic write with temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=self.data_path.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.dump(all_data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name
        
        Path(temp_path).replace(self.data_path)
        self.invalidate_cache()
        
        logger.info(f"✅ {component_type} written to {self.data_path} → {self.data_root_key}.{identifier}.{component_type}")
        
        # DUAL-WRITE POLICY (MANDATORY): Immediately sync field to frontmatter
        logger.info(f"🔄 Syncing {component_type} to frontmatter for {identifier}...")
        try:
            from generation.utils.frontmatter_sync import sync_field_to_frontmatter
            sync_field_to_frontmatter(identifier, component_type, content_data, domain=self.domain)
            logger.info(f"✅ Frontmatter sync complete for {identifier}")
        except Exception as sync_error:
            logger.error(f"❌ Frontmatter sync FAILED: {sync_error}")
            import traceback
            logger.error(traceback.format_exc())
            # Don't fail the whole generation - sync failure is non-fatal
            logger.warning("⚠️  Continuing despite sync failure - frontmatter can be manually updated")
    
    def extract_content(self, raw_response: str, component_type: str) -> Any:
        """
        Extract content from API response based on extraction strategy.
        
        Strategy is determined by generation/config.yaml component_extraction settings.
        
        Args:
            raw_response: Raw API response text
            component_type: Component type for strategy lookup
            
        Returns:
            Extracted content (string, dict, or list depending on strategy)
        """
        # Load extraction strategy from central config
        from generation.config.config_loader import get_config
        config = get_config()
        extraction_config = config.config.get('component_extraction', {})
        component_config = extraction_config.get(component_type, {})
        strategy = component_config.get('extraction_strategy', 'raw')
        
        # Apply extraction strategy
        if strategy == 'raw':
            return raw_response.strip()
        
        elif strategy == 'before_after':
            return self._extract_before_after(raw_response)
        
        elif strategy == 'json_list':
            return self._extract_json_list(raw_response)
        
        elif strategy == 'yaml':
            return self._extract_yaml(raw_response)
        
        else:
            logger.warning(f"Unknown extraction strategy '{strategy}', using raw")
            return raw_response.strip()
    
    def _extract_before_after(self, text: str) -> Dict[str, str]:
        """Extract before/after paragraph structure"""
        import re
        
        # Clean the text
        text = text.strip()
        
        # Try to split on double newline
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        
        if len(paragraphs) >= 2:
            return {
                'before': paragraphs[0],
                'after': paragraphs[1]
            }
        elif len(paragraphs) == 1:
            # Single paragraph - use as both
            return {
                'before': paragraphs[0],
                'after': paragraphs[0]
            }
        else:
            return {'before': text, 'after': text}
    
    def _extract_json_list(self, text: str) -> list:
        """Extract JSON list (for FAQ)"""
        import json
        import re
        
        # Try to find JSON array in response
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback: parse Q&A format
        qa_pairs = []
        pattern = r'\*\*(.+?)\*\*\s*\n\s*(.+?)(?=\n\n|\n\*\*|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for question, answer in matches:
            qa_pairs.append({
                'question': question.strip().rstrip('?') + '?',
                'answer': answer.strip()
            })
        
        return qa_pairs
    
    def _extract_yaml(self, text: str) -> Dict[str, Any]:
        """Extract YAML structure from response"""
        import re
        
        # Try to find YAML block
        yaml_match = re.search(r'```yaml\s*([\s\S]*?)\s*```', text)
        if yaml_match:
            try:
                return yaml.safe_load(yaml_match.group(1))
            except yaml.YAMLError:
                pass
        
        # Try parsing entire response as YAML
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError:
            pass
        
        # Fallback: return as raw string wrapped in dict
        return {'content': text.strip()}
    
    # =========================================================================
    # Abstract method implementations required by DataSourceAdapter
    # =========================================================================
    
    def extract_component_content(self, text: str, component_type: str) -> Any:
        """
        Extract component-specific content from generated text.
        
        Wraps extract_content() to satisfy DataSourceAdapter interface.
        
        Args:
            text: Generated text
            component_type: Component type
            
        Returns:
            Extracted content in appropriate format
        """
        return self.extract_content(text, component_type)
    
    def get_enrichment_data(self, identifier: str) -> Dict[str, Any]:
        """
        Get enrichment data (facts, properties, etc.) for prompt building.
        
        Builds a dict of relevant item data for prompt enrichment.
        
        Args:
            identifier: Item identifier
            
        Returns:
            Dict with enrichment data
        """
        try:
            item_data = self.get_item_data(identifier)
        except ValueError:
            logger.warning(f"Could not load data for '{identifier}', returning empty enrichment")
            return {}
        
        enrichment = {
            'identifier': identifier,
            'item_data': item_data,
            'context': self.build_context(item_data)
        }
        
        # Add common enrichment fields if present
        for key in ['category', 'properties', 'materialProperties', 'applications', 
                    'machine_settings', 'description', 'challenges']:
            if key in item_data:
                enrichment[key] = item_data[key]
        
        return enrichment
