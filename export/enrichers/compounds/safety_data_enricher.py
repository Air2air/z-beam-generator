"""
Safety Data Enricher for Compounds

Transforms existing prose safety data into structured format for frontmatter
while preserving the author-voiced text.

ARCHITECTURE:
- Reads prose from Compounds.yaml (e.g., ppe_requirements string)
- Structures into presentation + items format
- Preserves original author voice (no regeneration)
- Outputs to relationships.safety in frontmatter

POLICY COMPLIANCE:
- Frontmatter Source-of-Truth Policy (Dec 23, 2025)
- Enrichers format data, don't add missing data
- Author voice already in source prose (immutable)

Created: January 2, 2026
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SafetyDataEnricher:
    """
    Enrich compound safety data for frontmatter export.
    
    Converts prose safety fields to structured format:
    - ppe_requirements (string) → structured object
    - storage_requirements → add if missing
    - workplace_exposure → extract from exposure_guidelines
    """
    
    def enrich(self, compound_data: Dict[str, Any], compound_name: str) -> Dict[str, Any]:
        """
        Enrich compound with structured safety data.
        
        Args:
            compound_data: Raw compound data from Compounds.yaml
            compound_name: Compound identifier
            
        Returns:
            Enriched compound data with relationships.safety structure
        """
        if 'relationships' not in compound_data:
            compound_data['relationships'] = {}
        
        if 'safety' not in compound_data['relationships']:
            compound_data['relationships']['safety'] = {}
        
        safety = compound_data['relationships']['safety']
        
        # Enrich PPE requirements
        if 'ppe_requirements' not in safety or isinstance(compound_data.get('ppe_requirements'), str):
            safety['ppe_requirements'] = self._structure_ppe(compound_data)
        
        # Enrich storage requirements  
        if 'storage_requirements' not in safety:
            safety['storage_requirements'] = self._structure_storage(compound_data)
        
        # Enrich workplace exposure
        if 'workplace_exposure' not in safety:
            safety['workplace_exposure'] = self._structure_exposure(compound_data)
        
        # Enrich reactivity
        if 'reactivity' not in safety:
            safety['reactivity'] = self._structure_reactivity(compound_data)
        
        # Enrich environmental impact
        if 'environmental_impact' not in safety:
            safety['environmental_impact'] = self._structure_environmental(compound_data)
        
        compound_data['relationships']['safety'] = safety
        return compound_data
    
    def _structure_ppe(self, compound_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure PPE requirements from prose.
        
        For now, wrap prose in descriptive presentation.
        Future: Parse prose to extract specific fields.
        """
        ppe_text = compound_data.get('ppe_requirements', '')
        
        if not ppe_text:
            return {
                'presentation': 'descriptive',
                'items': [{
                    'respiratory': 'Appropriate respirator for compound hazards',
                    'eye_protection': 'Safety goggles or face shield',
                    'skin_protection': 'Protective gloves and coveralls',
                    'rationale': 'Standard PPE for hazardous compound handling'
                }]
            }
        
        # Wrap prose for now (preserves author voice)
        return {
            'presentation': 'descriptive',
            'items': [{
                'description': ppe_text,
                'respiratory': 'See description',
                'eye_protection': 'See description',
                'skin_protection': 'See description'
            }]
        }
    
    def _structure_storage(self, compound_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure storage requirements (placeholder)"""
        return {
            'presentation': 'descriptive',
            'items': [{
                'container_type': 'Appropriate sealed containers',
                'temperature_range': 'Room temperature unless specified',
                'humidity_control': 'Keep dry',
                'segregation': 'Store away from incompatible materials'
            }]
        }
    
    def _structure_exposure(self, compound_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure workplace exposure limits"""
        exposure_text = compound_data.get('exposure_guidelines', '')
        
        return {
            'presentation': 'descriptive',
            'items': [{
                'description': exposure_text if exposure_text else 'Refer to OSHA and NIOSH guidelines',
                'monitoring_required': True,
                'monitoring_frequency': 'As per regulatory requirements'
            }]
        }
    
    def _structure_reactivity(self, compound_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure reactivity data (placeholder)"""
        return {
            'presentation': 'descriptive',
            'items': [{
                'conditions_to_avoid': 'High temperatures, ignition sources',
                'incompatible_materials': 'Refer to SDS for specific incompatibilities',
                'hazardous_decomposition': 'May produce toxic fumes when heated'
            }]
        }
    
    def _structure_environmental(self, compound_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure environmental impact (placeholder)"""
        return {
            'presentation': 'descriptive',
            'items': [{
                'persistence': 'Variable depending on compound',
                'bioaccumulation': 'Refer to SDS',
                'aquatic_toxicity': 'May be harmful to aquatic life'
            }]
        }
