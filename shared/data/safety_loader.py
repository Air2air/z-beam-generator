# Centralized Loader for Safety and Standards Data
# Loads modular safety templates, fume compounds, citations, and laser presets
# Used by: exporters, generators, validation utilities
# Last updated: December 15, 2025

import yaml
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional, Any

class SafetyDataLoader:
    """Centralized loader for all modular safety and standards data."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent / 'data'
        self.safety_path = self.base_path / 'safety'
        self.standards_path = self.base_path / 'standards'
        self.laser_path = self.base_path / 'laser'
        
    @lru_cache(maxsize=1)
    def load_fume_compounds(self) -> Dict[str, Any]:
        """Load fume compounds library."""
        file_path = self.safety_path / 'Fume_Compounds.yaml'
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return data.get('compounds', {})
    
    @lru_cache(maxsize=1)
    def load_safety_templates(self) -> Dict[str, Any]:
        """Load safety templates (PPE, ventilation, risk levels)."""
        file_path = self.safety_path / 'Safety_Templates.yaml'
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    @lru_cache(maxsize=1)
    def load_citations(self) -> Dict[str, Any]:
        """Load citations and standards library."""
        file_path = self.standards_path / 'Citations.yaml'
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return data.get('standards', {})
    
    @lru_cache(maxsize=1)
    def load_laser_presets(self) -> Dict[str, Any]:
        """Load laser parameter presets."""
        file_path = self.laser_path / 'Parameter_Presets.yaml'
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return data.get('presets', {})
    
    def get_fume_compound(self, compound_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific fume compound by ID."""
        compounds = self.load_fume_compounds()
        return compounds.get(compound_id)
    
    def hydrate_fume_compounds(self, compound_refs: List[str]) -> List[Dict[str, Any]]:
        """
        Hydrate fume compound references to full objects.
        
        Args:
            compound_refs: List of compound IDs (e.g., ['carbon_monoxide', 'formaldehyde'])
            
        Returns:
            List of full compound objects with all fields
        """
        compounds = self.load_fume_compounds()
        hydrated = []
        
        for ref in compound_refs:
            if isinstance(ref, dict):
                # Already hydrated
                hydrated.append(ref)
            elif isinstance(ref, str):
                # Need to hydrate
                compound = compounds.get(ref)
                if compound:
                    hydrated.append(compound)
                else:
                    print(f"Warning: Fume compound '{ref}' not found in library")
                    
        return hydrated
    
    def get_ppe_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific PPE template by ID."""
        templates = self.load_safety_templates()
        return templates.get('ppe_levels', {}).get(template_id)
    
    def get_ventilation_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific ventilation template by ID."""
        templates = self.load_safety_templates()
        return templates.get('ventilation_requirements', {}).get(template_id)
    
    def get_citation(self, citation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific citation/standard by ID."""
        citations = self.load_citations()
        return citations.get(citation_id)
    
    def hydrate_citations(self, citation_refs: List[str]) -> List[str]:
        """
        Hydrate citation references to full names.
        
        Args:
            citation_refs: List of citation IDs (e.g., ['iec_60825', 'osha_ppe'])
            
        Returns:
            List of full citation names
        """
        citations = self.load_citations()
        hydrated = []
        
        for ref in citation_refs:
            if isinstance(ref, str):
                citation = citations.get(ref)
                if citation:
                    hydrated.append(citation.get('full_name', ref))
                else:
                    # Assume it's already a full name
                    hydrated.append(ref)
                    
        return hydrated
    
    def get_citation_set(self, set_name: str) -> List[str]:
        """Get a predefined citation set (e.g., 'general_laser_safety')."""
        file_path = self.standards_path / 'Citations.yaml'
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        citation_sets = data.get('citation_sets', {})
        citation_set = citation_sets.get(set_name, {})
        return citation_set.get('citations', [])
    
    def get_laser_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific laser parameter preset by ID."""
        presets = self.load_laser_presets()
        return presets.get(preset_id)
    
    def apply_laser_preset(self, preset_id: str, overrides: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Apply a laser preset with optional parameter overrides.
        
        Args:
            preset_id: Preset identifier (e.g., 'organic_light')
            overrides: Optional dict of parameters to override
            
        Returns:
            Complete laser parameters dict
        """
        preset = self.get_laser_preset(preset_id)
        if not preset:
            raise ValueError(f"Laser preset '{preset_id}' not found")
        
        # Deep copy preset parameters
        params = preset.get('laser_parameters', {}).copy()
        
        # Apply overrides if provided
        if overrides:
            for key, value in overrides.items():
                if isinstance(value, dict) and isinstance(params.get(key), dict):
                    # Merge nested dicts
                    params[key].update(value)
                else:
                    # Replace value
                    params[key] = value
        
        return params


# Convenience functions for backward compatibility
_loader = SafetyDataLoader()

def get_fume_compound(compound_id: str) -> Optional[Dict[str, Any]]:
    """Get a fume compound by ID."""
    return _loader.get_fume_compound(compound_id)

def hydrate_fume_compounds(compound_refs: List[str]) -> List[Dict[str, Any]]:
    """Hydrate fume compound references to full objects."""
    return _loader.hydrate_fume_compounds(compound_refs)

def get_ppe_template(template_id: str) -> Optional[Dict[str, Any]]:
    """Get a PPE template by ID."""
    return _loader.get_ppe_template(template_id)

def get_ventilation_template(template_id: str) -> Optional[Dict[str, Any]]:
    """Get a ventilation template by ID."""
    return _loader.get_ventilation_template(template_id)

def get_citation(citation_id: str) -> Optional[Dict[str, Any]]:
    """Get a citation/standard by ID."""
    return _loader.get_citation(citation_id)

def hydrate_citations(citation_refs: List[str]) -> List[str]:
    """Hydrate citation references to full names."""
    return _loader.hydrate_citations(citation_refs)

def get_laser_preset(preset_id: str) -> Optional[Dict[str, Any]]:
    """Get a laser parameter preset by ID."""
    return _loader.get_laser_preset(preset_id)

def apply_laser_preset(preset_id: str, overrides: Optional[Dict] = None) -> Dict[str, Any]:
    """Apply a laser preset with optional overrides."""
    return _loader.apply_laser_preset(preset_id, overrides)


if __name__ == '__main__':
    # Test loading
    loader = SafetyDataLoader()
    
    print("✅ Testing Fume Compounds Library...")
    compounds = loader.load_fume_compounds()
    print(f"   Loaded {len(compounds)} fume compounds")
    
    print("\n✅ Testing Safety Templates...")
    templates = loader.load_safety_templates()
    ppe_levels = templates.get('ppe_levels', {})
    print(f"   Loaded {len(ppe_levels)} PPE templates")
    
    print("\n✅ Testing Citations Library...")
    citations = loader.load_citations()
    print(f"   Loaded {len(citations)} citations/standards")
    
    print("\n✅ Testing Laser Presets...")
    presets = loader.load_laser_presets()
    print(f"   Loaded {len(presets)} laser presets")
    
    print("\n✅ Testing Hydration...")
    fumes = loader.hydrate_fume_compounds(['carbon_monoxide', 'formaldehyde'])
    print(f"   Hydrated {len(fumes)} fume compounds")
    
    cites = loader.hydrate_citations(['iec_60825', 'osha_ppe'])
    print(f"   Hydrated {len(cites)} citations")
    
    print("\n✅ All loaders working correctly!")
