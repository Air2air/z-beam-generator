"""
Enricher Registry and Factory

Central registry for all library enrichers with factory pattern.
"""

from typing import Dict, Type, Optional
from pathlib import Path

from export.enrichers.base import BaseLibraryEnricher
from .regulatory_enricher import RegulatoryStandardsEnricher
from .ppe_enricher import PPELibraryEnricher
from .emergency_response_enricher import EmergencyResponseEnricher
from .laser_parameters_enricher import LaserParametersEnricher
from .machine_settings_enricher import MachineSettingsEnricher
from .material_applications_enricher import MaterialApplicationsEnricher
from .material_properties_enricher import MaterialPropertiesEnricher
from .contaminant_appearance_enricher import ContaminantAppearanceEnricher
from .chemical_properties_enricher import ChemicalPropertiesEnricher
from .health_effects_enricher import HealthEffectsEnricher
from .environmental_impact_enricher import EnvironmentalImpactEnricher
from .detection_monitoring_enricher import DetectionMonitoringEnricher


class EnricherRegistry:
    """Registry of all available enrichers."""
    
    _enrichers: Dict[str, Type[BaseLibraryEnricher]] = {
        'regulatory_standards': RegulatoryStandardsEnricher,
        'ppe_requirements': PPELibraryEnricher,
        'emergency_response': EmergencyResponseEnricher,
        'laser_parameters': LaserParametersEnricher,
        'machine_settings': MachineSettingsEnricher,
        'material_applications': MaterialApplicationsEnricher,
        'material_properties': MaterialPropertiesEnricher,
        'contaminant_appearance': ContaminantAppearanceEnricher,
        'chemical_properties': ChemicalPropertiesEnricher,
        'health_effects': HealthEffectsEnricher,
        'environmental_impact': EnvironmentalImpactEnricher,
        'detection_monitoring': DetectionMonitoringEnricher,
    }
    
    @classmethod
    def get_enricher(
        cls,
        library_type: str,
        library_file: Optional[Path] = None
    ) -> Optional[BaseLibraryEnricher]:
        """
        Get an enricher instance by library type.
        
        Args:
            library_type: Type of library (e.g., 'regulatory_standards')
            library_file: Optional custom library file path
            
        Returns:
            Enricher instance or None if type not registered
        """
        enricher_class = cls._enrichers.get(library_type)
        if not enricher_class:
            return None
            
        return enricher_class(library_file)
    
    @classmethod
    def register_enricher(
        cls,
        library_type: str,
        enricher_class: Type[BaseLibraryEnricher]
    ) -> None:
        """
        Register a new enricher type.
        
        Args:
            library_type: Type identifier
            enricher_class: Enricher class to register
        """
        cls._enrichers[library_type] = enricher_class
    
    @classmethod
    def list_enrichers(cls) -> list[str]:
        """Get list of all registered enricher types."""
        return list(cls._enrichers.keys())
