#!/usr/bin/env python3
"""
Regulatory Standards Prompt Builder

Two-phase prompting for regulatory standards research within frontmatter generation.
"""

import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class RegulatoryStandardsPromptBuilder:
    """
    Build research-validated regulatory standards prompts.
    
    Pattern: research_prompt() → validate_response() → generation_prompt()
    """
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent / 'templates'
        self._load_templates()
    
    def _load_templates(self):
        """Load research template"""
        research_path = self.prompts_dir / 'regulatory_research_phase.md'
        
        if not research_path.exists():
            logger.warning(f"Regulatory prompt template not found in {self.prompts_dir}")
            self.research_template = None
            return
        
        with open(research_path, 'r') as f:
            self.research_template = f.read()
    
    def build_research_prompt(self, material_name: str, category: str,
                              industries: List[str]) -> str:
        """
        Phase 1: Build regulatory standards research prompt.
        
        Researches relevant standards for material + industries combination:
        - FDA (food, pharmaceutical)
        - ANSI (general industrial)
        - ISO (international standards)
        - OSHA (workplace safety)
        - IEC (electrical/electronic)
        - EPA (environmental)
        
        Args:
            material_name: Name of material
            category: Material category
            industries: List of validated industries for context
            
        Returns:
            Formatted research prompt
        """
        if not self.research_template:
            return self._build_inline_research_prompt(material_name, category, industries)
        
        return self.research_template.format(
            material_name=material_name,
            category=category,
            industries=", ".join(industries)
        )
    
    def _build_inline_research_prompt(self, material_name: str, 
                                     category: str, 
                                     industries: List[str]) -> str:
        """Fallback research prompt if template missing"""
        industries_text = ", ".join(industries[:5])
        
        return f"""Research applicable regulatory standards for laser cleaning of {material_name}.

CONTEXT:
- Material: {material_name}
- Category: {category}
- Industries: {industries_text}

RESEARCH REQUIREMENTS:

Identify regulatory standards that apply to laser cleaning of {material_name} in the given industries.

Consider these organizations:
1. FDA - Food and Drug Administration (food, pharmaceutical, medical)
2. ANSI - American National Standards Institute (general industrial)
3. ISO - International Organization for Standardization (all industries)
4. OSHA - Occupational Safety and Health Administration (workplace safety)
5. IEC - International Electrotechnical Commission (electrical/electronic)
6. EPA - Environmental Protection Agency (environmental compliance)

For EACH applicable standard, provide:
- Organization (FDA/ANSI/ISO/OSHA/IEC/EPA)
- Standard ID (e.g., "FDA 21 CFR Part 110", "ISO 9001")
- longName (full descriptive name of standard)
- Applicability reason (why it applies to this material/industries)
- Compliance requirements summary

OUTPUT FORMAT (YAML):

```yaml
standards:
  - organization: "FDA"
    standard_id: "21 CFR Part 110"
    longName: "Current Good Manufacturing Practice in Manufacturing, Packing, or Holding Human Food"
    applicability: "Applies to food industry {material_name} surface cleaning requirements"
    requirements: "Brief summary of relevant requirements"
```

Only include standards that are DIRECTLY applicable to laser cleaning of {material_name}.
"""
    
    def validate_research_quality(self, research_response: str) -> Dict:
        """
        Validate regulatory standards research quality.
        
        Returns:
            Dict with validation results
        """
        # Simple validation - in production would parse YAML properly
        has_standards = 'standard_id' in research_response or 'organization' in research_response
        
        return {
            'passed': has_standards,
            'quality_score': 80.0 if has_standards else 20.0,
            'standards': [],  # Would parse properly in full implementation
            'issues': [] if has_standards else ['No standards found in response']
        }
