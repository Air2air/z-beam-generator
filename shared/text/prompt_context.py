"""
Prompt Context - Unified Parameter Container

Simplifies PromptBuilder by grouping 15+ individual parameters into a single context object.

BEFORE (15+ individual parameters):
    prompt = PromptBuilder.build_unified_prompt(
        topic, voice, length, facts, context, component_type, domain,
        voice_params, enrichment_params, variation_seed, humanness_layer,
        faq_count, item_data, author, country, esl_traits, sentence_style
    )

AFTER (1 context object):
    context = PromptContext(
        topic=topic, voice=voice, facts=facts,
        domain=domain, component_type=component_type,
        humanness_layer=humanness_layer, item_data=item_data
    )
    prompt = PromptBuilder.build(context)

Created: January 20, 2026
Purpose: Reduce PromptBuilder complexity from 15+ params to 1 context object
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PromptContext:
    """
    Unified context container for prompt building.
    
    Groups all prompt parameters into a single structured object,
    replacing the 15+ individual parameters pattern with a clean interface.
    """
    
    # Core identification
    topic: str  # Material/item name
    component_type: str  # micro, description, faq, etc.
    domain: str  # materials, compounds, settings, etc.
    
    # Voice and author
    voice: Dict  # Full voice profile from persona YAML
    author: Optional[str] = None  # Author name (extracted from voice if needed)
    country: Optional[str] = None  # Author country (extracted from voice if needed)
    
    # Content context
    facts: Optional[str] = None  # Technical facts about the topic
    context: Optional[str] = None  # Additional contextual information
    item_data: Optional[Dict] = None  # Full item data for template placeholders
    
    # Generation parameters
    humanness_layer: Optional[str] = None  # Humanness instructions
    length: Optional[int] = None  # Target word count
    faq_count: Optional[int] = None  # Number of FAQ items (for FAQ generation)
    
    # Advanced parameters (optional)
    voice_params: Optional[Dict[str, float]] = None  # Voice parameter overrides
    enrichment_params: Optional[Dict] = None  # Technical intensity, etc.
    variation_seed: Optional[int] = None  # Structural variation seed
    
    # Legacy compatibility (auto-extracted if not provided)
    esl_traits: Optional[str] = field(default=None, init=False)
    sentence_style: Optional[str] = field(default=None, init=False)
    
    def __post_init__(self):
        """Auto-extract author info and legacy fields from voice profile"""
        if self.voice:
            # Extract author info if not provided
            if not self.author:
                self.author = self.voice.get('metadata', {}).get('name', 'Unknown')
            if not self.country:
                self.country = self.voice.get('metadata', {}).get('country', 'Unknown')
            
            # Extract legacy compatibility fields
            if not self.esl_traits and 'esl_linguistic_patterns' in self.voice:
                patterns = self.voice['esl_linguistic_patterns']
                self.esl_traits = ', '.join(patterns[:3]) if isinstance(patterns, list) else str(patterns)
            
            if not self.sentence_style and 'generation_constraints' in self.voice:
                constraints = self.voice['generation_constraints']
                self.sentence_style = constraints.get('sentence_structure', 'varied')
    
    def to_legacy_dict(self) -> Dict:
        """
        Convert to legacy parameter dict for backward compatibility.
        
        Returns dict suitable for old PromptBuilder.build_unified_prompt() signature.
        Allows gradual migration without breaking existing code.
        """
        return {
            'topic': self.topic,
            'voice': self.voice,
            'length': self.length,
            'facts': self.facts,
            'context': self.context,
            'component_type': self.component_type,
            'domain': self.domain,
            'voice_params': self.voice_params,
            'enrichment_params': self.enrichment_params,
            'variation_seed': self.variation_seed,
            'humanness_layer': self.humanness_layer,
            'faq_count': self.faq_count,
            'item_data': self.item_data,
            'author': self.author,
            'country': self.country,
            'esl_traits': self.esl_traits,
            'sentence_style': self.sentence_style
        }
    
    @classmethod
    def from_legacy_params(
        cls,
        topic: str,
        voice: Dict,
        component_type: str,
        domain: str,
        **kwargs
    ) -> 'PromptContext':
        """
        Create PromptContext from legacy individual parameters.
        
        Enables backward compatibility while migrating to context object pattern.
        """
        return cls(
            topic=topic,
            voice=voice,
            component_type=component_type,
            domain=domain,
            facts=kwargs.get('facts'),
            context=kwargs.get('context'),
            item_data=kwargs.get('item_data'),
            humanness_layer=kwargs.get('humanness_layer'),
            length=kwargs.get('length'),
            faq_count=kwargs.get('faq_count'),
            voice_params=kwargs.get('voice_params'),
            enrichment_params=kwargs.get('enrichment_params'),
            variation_seed=kwargs.get('variation_seed'),
            author=kwargs.get('author'),
            country=kwargs.get('country')
        )
    
    def validate(self) -> bool:
        """
        Validate that required fields are present.
        
        Returns:
            True if context is valid, raises ValueError otherwise
        """
        if not self.topic:
            raise ValueError("PromptContext missing required field: topic")
        if not self.component_type:
            raise ValueError("PromptContext missing required field: component_type")
        if not self.domain:
            raise ValueError("PromptContext missing required field: domain")
        if not self.voice:
            raise ValueError("PromptContext missing required field: voice")
        
        return True
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return (
            f"PromptContext("
            f"topic={self.topic}, "
            f"component={self.component_type}, "
            f"domain={self.domain}, "
            f"author={self.author}, "
            f"facts={len(self.facts) if self.facts else 0} chars, "
            f"humanness={len(self.humanness_layer) if self.humanness_layer else 0} chars"
            f")"
        )
