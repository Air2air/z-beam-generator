"""
Component Type Specifications

Defines characteristics and prompt templates for different content types.
Allows flexible generation without hardcoding in PromptBuilder.
"""

from typing import Dict, Optional
from dataclasses import dataclass


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
        if self.min_length is None:
            self.min_length = self.default_length - 2
        if self.max_length is None:
            self.max_length = self.default_length + 2


class ComponentRegistry:
    """
    Registry of all component types and their specifications.
    
    Supports dynamic addition of new component types without code changes.
    """
    
    # Built-in component specifications
    SPECS = {
        'subtitle': ComponentSpec(
            name='subtitle',
            default_length=15,
            format_rules='No period at end; concise and punchy',
            focus_areas='Unique characteristics, key benefits, practical applications',
            style_notes='Professional but natural; vary sentence structure; avoid formulaic patterns',
            end_punctuation=False
        ),
        
        'caption': ComponentSpec(
            name='caption',
            default_length=25,
            format_rules='Technical description with measurements when relevant',
            focus_areas='Surface analysis details, microscopy observations, specific data points',
            style_notes='Technical but accessible; include 1-2 measurements; mix short and long sentences',
            end_punctuation=True
        ),
        
        'description': ComponentSpec(
            name='description',
            default_length=150,
            min_length=140,
            max_length=160,
            format_rules='Comprehensive overview with multiple paragraphs',
            focus_areas='Properties, applications, cleaning process details, benefits',
            style_notes='Informative and detailed; balance technical accuracy with readability',
            end_punctuation=True
        ),
        
        'faq': ComponentSpec(
            name='faq',
            default_length=100,
            min_length=80,
            max_length=120,
            format_rules='Question-and-answer format; direct and helpful response',
            focus_areas='Common user concerns, practical guidance, troubleshooting tips, best practices',
            style_notes='Conversational yet authoritative; answer completely but concisely; use second person',
            end_punctuation=True
        ),
        
        'troubleshooter': ComponentSpec(
            name='troubleshooter',
            default_length=120,
            min_length=100,
            max_length=140,
            format_rules='Problem diagnosis and solution steps; actionable guidance',
            focus_areas='Issue identification, root causes, step-by-step solutions, prevention tips',
            style_notes='Clear and methodical; use numbered steps when appropriate; focus on actionable fixes',
            end_punctuation=True
        )
    }
    
    @classmethod
    def get_spec(cls, component_type: str) -> ComponentSpec:
        """
        Get specification for component type.
        
        Args:
            component_type: Component identifier
            
        Returns:
            ComponentSpec object
            
        Raises:
            KeyError: If component type not registered
        """
        spec = cls.SPECS.get(component_type)
        if not spec:
            raise KeyError(f"Unknown component type: {component_type}. "
                         f"Available: {', '.join(cls.SPECS.keys())}")
        return spec
    
    @classmethod
    def register(cls, spec: ComponentSpec):
        """
        Register new component type.
        
        Args:
            spec: ComponentSpec to register
        """
        cls.SPECS[spec.name] = spec
    
    @classmethod
    def list_types(cls) -> list:
        """Get list of all registered component types"""
        return list(cls.SPECS.keys())
    
    @classmethod
    def get_default_length(cls, component_type: str) -> int:
        """Get default length for component type"""
        return cls.get_spec(component_type).default_length


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
