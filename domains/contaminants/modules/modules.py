"""
Simple extraction modules for contaminants

These modules handle straightforward field extraction with minimal logic.
"""

import logging
from typing import Dict, Optional


class MediaModule:
    """Extract images and micro for contaminant frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Dict:
        """
        Extract media data (images, micro)
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with images and/or micro fields
        """
        self.logger.info("Extracting media data")
        
        result = {}
        
        # Extract images if present
        if 'images' in contaminant_data:
            result['images'] = contaminant_data['images']
            self.logger.info("✅ Extracted images")
        
        # Extract micro (before/after)
        if 'micro' in contaminant_data:
            result['micro'] = contaminant_data['micro']
            self.logger.info("✅ Extracted micro")
        
        return result


class EEATModule:
    """Extract EEAT (Experience, Expertise, Authoritativeness, Trust) data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[Dict]:
        """
        Extract EEAT data from contaminant
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            EEAT dictionary or None if not present
        """
        self.logger.info("Extracting EEAT data")
        
        eeat = contaminant_data.get('eeat')
        
        if not eeat:
            self.logger.warning("No EEAT data in contaminant")
            return None
        
        self.logger.info("✅ Extracted EEAT data")
        return eeat


class OpticalModule:
    """Extract optical properties for contaminant frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[Dict]:
        """
        Extract optical properties from contaminant data
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with optical_properties or None if not present
        """
        self.logger.info("Extracting optical properties")
        
        optical = contaminant_data.get('optical_properties')
        
        if not optical:
            self.logger.warning("No optical_properties in contaminant data")
            return None
        
        self.logger.info("✅ Extracted optical_properties")
        return optical


class RemovalModule:
    """Extract removal characteristics for contaminant frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[Dict]:
        """
        Extract removal characteristics from contaminant data
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with removal_characteristics or None if not present
        """
        self.logger.info("Extracting removal characteristics")
        
        removal = contaminant_data.get('removal_characteristics')
        
        if not removal:
            self.logger.warning("No removal_characteristics in contaminant data")
            return None
        
        self.logger.info("✅ Extracted removal_characteristics")
        return removal


class SafetyModule:
    """Extract safety data for contaminant frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[Dict]:
        """
        Extract safety data from contaminant data
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with safety_data or None if not present
        """
        self.logger.info("Extracting safety data")
        
        safety = contaminant_data.get('safety_data')
        
        if not safety:
            self.logger.warning("No safety_data in contaminant data")
            return None
        
        self.logger.info("✅ Extracted safety_data")
        return safety
