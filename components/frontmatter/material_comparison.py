import os
import re
import yaml
import logging
from typing import Dict, Any, List, Optional
from components.base import BaseComponent

logger = logging.getLogger(__name__)

class MaterialComparison:
    """Compare materials based on properties and composition from markdown files."""
    
    def __init__(self, output_dir: str):
        """Initialize with material markdown directory."""
        self.output_dir = output_dir
        
    def get_similar_materials(self, current_material: Dict[str, Any], max_results: int = 3) -> List[Dict[str, Any]]:
        """Find materials similar to the current one based on markdown files."""
        try:
            # Get list of markdown files
            md_files = [f for f in os.listdir(self.output_dir) if f.endswith('.md')]
            
            similarities = []
            
            for file in md_files:
                try:
                    # Extract material data from markdown frontmatter
                    material_data = self._extract_frontmatter(os.path.join(self.output_dir, file))
                    
                    if not material_data or material_data.get("name") == current_material.get("name"):
                        continue
                        
                    # Calculate similarity score
                    similarity = self._calculate_similarity(current_material, material_data)
                    
                    similarities.append({
                        "name": material_data.get("name"),
                        "similarity": similarity,
                        "file": file
                    })
                    
                except Exception as e:
                    logger.warning(f"Error processing markdown file {file}: {str(e)}")
                    continue
            
            # Sort by similarity score (higher is more similar)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top N similar materials
            return similarities[:max_results]
            
        except Exception as e:
            logger.error(f"Error finding similar materials: {str(e)}")
            return []
    
    def _extract_frontmatter(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from markdown file.
        
        Uses the standardized BaseComponent method for extraction.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Dictionary of frontmatter data or None if extraction fails
        """
        return BaseComponent.extract_frontmatter_from_file(file_path)
    
    def _calculate_similarity(self, material1: Dict[str, Any], material2: Dict[str, Any]) -> float:
        """Calculate similarity score between two materials."""
        score = 0.0
        
        # Compare composition
        comp1 = {item.get("component", ""): item.get("percentage", "") 
                for item in material1.get("composition", [])}
        comp2 = {item.get("component", ""): item.get("percentage", "") 
                for item in material2.get("composition", [])}
        
        # Get common components
        common_components = set(comp1.keys()) & set(comp2.keys())
        score += len(common_components) * 2  # Each common component is worth 2 points
        
        # Compare properties
        prop1 = material1.get("properties", {})
        prop2 = material2.get("properties", {})
        
        common_props = set(prop1.keys()) & set(prop2.keys())
        score += len(common_props)  # Each common property is worth 1 point
        
        # Compare compatibility
        compat1 = {item.get("material", "") for item in material1.get("compatibility", [])}
        compat2 = {item.get("material", "") for item in material2.get("compatibility", [])}
        
        common_compat = compat1 & compat2
        score += len(common_compat)  # Each common compatibility is worth 1 point
        
        return score