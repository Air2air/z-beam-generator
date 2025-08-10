"""
Bullet point formatting utilities for Z-Beam Generator.

This module handles all bullet point processing that was previously done in generators.
"""

import re
from typing import List


def extract_bullet_points(content: str) -> List[str]:
    """Extract bullet points from AI-generated content.
    
    Args:
        content: Raw generated content with bullet points
        
    Returns:
        List[str]: Extracted bullet points
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


def format_bullet_points(bullet_items: List[str], expected_count: int = 5) -> List[str]:
    """Format and validate bullet points.
    
    Args:
        bullet_items: Extracted bullet points
        expected_count: Expected number of bullet points
        
    Returns:
        List[str]: Formatted bullet points
        
    Raises:
        ValueError: If validation fails
    """
    # Ensure we have the expected number of bullets
    if len(bullet_items) < expected_count:
        raise ValueError(f"Generated only {len(bullet_items)} bullet points, expected {expected_count}. AI should regenerate with correct count.")
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


def format_bullet_points_as_markdown(bullet_items: List[str]) -> str:
    """Format bullet points as markdown list.
    
    Args:
        bullet_items: List of formatted bullet points
        
    Returns:
        str: Markdown formatted bullet list
    """
    if not bullet_items:
        return ""
    
    return '\n'.join(f'* {bullet}' for bullet in bullet_items)
