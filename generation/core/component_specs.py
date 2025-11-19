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
            - 'raw': Return text as-is (subtitle, description)
            - 'before_after': Parse before/after sections (caption)
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
    
    @classmethod
    def _load_config(cls) -> Dict:
        """Load config.yaml if not already loaded."""
        if cls._config is None:
            if cls._config_path is None:
                # Default path relative to this file
                cls._config_path = Path(__file__).parent.parent / "config.yaml"
            
            try:
                with open(cls._config_path, 'r', encoding='utf-8') as f:
                    cls._config = yaml.safe_load(f)
            except Exception as e:
                # Fallback to defaults if config not found
                cls._config = {
                    'component_lengths': {
                        'subtitle': {'default': 15, 'min': 13, 'max': 17},
                        'caption': {'default': 25, 'min': 23, 'max': 27},
                        'description': {'default': 150, 'min': 140, 'max': 160},
                        'faq': {'default': 100, 'min': 80, 'max': 120},
                        'troubleshooter': {'default': 120, 'min': 100, 'max': 140}
                    }
                }
        return cls._config
    
    @classmethod
    def _get_component_lengths(cls, component_type: str) -> Dict[str, int]:
        """Get length configuration for component type from config.yaml.
        
        Dynamically calculates min/max from length_variation_range slider.
        """
        config = cls._load_config()
        lengths = config.get('component_lengths', {}).get(component_type, {})
        
        # Get default length (simplified config format)
        if isinstance(lengths, int):
            default = lengths
            extraction_strategy = None
        elif isinstance(lengths, dict):
            if 'default' not in lengths:
                raise ValueError(f"Component '{component_type}' missing 'default' length in config")
            default = lengths['default']
            extraction_strategy = lengths.get('extraction_strategy')  # May be None
        else:
            raise ValueError(f"Component '{component_type}' has invalid length config format: {type(lengths)}")
        
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
        except Exception:
            # Fallback calculation
            result = {
                'default': default,
                'min': max(int(default * 0.9), default - 5),
                'max': min(int(default * 1.1), default + 5)
            }
            
            # Add extraction_strategy if present
            if extraction_strategy is not None:
                result['extraction_strategy'] = extraction_strategy
            
            return result
    
    # Component specifications discovered dynamically from:
    # 1. prompts/*.txt files (content instructions)
    # 2. config.yaml component_lengths section (word counts)
    # NO hardcoded component types - all defined externally
    
    @classmethod
    def _discover_components(cls) -> Dict[str, Dict]:
        """Discover available components from prompts/components directory.
        
        Returns component specs by scanning prompts/components/*.txt files.
        Each .txt file defines a component type.
        """
        specs = {}
        components_dir = Path(__file__).parent.parent.parent / 'domains' / 'materials' / 'prompts'
        
        if not components_dir.exists():
            return specs
        
        # Scan for .txt files in prompts/components directory
        for prompt_file in components_dir.glob('*.txt'):
            component_type = prompt_file.stem  # filename without .txt
            
            # Skip system/utility prompts (shouldn't be any, but just in case)
            if component_type.startswith('_'):
                continue
            
            specs[component_type] = {
                'end_punctuation': True,  # Default, can be overridden in config
                'prompt_template_file': f'domains/materials/prompts/{prompt_file.name}'
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
            enrichment_strategy='Extract from Materials.yaml machineSettings: power, frequency, pulse duration, etc.',
            example_facts='Power: 100W; Frequency: 50kHz; Pulse Duration: 200ns; Spot Size: 50μm',
            terminology_style='Precise and technical; always include units; cite ranges and thresholds; explain trade-offs'
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
            'settings': cls.settings
        }
        
        factory = method_map.get(domain)
        if not factory:
            raise ValueError(f"Unknown domain: {domain}. "
                           f"Available: {', '.join(method_map.keys())}")
        
        return factory()
