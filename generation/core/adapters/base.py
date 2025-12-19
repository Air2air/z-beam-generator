"""
Abstract Data Source Adapter Interface

Defines contract for data source adapters that enable UnifiedOrchestrator
to work with any YAML data source (Materials, Regions, Applications, etc.)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class DataSourceAdapter(ABC):
    """
    Abstract interface for data source adapters.
    
    Enables UnifiedOrchestrator to work with different YAML structures
    without hard-coding assumptions about Materials.yaml.
    """
    
    @abstractmethod
    def get_data_path(self) -> Path:
        """
        Get path to data file (Materials.yaml, Regions.yaml, etc.)
        
        Returns:
            Path to YAML data file
        """
        pass
    
    @abstractmethod
    def load_all_data(self) -> Dict[str, Any]:
        """
        Load complete data structure from YAML.
        
        Returns:
            Dict with full YAML structure
        """
        pass
    
    @abstractmethod
    def get_item_data(self, identifier: str) -> Dict[str, Any]:
        """
        Load data for specific item (material, region, etc.)
        
        Args:
            identifier: Item identifier (material name, region name, etc.)
            
        Returns:
            Dict with item-specific data
            
        Raises:
            ValueError: If identifier not found
        """
        pass
    
    @abstractmethod
    def build_context(self, item_data: Dict[str, Any]) -> str:
        """
        Build context string from item data for prompt enrichment.
        
        Args:
            item_data: Data for specific item
            
        Returns:
            Formatted context string
        """
        pass
    
    @abstractmethod
    def get_author_id(self, item_data: Dict[str, Any]) -> int:
        """
        Extract author ID from item data.
        
        Args:
            item_data: Data for specific item
            
        Returns:
            Author ID (1-4)
        """
        pass
    
    @abstractmethod
    def write_component(
        self,
        identifier: str,
        component_type: str,
        content_data: Any
    ) -> None:
        """
        Write generated component content to data source atomically.
        
        Args:
            identifier: Item identifier
            component_type: Component type (micro, faq, etc.)
            content_data: Content to write
            
        Raises:
            ValueError: If identifier not found
            IOError: If write fails
        """
        pass
    
    @abstractmethod
    def get_enrichment_data(self, identifier: str) -> Dict[str, Any]:
        """
        Get enrichment data (facts, properties, etc.) for prompt building.
        
        Args:
            identifier: Item identifier
            
        Returns:
            Dict with enrichment data (properties, applications, etc.)
        """
        pass
    
    @abstractmethod
    def extract_component_content(
        self,
        text: str,
        component_type: str
    ) -> Any:
        """
        Extract component-specific content from generated text.
        
        Different components need different extraction logic:
        - micro: Extract before/after sections
        - faq: Parse JSON structure
        - description: Return text as-is
        
        Args:
            text: Generated text
            component_type: Component type
            
        Returns:
            Extracted content in appropriate format
        """
        pass
