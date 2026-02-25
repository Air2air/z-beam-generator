"""
Generic DataLoader Factory

Consolidates repeated DataLoader initialization patterns across all domains.
Eliminates 80+ lines of duplicate boilerplate code.

Usage:
    from shared.data.loader_factory import create_data_loader
    
    # Instead of domain-specific imports
    materials_loader = create_data_loader('materials')
    contaminants_loader = create_data_loader('contaminants')
    settings_loader = create_data_loader('settings')
    compounds_loader = create_data_loader('compounds')
"""

from pathlib import Path
from typing import Optional, Dict, Any, Type

from shared.data.base_loader import BaseDataLoader


class GenericDataLoader(BaseDataLoader):
    """
    Generic data loader that works for any domain.
    
    Eliminates the need for separate MaterialsDataLoader, ContaminantsDataLoader,
    SettingsDataLoader, and CompoundsDataLoader classes that all do the same thing.
    """
    
    def __init__(self, domain: str, project_root: Optional[Path] = None):
        """
        Initialize generic data loader.
        
        Args:
            domain: Domain name (materials, contaminants, settings, compounds)
            project_root: Project root path
        """
        super().__init__(project_root)
        self.domain = domain
        self.data_dir = self.project_root / 'data' / domain
        
        # Domain-specific settings for materials only
        if domain == 'materials':
            self.settings_dir = self.project_root / 'data' / 'settings'
    
    def _get_data_file_path(self) -> Path:
        """Get path to data file for this domain."""
        file_mapping = {
            'materials': 'data/materials/Materials.yaml',
            'contaminants': 'data/contaminants/Contaminants.yaml',
            'settings': 'data/settings/Settings.yaml',
            'compounds': 'data/compounds/Compounds.yaml'
        }
        
        if self.domain not in file_mapping:
            raise ValueError(f"Unknown domain: {self.domain}")
            
        return self.project_root / file_mapping[self.domain]
    
    def _validate_loaded_data(self, data: Dict[str, Any]) -> bool:
        """Validate loaded data structure for this domain."""
        root_key_mapping = {
            'materials': 'materials',
            'contaminants': 'contamination_patterns', 
            'settings': 'settings',
            'compounds': 'compounds'
        }
        
        expected_key = root_key_mapping.get(self.domain)
        if not expected_key:
            return False
            
        return expected_key in data
    
    def __getattr__(self, name: str):
        """
        Dynamically handle domain-specific methods.
        
        This allows the generic loader to support all domain-specific methods
        like load_materials(), get_pattern(), etc. without explicit implementation.
        """
        if name.startswith('load_') or name.startswith('get_'):
            def dynamic_method(*args, **kwargs):
                # Load the main data file
                data = self._load_yaml_file(self._get_data_file_path())
                
                # For load_* methods, typically return a section of the data
                if name.startswith('load_'):
                    section_name = name[5:]  # Remove 'load_' prefix
                    if section_name in data:
                        return data[section_name]
                    # Try the domain's root key
                    root_key = self._get_root_key()
                    if root_key in data:
                        return data[root_key]
                    return {}
                
                # For get_* methods, typically return specific items
                elif name.startswith('get_'):
                    if len(args) > 0:
                        item_id = args[0]
                        root_key = self._get_root_key()
                        if root_key in data and item_id in data[root_key]:
                            return data[root_key][item_id]
                        return None
                    else:
                        # get_all_* style methods
                        root_key = self._get_root_key()
                        return data.get(root_key, {})
                
                return None
            
            return dynamic_method
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def _get_root_key(self) -> str:
        """Get the root key for this domain's data."""
        root_key_mapping = {
            'materials': 'materials',
            'contaminants': 'contamination_patterns', 
            'settings': 'settings',
            'compounds': 'compounds'
        }
        return root_key_mapping.get(self.domain, self.domain)


# Domain configurations - replaces hardcoded per-domain classes
DOMAIN_CONFIG = {
    'materials': {
        'description': 'Core material metadata and properties',
        'files': ['Materials.yaml', 'MaterialProperties.yaml', 'IndustryApplications.yaml']
    },
    'contaminants': {
        'description': 'Pattern metadata, laser properties, safety data',
        'files': ['Contaminants.yaml']
    },
    'settings': {
        'description': 'Laser cleaning parameter configurations',
        'files': ['Settings.yaml']
    },
    'compounds': {
        'description': 'Chemical compound data and relationships',
        'files': ['Compounds.yaml']
    }
}


def create_data_loader(domain: str, project_root: Optional[Path] = None) -> GenericDataLoader:
    """
    Factory function to create domain-specific data loaders.
    
    Args:
        domain: Domain name (materials, contaminants, settings, compounds)
        project_root: Optional project root path
        
    Returns:
        GenericDataLoader configured for the specified domain
        
    Raises:
        ValueError: If domain is not supported
    """
    if domain not in DOMAIN_CONFIG:
        raise ValueError(f"Unsupported domain: {domain}. Supported: {list(DOMAIN_CONFIG.keys())}")
    
    # Auto-detect project root if not provided
    if project_root is None:
        # Go up from shared/data/loader_factory.py to project root
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
    
    return GenericDataLoader(domain, project_root)


# Backward compatibility aliases
def MaterialsDataLoader(project_root: Optional[Path] = None) -> GenericDataLoader:
    """Backward compatibility alias for materials data loader"""
    return create_data_loader('materials', project_root)


def ContaminantsDataLoader(project_root: Optional[Path] = None) -> GenericDataLoader:
    """Backward compatibility alias for contaminants data loader"""
    return create_data_loader('contaminants', project_root)


def SettingsDataLoader(project_root: Optional[Path] = None) -> GenericDataLoader:
    """Backward compatibility alias for settings data loader"""
    return create_data_loader('settings', project_root)


def CompoundsDataLoader(project_root: Optional[Path] = None) -> GenericDataLoader:
    """Backward compatibility alias for compounds data loader"""
    return create_data_loader('compounds', project_root)