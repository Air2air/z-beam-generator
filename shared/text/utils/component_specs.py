"""
Component Type Specifications

Defines characteristics and prompt templates for different content types.
Dynamically loads component lengths from generation/text_field_config.yaml.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml
from shared.text.utils.prompt_registry_service import PromptRegistryService


@dataclass
class ComponentSpec:
    """
    Specification for a component type.
    
    CRITICAL: Content instructions (focus, format, style) are ONLY defined in prompts/*.txt files.
    This class contains ONLY structural metadata (lengths, punctuation).
    
    Attributes:
        name: Component identifier (matches prompts/{name}.txt)
        default_length: Target word count
        end_punctuation: Whether to include period at end
        prompt_template_file: Path to prompt template file
        extraction_strategy: How to extract content from generated text
            - 'raw': Return text as-is (description)
            - 'before_after': Parse before/after sections (micro)
            - 'json_list': Parse JSON array (faq)
    """
    name: str
    default_length: int
    end_punctuation: bool = True
    prompt_template_file: Optional[str] = None
    extraction_strategy: str = 'raw'


class ComponentRegistry:
    """
    Registry of all component types and their specifications.
    
    Dynamically loads component lengths from centralized text field config.
    Component specs define content characteristics while centralized config controls lengths.
    """
    
    # Centralized text field config cache
    _text_field_config = None

    LEGACY_COMPONENT_ALIASES = {
        'description': 'pageDescription',
    }
    
    @classmethod
    def _load_text_field_config(cls) -> Dict:
        """Load centralized text field config from generation/text_field_config.yaml."""
        if cls._text_field_config is None:
            project_root = Path(__file__).parent.parent.parent.parent
            config_path = project_root / 'generation' / 'text_field_config.yaml'

            if not config_path.exists():
                config_path = Path('generation') / 'text_field_config.yaml'

            if not config_path.exists():
                raise FileNotFoundError(
                    f"Text field config not found: {config_path}. "
                    "Cannot resolve text field lengths without centralized config."
                )

            with open(config_path, 'r', encoding='utf-8') as file_handle:
                cls._text_field_config = yaml.safe_load(file_handle)

            if not isinstance(cls._text_field_config, dict):
                raise ValueError("generation/text_field_config.yaml must contain a YAML dictionary")

        return cls._text_field_config
    
    @classmethod
    def _get_component_lengths(cls, component_type: str) -> Dict[str, int]:
        """Get length configuration for component type from centralized text_field_config.yaml.

        Field config is keyed by component name globally and shared across all domains.
        """
        config = cls._load_text_field_config()

        defaults = config.get('defaults')
        if not isinstance(defaults, dict):
            raise ValueError("Missing required 'defaults' block in generation/text_field_config.yaml")

        fields_cfg = config.get('fields')
        if not isinstance(fields_cfg, dict):
            raise ValueError("Missing required fields block in generation/text_field_config.yaml")

        if component_type not in fields_cfg:
            raise ValueError(
                f"Missing field '{component_type}' under fields in generation/text_field_config.yaml"
            )

        field_cfg = fields_cfg.get(component_type) or {}
        if not isinstance(field_cfg, dict):
            raise ValueError(
                f"Invalid field config for '{component_type}' in generation/text_field_config.yaml"
            )

        default = field_cfg.get('base_length', defaults.get('base_length'))
        extraction_strategy = field_cfg.get('extraction_strategy', defaults.get('extraction_strategy'))

        if not isinstance(default, int) or default <= 0:
            raise ValueError(
                f"Invalid base_length for '{component_type}': {default}"
            )
        if not isinstance(extraction_strategy, str) or not extraction_strategy:
            raise ValueError(
                f"Invalid extraction_strategy for '{component_type}': {extraction_strategy}"
            )

        return {
            'default': default,
            'extraction_strategy': extraction_strategy,
        }
    
    # Component specifications discovered dynamically from prompt catalog YAML.
    # No hardcoded component types - all defined externally.
    
    @classmethod
    def _discover_components(cls) -> Dict[str, Dict]:
        """Discover available components from consolidated prompt catalog.
        
        Returns component specs by scanning catalog.byPath entries for
        prompts/<domain>/*.txt templates.
        
        Directory structure:
        prompts/
        ├── materials/micro.txt, faq.txt, description.txt
        ├── settings/settings_description.txt, component_summaries.txt
        ├── contaminants/micro.txt
        └── etc.
        """
        specs = {}
        project_root = Path(__file__).parent.parent.parent.parent

        prompt_catalog = PromptRegistryService.get_prompt_catalog()
        by_path = prompt_catalog.get('catalog', {}).get('byPath')
        if not isinstance(by_path, dict):
            raise ValueError("Prompt catalog is missing required 'catalog.byPath' mapping")

        shared_components = prompt_catalog.get('catalog', {}).get('shared', {}).get('components')
        if not isinstance(shared_components, dict):
            raise ValueError("Prompt catalog is missing required 'catalog.shared.components' mapping")
        
        component_sources: Dict[str, list] = {}

        # Scan domain prompt entries in catalog.byPath (prompts/<domain>/*.txt)
        for relative_path, content in sorted(by_path.items(), key=lambda item: item[0]):
            if not isinstance(relative_path, str):
                continue
            if not relative_path.startswith('prompts/') or not relative_path.endswith('.txt'):
                continue

            parts = relative_path.split('/')
            if len(parts) != 3:
                continue

            domain_name = parts[1]
            if domain_name not in {'materials', 'settings', 'contaminants', 'compounds', 'applications'}:
                continue

            component_type = Path(parts[2]).stem
            if component_type.startswith('_'):
                continue

            if not isinstance(content, str):
                raise ValueError(f"Prompt catalog byPath entry is not a string: {relative_path}")

            component_sources.setdefault(component_type, []).append({
                'domain': domain_name,
                'relative_path': relative_path,
                'content': content.strip(),
            })

        # Resolve discovered sources per component.
        # If a component exists in multiple domains:
        # - identical content => route to shared/components/<component>.txt
        # - divergent content => fail-fast (domain-agnostic registry cannot choose safely)
        for component_type, sources in sorted(component_sources.items(), key=lambda item: item[0]):
            if len(sources) == 1:
                specs[component_type] = {
                    'end_punctuation': True,
                    'prompt_template_file': sources[0]['relative_path']
                }
                continue

            unique_contents = {source['content'] for source in sources}
            if len(unique_contents) == 1:
                shared_relative_path = f'prompts/shared/components/{component_type}.txt'
                shared_content = shared_components.get(component_type)
                if not isinstance(shared_content, str) or not shared_content.strip():
                    raise FileNotFoundError(
                        f"Centralized shared prompt not found for '{component_type}' in prompt catalog. "
                        "Populate catalog.shared.components.<component> for identical multi-domain templates."
                    )

                specs[component_type] = {
                    'end_punctuation': True,
                    'prompt_template_file': shared_relative_path
                }
                continue

            variant_paths = ', '.join(source['relative_path'] for source in sources)
            raise ValueError(
                f"Ambiguous prompt templates for component '{component_type}' across domains: {variant_paths}. "
                "Either unify content or introduce explicit domain-aware prompt resolution."
            )
        
        # ALSO discover schema-based components from section_display_schema.yaml
        schema_specs = cls._discover_schema_components()
        specs.update(schema_specs)
        
        return specs

    @classmethod
    def _discover_schema_components(cls) -> Dict[str, Dict]:
        """Discover components defined in section_display_schema.yaml.
        
        Returns:
            Dict of component specs for schema-based components
        """
        specs = {}
        
        try:
            # Load the schema file
            project_root = Path(__file__).parent.parent.parent.parent
            schema_path = project_root / 'data' / 'schemas' / 'section_display_schema.yaml'
            
            if not schema_path.exists():
                # Fallback: try relative path from cwd
                schema_path = Path('data/schemas/section_display_schema.yaml')
            
            if not schema_path.exists():
                return specs
                
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)
                
            # Extract component types from sections
            sections = schema.get('sections', {})
            for component_type, section_config in sections.items():
                # Skip if missing required prompt reference
                if not section_config.get('prompt') and not section_config.get('prompt_ref'):
                    continue
                    
                specs[component_type] = {
                    'end_punctuation': True,  # Default
                    'schema_based': True,  # Flag to indicate schema source
                    'wordCount': section_config.get('wordCount', 100)  # Default word count
                }
                
        except Exception as e:
            # Don't fail if schema can't be loaded - just don't add schema components
            pass
            
        return specs
    
    @classmethod
    def _get_spec_definitions(cls) -> Dict[str, Dict]:
        """Get component spec definitions, cached for performance."""
        if not hasattr(cls, '_cached_specs'):
            cls._cached_specs = cls._discover_components()
        return cls._cached_specs
    
    @classmethod
    def get_spec(cls, component_type: str) -> ComponentSpec:
        """Get specification for component type.
        
        Dynamically discovers components from prompt catalog YAML.
        Loads lengths from generation/text_field_config.yaml.
        
        Args:
            component_type: Component identifier (must match prompts/{type}.txt)
            
        Returns:
            ComponentSpec object with lengths from centralized text field config and prompt template file
            
        Raises:
            KeyError: If component type not found in prompts/ or config
        """
        spec_defs = cls._get_spec_definitions()
        canonical_component_type = cls.LEGACY_COMPONENT_ALIASES.get(component_type, component_type)
        spec_def = spec_defs.get(canonical_component_type)
        
        if not spec_def:
            available = ', '.join(spec_defs.keys())
            raise KeyError(
                f"Component type '{component_type}' not found. "
                f"Add it to prompt catalog domain entries to define it. "
                f"Available: {available}"
            )
        
        # Get lengths - handle schema-based components differently
        if spec_def.get('schema_based'):
            # For schema-based components, use wordCount from schema if available
            schema_word_count = spec_def.get('wordCount', 100)
            lengths = {
                'default': schema_word_count,
                'extraction_strategy': 'raw'  # Default for schema components
            }
        else:
            # Regular components use centralized text field config
            lengths = cls._get_component_lengths(canonical_component_type)
        
        # Get extraction strategy from config (default to 'raw')
        extraction_strategy = 'raw'
        if 'extraction_strategy' in lengths:
            extraction_strategy = lengths['extraction_strategy']
        
        # Build ComponentSpec with config lengths and prompt template file
        return ComponentSpec(
            name=canonical_component_type,
            default_length=lengths['default'],
            end_punctuation=spec_def['end_punctuation'],
            prompt_template_file=spec_def.get('prompt_template_file'),
            extraction_strategy=extraction_strategy
        )
    
    @classmethod
    def register(cls, spec: ComponentSpec):
        """Register new component type dynamically.
        
        Note: Lengths still come from generation/text_field_config.yaml. This only registers
        the component definition for runtime discovery.
        
        Args:
            spec: ComponentSpec to register
        """
        if not hasattr(cls, '_cached_specs'):
            cls._cached_specs = {}
        
        cls._cached_specs[spec.name] = {
            'end_punctuation': spec.end_punctuation,
            'prompt_template_file': spec.prompt_template_file
        }
    
    @classmethod
    def list_types(cls) -> list:
        """Get list of all available component types (discovered from prompt catalog)."""
        return list(cls._get_spec_definitions().keys())
    
    @classmethod
    def get_default_length(cls, component_type: str) -> int:
        """Get default length for component type from centralized text field config."""
        lengths = cls._get_component_lengths(component_type)
        return lengths['default']
    
    @classmethod
    def set_config_path(cls, path: str):
        """Set custom text field config path (useful for testing)."""
        cls._text_field_config = None  # Force reload
        custom_path = Path(path)
        if not custom_path.exists():
            raise FileNotFoundError(f"Custom text field config not found: {path}")
        with open(custom_path, 'r', encoding='utf-8') as file_handle:
            cls._text_field_config = yaml.safe_load(file_handle)
        if not isinstance(cls._text_field_config, dict):
            raise ValueError("Custom text field config must contain a YAML dictionary")


@dataclass
class DomainContext:
    """
    Domain-specific context for content generation.
    
    Allows same system to generate for different content domains
    (materials, history, recipes, etc.) by providing domain-specific guidance.
    """
    domain: str
    focus_template: str
    enrichment_strategy: str
    example_facts: str
    terminology_style: str
    
    @classmethod
    def materials(cls) -> 'DomainContext':
        """Context for material science domain"""
        return cls(
            domain='materials',
            focus_template='Physical properties, industrial applications, laser cleaning characteristics',
            enrichment_strategy='Extract from Materials.yaml: properties, machine settings, applications',
            example_facts='Hardness: 2.5-3 Mohs; Melting point: 660°C; Applications: Aerospace, automotive',
            terminology_style='Technical but accessible; use proper material science terms; cite specific values'
        )
    
    @classmethod
    def settings(cls) -> 'DomainContext':
        """Context for machine settings and parameters domain"""
        return cls(
            domain='settings',
            focus_template='Operating parameters, optimal ranges, adjustment guidelines, effects on outcomes',
            enrichment_strategy='Extract from Settings.yaml machine_settings: power, frequency, pulse duration, etc.',
            example_facts='Power: 100W; Frequency: 50kHz; Pulse Duration: 200ns; Spot Size: 50μm',
            terminology_style='Precise and technical; always include units; cite ranges and thresholds; explain trade-offs'
        )
    
    @classmethod
    def contaminants(cls) -> 'DomainContext':
        """Context for contaminants and contamination patterns domain"""
        return cls(
            domain='contaminants',
            focus_template='Contamination characteristics, formation patterns, material-specific behavior, cleaning challenges',
            enrichment_strategy='Extract from Contaminants.yaml: category, context notes, description, visual characteristics',
            example_facts='Hardness: 2.5-3 Mohs; Melting point: 660°C; Applications: Aerospace, automotive',
            terminology_style='Descriptive and precise; focus on visual characteristics; explain formation and behavior'
        )

    @classmethod
    def applications(cls) -> 'DomainContext':
        """Context for applications domain"""
        return cls(
            domain='applications',
            focus_template='Use-case context, operational outcomes, deployment constraints, and safety/compliance implications',
            enrichment_strategy='Extract from Applications.yaml: category, subcategory, contentCards, keywords, and operational details',
            example_facts='Use case: Aerospace MRO; Typical fluence: 2-8 J/cm²; Outcomes: 50-80% faster turnaround',
            terminology_style='Operationally precise and outcome-focused; include concrete deployment constraints and measurable results'
        )
    
    @classmethod
    def get_domain(cls, domain: str) -> 'DomainContext':
        """
        Get domain context by name.
        
        Args:
            domain: Domain identifier
            
        Returns:
            DomainContext object
        """
        method_map = {
            'materials': cls.materials,
            'settings': cls.settings,
            'contaminants': cls.contaminants,
            'applications': cls.applications
        }
        
        factory = method_map.get(domain)
        if not factory:
            raise ValueError(f"Unknown domain: {domain}. "
                           f"Available: {', '.join(method_map.keys())}")
        
        return factory()
