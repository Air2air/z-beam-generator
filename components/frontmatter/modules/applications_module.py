"""
ApplicationsModule - Extract applications list from Materials.yaml

Handles: applications array extraction

Architecture:
- Pure extraction from Materials.yaml
- Multiple fallback sources (applications, industryTags, existing frontmatter)
- No AI enhancement
- Returns empty list if none found (fail-safe with warning)
"""

import logging
from typing import Dict, List
from pathlib import Path


class ApplicationsModule:
    """Extract applications list for frontmatter"""
    
    def __init__(self):
        """Initialize applications module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_name: str, material_data: Dict) -> List[str]:
        """
        Extract applications list from material data
        
        Data sources (priority order):
        1. material_data['applications'] - Direct applications list
        2. material_data['material_metadata']['industryTags'] - Industry tags
        3. Existing frontmatter file - Backward compatibility
        4. Empty list with warning - Fail-safe
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            List of application strings
            
        Note:
            Never fails - returns empty list if no applications found.
            This is intentional for backward compatibility and gradual migration.
        """
        self.logger.info(f"Extracting applications for {material_name}")
        
        # 1. Check direct applications field
        if 'applications' in material_data:
            apps = material_data['applications']
            if isinstance(apps, list) and apps:
                self.logger.info(f"✅ Using {len(apps)} applications from Materials.yaml")
                return apps
        
        # 2. Check material_metadata.industryTags
        if 'material_metadata' in material_data:
            metadata = material_data['material_metadata']
            
            if 'industryTags' in metadata:
                tags = metadata['industryTags']
                
                # Handle list format
                if isinstance(tags, list) and tags:
                    self.logger.info(
                        f"✅ Using {len(tags)} applications from Materials.yaml "
                        f"industryTags (list)"
                    )
                    return tags
                
                # Handle structured format (primary/secondary)
                if isinstance(tags, dict):
                    apps = []
                    if 'primary_industries' in tags:
                        apps.extend(tags['primary_industries'])
                    if 'secondary_industries' in tags:
                        apps.extend(tags['secondary_industries'])
                    
                    if apps:
                        self.logger.info(
                            f"✅ Using {len(apps)} applications from Materials.yaml "
                            f"structured industryTags"
                        )
                        return apps
        
        # 3. Check existing frontmatter file (backward compatibility)
        apps = self._load_from_existing_frontmatter(material_name)
        if apps:
            self.logger.info(
                f"✅ Using {len(apps)} applications from existing frontmatter "
                f"(backward compatibility)"
            )
            return apps
        
        # 4. No applications found - return empty list with warning
        self.logger.warning(
            f"⚠️  No applications found for {material_name} "
            f"(no applications, no industryTags, no existing frontmatter). "
            f"Using empty list."
        )
        
        return []
    
    def _load_from_existing_frontmatter(self, material_name: str) -> List[str]:
        """
        Load applications from existing frontmatter file
        
        This provides backward compatibility during migration.
        
        Returns:
            List of applications or empty list if not found
        """
        try:
            import yaml
            
            # Generate frontmatter filename
            filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
            frontmatter_path = Path("content/frontmatter") / filename
            
            if not frontmatter_path.exists():
                return []
            
            with open(frontmatter_path, 'r') as f:
                existing_data = yaml.safe_load(f)
            
            if existing_data and 'applications' in existing_data:
                apps = existing_data['applications']
                if isinstance(apps, list) and apps:
                    self.logger.debug(
                        f"Loaded {len(apps)} applications from existing frontmatter"
                    )
                    return apps
            
            return []
            
        except Exception as e:
            self.logger.debug(f"Could not load existing frontmatter: {e}")
            return []


# Backward compatibility
class ApplicationsGenerator(ApplicationsModule):
    """Alias for backward compatibility"""
    pass
