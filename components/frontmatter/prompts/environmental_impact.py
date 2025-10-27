#!/usr/bin/env python3
"""
Environmental Impact Prompt Builder

Two-phase prompting for environmental impact assessment within frontmatter generation.
"""

import logging
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class EnvironmentalImpactPromptBuilder:
    """
    Build research-validated environmental impact prompts.
    
    Pattern: research_prompt() → validate_response() → generation_prompt()
    """
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent / 'templates'
        self._load_templates()
    
    def _load_templates(self):
        """Load research template"""
        research_path = self.prompts_dir / 'environmental_research_phase.md'
        
        if not research_path.exists():
            logger.warning(f"Environmental prompt template not found in {self.prompts_dir}")
            self.research_template = None
            return
        
        with open(research_path, 'r') as f:
            self.research_template = f.read()
    
    def build_research_prompt(self, material_name: str, category: str) -> str:
        """
        Phase 1: Build environmental impact research prompt.
        
        Researches environmental benefits vs chemical/mechanical cleaning:
        - Chemical waste reduction
        - Water consumption
        - VOC emissions
        - Energy efficiency
        - Waste disposal
        
        Args:
            material_name: Name of material
            category: Material category
            
        Returns:
            Formatted research prompt
        """
        if not self.research_template:
            return self._build_inline_research_prompt(material_name, category)
        
        return self.research_template.format(
            material_name=material_name,
            category=category
        )
    
    def _build_inline_research_prompt(self, material_name: str, category: str) -> str:
        """Fallback research prompt if template missing"""
        return f"""Research the environmental impact of laser cleaning {material_name} compared to traditional methods.

CONTEXT:
- Material: {material_name}
- Category: {category}

RESEARCH REQUIREMENTS:

Compare laser cleaning to chemical and mechanical cleaning methods for {material_name} across these dimensions:

1. Chemical Waste Reduction
   - What chemicals would traditional methods use?
   - Volume of chemical waste eliminated
   - Hazardous waste classification

2. Water Consumption
   - Water usage comparison (liters/m²)
   - Wastewater treatment requirements
   - Water conservation benefits

3. VOC Emissions
   - Volatile organic compounds from solvents
   - Air quality improvements
   - Regulatory compliance (EPA standards)

4. Energy Efficiency
   - Energy consumption comparison (kWh/m²)
   - Carbon footprint reduction
   - Renewable energy compatibility

5. Waste Disposal
   - Solid waste generation
   - Disposal requirements and costs
   - Recyclability of removed material

OUTPUT FORMAT (YAML):

```yaml
environmental_impact:
  chemical_waste_reduction:
    traditional_chemicals: ["Chemical 1", "Chemical 2"]
    waste_volume_reduction: "X% reduction"
    benefits: "Description of benefits"
  
  water_consumption:
    traditional_usage: "X liters/m²"
    laser_usage: "Y liters/m² (or zero)"
    reduction: "Z% reduction"
  
  voc_emissions:
    traditional_emissions: "Description"
    laser_emissions: "Zero or minimal"
    air_quality_benefit: "Description"
  
  energy_efficiency:
    comparison: "Description of energy usage"
    carbon_reduction: "X% reduction"
  
  waste_disposal:
    traditional_waste: "Description"
    laser_waste: "Minimal particulate"
    disposal_simplification: "Description"
```

Focus on quantifiable metrics where possible. Cite EPA or industry standards.
"""
    
    def validate_research_quality(self, research_response: str) -> Dict:
        """
        Validate environmental impact research quality.
        
        Returns:
            Dict with validation results
        """
        # Simple validation
        has_metrics = any(keyword in research_response.lower() 
                         for keyword in ['reduction', 'waste', 'emission', 'consumption'])
        
        return {
            'passed': has_metrics,
            'quality_score': 75.0 if has_metrics else 25.0,
            'impact_data': {},  # Would parse properly in full implementation
            'issues': [] if has_metrics else ['No environmental metrics found']
        }
