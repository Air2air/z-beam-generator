"""
Component Type Specifications

Defines characteristics and prompt templates for different content types.
Dynamically loads component lengths from config.yaml instead of hardcoding.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import yaml
from pathlib import Path


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
        min_length: Minimum word count (from config)
        max_length: Maximum word count (from config)
        prompt_template_file: Path to prompt template file
        extraction_strategy: How to extract content from generated text
            - 'raw': Return text as-is (description)
            - 'before_after': Parse before/after sections (micro)
            - 'json_list': Parse JSON array (faq)
    """
    name: str
    default_length: int
    end_punctuation: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    prompt_template_file: Optional[str] = None
    extraction_strategy: str = 'raw'
    
    def __post_init__(self):
        # Set defaults if not provided (backward compatibility)
        if self.min_length is None:
            self.min_length = max(int(self.default_length * 0.9), self.default_length - 5)
        if self.max_length is None:
            self.max_length = min(int(self.default_length * 1.1), self.default_length + 5)


class ComponentRegistry:
    """
    Registry of all component types and their specifications.
    
    Dynamically loads component lengths from config.yaml.
    Component specs define content characteristics while config.yaml controls lengths.
    """
    
    # Config cache
    _config = None
    _config_path = None
    
    # Component type to domain mapping
    # Used to load domain-specific configs from domains/{domain}/config.yaml
    _component_domain_map = {
        'description': 'materials',
        'micro': 'materials',
        'faq': 'materials',
        'settings_description': 'settings',
        'component_summaries': 'settings',
    }
    
    @classmethod
    def _deep_merge(cls, base: Dict, override: Dict) -> Dict:
        """Deep merge override dict into base dict.
        
        Args:
            base: Base dictionary
            override: Override dictionary (takes precedence)
            
        Returns:
            Merged dictionary (base + override)
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    @classmethod
    def _load_domain_config(cls, domain: str) -> Optional[Dict]:
        """Load domain-specific config from domains/{domain}/config.yaml.
        
        Args:
            domain: Domain name (e.g., 'materials', 'settings')
            
        Returns:
            Domain config dict or None if not found
        """
        # Path from shared/text/utils/ -> project root is 4 levels up
        project_root = Path(__file__).parent.parent.parent.parent
        domain_config_path = project_root / 'domains' / domain / 'config.yaml'
        
        if not domain_config_path.exists():
            # Fallback: try relative path from cwd
            domain_config_path = Path('domains') / domain / 'config.yaml'
        
        if not domain_config_path.exists():
            return None
        
        try:
            with open(domain_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return None
    
    @classmethod
    def _load_config(cls) -> Dict:
        """Load config.yaml and merge domain-specific configs.
        
        Loading strategy:
        1. Load generation/config.yaml (global config)
        2. For each domain with config file, merge domain config
        3. Domain configs override global configs (domain takes precedence)
        
        Returns:
            Merged config dict
        """
        if cls._config is None:
            if cls._config_path is None:
                # Path to generation/config.yaml from shared/text/utils/
                # shared/text/utils/ -> parent.parent.parent = shared
                # Need to go up to project root then into generation/
                project_root = Path(__file__).parent.parent.parent.parent
                cls._config_path = project_root / "generation" / "config.yaml"
            
            # Load global config - FAIL-FAST: No fallbacks
            if not cls._config_path.exists():
                raise FileNotFoundError(
                    f"Config file not found: {cls._config_path}. "
                    f"Cannot operate without configuration - fail-fast architecture."
                )
            
            with open(cls._config_path, 'r', encoding='utf-8') as f:
                cls._config = yaml.safe_load(f)
            
            if not cls._config:
                raise ValueError(f"Config file is empty: {cls._config_path}")
            
            # Merge domain-specific configs
            # Discover all domains with config files
            # Path: shared/text/utils/ -> parent.parent.parent.parent = project root
            project_root = Path(__file__).parent.parent.parent.parent
            domains_dir = project_root / 'domains'
            if domains_dir.exists():
                for domain_dir in domains_dir.iterdir():
                    if domain_dir.is_dir():
                        domain_name = domain_dir.name
                        domain_config = cls._load_domain_config(domain_name)
                        if domain_config:
                            # Deep merge domain config into global config
                            cls._config = cls._deep_merge(cls._config, domain_config)
        
        return cls._config
    
    @classmethod
    def _get_component_lengths(cls, component_type: str) -> Dict[str, int]:
        """Get length configuration for component type from config.yaml.
        
        NOTE: Word counts are now in prompts (Option B: Prompts Only).
        This function now primarily returns extraction_strategy.
        Default word count is used only for legacy compatibility.
        
        Looks for config in:
        1. component_extraction (new - extraction_strategy only)
        2. component_lengths (legacy - backward compatibility)
        """
        config = cls._load_config()
        
        # Try new config location first (extraction_strategy only)
        extraction_config = config.get('component_extraction', {}).get(component_type, {})
        
        # Fall back to legacy location
        lengths = config.get('component_lengths', {}).get(component_type, {})
        
        # Get extraction_strategy - FAIL-FAST: Must be explicitly configured
        if isinstance(extraction_config, dict) and 'extraction_strategy' in extraction_config:
            extraction_strategy = extraction_config['extraction_strategy']
        elif isinstance(lengths, dict) and 'extraction_strategy' in lengths:
            extraction_strategy = lengths['extraction_strategy']
        else:
            raise ValueError(
                f"No extraction_strategy found for component '{component_type}'. "
                f"Must be defined in component_extraction.{component_type}.extraction_strategy - fail-fast architecture."
            )
        
        # Word count is now in prompts (Option B: Prompts Only)
        # Use a nominal default for range calculation only - actual length from prompt
        default = 100  # Nominal value for range calculation
        
        # Calculate dynamic range from length_variation_range slider
        try:
            if 'length_variation_range' not in config:
                raise ValueError("Config missing 'length_variation_range' - required for dynamic length calculation")
            length_variation = config['length_variation_range']  # 1-10 scale (normalized Nov 16, 2025)
            
            # Normalize 1-10 scale to variation percentages:
            # 1 = ±10% (tightest)
            # 5.5 = ±35% (moderate)
            # 10 = ±60% (loosest/maximum)
            # Linear mapping: variation_pct = 0.10 + ((slider - 1) / 9) * 0.50
            if not isinstance(length_variation, (int, float)) or length_variation < 1 or length_variation > 10:
                raise ValueError(f"length_variation_range must be 1-10, got: {length_variation}")
            
            variation_pct = 0.10 + ((length_variation - 1) / 9.0) * 0.50
            variation_words = int(default * variation_pct)
            
            result = {
                'default': default,
                'min': max(1, default - variation_words),
                'max': default + variation_words
            }
            
            # Add extraction_strategy if present
            if extraction_strategy is not None:
                result['extraction_strategy'] = extraction_strategy
            
            return result
        except Exception as e:
            # FAIL-FAST: No fallback calculation
            raise ValueError(
                f"Failed to calculate length range for '{component_type}': {e}. "
                f"Check 'length_variation_range' in config.yaml - fail-fast architecture."
            )
    
    # Component specifications discovered dynamically from:
    # 1. prompts/*.txt files (content instructions)
    # 2. config.yaml component_lengths section (word counts)
    # NO hardcoded component types - all defined externally
    
    @classmethod
    def _discover_components(cls) -> Dict[str, Dict]:
        """Discover available components from all domain prompts directories.
        
        Returns component specs by scanning domains/*/prompts/*.txt files.
        Each .txt file defines a component type.
        
        Directory structure:
        domains/
        ├── materials/prompts/micro.txt, faq.txt, description.txt
        ├── settings/prompts/settings_description.txt, component_summaries.txt
        ├── contaminants/prompts/micro.txt
        └── etc.
        """
        specs = {}
        # Path from shared/text/utils/ -> project root is 4 levels up
        # shared/text/utils/component_specs.py -> shared/text/utils -> shared/text -> shared -> project_root
        project_root = Path(__file__).parent.parent.parent.parent
        domains_dir = project_root / 'domains'
        
        if not domains_dir.exists():
            # Fallback: try relative path from cwd
            domains_dir = Path('domains')
        
        if not domains_dir.exists():
            return specs
        
        # Scan each domain's prompts directory
        for domain_dir in domains_dir.iterdir():
            if not domain_dir.is_dir():
                continue
            
            prompts_dir = domain_dir / 'prompts'
            if not prompts_dir.exists():
                continue
            
            # Scan for .txt files in this domain's prompts directory
            for prompt_file in prompts_dir.glob('*.txt'):
                component_type = prompt_file.stem  # filename without .txt
                
                # Skip system/utility prompts (shouldn't be any, but just in case)
                if component_type.startswith('_'):
                    continue
                
                # Store relative path from workspace root
                relative_path = f'domains/{domain_dir.name}/prompts/{prompt_file.name}'
                
                specs[component_type] = {
                    'end_punctuation': True,  # Default, can be overridden in config
                    'prompt_template_file': relative_path
                }
        
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
        
        Dynamically discovers components from prompts/*.txt files.
        Loads lengths from config.yaml component_lengths section.
        
        Args:
            component_type: Component identifier (must match prompts/{type}.txt)
            
        Returns:
            ComponentSpec object with lengths from config and prompt template file
            
        Raises:
            KeyError: If component type not found in prompts/ or config
        """
        spec_defs = cls._get_spec_definitions()
        spec_def = spec_defs.get(component_type)
        
        if not spec_def:
            available = ', '.join(spec_defs.keys())
            raise KeyError(
                f"Component type '{component_type}' not found. "
                f"Create prompts/{component_type}.txt to define it. "
                f"Available: {available}"
            )
        
        # Get lengths from config
        lengths = cls._get_component_lengths(component_type)
        
        # Get extraction strategy from config (default to 'raw')
        extraction_strategy = 'raw'
        if 'extraction_strategy' in lengths:
            extraction_strategy = lengths['extraction_strategy']
        
        # Build ComponentSpec with config lengths and prompt template file
        return ComponentSpec(
            name=component_type,
            default_length=lengths['default'],
            min_length=lengths['min'],
            max_length=lengths['max'],
            end_punctuation=spec_def['end_punctuation'],
            prompt_template_file=spec_def.get('prompt_template_file'),
            extraction_strategy=extraction_strategy
        )
    
    @classmethod
    def register(cls, spec: ComponentSpec):
        """Register new component type dynamically.
        
        Note: Lengths still come from config.yaml. This only registers
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
        """Get list of all available component types (discovered from prompts/)."""
        return list(cls._get_spec_definitions().keys())
    
    @classmethod
    def get_default_length(cls, component_type: str) -> int:
        """Get default length for component type from config"""
        lengths = cls._get_component_lengths(component_type)
        return lengths['default']
    
    @classmethod
    def set_config_path(cls, path: str):
        """Set custom config path (useful for testing)"""
        cls._config_path = Path(path)
        cls._config = None  # Force reload


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
            'contaminants': cls.contaminants
        }
        
        factory = method_map.get(domain)
        if not factory:
            raise ValueError(f"Unknown domain: {domain}. "
                           f"Available: {', '.join(method_map.keys())}")
        
        return factory()
