"""
General Text Prompt Builder for All Components

Simplified prompt generation system for subtitles, captions, FAQs, and other text components.
Generates CONTEXT-ONLY prompts without author voice markers.
Author voice is added later by the voice postprocessor.

Architecture:
1. Generate context-only prompt (this module)
2. Call API to generate content
3. Apply voice postprocessor (adds author-specific markers)
4. Save to Materials.yaml
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


# Component-specific configurations
COMPONENT_CONFIGS = {
    "subtitle": {
        "length": "12-16 words",
        "tone": "Accessible and engaging (voice added by postprocessor)",
        "examples": {
            "excellent": [
                "Laser cleaning removes rust and contaminants from Copper while preserving its conductivity",
                "Gentle laser pulses restore Bronze surfaces and protect the original patina",
                "Controlled laser treatment cleans Marble without causing cracks or surface damage to the stone",
                "Short laser pulses remove old coatings from Glass and maintain the surface clarity",
                "Laser cleaning provides a way to restore Oak's natural grain without causing charring or burning",
                "Pulsed lasers remove dirt from Granite surfaces while preserving the stone's original texture"
            ],
            "avoid": [
                "Optimized fluence effectively removes contaminants without thermal distortion (too technical)",
                "Low-fluence photonic ablation minimizes delamination risks (excessive jargon)",
                "Nanosecond pulses modulate oxide stoichiometry (overly technical)"
            ]
        }
    },
    "caption": {
        "length": "15-25 words",
        "tone": "Informative and descriptive (voice added by postprocessor)",
        "examples": {
            "excellent": [
                "This detailed view shows how laser cleaning restores the original surface of aged Bronze, carefully removing oxidation while preserving the metal's natural patina and structural integrity"
            ],
            "avoid": [
                "Photonic ablation removes oxide layers (too technical)"
            ]
        }
    },
    "faq_answer": {
        "length": "40-80 words",
        "tone": "Conversational and helpful (voice added by postprocessor)",
        "examples": {
            "excellent": [
                "Laser cleaning removes rust and contaminants from metal surfaces by using concentrated light pulses. The laser beam heats the unwanted material, causing it to vaporize or flake away. This process works well because it targets only the contamination, leaving the underlying metal surface intact. It is particularly effective for delicate surfaces where traditional abrasive methods might cause damage or alter the original finish."
            ],
            "avoid": [
                "Photonic ablation utilizes high-fluence nanosecond pulses (too technical)"
            ]
        }
    }
}


@dataclass
class FocusArea:
    """Represents a content focus area for variation"""
    id: str
    name: str
    prompt_addition: str


class TextPromptBuilder:
    """
    Universal prompt builder for all text generation components.
    
    Generates CONTEXT-ONLY prompts without author voice markers.
    Voice is added by postprocessor after API generation.
    
    Features:
    - Component-specific length/tone requirements
    - Plain language anti-jargon rules
    - Focus area variation support
    - Sibling material comparison
    """
    
    def __init__(self):
        self.component_configs = COMPONENT_CONFIGS
    
    def build_prompt(
        self,
        component_type: str,
        material_name: str,
        category: str,
        subcategory: str = "",
        author_id: int = None,
        focus_area: Optional[FocusArea] = None,
        siblings: List[str] = None,
        additional_context: Dict = None
    ) -> str:
        """
        Build a complete prompt for any text component.
        
        Args:
            component_type: 'subtitle', 'caption', 'faq_answer', etc.
            material_name: Name of the material
            category: Material category
            subcategory: Material subcategory (optional)
            author_id: Author ID (1-4) for voice pattern
            focus_area: Optional FocusArea for content variation
            siblings: List of sibling material names for comparison
            additional_context: Extra context specific to component type
        
        Returns:
            Complete prompt string ready for API
        """
        
        # Get component configuration
        config = self.component_configs.get(
            component_type,
            self.component_configs["subtitle"]  # Default to subtitle
        )
        
        # Build prompt sections
        prompt_parts = []
        
        # Header
        prompt_parts.append(
            f"Generate a professional {component_type} for a laser cleaning guide about {material_name}."
        )
        prompt_parts.append("\nNOTE: Write in neutral professional tone. Author voice will be added in postprocessing.")
        
        # Material context
        context_lines = [
            f"- Material: {material_name}",
            f"- Category: {category}",
            f"- Subcategory: {subcategory or 'N/A'}"
        ]
        
        # Add sibling comparison if applicable
        if siblings and focus_area and 'sibling' in focus_area.id.lower():
            context_lines.append(f"- Sibling materials: {', '.join(siblings)}")
        
        # Add any additional context
        if additional_context:
            for key, value in additional_context.items():
                context_lines.append(f"- {key}: {value}")
        
        prompt_parts.append("MATERIAL CONTEXT:\n" + "\n".join(context_lines))
        
        # Requirements section
        requirements = [
            f"1. Length: {config['length']}",
            f"2. Tone: {config['tone']}",
            "3. Avoid technical jargon: NO \"fluence\", \"ablation\", \"thermal distortion\", \"stoichiometry\", \"delamination\"",
            "4. Use plain language: \"damage\" instead of \"thermal distortion\", \"separation\" instead of \"delamination\"",
            "5. Complete sentences with proper capitalization",
            "6. Material name should be capitalized",
            "7. Focus on practical benefits and real-world outcomes",
            "8. Use neutral professional tone (no casual markers like 'pretty', 'basically')"
        ]
        
        prompt_parts.append(f"{component_type.upper()} REQUIREMENTS:\n" + "\n".join(requirements))
        
        # Focus area section (if provided)
        if focus_area:
            prompt_parts.append(f"""
FOCUS AREA: {focus_area.name}
{focus_area.prompt_addition}
""")
        
        # Examples section
        if config["examples"]["excellent"]:
            excellent_examples = "\n- ".join(config["examples"]["excellent"])
            prompt_parts.append(f"""
EXCELLENT EXAMPLES (neutral professional tone, appropriate length):
- {excellent_examples}
""")
        
        if config["examples"]["avoid"]:
            avoid_examples = "\n- ".join(config["examples"]["avoid"])
            prompt_parts.append(f"""
AVOID EXAMPLES (problems to watch for):
- {avoid_examples}
""")
        
        # Final instruction
        prompt_parts.append(f"\nGenerate ONLY the {component_type} text (no quotes, no explanation):")
        
        return "\n".join(prompt_parts)
    
    def get_component_config(self, component_type: str) -> Dict:
        """Get configuration for a specific component type"""
        return self.component_configs.get(
            component_type,
            self.component_configs["subtitle"]
        )
    
    def add_component_config(self, component_type: str, config: Dict):
        """
        Add or update configuration for a new component type.
        
        Args:
            component_type: Name of the component (e.g., 'description', 'title')
            config: Configuration dict with 'length', 'tone', 'examples'
        """
        self.component_configs[component_type] = config


# Convenience function for quick access
def build_text_prompt(
    component_type: str,
    material_name: str,
    category: str,
    **kwargs
) -> str:
    """
    Quick function to build a text prompt without instantiating builder.
    
    Usage:
        prompt = build_text_prompt('subtitle', 'Bronze', 'Metals', author_id=2)
    """
    builder = TextPromptBuilder()
    return builder.build_prompt(component_type, material_name, category, **kwargs)
