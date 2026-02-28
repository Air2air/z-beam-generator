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
import json
import re
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from shared.utils.yaml_utils import load_yaml
from shared.text.utils.prompt_registry_service import PromptRegistryService

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
        
        # Extract required paths from nested config (fail-fast)
        if 'data_adapter' not in self.config or not isinstance(self.config['data_adapter'], dict):
            raise ValueError(
                f"Domain '{domain}' config must define 'data_adapter' object with required keys"
            )

        adapter_config = self.config['data_adapter']
        required_keys = ['data_path', 'data_root_key', 'author_key', 'context_keys']
        missing = [key for key in required_keys if key not in adapter_config]
        if missing:
            raise KeyError(
                f"Domain '{domain}' data_adapter missing required keys: {', '.join(missing)}"
            )

        self.data_path = Path(adapter_config['data_path'])
        self.data_root_key = adapter_config['data_root_key']
        self.author_key = adapter_config['author_key']
        self.context_keys = adapter_config['context_keys']
        self.domain_generation = self._get_domain_generation_config()
        self.author_resolution = self._get_author_resolution_config(self.domain_generation)
        
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

    def _get_domain_generation_config(self) -> Dict[str, Any]:
        from generation.config.config_loader import get_config

        config = get_config().config
        domain_generation = config.get('domain_generation')
        if not isinstance(domain_generation, dict):
            raise KeyError("Missing required config block: domain_generation")
        if self.domain not in domain_generation:
            raise KeyError(
                f"Missing domain_generation config for domain '{self.domain}'"
            )
        domain_config = domain_generation[self.domain]
        if not isinstance(domain_config, dict):
            raise TypeError(
                f"domain_generation.{self.domain} must be a dictionary"
            )
        return domain_config

    def _get_author_resolution_config(self, domain_generation: Dict[str, Any]) -> Dict[str, Any]:
        author_resolution = domain_generation.get('author_resolution')
        if not isinstance(author_resolution, dict):
            raise KeyError(
                f"domain_generation.{self.domain}.author_resolution must be a dictionary"
            )
        if 'strategy' not in author_resolution:
            raise KeyError(
                f"domain_generation.{self.domain}.author_resolution missing required key: strategy"
            )
        if not isinstance(author_resolution['strategy'], str):
            raise TypeError(
                f"domain_generation.{self.domain}.author_resolution.strategy must be a string"
            )
        return author_resolution
    
    def get_data_path(self) -> Path:
        """Get path to domain data YAML"""
        return self.data_path

    def get_items_root(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Public wrapper for resolving domain items root."""
        return self._get_items_root(all_data)
    
    def load_all_data(self) -> Dict[str, Any]:
        """Load complete data structure from domain YAML"""
        if self._data_cache is None:
            if not self.data_path.exists():
                raise FileNotFoundError(f"Data file not found: {self.data_path}")
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self._data_cache = yaml.safe_load(f)

            items = self._get_items_root(self._data_cache)
            self._normalize_author_identity(items)
            item_count = len(items)
            logger.debug(f"Loaded {item_count} items from {self.data_path}")
        
        return self._data_cache

    def _normalize_author_identity(self, items: Dict[str, Any]) -> None:
        """Normalize legacy authorId into canonical in-memory author shape."""
        if not isinstance(items, dict):
            return

        for item_data in items.values():
            if not isinstance(item_data, dict):
                continue

            if 'author' in item_data:
                continue

            legacy_author_id = item_data.get('authorId')
            if isinstance(legacy_author_id, int):
                item_data['author'] = {'id': legacy_author_id}

    def _get_items_root(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve configured root key with strict fail-fast contract."""
        if not isinstance(all_data, dict):
            raise ValueError(f"Expected domain data to be dict, got: {type(all_data)}")

        if self.data_root_key in all_data:
            items = all_data[self.data_root_key]
            if not isinstance(items, dict):
                raise ValueError(
                    f"Root key '{self.data_root_key}' in {self.data_path} must map to dict, got: {type(items)}"
                )
            return items

        raise KeyError(
            f"Missing required root key '{self.data_root_key}' in {self.data_path}. "
            "Configure domains/<domain>/config.yaml data_adapter.data_root_key to match source data exactly."
        )
    
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
        items = self._get_items_root(all_data)
        
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
                    if not isinstance(value, dict):
                        value = None
                        break
                    if part not in value:
                        value = None
                        break
                    value = value[part]
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
        
        # Schema compatibility: support canonical top-level authorId across domains
        if value is None:
            legacy_author_id = item_data.get('authorId')
            if legacy_author_id is not None:
                value = legacy_author_id

        # Source-data compatibility: support scalar top-level author reference
        if value is None:
            scalar_author_id = item_data.get('author')
            if isinstance(scalar_author_id, int):
                value = scalar_author_id

        if value is None:
            strategy = self.author_resolution['strategy']
            if strategy == 'inherit_from_material':
                material_key = self.author_resolution.get('material_key')
                source_path = self.author_resolution.get('source_data_path')
                source_root_key = self.author_resolution.get('source_root_key')
                source_author_key = self.author_resolution.get('source_author_key')

                missing = [
                    key for key in ['material_key', 'source_data_path', 'source_root_key', 'source_author_key']
                    if self.author_resolution.get(key) in [None, '']
                ]
                if missing:
                    raise KeyError(
                        f"Author resolution strategy 'inherit_from_material' missing keys: {', '.join(missing)}"
                    )

                material_name = item_data.get(material_key)
                if material_name:
                    try:
                        materials_path = Path(source_path)
                        if not materials_path.exists():
                            raise FileNotFoundError(f"Author source data not found: {materials_path}")

                        import yaml
                        with open(materials_path, 'r') as f:
                            materials_data = yaml.safe_load(f)

                        if not isinstance(materials_data, dict) or source_root_key not in materials_data:
                            raise KeyError(
                                f"Source data missing required root key '{source_root_key}': {materials_path}"
                            )
                        if material_name not in materials_data[source_root_key]:
                            raise KeyError(
                                f"Material '{material_name}' not found in {materials_path} for author resolution"
                            )

                        material = materials_data[source_root_key][material_name]
                        author_data = material
                        for part in str(source_author_key).split('.'):
                            if isinstance(author_data, dict):
                                author_data = author_data.get(part)
                            else:
                                author_data = None
                                break

                        if author_data is not None:
                            logger.info(f"Using author {author_data} from {materials_path} for {material_name}")
                            return int(author_data)
                    except Exception as e:
                        raise RuntimeError(
                            f"Failed resolving author from {source_path} for '{material_name}': {e}"
                        ) from e
            elif strategy != 'direct':
                raise ValueError(
                    f"Unknown author resolution strategy '{strategy}' for domain '{self.domain}'"
                )
        
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
        Get prompt template for component type from schema registry.
        
        Args:
            component_type: Component type (e.g., 'micro', 'contaminatedBy', 'materialCharacteristics')
            
        Returns:
            Prompt template string

        Raises:
            ValueError: If prompt cannot be resolved from schema/registry
        """
        schema_prompt = self._get_schema_prompt(component_type)
        if schema_prompt:
            return schema_prompt

        raise ValueError(
            f"No schema prompt resolved for component '{component_type}' in domain '{self.domain}'. "
            "Fail-fast prompt architecture requires schema/registry prompt resolution."
        )
    
    def _get_schema_prompt(self, component_type: str) -> Optional[str]:
        """
        Load prompt from section_display_schema.yaml.
        
        Args:
            component_type: Component type to look up
            
        Returns:
            Prompt string or None if not found in schema
        """
        return PromptRegistryService.get_schema_prompt(
            domain=self.domain,
            component_type=component_type,
            include_descriptor=True,
        )

    def get_section_metadata(self, component_type: str) -> Dict[str, Any]:
        """
        Get section metadata (title, description, icon, etc.) from schema.
        
        Args:
            component_type: Component type to look up
            
        Returns:
            Dict with title, description, icon, order, variant, wordCount
        """
        section_data = PromptRegistryService.get_section(component_type)
        if not section_data:
            raise ValueError(f"No section metadata found for component '{component_type}'")

        required_keys = ['title', 'description', 'icon', 'order', 'variant', 'wordCount']
        missing = [key for key in required_keys if key not in section_data]
        if missing:
            raise KeyError(
                f"Section metadata for '{component_type}' missing required keys: {', '.join(missing)}"
            )

        return {
            'title': section_data['title'],
            'description': section_data['description'],
            'icon': section_data['icon'],
            'order': section_data['order'],
            'variant': section_data['variant'],
            'wordCount': section_data['wordCount']
        }
    
    def write_component(
        self,
        identifier: str,
        component_type: str,
        content_data: Any
    ) -> None:
        """
        Write generated content to domain data YAML atomically.
        
        SCHEMA INTEGRATION (Jan 13, 2026):
        Supports schema-based generation with title/description parsing.
        
        CORE PRINCIPLE 0.6 COMPLIANCE (Jan 5, 2026):
        Enriches data at GENERATION TIME, not export time.
        Adds: expanded author, timestamps, id, breadcrumbs.
        
        PHASE 2 FIX (Jan 5, 2026):
        Converts collapsible components (FAQ, applications, standards) to unified format
        BEFORE saving to source YAML. Export tasks will eventually become no-ops.
        
        Args:
            identifier: Item name/ID
            component_type: Component type
            content_data: Content to write (may be parsed into title/description)
        """
        # Reload fresh data
        self.invalidate_cache()
        all_data = self.load_all_data()
        
        # Verify item exists
        items = self._get_items_root(all_data)
        if identifier not in items:
            raise ValueError(f"'{identifier}' not found in {self.data_path}")
        
        # CHECK FOR SCHEMA-BASED GENERATION (NEW Jan 13, 2026)
        schema_metadata = self.get_section_metadata(component_type)
        if schema_metadata and self._is_schema_based_component(component_type):
            # Check if this is new generation or conversion of existing content
            if isinstance(content_data, dict) and 'title' in content_data:
                # Already schema-formatted content (from new generation)
                content_to_save = content_data
            else:
                # Convert existing content with embedded titles to schema format
                content_to_save = self._convert_existing_to_schema_format(content_data, schema_metadata)
                logger.info(f"📝 Schema-based conversion for {component_type}: separated title + description")
        else:
            # LEGACY: Convert to collapsible format if applicable
            content_to_save = self._convert_to_collapsible_if_needed(
                content_data, 
                component_type, 
                identifier,
                items.get(identifier)  # Pass item data for author/metadata
            )

        normalize_components = self.domain_generation.get('normalize_components')
        if not isinstance(normalize_components, list):
            raise KeyError(
                f"domain_generation.{self.domain}.normalize_components must be a list"
            )
        if component_type in normalize_components:
            content_to_save = self._normalize_page_description_output(content_to_save)
        
        # Determine target field (may differ from component_type)
        target_field = self._get_target_field(component_type)
        
        # Write content to target field
        if '.' in target_field:
            # Nested field (e.g., 'operational.expert_answers')
            parts = target_field.split('.')
            current = items[identifier]
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = content_to_save
        else:
            # Top-level field
            items[identifier][target_field] = content_to_save
        
        # GENERATION-TIME ENRICHMENT (Jan 5, 2026): Add ALL metadata at generation time
        # Complies with Core Principle 0.6: "No Build-Time Data Enhancement"
        logger.info(f"🔧 Enriching {identifier} with generation-time metadata...")
        from generation.context.generation_metadata import enrich_for_generation
        items[identifier] = enrich_for_generation(items[identifier], identifier, self.domain)
        logger.info(f"✅ Generation-time enrichment complete for {identifier}")
        
        # PHASE 2 (Jan 7, 2026): Add complete software metadata at generation time
        logger.info(f"🔧 Adding software metadata for {identifier}...")
        items[identifier] = self.enrich_on_save(items[identifier], identifier)
        logger.info(f"✅ Software metadata complete for {identifier}")
        
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
            sync_field_to_frontmatter(identifier, component_type, content_to_save, domain=self.domain)
            logger.info(f"✅ Frontmatter sync complete for {identifier}.{component_type}")
        except Exception as sync_error:
            raise RuntimeError(
                f"Frontmatter sync failed for {identifier}.{component_type}: {sync_error}"
            ) from sync_error
    
    def _get_target_field(self, component_type: str) -> str:
        """
        Get target field name for component type.
        
        Maps component types to their storage location in data YAML.
        Some components save to different field names.
        """
        field_mappings = self.domain_generation.get('field_mappings')
        if not isinstance(field_mappings, dict):
            raise KeyError(
                f"domain_generation.{self.domain}.field_mappings must be a dictionary"
            )
        if component_type in field_mappings:
            return field_mappings[component_type]
        return component_type
    
    def _convert_to_collapsible_if_needed(
        self, 
        content_data: Any, 
        component_type: str, 
        identifier: str,
        item_data: Optional[Dict] = None
    ) -> Any:
        """
        Convert content to collapsible format if component type requires it.
        
        PHASE 2 FIX (Jan 5, 2026): Implements build-time policy compliance.
        New content generated after Jan 5, 2026 will be saved in collapsible format.
        
        Args:
            content_data: Raw content from generation
            component_type: Component type
            identifier: Material/item name
            
        Returns:
            Content in appropriate format (collapsible or original)
        """
        if component_type == 'faq':
            return self._normalize_faq_content(content_data, item_data)

        # Check if data already has presentation format (already structured)
        if isinstance(content_data, dict) and 'presentation' in content_data:
            logger.debug(f"✅ {component_type} already in structured format (presentation: {content_data.get('presentation')})")
            return content_data

        # If data is already structured but missing presentation field, infer it
        if isinstance(content_data, dict) and 'items' in content_data:
            logger.debug(f"✅ {component_type} has items structure, returning as-is")
            return content_data
        
        # Data is raw (list/simple format) - needs conversion
        # Infer conversion type from data structure
        if isinstance(content_data, list):
            logger.debug(f"Raw list data for {component_type}, returning as-is")
            return content_data
        
        # Unknown format, return as-is
        return content_data

    def _build_faq_section_metadata(self) -> Optional[Dict[str, Any]]:
        """Build FAQ _section metadata from canonical schema metadata."""
        section_metadata = self.get_section_metadata('faq')
        if not section_metadata:
            return None

        return {
            'sectionTitle': section_metadata['title'],
            'sectionDescription': section_metadata['description'],
            'sectionMetadata': 'faq',
            'icon': section_metadata['icon'],
            'order': section_metadata['order'],
            'variant': section_metadata['variant']
        }

    def _normalize_faq_content(self, content_data: Any, item_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Normalize FAQ content using the standard text pipeline with leaf-level Q/A shaping only."""
        if isinstance(content_data, dict) and content_data.get('presentation') == 'collapsible':
            items = content_data.get('items')
            if not isinstance(items, list):
                raise ValueError("FAQ collapsible payload missing required list at 'items'")
            return self._convert_faq_to_collapsible(items, item_data)

        if isinstance(content_data, dict) and isinstance(content_data.get('items'), list):
            return self._convert_faq_to_collapsible(content_data['items'], item_data)

        if isinstance(content_data, list):
            return self._convert_faq_to_collapsible(content_data, item_data)

        if isinstance(content_data, str):
            faq_items = self._extract_json_list(content_data)
            return self._convert_faq_to_collapsible(faq_items, item_data)

        raise ValueError(f"Unsupported FAQ content type: {type(content_data).__name__}")

    def _normalize_page_description_output(self, content: Any) -> Any:
        """
        Normalize pageDescription output to clean prose.

        Handles common generator outputs:
        - JSON section payloads with sectionContent/sectionDescription
        - Markdown headings (e.g., "### Laser Cleaning Aluminum")
        - Template labels (e.g., "### Title:", "### Description:")
        """
        if not isinstance(content, str):
            return content

        text = content.strip()
        if not text:
            return text

        # Try JSON payload extraction first
        if text.startswith('{') and text.endswith('}'):
            try:
                payload = json.loads(text)
                extracted = (
                    payload.get('sectionContent')
                    or payload.get('sectionDescription')
                    or payload.get('description')
                )
                if isinstance(extracted, str) and extracted.strip():
                    text = extracted.strip()
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON payload in pageDescription output") from exc

        # Remove explicit template labels
        text = re.sub(r"(?im)^\s*#{1,6}\s*title\s*:\s*", "", text)
        text = re.sub(r"(?im)^\s*#{1,6}\s*description\s*:\s*", "", text)

        # If description marker appears inline, keep only the description segment
        inline_desc = re.split(r"(?i)#{1,6}\s*description\s*:\s*", text, maxsplit=1)
        if len(inline_desc) == 2:
            text = inline_desc[1].strip()

        # Remove leading markdown heading line only
        text = re.sub(r"\A\s*#{1,6}\s+[^\n]+\n+", "", text)

        # Remove any remaining markdown heading tokens inline
        text = re.sub(r"(?i)#{1,6}\s*title\s*:\s*", "", text)
        text = re.sub(r"(?i)#{1,6}\s*description\s*:\s*", "", text)

        # Normalize spacing and punctuation artifacts
        text = re.sub(r"\n{2,}", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()
        text = text.replace('..', '.')

        return text
    
    def _convert_faq_to_collapsible(self, faq_data: list, item_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Convert FAQ list to unified collapsible structure with complete metadata.
        
        MAXIMUM FORMATTING AT SOURCE (Jan 7, 2026):
        Generates complete collapsible FAQ structure during generation, not during export.
        Includes ALL metadata: expertInfo, severity, topic, acceptedAnswer.
        
        Per Core Principle 0.6: Maximum data population at source.
        
        Input format (from generation):
        [
            {'question': 'Q1?', 'answer': 'A1'},
            {'question': 'Q2?', 'answer': 'A2'}
        ]
        
        Output format (collapsible with full metadata):
        {
            'presentation': 'collapsible',
            'items': [
                {
                    'id': 'suitable-for-industrial',
                    'title': 'Q1?',
                    'content': 'A1',
                    'metadata': {
                        'topic': 'suitable for industrial',
                        'severity': 'medium',
                        'acceptedAnswer': True,
                        'expertInfo': {...}
                    },
                    '_display': {'_open': True, 'order': 1}
                }
            ],
            'options': {'autoOpenFirst': True, 'sortBy': 'severity'}
        }
        """
        if not isinstance(faq_data, list):
            logger.warning(f"FAQ data not a list, returning as-is: {type(faq_data)}")
            return faq_data
        
        # Get author info for expert metadata
        expert_info = None
        if item_data and isinstance(item_data, dict):
            author_data = item_data.get('author')
            if author_data and isinstance(author_data, dict):
                required_author_fields = ['name', 'title', 'expertise']
                if all(field in author_data for field in required_author_fields):
                    expert_info = {
                        'name': author_data['name'],
                        'title': author_data['title'],
                        'expertise': author_data['expertise']
                    }
        
        # Severity keywords for classification
        severity_keywords = {
            'critical': ['damage', 'safety', 'hazard', 'prevent', 'fragile', 'sensitive'],
            'high': ['suitable', 'ideal', 'restore', 'optimize', 'proper'],
            'medium': ['effective', 'clean', 'remove', 'work', 'use'],
            'low': ['maintain', 'typical', 'common', 'regular']
        }
        
        items = []
        for idx, faq in enumerate(faq_data):
            if not isinstance(faq, dict):
                raise ValueError(f"FAQ item at index {idx} must be dict, got: {type(faq)}")
            
            if 'question' not in faq or 'answer' not in faq:
                raise KeyError(f"FAQ item at index {idx} missing required keys 'question' and/or 'answer'")
            question = faq['question']
            answer = faq['answer']
            
            if not isinstance(question, str) or not question.strip():
                raise ValueError(f"FAQ item at index {idx} has invalid question value")
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError(f"FAQ item at index {idx} has invalid answer value")
            
            # Generate ID from question
            faq_id = question.lower()
            faq_id = ''.join(c if c.isalnum() or c.isspace() else '' for c in faq_id)
            faq_id = '-'.join(faq_id.split()[:6])  # First 6 words
            
            # Extract topic (first few meaningful words from question)
            topic = question.lower().replace('?', '')
            for word in ['what', 'how', 'why', 'when', 'where', 'does', 'is', 'are', 'can']:
                topic = topic.replace(word, '')
            topic = ' '.join(topic.split()[:5]).strip()
            
            # Classify severity based on keywords in question and answer
            text_combined = (question + ' ' + answer).lower()
            severity = 'medium'  # default
            for sev, keywords in severity_keywords.items():
                if any(keyword in text_combined for keyword in keywords):
                    severity = sev
                    break
            
            # Build item with complete metadata
            item = {
                'id': faq_id,
                'title': question,
                'content': answer,
                'metadata': {
                    'topic': topic,
                    'severity': severity,
                    'acceptedAnswer': True
                },
                '_display': {
                    '_open': idx == 0,  # First item open
                    'order': idx + 1
                }
            }
            
            # Add expert info if available
            if expert_info:
                item['metadata']['expertInfo'] = expert_info
            
            items.append(item)
        
        logger.info(f"✅ Converted {len(items)} FAQ items to collapsible format with full metadata")

        section = self._build_faq_section_metadata()
        normalized_faq = {}
        if section:
            normalized_faq['_section'] = section

        normalized_faq.update({
            'presentation': 'collapsible',
            'items': items,
            'options': {
                'autoOpenFirst': True,
                'sortBy': 'severity'
            }
        })

        return normalized_faq
    
    def _convert_applications_to_card(self, apps_data: list) -> Dict[str, Any]:
        """
        Convert applications list to card format structure.
        
        Input: ['Aerospace', 'Automotive', 'Medical']
        
        Output: Card format with items
        """
        if not isinstance(apps_data, list):
            logger.warning(f"Applications data not a list, returning as-is: {type(apps_data)}")
            return apps_data
        
        items = []
        for idx, app_name in enumerate(apps_data):
            if not isinstance(app_name, str):
                continue
            
            # Generate brief description (placeholder - could be enhanced with AI)
            description = f"{app_name} industry applications and manufacturing requirements for laser cleaning."
            
            items.append({
                'title': app_name,
                'description': description,
                'metadata': {
                    'category': 'Industrial Applications',
                    'commonality': 'common'
                },
                'order': idx + 1
            })
        
        logger.info(f"✅ Converted {len(items)} applications to card format")
        
        return {
            'presentation': 'card',
            'items': items
        }
    
    def _convert_standards_to_collapsible(self, standards_data: Any) -> Dict[str, Any]:
        """
        Convert regulatory standards to unified collapsible structure.
        
        Input could be:
        - List of standard objects
        - Dict with 'items' key
        - Already collapsible format
        """
        # If already collapsible, return as-is
        if isinstance(standards_data, dict) and standards_data.get('presentation') == 'collapsible':
            logger.info("Standards already in collapsible format")
            return standards_data
        
        # Extract items
        if isinstance(standards_data, dict) and 'items' in standards_data:
            items_list = standards_data['items']
        elif isinstance(standards_data, list):
            items_list = standards_data
        else:
            logger.warning(f"Standards data format unknown, returning as-is: {type(standards_data)}")
            return standards_data
        
        items = []
        for idx, standard in enumerate(items_list):
            if not isinstance(standard, dict):
                raise ValueError(f"Standard item at index {idx} must be dict, got: {type(standard)}")
            
            if 'description' not in standard:
                raise KeyError(f"Standard item at index {idx} missing required key 'description'")

            name = standard.get('name')
            long_name = standard.get('longName')
            description = standard['description']

            if not isinstance(description, str) or not description.strip():
                raise ValueError(f"Standard item at index {idx} has invalid description")

            if name is not None and not isinstance(name, str):
                raise ValueError(f"Standard item at index {idx} has non-string name")
            if long_name is not None and not isinstance(long_name, str):
                raise ValueError(f"Standard item at index {idx} has non-string longName")

            if not (isinstance(name, str) and name.strip()) and not (isinstance(long_name, str) and long_name.strip()):
                raise ValueError(f"Standard item at index {idx} must include non-empty 'name' or 'longName'")
            
            if isinstance(name, str) and name.strip() and isinstance(long_name, str) and long_name.strip():
                title = f"{name} - {long_name}"
            else:
                title = name if isinstance(name, str) and name.strip() else long_name

            if title is None:
                raise ValueError(f"Failed to build title for standard item at index {idx}")

            metadata = {
                'organization': name,
                'category': 'laser-safety'
            }

            if 'url' in standard:
                metadata['url'] = standard['url']
            if 'image' in standard:
                metadata['image'] = standard['image']
            
            items.append({
                'title': title,
                'content': description,
                'metadata': metadata,
                '_display': {
                    '_open': idx == 0,  # First item open
                    'order': idx + 1
                }
            })
        
        logger.info(f"✅ Converted {len(items)} standards to collapsible format")
        
        return {
            'presentation': 'collapsible',
            'items': items
        }
    
    def extract_content(self, raw_response: str, component_type: str) -> Any:
        """
        Extract content from API response based on extraction strategy.
        
        Strategy is determined by generation/config.yaml component_extraction settings.
        
        SCHEMA-BASED COMPONENTS (NEW Jan 14, 2026):
        For schema-based components (contaminatedBy, relatedMaterials, etc.),
        automatically parses "Title: ... Description: ..." format into structured dict.
        
        Args:
            raw_response: Raw API response text
            component_type: Component type for strategy lookup
            
        Returns:
            Extracted content (string, dict, or list depending on strategy)
        """
        # CHECK FOR SCHEMA-BASED COMPONENT FIRST (Priority over config strategy)
        if self._is_schema_based_component(component_type):
            # Parse Title/Description format into structured dict
            import re
            
            # Try to extract Title and Description from formatted output
            title_match = re.search(r'(?:^|\n)\s*Title:\s*(.+?)(?:\n|$)', raw_response, re.MULTILINE)
            desc_match = re.search(r'(?:^|\n)\s*Description:\s*(.+?)(?=\n\n|\Z)', raw_response, re.MULTILINE | re.DOTALL)
            
            if title_match and desc_match:
                # Successful parse - return structured dict
                schema_metadata = self.get_section_metadata(component_type)
                return {
                    'title': title_match.group(1).strip(),
                    'description': desc_match.group(1).strip(),
                    '_metadata': {
                        'icon': schema_metadata['icon'],
                        'order': schema_metadata['order'],
                        'variant': schema_metadata['variant'],
                        'generatedAt': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
                    }
                }
            else:
                raise ValueError(
                    f"Schema component '{component_type}' response missing required Title/Description format"
                )
        
        # Load extraction strategy from central config for non-schema components
        from generation.config.config_loader import get_config
        config = get_config()
        strategy = config.get_extraction_strategy(component_type)
        
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
            raise ValueError(f"Unknown extraction strategy '{strategy}' for component '{component_type}'")
    
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
        """Extract FAQ list from strict JSON payload or plain Q/A text."""
        import json
        import re

        def _normalize_faq_list(items: list) -> list | None:
            normalized: list = []
            for entry in items:
                if not isinstance(entry, dict):
                    return None

                question = entry.get("question") or entry.get("q") or entry.get("title")
                answer = entry.get("answer") or entry.get("a") or entry.get("description") or entry.get("content")

                if not isinstance(question, str) or not question.strip():
                    return None
                if not isinstance(answer, str) or not answer.strip():
                    return None

                normalized.append({"question": question.strip(), "answer": answer.strip()})

            return normalized if normalized else None

        def _extract_list_from_object(payload: dict) -> list | None:
            for key in ("faq", "faqs", "items", "questions", "faqItems", "entries"):
                value = payload.get(key)
                if isinstance(value, list):
                    normalized = _normalize_faq_list(value)
                    if normalized is not None:
                        return normalized
            if isinstance(payload.get("question"), str) and isinstance(payload.get("answer"), str):
                return [{"question": payload["question"], "answer": payload["answer"]}]
            return None

        def _parse_json(candidate_text: str):
            try:
                return json.loads(candidate_text)
            except json.JSONDecodeError:
                return None

        # 1) Parse full response as strict JSON (array or wrapped object)
        payload = _parse_json(text.strip())
        if isinstance(payload, list):
            normalized = _normalize_faq_list(payload)
            if normalized is not None:
                return normalized
        if isinstance(payload, dict):
            extracted = _extract_list_from_object(payload)
            if extracted is not None:
                return extracted

        # 2) Parse fenced JSON block if present
        fenced_match = re.search(r'```json\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
        if fenced_match:
            payload = _parse_json(fenced_match.group(1).strip())
            if isinstance(payload, list):
                normalized = _normalize_faq_list(payload)
                if normalized is not None:
                    return normalized
            if isinstance(payload, dict):
                extracted = _extract_list_from_object(payload)
                if extracted is not None:
                    return extracted

        # 3) Parse first JSON array found in response
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            payload = _parse_json(json_match.group())
            if isinstance(payload, list):
                normalized = _normalize_faq_list(payload)
                if normalized is not None:
                    return normalized

        # 4) Parse first JSON object found in response and extract wrapped list
        object_match = re.search(r'\{[\s\S]*\}', text)
        if object_match:
            payload = _parse_json(object_match.group())
            if isinstance(payload, dict):
                extracted = _extract_list_from_object(payload)
                if extracted is not None:
                    return extracted

        # 5) Minimal fallback: plain-text Q/A pairs
        qa_pattern = re.compile(
            r'(?:^|\n)\s*(?:[-*]\s*)?(?:Q(?:uestion)?\s*[:\-])\s*(.+?)\s*(?:\n|$)\s*(?:[-*]\s*)?(?:A(?:nswer)?\s*[:\-])\s*(.+?)(?=(?:\n\s*(?:[-*]\s*)?(?:Q(?:uestion)?\s*[:\-]))|\Z)',
            re.IGNORECASE | re.DOTALL,
        )
        qa_matches = qa_pattern.findall(text)
        if qa_matches:
            normalized = []
            for question, answer in qa_matches:
                q = question.strip()
                a = answer.strip()
                if q and a:
                    normalized.append({"question": q, "answer": a})
            if normalized:
                return normalized

        # 6) Minimal fallback: first line as question, remaining lines as answer
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) >= 2 and lines[0].endswith('?'):
            answer = " ".join(lines[1:]).strip()
            if answer:
                return [{"question": lines[0], "answer": answer}]

        # 7) Minimal fallback: single-line "Question? Answer..." format
        compact_text = text.strip()
        question_mark_index = compact_text.find('?')
        if question_mark_index > 0:
            question = compact_text[:question_mark_index + 1].strip()
            answer = compact_text[question_mark_index + 1:].strip()
            if question and answer:
                return [{"question": question, "answer": answer}]

        raise ValueError("Could not find JSON array in response")
    
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
            raise ValueError("Could not extract valid YAML from response")
    
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
        for key in ['category', 'properties', 'properties', 'applications', 
                    'machine_settings', 'description', 'challenges']:
            if key in item_data:
                enrichment[key] = item_data[key]
        
        return enrichment
    
    def _enrich_author_field(self, author_field: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich minimal author field with full metadata from registry.
        
        Transforms author: {id: 2} into author: {id: 2, name: "...", country: "...", ...}
        This ensures Materials.yaml has complete author data for display/evaluation.
        
        Args:
            author_field: Minimal author dict (may only have 'id')
            
        Returns:
            Enriched author dict with name, country, and other essential fields
            
        Implementation:
            - Checks if already enriched (has name and country)
            - Looks up full data in data/authors/registry.py
            - Returns essential fields (id, name, country, title, sex, expertise)
            - Omits internal fields (persona_file, formatting_file)
        
        Created: December 30, 2025 - Author Attribution Refactor
        """
        # Validate input
        if not isinstance(author_field, dict):
            logger.warning(f"Author field not a dict: {type(author_field)}")
            return author_field
        
        if 'id' not in author_field:
            logger.warning("Author field missing 'id' - cannot enrich")
            return author_field
        
        # Check if already enriched
        if 'name' in author_field and 'country' in author_field:
            logger.debug(f"Author {author_field['id']} already enriched")
            return author_field
        
        # Enrich from registry
        try:
            from data.authors.registry import get_author
            full_author = get_author(author_field['id'])
            
            # Return essential fields only (no internal prompt files)
            enriched = {
                'id': full_author['id'],
                'name': full_author['name'],
                'country': full_author['country'],
                'country_display': full_author['country_display'],
                'title': full_author['title'],
                'sex': full_author['sex'],
                'expertise': full_author['expertise'],
            }
            
            logger.info(f"✅ Enriched author {enriched['id']}: {enriched['name']} ({enriched['country']})")
            return enriched
            
        except KeyError as e:
            logger.error(f"❌ Author ID {author_field['id']} not found in registry: {e}")
            raise KeyError(
                f"Author enrichment failed for author ID {author_field['id']}: {e}"
            ) from e
        except Exception as e:
            logger.error(f"❌ Error enriching author field: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Author enrichment failed: {e}") from e

    def enrich_on_save(self, item_data: Dict[str, Any], identifier: str) -> Dict[str, Any]:
        """
        Add complete software metadata to item before saving to source YAML.
        
        PHASE 2 IMPLEMENTATION (Jan 7, 2026):
        Ensures NEW items generated after Jan 7, 2026 have complete metadata in source.
        
        Fields added (if missing):
        - fullPath: Generated from category/subcategory/id
        - pageTitle: Page title for frontend (from title or name)
        - breadcrumb: Navigation hierarchy array
        - pageDescription: SEO description from micro/description
        - dateModified: Current timestamp
        - datePublished: Preserved or current timestamp
        
        Args:
            item_data: Item data dict to enrich
            identifier: Item ID (e.g., 'aluminum-laser-cleaning')
            
        Returns:
            Enriched item data with complete software metadata
            
        Compliance: Core Principle 0.6 - Maximum Formatting at Source
        """
        from datetime import datetime
        
        # 1. fullPath (from category/subcategory/id)
        if 'fullPath' not in item_data:
            if self.domain == 'applications':
                item_data['fullPath'] = f"/{self.domain}/{identifier}"
            else:
                path_parts = [self.domain]
                if item_data.get('category'):
                    path_parts.append(item_data['category'])
                if item_data.get('subcategory'):
                    path_parts.append(item_data['subcategory'])
                path_parts.append(identifier)
                item_data['fullPath'] = '/' + '/'.join(path_parts)
            logger.debug(f"  + fullPath: {item_data['fullPath']}")
        
        # 2. pageTitle (for frontend compatibility)
        if 'pageTitle' not in item_data:
            # First priority: Use SEO-generated page_title from SEO generators
            if 'page_title' in item_data:
                page_title = item_data['page_title']
            # Use title or name from source data
            else:
                page_title = item_data.get('title') or item_data.get('name')
            if not page_title:
                raise ValueError(
                    f"Missing page title source for '{identifier}': require page_title, title, or name"
                )
            item_data['pageTitle'] = page_title
            logger.debug(f"  + pageTitle: {page_title}")
        
        # 3. breadcrumb (from category hierarchy)
        if 'breadcrumb' not in item_data:
            breadcrumbs = [{'label': 'Home', 'href': '/'}]
            
            # Add domain breadcrumb
            domain_labels = {
                'materials': 'Materials',
                'contaminants': 'Contaminants',
                'compounds': 'Compounds',
                'settings': 'Settings',
                'applications': 'Applications',
            }
            if self.domain not in domain_labels:
                raise KeyError(f"Missing domain label mapping for domain '{self.domain}'")
            breadcrumbs.append({
                'label': domain_labels[self.domain],
                'href': f'/{self.domain}'
            })
            
            if self.domain != 'applications':
                # Add category breadcrumb
                if item_data.get('category'):
                    category = item_data['category']
                    breadcrumbs.append({
                        'label': category.replace('-', ' ').title(),
                        'href': f'/{self.domain}/{category}'
                    })
                    
                    # Add subcategory breadcrumb
                    if item_data.get('subcategory'):
                        subcategory = item_data['subcategory']
                        breadcrumbs.append({
                            'label': subcategory.replace('-', ' ').title(),
                            'href': f'/{self.domain}/{category}/{subcategory}'
                        })
            
            item_data['breadcrumb'] = breadcrumbs
            logger.debug(f"  + breadcrumb: {len(breadcrumbs)} levels")
        
        # 4. pageDescription (from micro or description)
        if 'pageDescription' not in item_data:
            # Try micro.before first
            micro_value = item_data['micro'] if 'micro' in item_data else None
            if isinstance(micro_value, dict):
                if 'before' not in micro_value:
                    raise KeyError(
                        f"Invalid micro structure for '{identifier}': missing required key 'before'"
                    )
                micro_text = micro_value['before']
                if not isinstance(micro_text, str):
                    raise ValueError(
                        f"Invalid micro.before value for '{identifier}': expected string, got {type(micro_text)}"
                    )
                if micro_text:
                    item_data['pageDescription'] = micro_text[:157] + '...' if len(micro_text) > 160 else micro_text
            
            # Try description if no micro
            if 'pageDescription' not in item_data and item_data.get('description'):
                desc = item_data['description']
                item_data['pageDescription'] = desc[:157] + '...' if len(desc) > 160 else desc
            
            if 'pageDescription' not in item_data:
                raise ValueError(
                    f"Missing pageDescription source for '{identifier}': require micro.before or description"
                )
            
            logger.debug(f"  + pageDescription: {len(item_data['pageDescription'])} chars")
        
        # 5. datePublished (preserve existing or use current)
        if 'datePublished' not in item_data:
            # Check for legacy metadata.created_date
            metadata = item_data['metadata'] if 'metadata' in item_data else None
            if isinstance(metadata, dict) and 'created_date' in metadata and metadata['created_date']:
                item_data['datePublished'] = metadata['created_date']
            else:
                item_data['datePublished'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            logger.debug(f"  + datePublished: {item_data['datePublished']}")
        
        # 6. dateModified (always update to current)
        item_data['dateModified'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        logger.debug(f"  + dateModified: {item_data['dateModified']}")
        
        return item_data

    def _is_schema_based_component(self, component_type: str) -> bool:
        """
        Check if component type is schema-based (uses title/description structure).
        
        Args:
            component_type: Component type to check
            
        Returns:
            True if component uses schema-based generation
        """
        # List of schema-based components that generate title + description
        schema_components = {
            'contaminatedBy', 'relatedMaterials', 'materialCharacteristics',
            'laserMaterialInteraction', 'physicalProperties', 'appearanceVariations',
            'healthEffects', 'exposureLimits', 'ppeRequirements', 'emergencyResponse',
            'storageRequirements', 'regulatoryStandards', 'regulatoryClassification',
            'industryApplications', 'commonChallenges', 'detectionMethods',
            'preventionStrategies', 'removalMethods', 'environmentalImpact',
            'continuousMonitoring', 'reactivity', 'producedByMaterials',
            'producedFromContaminants', 'relatedContaminants', 'relatedCompounds'
        }
        return component_type in schema_components

    def _parse_schema_output(self, content_data: str, schema_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse LLM output into title and description fields.
        
        The LLM generates content like:
        "Title: Steel Contamination Issues
        
        Description: Steel surfaces typically accumulate rust, oils, and industrial debris..."
        
        Args:
            content_data: Raw LLM output string
            schema_metadata: Schema metadata with expected structure
            
        Returns:
            Dict with title, description, and metadata
        """
        import re
        
        # Initialize result with metadata
        result = {
            'title': '',
            'description': '',
            '_metadata': {
                'icon': schema_metadata['icon'],
                'order': schema_metadata['order'],
                'variant': schema_metadata['variant'],
                'generatedAt': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            }
        }
        
        # Clean the content
        content = str(content_data).strip()
        
        # Parse structured output (Title: ... Description: ...)
        title_match = re.search(r'(?:^|\n)\s*(?:Title|TITLE):\s*(.+?)(?:\n|$)', content, re.MULTILINE)
        desc_match = re.search(r'(?:Description|DESCRIPTION):\s*(.+)', content, re.DOTALL)

        if not title_match or not desc_match:
            raise ValueError("Schema output must include both Title and Description fields")

        result['title'] = title_match.group(1).strip()
        result['description'] = desc_match.group(1).strip()
        
        # Clean up title (remove colons, extra punctuation)
        result['title'] = re.sub(r'[:\-]+$', '', result['title']).strip()
        
        # Ensure we have content
        if not result['title'] or not result['description']:
            raise ValueError("Parsed schema output is missing title or description content")
            
        return result

    def _convert_existing_to_schema_format(self, content: str, schema_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert existing content with embedded titles to proper schema format.
        
        Handles content like '### Related Ferrous Metals Steel shares...' 
        and separates into title and description.
        
        Args:
            content: Existing content string with embedded title
            schema_metadata: Schema metadata for the component
            
        Returns:
            Dict with separated title, description, and metadata
        """
        import re
        
        # Initialize result with metadata
        result = {
            'title': '',
            'description': '',
            '_metadata': {
                'icon': schema_metadata['icon'],
                'order': schema_metadata['order'],
                'variant': schema_metadata['variant'],
                'convertedAt': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            }
        }
        
        # Clean the content
        content = str(content).strip()

        if 'title' not in schema_metadata or not isinstance(schema_metadata['title'], str) or not schema_metadata['title'].strip():
            raise KeyError("Schema metadata missing required non-empty 'title'")
        default_title = schema_metadata['title'].strip()
        
        # Look for markdown heading (### Title)
        heading_match = re.search(r'^###\s+(.+?)(?:\n|$)', content, re.MULTILINE)
        if heading_match:
            # Extract the full heading line
            heading_line = heading_match.group(1).strip()
            
            # If heading is very long (> 50 chars), extract just the first 3-5 words as title
            if len(heading_line) > 50:
                # Split into words and take first 3-5 words
                words = heading_line.split()
                result['title'] = ' '.join(words[:4])  # Take first 4 words as title
                # Everything else (including remaining words from heading) becomes description
                remaining_words = ' '.join(words[4:])
                heading_end = heading_match.end()
                after_heading = content[heading_end:].strip()
                result['description'] = (remaining_words + ' ' + after_heading).strip()
            else:
                # Short heading - use as-is for title
                result['title'] = heading_line
                # Get everything after the heading line
                heading_end = heading_match.end()
                result['description'] = content[heading_end:].strip() or heading_line
        else:
            # Try to find title at start of content
            lines = content.split('\n', 1)
            if len(lines) >= 2:
                # First line might be title
                potential_title = lines[0].strip()
                # Check if first line looks like a title (short, no punctuation at end)
                if len(potential_title) < 80 and not potential_title.endswith(('.', '!', '?')):
                    result['title'] = potential_title
                    result['description'] = lines[1].strip()
                else:
                    # Extract first sentence as title
                    sentences = content.split('. ', 1)
                    if len(sentences) >= 2:
                        result['title'] = sentences[0].strip() + '.'
                        result['description'] = sentences[1].strip()
                    else:
                        # Use default title from schema
                        result['title'] = default_title
                        result['description'] = content
            else:
                # Single block - use default title
                result['title'] = default_title
                result['description'] = content
        
        # Clean up title (remove extra punctuation)
        result['title'] = re.sub(r'[:#\-]+$', '', result['title']).strip()
        
        # Ensure we have content
        if not result['title']:
            result['title'] = default_title
        if not result['description']:
            result['description'] = content
            
        return result
        return result