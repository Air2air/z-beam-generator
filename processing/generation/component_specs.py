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
    
    Attributes:
        name: Component identifier (subtitle, caption, etc.)
        default_length: Target word count
        format_rules: Specific formatting requirements
        focus_areas: What to emphasize in content
        style_notes: Additional style guidance
        end_punctuation: Whether to include period at end
        min_length: Minimum word count (from config)
        max_length: Maximum word count (from config)
    """
    name: str
    default_length: int
    format_rules: str
    focus_areas: str
    style_notes: str
    end_punctuation: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    
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
        elif isinstance(lengths, dict):
            if 'default' not in lengths:
                raise ValueError(f"Component '{component_type}' missing 'default' length in config")
            default = lengths['default']
        else:
            raise ValueError(f"Component '{component_type}' has invalid length config format: {type(lengths)}")
        
        # Calculate dynamic range from length_variation_range slider
        try:
            if 'length_variation_range' not in config:
                raise ValueError("Config missing 'length_variation_range' - required for dynamic length calculation")
            length_variation = config['length_variation_range']  # 0-100
            # Map slider to percentage: 0→10%, 50→25%, 100→40%
            variation_pct = 0.10 + (length_variation / 100.0 * 0.30)
            variation_words = int(default * variation_pct)
            
            return {
                'default': default,
                'min': max(1, default - variation_words),
                'max': default + variation_words
            }
        except Exception:
            # Fallback calculation
            return {
                'default': default,
                'min': max(int(default * 0.9), default - 5),
                'max': min(int(default * 1.1), default + 5)
            }
    
    # Component specifications (content characteristics only - lengths come from config)
    SPEC_DEFINITIONS = {
        'subtitle': {
            'format_rules': 'No period at end; concise and punchy',
            'focus_areas': 'Unique characteristics, key benefits, practical applications',
            'style_notes': 'Professional but natural; vary sentence structure; avoid formulaic patterns',
            'end_punctuation': False
        },
        
        'caption': {
            'format_rules': 'Technical description with measurements when relevant',
            'focus_areas': 'Surface analysis details, microscopy observations, specific data points',
            'style_notes': 'Technical but accessible; include 1-2 measurements; mix short and long sentences',
            'end_punctuation': True
        },
        
        'description': {
            'format_rules': 'Comprehensive overview with multiple paragraphs',
            'focus_areas': 'Properties, applications, cleaning process details, benefits',
            'style_notes': 'Informative and detailed; balance technical accuracy with readability',
            'end_punctuation': True
        },
        
        'faq': {
            'format_rules': 'Question-and-answer format; direct and helpful response',
            'focus_areas': 'Common user concerns, practical guidance, troubleshooting tips, best practices',
            'style_notes': 'Conversational yet authoritative; answer completely but concisely; use second person',
            'end_punctuation': True
        },
        
        'troubleshooter': {
            'format_rules': 'Problem diagnosis and solution steps; actionable guidance',
            'focus_areas': 'Issue identification, root causes, step-by-step solutions, prevention tips',
            'style_notes': 'Clear and methodical; use numbered steps when appropriate; focus on actionable fixes',
            'end_punctuation': True
        }
    }
    
    @classmethod
    def get_spec(cls, component_type: str) -> ComponentSpec:
        """
        Get specification for component type.
        Dynamically loads lengths from config.yaml.
        
        Args:
            component_type: Component identifier
            
        Returns:
            ComponentSpec object with lengths from config
            
        Raises:
            KeyError: If component type not registered
        """
        spec_def = cls.SPEC_DEFINITIONS.get(component_type)
        if not spec_def:
            raise KeyError(f"Unknown component type: {component_type}. "
                         f"Available: {', '.join(cls.SPEC_DEFINITIONS.keys())}")
        
        # Get lengths from config
        lengths = cls._get_component_lengths(component_type)
        
        # Build ComponentSpec with config lengths
        return ComponentSpec(
            name=component_type,
            default_length=lengths['default'],
            min_length=lengths['min'],
            max_length=lengths['max'],
            format_rules=spec_def['format_rules'],
            focus_areas=spec_def['focus_areas'],
            style_notes=spec_def['style_notes'],
            end_punctuation=spec_def['end_punctuation']
        )
    
    @classmethod
    def register(cls, spec: ComponentSpec):
        """
        Register new component type.
        Note: This now registers the definition only. Lengths come from config.
        
        Args:
            spec: ComponentSpec to register
        """
        cls.SPEC_DEFINITIONS[spec.name] = {
            'format_rules': spec.format_rules,
            'focus_areas': spec.focus_areas,
            'style_notes': spec.style_notes,
            'end_punctuation': spec.end_punctuation
        }
    
    @classmethod
    def list_types(cls) -> list:
        """Get list of all registered component types"""
        return list(cls.SPEC_DEFINITIONS.keys())
    
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
