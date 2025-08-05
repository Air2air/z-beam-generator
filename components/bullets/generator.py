"""
Bullets generator for Z-Beam Generator.

Enhanced implementation with local formatting and validation.
"""

import logging
import re
from components.base.component import BaseComponent
from components.base.utils.formatting import format_bullet_points

logger = logging.getLogger(__name__)

class BulletsGenerator(BaseComponent):
    """Generator for bullet point content with enhanced local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated bullet points with enhanced local formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed bullet points
            
        Raises:
            ValueError: If content is invalid
        """
        # Extract bullet points from content
        bullet_items = self._extract_bullet_points(content)
        
        # Format and validate bullet points
        expected_count = self.get_component_config("count")
        bullet_items = self._format_and_validate_bullets(bullet_items, expected_count)
        
        # Format bullet points using utility function
        return format_bullet_points(bullet_items)
    
    def _extract_bullet_points(self, content: str) -> list:
        """Extract bullet points from content.
        
        Args:
            content: Raw generated content
            
        Returns:
            list: Extracted bullet points
        """
        lines = content.strip().split('\n')
        bullet_items = []
        
        # Process lines to extract bullet content
        current_bullet = None
        
        for line in lines:
            line = line.strip()
            # Check if this line starts a bullet point
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                # If we have a bullet in progress, save it
                if current_bullet:
                    bullet_items.append(current_bullet)
                
                # Start a new bullet
                current_bullet = line[1:].strip()
            # Check if this is a numbered bullet
            elif re.match(r'^\d+\.', line):
                # If we have a bullet in progress, save it
                if current_bullet:
                    bullet_items.append(current_bullet)
                
                # Start a new bullet (remove the number and period)
                current_bullet = re.sub(r'^\d+\.', '', line).strip()
            # Check if this is a continuation of the current bullet
            elif current_bullet and line:
                # Append to current bullet with a space
                current_bullet += " " + line
        
        # Add the last bullet if there's one in progress
        if current_bullet:
            bullet_items.append(current_bullet)
        
        return [item for item in bullet_items if item.strip()]
    
    def _format_and_validate_bullets(self, bullet_items: list, expected_count: int) -> list:
        """Format and validate bullet points.
        
        Args:
            bullet_items: Extracted bullet points
            expected_count: Expected number of bullet points
            
        Returns:
            list: Formatted bullet points
            
        Raises:
            ValueError: If validation fails
        """
        # Ensure we have the expected number of bullets
        if len(bullet_items) < expected_count:
            # If we have frontmatter data, we can try to generate missing bullets
            if hasattr(self, '_frontmatter_data') and self._frontmatter_data:
                # Add bullets based on frontmatter data
                bullet_items = self._add_missing_bullets(bullet_items, expected_count)
            else:
                raise ValueError(f"Generated only {len(bullet_items)} bullet points, expected {expected_count}")
        elif len(bullet_items) > expected_count:
            # Keep only the first expected_count bullet points
            bullet_items = bullet_items[:expected_count]
        
        # Format each bullet for consistency
        formatted_bullets = []
        for bullet in bullet_items:
            # Ensure bullet starts with a capital letter
            if bullet and not bullet[0].isupper():
                bullet = bullet[0].upper() + bullet[1:]
            
            # Ensure bullet ends with a period
            if bullet and not bullet.endswith(('.', '!', '?')):
                bullet += '.'
            
            formatted_bullets.append(bullet)
        
        return formatted_bullets
    
    def _add_missing_bullets(self, bullet_items: list, expected_count: int) -> list:
        """Add missing bullet points based on frontmatter data.
        
        Args:
            bullet_items: Current bullet points
            expected_count: Expected number of bullet points
            
        Returns:
            list: Expanded bullet points
        """
        missing_count = expected_count - len(bullet_items)
        if missing_count <= 0:
            return bullet_items
        
        # Get data from frontmatter
        frontmatter = self._frontmatter_data
        new_bullets = list(bullet_items)
        
        # Add bullets based on available frontmatter sections
        potential_bullets = []
        
        # Add from technical specifications
        if 'technicalSpecifications' in frontmatter:
            for key, value in frontmatter['technicalSpecifications'].items():
                potential_bullets.append(f"Features {key}: {value}.")
        
        # Add from applications
        if 'applications' in frontmatter and isinstance(frontmatter['applications'], list):
            for app in frontmatter['applications']:
                if isinstance(app, dict) and 'name' in app:
                    potential_bullets.append(f"Ideal for {app['name']} applications.")
        
        # Add from environmental impact
        if 'environmentalImpact' in frontmatter and isinstance(frontmatter['environmentalImpact'], list):
            for impact in frontmatter['environmentalImpact']:
                if isinstance(impact, dict) and 'benefit' in impact:
                    potential_bullets.append(f"Offers {impact['benefit']} environmental benefits.")
        
        # Add from regulatory standards
        if 'regulatoryStandards' in frontmatter and isinstance(frontmatter['regulatoryStandards'], list):
            for standard in frontmatter['regulatoryStandards']:
                if isinstance(standard, dict) and 'code' in standard:
                    potential_bullets.append(f"Complies with {standard['code']} standards.")
        
        # Add bullets until we reach expected count
        for bullet in potential_bullets:
            if len(new_bullets) < expected_count:
                if bullet not in new_bullets:
                    new_bullets.append(bullet)
            else:
                break
        
        # If we still need more bullets, add generic ones
        while len(new_bullets) < expected_count:
            new_bullets.append(f"Provides effective cleaning solutions for {self.subject} applications.")
        
        return new_bullets