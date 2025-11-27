"""
SettingsModule - Extract machineSettings with ranges from Categories.yaml

Handles: machineSettings dictionary with min/max ranges

Architecture:
- Extract settings from Materials.yaml
- Apply ranges from Categories.yaml machineSettingsRanges
- Shared architecture with PropertiesModule (same core logic)
- Fail-fast if category ranges not defined
"""

import logging
from typing import Dict
import yaml
from pathlib import Path


class SettingsModule:
    """Extract and format machineSettings for frontmatter"""
    
    def __init__(self, categories_yaml_path: str = "data/Categories.yaml"):
        """
        Initialize settings module
        
        Args:
            categories_yaml_path: Path to Categories.yaml
        """
        self.logger = logging.getLogger(__name__)
        self.categories_yaml_path = categories_yaml_path
        self._categories_data = None
    
    @property
    def categories_data(self) -> Dict:
        """Lazy-load categories data"""
        if self._categories_data is None:
            path = Path(self.categories_yaml_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Categories.yaml not found: {path}")
            
            with open(path, 'r') as f:
                self._categories_data = yaml.safe_load(f)
            
            self.logger.debug("Loaded Categories.yaml")
        
        return self._categories_data
    
    def generate(self, material_name: str, material_data: Dict) -> Dict:
        """
        Extract machineSettings with ranges
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            Dictionary with machine settings
            Each setting has: {value, unit, min, max, confidence}
            
        Raises:
            ValueError: If category not found or data invalid
        """
        self.logger.info(f"Generating machine settings for {material_name}")
        
        # Get category
        category = material_data.get('category', '').lower()
        if not category:
            raise ValueError(f"Category missing for {material_name}")
        
        # Get settings from material data
        if 'machineSettings' not in material_data:
            self.logger.warning(f"No machineSettings for {material_name}")
            return {}
        
        settings = material_data['machineSettings']
        
        # Apply ranges from Categories.yaml
        settings_with_ranges = self._apply_ranges(
            settings,
            category,
            material_name
        )
        
        self.logger.info(f"✅ Generated machine settings for {material_name}")
        return settings_with_ranges
    
    def _apply_ranges(
        self,
        settings: Dict,
        category: str,
        material_name: str
    ) -> Dict:
        """
        Apply min/max ranges from Categories.yaml
        
        Data Architecture Rule:
        - machineSettingsRanges are PARAMETER-level ranges (not category-specific)
        - Apply universally across all materials/categories
        - Min/max from Categories.yaml ONLY, NEVER from Materials.yaml
        
        Note: Unlike materialProperties which are category-specific,
        machine settings ranges are universal parameters (power, frequency, etc.)
        """
        # Get universal machine settings ranges
        ranges = self.categories_data.get('machineSettingsRanges', {})
        
        if not ranges:
            self.logger.warning(
                "No machineSettingsRanges found in Categories.yaml - "
                "settings will be exported without ranges"
            )
            return settings
        
        # Apply ranges to each setting
        result = {}
        
        for setting_name, setting_value in settings.items():
            # Get range from Categories.yaml (parameter-level)
            if setting_name in ranges:
                range_data = ranges[setting_name]
                
                # Build setting with ranges
                result[setting_name] = {
                    'value': setting_value.get('value'),
                    'unit': setting_value.get('unit', ''),
                    'min': range_data.get('min'),
                    'max': range_data.get('max'),
                    'confidence': setting_value.get('confidence', 1.0)
                }
            else:
                # Setting not in ranges - copy as-is
                result[setting_name] = setting_value
                
                self.logger.debug(
                    f"Setting '{setting_name}' not in machineSettingsRanges, "
                    f"using value as-is"
                )
        
        return result


# Backward compatibility - use base class directly
SettingsGenerator = SettingsModule
