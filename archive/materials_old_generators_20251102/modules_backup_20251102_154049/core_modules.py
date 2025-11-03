"""
Core Frontmatter Modules - Consolidated

Combines simple data extraction modules for improved organization:
- Author information
- Properties (materialProperties)
- Machine settings
- Applications
- Compliance (regulatoryStandards)
- Media (images, caption)
- Characteristics (qualitative properties)

Each module has a clear, single responsibility with minimal logic.
Consolidation reduces file count while maintaining code clarity.
"""

import logging
from typing import Dict, List

from shared.utils.core.author_manager import get_author_info_for_material


# ============================================================================
# AUTHOR MODULE
# ============================================================================

class AuthorModule:
    """Extract and validate author information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> Dict:
        """
        Extract author information using shared author manager.
        
        Args:
            material_data: Material data from Materials.yaml
            
        Returns:
            Author info dict with id, name, title, country, expertise, sex, image
        """
        self.logger.info("Extracting author information")
        
        try:
            author = get_author_info_for_material(material_data)
            
            # Validate required fields
            self._validate_author(author)
            
            self.logger.info(f"✅ Author: {author['name']} ({author['country']})")
            return author
            
        except Exception as e:
            self.logger.error(f"Author extraction failed: {e}")
            raise
    
    def _validate_author(self, author: Dict) -> None:
        """Validate author has required fields"""
        required = ['id', 'name', 'title', 'country', 'expertise', 'sex', 'image']
        
        for field in required:
            if field not in author:
                raise ValueError(f"Author missing required field: {field}")
        
        # Validate non-empty strings
        if not isinstance(author['name'], str) or not author['name'].strip():
            raise ValueError("Author name must be non-empty string")
        
        if not isinstance(author['country'], str) or not author['country'].strip():
            raise ValueError("Author country must be non-empty string")
        
        self.logger.debug(f"Author validation passed: {author['name']}")


# ============================================================================
# PROPERTIES MODULE
# ============================================================================

class PropertiesModule:
    """Extract materialProperties with proper structure"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_name: str, material_data: Dict) -> Dict:
        """
        Extract material properties in GROUPED format.
        
        Properties are organized into groups:
        - material_characteristics: Physical, mechanical, chemical properties
        - laser_material_interaction: Thermal, optical, laser-specific properties
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            Properties dict with GROUPED structure
        """
        self.logger.info(f"Extracting properties for {material_name}")
        
        mat_props = material_data.get('materialProperties', {})
        
        if not mat_props:
            self.logger.warning(f"No materialProperties found for {material_name}")
            return {}
        
        # Validate GROUPED structure
        result = {}
        for group_name, group_data in mat_props.items():
            if not isinstance(group_data, dict):
                self.logger.warning(f"Group '{group_name}' is not a dict, skipping")
                continue
            
            if 'label' not in group_data or 'properties' not in group_data:
                self.logger.warning(
                    f"Group '{group_name}' missing required fields "
                    "(label, properties), skipping"
                )
                continue
            
            result[group_name] = group_data
            props_count = len(group_data.get('properties', {}))
            self.logger.debug(
                f"  Group '{group_name}': {props_count} properties"
            )
        
        self.logger.info(f"✅ Extracted {len(result)} property groups")
        return result


# ============================================================================
# SETTINGS MODULE
# ============================================================================

class SettingsModule:
    """Extract machine settings with ranges"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_name: str, material_data: Dict) -> Dict:
        """
        Extract machine settings.
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            Machine settings dict
        """
        self.logger.info(f"Extracting machine settings for {material_name}")
        
        settings = material_data.get('machineSettings', {})
        
        if not settings:
            self.logger.warning(f"No machineSettings found for {material_name}")
            return {}
        
        if not isinstance(settings, dict):
            self.logger.error(f"machineSettings not a dict: {type(settings)}")
            return {}
        
        # Validate structure
        result = {}
        for setting_name, setting_data in settings.items():
            if isinstance(setting_data, dict):
                result[setting_name] = setting_data
                self.logger.debug(f"  Setting '{setting_name}': {setting_data}")
            else:
                self.logger.warning(
                    f"Setting '{setting_name}' not a dict, "
                    f"using value as-is"
                )
        
        return result


# ============================================================================
# APPLICATIONS MODULE
# ============================================================================

class ApplicationsModule:
    """Extract applications list"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_name: str, material_data: Dict) -> List[str]:
        """
        Extract applications list.
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            List of application strings
        """
        self.logger.info(f"Extracting applications for {material_name}")
        
        apps = material_data.get('applications', [])
        
        if not isinstance(apps, list):
            self.logger.warning(f"applications not a list: {type(apps)}")
            return []
        
        # Filter to strings only
        result = [app for app in apps if isinstance(app, str)]
        
        if len(result) != len(apps):
            self.logger.warning(
                f"Filtered {len(apps) - len(result)} non-string applications"
            )
        
        self.logger.info(f"✅ Extracted {len(result)} applications")
        return result


# ============================================================================
# COMPLIANCE MODULE
# ============================================================================

class ComplianceModule:
    """Extract regulatoryStandards for frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> List[str]:
        """Extract regulatory standards list"""
        self.logger.info("Extracting regulatory standards")
        
        standards = material_data.get('regulatoryStandards', [])
        
        if not isinstance(standards, list):
            self.logger.warning(f"regulatoryStandards not a list: {type(standards)}")
            return []
        
        self.logger.info(f"✅ Extracted {len(standards)} standards")
        return standards


# ============================================================================
# MEDIA MODULE
# ============================================================================

class MediaModule:
    """Extract images and caption for frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> Dict:
        """Extract media data (images, caption)"""
        self.logger.info("Extracting media data")
        
        result = {}
        
        # Extract images
        if 'images' in material_data:
            result['images'] = material_data['images']
        else:
            self.logger.warning("No images found")
            result['images'] = {}
        
        # Extract caption
        if 'caption' in material_data:
            result['caption'] = material_data['caption']
        else:
            self.logger.warning("No caption found")
            result['caption'] = {}
        
        self.logger.info("✅ Extracted media data")
        return result


# ============================================================================
# CHARACTERISTICS MODULE
# ============================================================================

class CharacteristicsModule:
    """Extract materialCharacteristics (qualitative properties) for frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> List[str]:
        """
        Extract material characteristics.
        
        Data Architecture Rule:
        Qualitative properties MUST be stored in materialCharacteristics,
        NOT in materialProperties (which is for quantitative data only).
        """
        self.logger.info("Extracting material characteristics")
        
        characteristics = material_data.get('materialCharacteristics', [])
        
        if not isinstance(characteristics, list):
            self.logger.warning(f"materialCharacteristics not a list: {type(characteristics)}")
            return []
        
        self.logger.info(f"✅ Extracted {len(characteristics)} characteristics")
        return characteristics


# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Use base classes directly - no empty wrappers needed
AuthorGenerator = AuthorModule
PropertiesGenerator = PropertiesModule
SettingsGenerator = SettingsModule
ApplicationsGenerator = ApplicationsModule
ComplianceGenerator = ComplianceModule
MediaGenerator = MediaModule
CharacteristicsGenerator = CharacteristicsModule
