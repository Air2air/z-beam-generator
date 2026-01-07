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
from typing import Any, Dict, Optional

from shared.utils.yaml_utils import load_yaml

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
        
        # Extract required paths from config (support both old flat and new nested structure)
        if 'data_adapter' in self.config:
            # New nested structure
            adapter_config = self.config['data_adapter']
            self.data_path = Path(adapter_config.get('data_path', f"data/{domain}/{domain.title()}.yaml"))
            self.data_root_key = adapter_config.get('data_root_key', domain)
            self.author_key = adapter_config.get('author_key', 'author.id')
            self.context_keys = adapter_config.get('context_keys', ['category'])
        else:
            # Old flat structure (backward compatibility)
            self.data_path = Path(self.config.get('data_path', f"data/{domain}/{domain.title()}.yaml"))
            self.data_root_key = self.config.get('data_root_key', domain)
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
        
        Supports two formats:
        1. Inline prompt: prompt content directly in config YAML
        2. External file: "@path/to/file.txt" loads from external file
        
        Args:
            component_type: Component type (e.g., 'micro', 'component_summary', 'page_title')
            
        Returns:
            Prompt template string or None if not found
        """
        prompts = self.config.get('prompts', {})
        prompt_value = prompts.get(component_type)
        
        if not prompt_value:
            return None
        
        # Check if this is an external file reference (starts with @)
        if isinstance(prompt_value, str) and prompt_value.startswith('@'):
            # Remove @ and load from file
            file_path = prompt_value[1:]  # Remove @ prefix
            from pathlib import Path
            
            # Resolve relative to project root
            # domain_adapter.py is at generation/core/adapters/
            # Go up 3 levels to reach project root
            project_root = Path(__file__).parent.parent.parent.parent
            full_path = project_root / file_path
            
            if not full_path.exists():
                logger.error(f"Prompt file not found: {full_path}")
                raise FileNotFoundError(f"Prompt file referenced in config not found: {file_path}")
            
            # Load file content
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Regular inline prompt
        return prompt_value
    
    def write_component(
        self,
        identifier: str,
        component_type: str,
        content_data: Any
    ) -> None:
        """
        Write generated content to domain data YAML atomically.
        
        CORE PRINCIPLE 0.6 COMPLIANCE (Jan 5, 2026):
        Enriches data at GENERATION TIME, not export time.
        Adds: expanded author, timestamps, id, breadcrumbs.
        
        PHASE 2 FIX (Jan 5, 2026):
        Converts collapsible components (FAQ, applications, standards) to unified format
        BEFORE saving to source YAML. Export tasks will eventually become no-ops.
        
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
        
        # PHASE 2: Convert to collapsible format if applicable (NEW Jan 5, 2026)
        content_to_save = self._convert_to_collapsible_if_needed(
            content_data, 
            component_type, 
            identifier
        )
        
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
        from generation.enrichment.generation_time_enricher import enrich_for_generation
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
            sync_field_to_frontmatter(identifier, component_type, content_data, domain=self.domain)
            logger.info(f"✅ Frontmatter sync complete for {identifier}")
        except Exception as sync_error:
            logger.error(f"❌ Frontmatter sync FAILED: {sync_error}")
            import traceback
            logger.error(traceback.format_exc())
            # Don't fail the whole generation - sync failure is non-fatal
            logger.warning("⚠️  Continuing despite sync failure - frontmatter can be manually updated")
    
    def _get_target_field(self, component_type: str) -> str:
        """
        Get target field name for component type.
        
        Maps component types to their storage location in data YAML.
        Some components save to different field names.
        """
        # Component type → target field mapping
        FIELD_MAPPING = {
            'faq': 'operational.expert_answers',  # FAQ saves as expert_answers
            # Add other mappings as needed
        }
        
        return FIELD_MAPPING.get(component_type, component_type)
    
    def _convert_to_collapsible_if_needed(
        self, 
        content_data: Any, 
        component_type: str, 
        identifier: str
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
            # Check if it's FAQ format (list of Q&A dicts)
            if content_data and isinstance(content_data[0], dict) and 'question' in content_data[0]:
                logger.info(f"🔄 Converting FAQ data to collapsible format for {identifier}")
                return self._convert_faq_to_collapsible(content_data)
            # Simple string list - could be applications or other
            else:
                logger.debug(f"Raw list data for {component_type}, returning as-is")
                return content_data
        
        # Unknown format, return as-is
        return content_data
    
    def _convert_faq_to_collapsible(self, faq_data: list) -> Dict[str, Any]:
        """
        Convert FAQ list to unified collapsible structure.
        
        Input format (from generation):
        [
            {'question': 'Q1?', 'answer': 'A1'},
            {'question': 'Q2?', 'answer': 'A2'}
        ]
        
        Output format (collapsible):
        {
            'presentation': 'collapsible',
            'items': [
                {
                    'title': 'Q1?',
                    'content': 'A1',
                    'metadata': {'category': 'Technical', 'difficulty': 'intermediate'},
                    '_display': {'_open': True, 'order': 1}
                }
            ]
        }
        """
        if not isinstance(faq_data, list):
            logger.warning(f"FAQ data not a list, returning as-is: {type(faq_data)}")
            return faq_data
        
        items = []
        for idx, faq in enumerate(faq_data):
            if not isinstance(faq, dict):
                continue
            
            question = faq.get('question', '')
            answer = faq.get('answer', '')
            
            if not question or not answer:
                continue
            
            items.append({
                'title': question,
                'content': answer,
                'metadata': {
                    'category': 'Technical',
                    'difficulty': 'intermediate'
                },
                '_display': {
                    '_open': idx == 0,  # First item open
                    'order': idx + 1
                }
            })
        
        logger.info(f"✅ Converted {len(items)} FAQ items to collapsible format")
        
        return {
            'presentation': 'collapsible',
            'items': items
        }
    
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
                continue
            
            name = standard.get('name', '')
            long_name = standard.get('longName', '')
            description = standard.get('description', '')
            
            title = f"{name} - {long_name}" if name and long_name else name or long_name or 'Standard'
            
            items.append({
                'title': title,
                'content': description,
                'metadata': {
                    'organization': name,
                    'category': 'laser-safety',
                    'url': standard.get('url', ''),
                    'image': standard.get('image', '')
                },
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
            return author_field  # Return original on error
        except Exception as e:
            logger.error(f"❌ Error enriching author field: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return author_field  # Return original on error    
    def enrich_on_save(self, item_data: Dict[str, Any], identifier: str) -> Dict[str, Any]:
        """
        Add complete software metadata to item before saving to source YAML.
        
        PHASE 2 IMPLEMENTATION (Jan 7, 2026):
        Ensures NEW items generated after Jan 7, 2026 have complete metadata in source.
        
        Fields added (if missing):
        - fullPath: Generated from category/subcategory/id
        - breadcrumb: Navigation hierarchy array
        - metaDescription: SEO description from micro/description
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
            path_parts = [self.domain]
            if item_data.get('category'):
                path_parts.append(item_data['category'])
            if item_data.get('subcategory'):
                path_parts.append(item_data['subcategory'])
            path_parts.append(identifier)
            item_data['fullPath'] = '/' + '/'.join(path_parts)
            logger.debug(f"  + fullPath: {item_data['fullPath']}")
        
        # 2. breadcrumb (from category hierarchy)
        if 'breadcrumb' not in item_data:
            breadcrumbs = [{'label': 'Home', 'href': '/'}]
            
            # Add domain breadcrumb
            domain_labels = {
                'materials': 'Materials',
                'contaminants': 'Contaminants',
                'compounds': 'Compounds',
                'settings': 'Settings',
            }
            breadcrumbs.append({
                'label': domain_labels.get(self.domain, self.domain.title()),
                'href': f'/{self.domain}'
            })
            
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
        
        # 3. metaDescription (from micro or description)
        if 'metaDescription' not in item_data:
            # Try micro.before first
            if isinstance(item_data.get('micro'), dict):
                micro_text = item_data['micro'].get('before', '')
                if micro_text:
                    item_data['metaDescription'] = micro_text[:157] + '...' if len(micro_text) > 160 else micro_text
            
            # Try description if no micro
            if 'metaDescription' not in item_data and item_data.get('description'):
                desc = item_data['description']
                item_data['metaDescription'] = desc[:157] + '...' if len(desc) > 160 else desc
            
            # Fallback: generic description
            if 'metaDescription' not in item_data:
                name = item_data.get('name', identifier)
                item_data['metaDescription'] = f"{name} laser cleaning guide. Technical specifications and applications."
            
            logger.debug(f"  + metaDescription: {len(item_data['metaDescription'])} chars")
        
        # 4. datePublished (preserve existing or use current)
        if 'datePublished' not in item_data:
            # Check for legacy metadata.created_date
            metadata = item_data.get('metadata', {})
            if isinstance(metadata, dict) and metadata.get('created_date'):
                item_data['datePublished'] = metadata['created_date']
            else:
                item_data['datePublished'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            logger.debug(f"  + datePublished: {item_data['datePublished']}")
        
        # 5. dateModified (always update to current)
        item_data['dateModified'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        logger.debug(f"  + dateModified: {item_data['dateModified']}")
        
        return item_data