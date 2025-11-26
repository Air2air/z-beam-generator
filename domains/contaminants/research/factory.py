"""
Contamination Researcher Factory

Creates appropriate researcher for contamination research tasks.
Mirrors domains.materials.research.factory.ResearcherFactory

Author: AI Assistant
Date: November 25, 2025
"""

from typing import Any, Dict, Type
from domains.contaminants.research.base import ContaminationResearcher
from domains.contaminants.research.pattern_researcher import PatternResearcher
from domains.contaminants.research.laser_properties_researcher import LaserPropertiesResearcher


class ContaminationResearcherFactory:
    """
    Factory for creating contamination researchers.
    
    Maps research task type → Researcher class
    
    Currently supports:
        - pattern: Research contamination pattern details (PatternResearcher)
        - laser: Research laser-specific properties (LaserPropertiesResearcher)
    
    Future extensibility:
        - compatibility: Research material-contamination compatibility
        - removal: Research contamination removal methods
        - formation: Research contamination formation processes
    
    Example:
        factory = ContaminationResearcherFactory()
        researcher = factory.create_researcher('laser', api_client)
        result = researcher.research('rust_oxidation', research_spec)
    """
    
    # Default researcher mappings
    _researchers: Dict[str, Type[ContaminationResearcher]] = {
        'pattern': PatternResearcher,
        'detail': PatternResearcher,  # Alias
        'information': PatternResearcher,  # Alias
        'laser': LaserPropertiesResearcher,
        'laser_properties': LaserPropertiesResearcher,  # Alias
        'optical': LaserPropertiesResearcher,  # Alias for optical properties
    }
    
    @classmethod
    def create_researcher(
        cls,
        researcher_type: str = 'pattern',
        api_client: Any = None
    ) -> ContaminationResearcher:
        """
        Create researcher for specific research task.
        
        Args:
            researcher_type: Type of researcher (pattern, compatibility, etc.)
            api_client: API client for AI research
        
        Returns:
            Researcher instance
        
        Raises:
            ValueError: If no researcher registered for type or api_client is None
        """
        if api_client is None:
            raise ValueError(
                "API client required for contamination research. "
                "Cannot create researcher with None api_client."
            )
        
        researcher_class = cls._researchers.get(researcher_type.lower())
        
        if not researcher_class:
            raise ValueError(
                f"No researcher registered for type: {researcher_type}. "
                f"Available types: {list(cls._researchers.keys())}"
            )
        
        return researcher_class(api_client)
    
    @classmethod
    def register_researcher(
        cls,
        researcher_type: str,
        researcher_class: Type[ContaminationResearcher]
    ):
        """
        Register new researcher type (extensibility).
        
        Args:
            researcher_type: Research task type identifier
            researcher_class: Researcher class to instantiate
        
        Example:
            class CompatibilityResearcher(ContaminationResearcher):
                ...
            
            ContaminationResearcherFactory.register_researcher(
                'compatibility',
                CompatibilityResearcher
            )
        """
        cls._researchers[researcher_type.lower()] = researcher_class
    
    @classmethod
    def get_available_types(cls) -> list:
        """Get list of supported researcher types"""
        return list(cls._researchers.keys())
    
    @classmethod
    def create_pattern_researcher(cls, api_client: Any) -> PatternResearcher:
        """
        Convenience method for creating pattern researcher.
        
        Args:
            api_client: API client for AI research
        
        Returns:
            PatternResearcher instance
        """
        return cls.create_researcher('pattern', api_client)
    
    @classmethod
    def create_laser_researcher(cls, api_client: Any) -> LaserPropertiesResearcher:
        """
        Convenience method for creating laser properties researcher.
        
        Args:
            api_client: API client for AI research
        
        Returns:
            LaserPropertiesResearcher instance
        """
        return cls.create_researcher('laser', api_client)
