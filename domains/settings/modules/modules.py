"""
Simple extraction modules for settings

These modules handle straightforward field extraction.
"""

import logging
from typing import Dict, Optional


class ChallengesModule:
    """Extract challenges for settings frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, settings_data: Dict) -> Optional[Dict]:
        """
        Extract material challenges from settings data
        
        Args:
            settings_data: Settings data from Settings.yaml
            
        Returns:
            Dictionary with challenges or None if not present
        """
        self.logger.info("Extracting material challenges")
        
        challenges = settings_data.get('challenges')
        
        if not challenges:
            self.logger.warning("No challenges in settings data")
            return None
        
        self.logger.info("✅ Extracted challenges")
        return challenges


class DescriptionModule:
    """Extract settings_description for settings frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, settings_data: Dict) -> Optional[str]:
        """
        Extract settings description from settings data
        
        Args:
            settings_data: Settings data from Settings.yaml
            
        Returns:
            Settings description string or None if not present
        """
        self.logger.info("Extracting settings description")
        
        description = settings_data.get('settings_description')
        
        if not description:
            self.logger.warning("No settings_description in settings data")
            return None
        
        self.logger.info("✅ Extracted settings_description")
        return description


class AuthorModule:
    """Extract author data for settings frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, settings_data: Dict) -> Optional[Dict]:
        """
        Extract author data from settings
        
        Args:
            settings_data: Settings data from Settings.yaml
            
        Returns:
            Author dictionary or None if not present
        """
        self.logger.info("Extracting author data")
        
        author = settings_data.get('author')
        
        if not author:
            self.logger.debug("No author data in settings")
            return None
        
        self.logger.info("✅ Extracted author data")
        return author


class EEATModule:
    """Extract EEAT (Experience, Expertise, Authoritativeness, Trust) data for settings"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, settings_data: Dict) -> Dict:
        """
        Generate EEAT data for settings frontmatter
        
        Args:
            settings_data: Settings data from Settings.yaml
            
        Returns:
            EEAT dictionary with citations and reviewedBy
        """
        self.logger.info("Generating EEAT data for settings")
        
        # Check if EEAT already exists in settings data
        if 'eeat' in settings_data:
            self.logger.info("✅ Using existing EEAT data from Settings.yaml")
            return settings_data['eeat']
        
        # Generate default EEAT for machine settings
        eeat = {
            'citations': [
                'ISO 11146 - Lasers and laser-related equipment',
                'IEC 60825 - Safety of Laser Products',
                'OSHA laser safety standards'
            ],
            'isBasedOn': {
                'name': 'ISO 11146 - Test methods for laser beam widths',
                'url': 'https://www.iso.org/standard/33625.html'
            },
            'reviewedBy': 'Z-Beam Quality Assurance Team'
        }
        
        self.logger.info("✅ Generated default EEAT data")
        return eeat
