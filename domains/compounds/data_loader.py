"""
Compound Data Loader
Loads hazardous compound data from Compounds.yaml
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class CompoundDataLoader:
    """
    Loads and provides access to hazardous compound data.
    Single source of truth: data/compounds/Compounds.yaml
    """
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize data loader.
        
        Args:
            data_file: Optional path to Compounds.yaml (uses default if not provided)
        """
        if data_file:
            self.data_file = Path(data_file)
        else:
            # Default to data/compounds/Compounds.yaml
            self.data_file = Path(__file__).parent.parent.parent / "data" / "compounds" / "Compounds.yaml"
        
        if not self.data_file.exists():
            raise FileNotFoundError(
                f"Compounds data file not found: {self.data_file}\n"
                f"Expected location: data/compounds/Compounds.yaml"
            )
        
        logger.info(f"CompoundDataLoader initialized with {self.data_file}")
    
    @lru_cache(maxsize=1)
    def _load_data(self) -> Dict[str, Any]:
        """
        Load compound data from YAML (cached).
        
        Returns:
            Dict with metadata and compounds sections
            
        Raises:
            FileNotFoundError: If data file doesn't exist
            yaml.YAMLError: If data file is malformed
        """
        logger.debug(f"Loading compound data from {self.data_file}")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise ValueError(f"Empty data file: {self.data_file}")
        
        if 'compounds' not in data:
            raise ValueError(
                f"Data file missing 'compounds' section: {self.data_file}"
            )
        
        logger.info(
            f"Loaded {len(data['compounds'])} compounds "
            f"(version {data.get('metadata', {}).get('version', 'unknown')})"
        )
        
        return data
    
    def get_compound(self, compound_id: str) -> Optional[Dict[str, Any]]:
        """
        Get compound data by ID.
        
        Args:
            compound_id: Compound identifier (e.g., "formaldehyde")
            
        Returns:
            Dict with compound data, or None if not found
        """
        data = self._load_data()
        return data['compounds'].get(compound_id)
    
    def get_all_compounds(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all compound data.
        
        Returns:
            Dict mapping compound_id -> compound data
        """
        data = self._load_data()
        return data['compounds']
    
    def list_compound_ids(self) -> List[str]:
        """
        Get list of all compound IDs.
        
        Returns:
            List of compound identifiers
        """
        data = self._load_data()
        return list(data['compounds'].keys())
    
    def get_compounds_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all compounds in a specific category.
        
        Args:
            category: Category name (e.g., "carcinogen", "toxic_gas")
            
        Returns:
            Dict mapping compound_id -> compound data for matching compounds
        """
        data = self._load_data()
        return {
            comp_id: comp_data
            for comp_id, comp_data in data['compounds'].items()
            if comp_data.get('category') == category
        }
    
    def get_compounds_by_hazard_class(self, hazard_class: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all compounds with a specific hazard classification.
        
        Args:
            hazard_class: Hazard class (e.g., "carcinogenic", "toxic", "corrosive")
            
        Returns:
            Dict mapping compound_id -> compound data for matching compounds
        """
        data = self._load_data()
        return {
            comp_id: comp_data
            for comp_id, comp_data in data['compounds'].items()
            if comp_data.get('hazard_class') == hazard_class
        }
    
    def search_compounds(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        hazard_class: Optional[str] = None,
        requires_monitoring: Optional[bool] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Search compounds by multiple criteria.
        
        Args:
            name: Partial match on compound name
            category: Exact match on category
            hazard_class: Exact match on hazard class
            requires_monitoring: Filter by monitoring requirement
            
        Returns:
            Dict mapping compound_id -> compound data for matching compounds
        """
        data = self._load_data()
        results = {}
        
        for comp_id, comp_data in data['compounds'].items():
            # Name filter
            if name and name.lower() not in comp_data.get('name', '').lower():
                continue
            
            # Category filter
            if category and comp_data.get('category') != category:
                continue
            
            # Hazard class filter
            if hazard_class and comp_data.get('hazard_class') != hazard_class:
                continue
            
            # Monitoring filter
            if requires_monitoring is not None:
                if comp_data.get('monitoring_required') != requires_monitoring:
                    continue
            
            results[comp_id] = comp_data
        
        return results
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata section from data file.
        
        Returns:
            Dict with version, total_compounds, etc.
        """
        data = self._load_data()
        return data.get('metadata', {})


# Convenience functions for quick access
def get_compound(compound_id: str) -> Optional[Dict[str, Any]]:
    """Quick access to compound data."""
    loader = CompoundDataLoader()
    return loader.get_compound(compound_id)


def list_all_compounds() -> List[str]:
    """Quick access to list of compound IDs."""
    loader = CompoundDataLoader()
    return loader.list_compound_ids()
