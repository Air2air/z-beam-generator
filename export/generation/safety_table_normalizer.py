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
        
        # Merge with existing safety data (preserve regulatory_standards, etc.)
        data['relationships']['safety'].update(safety_data)
        
        logger.info(f"✓ Migrated safety_data to relationships.safety")
        
        return data
    
    def _normalize_tables(self, safety: Dict[str, Any]) -> None:
        """Normalize table structures in-place."""
        
        # Normalize fumes_generated (array → presentation + items)
        if 'fumes_generated' in safety:
            fumes = safety['fumes_generated']
            if isinstance(fumes, list):
                safety['fumes_generated'] = {
                    'presentation': 'table',
                    'items': fumes
                }
                
        # Normalize particulate_generation (dict → presentation + items)
        if 'particulate_generation' in safety:
            particulate = safety['particulate_generation']
            if isinstance(particulate, dict) and 'presentation' not in particulate:
                safety['particulate_generation'] = {
                    'presentation': 'table',
                    'items': [particulate]
                }
        
        # Normalize risk assessments (dict → presentation + items)
        risk_fields = ['fire_explosion_risk', 'toxic_gas_risk', 'visibility_hazard']
        for field in risk_fields:
            if field in safety:
                risk = safety[field]
                if isinstance(risk, dict) and 'presentation' not in risk:
                    safety[field] = {
                        'presentation': 'card',
                        'items': [risk]
                    }
        
        # Normalize descriptive fields (dict → presentation + items)  
        descriptive_fields = ['ppe_requirements', 'ventilation_requirements']
        for field in descriptive_fields:
            if field in safety:
                desc = safety[field]
                if isinstance(desc, dict) and 'presentation' not in desc:
                    safety[field] = {
                        'presentation': 'descriptive',
                        'items': [desc]
                    }
