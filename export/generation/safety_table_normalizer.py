"""
Safety Data Migration Enricher for Contaminants

Performs two critical operations:
1. MOVE safety_data from nested location to relationships.safety
2. NORMALIZE table structures (add presentation + items wrappers)

Migration path:
  FROM: relationships.operational.laser_properties.items[0].safety_data
  TO:   relationships.safety.*

Author: Z-Beam Generator
Date: January 2, 2026
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SafetyTableNormalizer:
    """Move and normalize safety data to relationships.safety with proper table structures."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize normalizer with optional config."""
        self.config = config or {}
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generator interface - calls enrich() internally."""
        return self.enrich(data)
    
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate safety_data to relationships.safety and normalize table structures."""
        # Step 1: Extract safety_data from nested location
        safety_data = None
        
        if 'relationships' in data:
            operational = data['relationships'].get('operational', {})
            if 'laser_properties' in operational:
                lp = operational['laser_properties']
                if isinstance(lp, dict) and 'items' in lp and len(lp['items']) > 0:
                    safety_data = lp['items'][0].pop('safety_data', None)
        
        if not safety_data:
            return data
        
        # Step 2: Normalize table structures
        self._normalize_tables(safety_data)
        
        # Step 3: Move to relationships.safety
        if 'relationships' not in data:
            data['relationships'] = {}
        if 'safety' not in data['relationships']:
            data['relationships']['safety'] = {}
        
        # Merge with existing safety data, preserving _section metadata from existing sections
        existing_safety = data['relationships']['safety']
        for key, value in safety_data.items():
            if key in existing_safety and isinstance(existing_safety[key], dict) and isinstance(value, dict):
                # Section exists in both - preserve _section from existing
                existing_section_meta = existing_safety[key].get('_section')
                existing_safety[key] = value  # Update with new data
                if existing_section_meta:
                    existing_safety[key]['_section'] = existing_section_meta  # Restore _section
            else:
                # New section - just add it
                existing_safety[key] = value
        
        logger.info(f"✓ Migrated safety_data to relationships.safety (preserved _section metadata)")
        
        return data
    
    def _normalize_tables(self, safety: Dict[str, Any]) -> None:
        """Normalize table structures in-place, preserving _section metadata."""
        
        # Normalize fumes_generated (array → presentation + items)
        if 'fumes_generated' in safety:
            fumes = safety['fumes_generated']
            if isinstance(fumes, list):
                # Preserve _section if it exists
                existing_section = safety['fumes_generated'].get('_section') if isinstance(safety.get('fumes_generated'), dict) else None
                safety['fumes_generated'] = {
                    'presentation': 'table',
                    'items': fumes
                }
                if existing_section:
                    safety['fumes_generated']['_section'] = existing_section
            elif isinstance(fumes, dict) and 'items' not in fumes and 'presentation' not in fumes:
                # Has data but not normalized - preserve _section
                existing_section = fumes.pop('_section', None)
                safety['fumes_generated'] = {
                    'presentation': 'table',
                    'items': [fumes]
                }
                if existing_section:
                    safety['fumes_generated']['_section'] = existing_section
                
        # Normalize particulate_generation (dict → presentation + items)
        if 'particulate_generation' in safety:
            particulate = safety['particulate_generation']
            if isinstance(particulate, dict):
                existing_section = particulate.pop('_section', None)
                if 'presentation' not in particulate or 'items' not in particulate:
                    # Needs normalization
                    if 'items' in particulate:
                        items = particulate['items']
                    else:
                        items = [particulate] if any(k for k in particulate.keys() if not k.startswith('_')) else []
                    safety['particulate_generation'] = {
                        'presentation': 'table',
                        'items': items
                    }
                if existing_section:
                    safety['particulate_generation']['_section'] = existing_section
        
        # Normalize risk assessments (dict → presentation + items), preserve _section
        risk_fields = ['fire_explosion_risk', 'toxic_gas_risk', 'visibility_hazard']
        for field in risk_fields:
            if field in safety:
                risk = safety[field]
                if isinstance(risk, dict):
                    existing_section = risk.pop('_section', None)
                    if 'presentation' not in risk or 'items' not in risk:
                        # Needs normalization
                        if 'items' in risk:
                            items = risk['items']
                        else:
                            items = [risk] if any(k for k in risk.keys() if not k.startswith('_')) else []
                        safety[field] = {
                            'presentation': 'card',
                            'items': items
                        }
                    if existing_section:
                        safety[field]['_section'] = existing_section
        
        # Normalize descriptive fields (dict → presentation + items), preserve _section
        descriptive_fields = ['ppe_requirements', 'ventilation_requirements']
        for field in descriptive_fields:
            if field in safety:
                desc = safety[field]
                if isinstance(desc, dict):
                    existing_section = desc.pop('_section', None)
                    if 'presentation' not in desc or 'items' not in desc:
                        # Needs normalization
                        if 'items' in desc:
                            items = desc['items']
                        else:
                            items = [desc] if any(k for k in desc.keys() if not k.startswith('_')) else []
                        safety[field] = {
                            'presentation': 'descriptive',
                            'items': items
                        }
                    if existing_section:
                        safety[field]['_section'] = existing_section

