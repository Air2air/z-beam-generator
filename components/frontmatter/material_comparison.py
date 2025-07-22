"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import os
import re
import yaml
import logging
from typing import Dict, Any, List, Optional
from components.base import BaseComponent

logger = logging.getLogger(__name__)

class MaterialComparison(BaseComponent):
    """Compare materials based on properties and composition from markdown files."""
    
    def __init__(self, output_dir: str):
        """Initialize with material markdown directory."""
        super().__init__("material_comparison", "comparison")
        self.output_dir = output_dir
    
    def generate(self) -> str:
        """Generate material comparison content."""
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for material comparison")
                return self._create_error_markdown("Missing frontmatter data")
            
            # 2. Prepare data
            similar_materials = self._prepare_data(frontmatter_data)
            
            if not similar_materials:
                logger.info("No similar materials found")
                return ""
            
            # 3. Post-process and format comparison (no API call needed)
            return self._post_process(similar_materials)
            
        except Exception as e:
            logger.error(f"Error generating material comparison: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, frontmatter_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find materials similar to the current one based on markdown files."""
        try:
            # Get list of markdown files
            md_files = [f for f in os.listdir(self.output_dir) if f.endswith('.md')]
            
            similarities = []
            
            # Get current material name from frontmatter
            current_material = frontmatter_data.get("name", self.subject)
            
            # Process each material file to find similarities
            for file_name in md_files:
                # Skip current material
                if current_material in file_name:
                    continue
                
                file_path = os.path.join(self.output_dir, file_name)
                material_data = self._extract_frontmatter(file_path)
                
                if not material_data:
                    continue
                
                # Calculate similarity with current material
                similarity = self._calculate_similarity(frontmatter_data, material_data)
                
                if similarity > 0:
                    # Extract material name from filename
                    material_name = os.path.splitext(file_name)[0]
                    
                    similarities.append({
                        "name": material_name,
                        "similarity": similarity,
                        "data": material_data
                    })
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top similar materials (limit to 3)
            return similarities[:3]
            
        except Exception as e:
            logger.error(f"Error finding similar materials: {str(e)}")
            return []
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data (not used in MaterialComparison)."""
        # Material comparison doesn't use API calls, but included for standard conformance
        return ""
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt (not used in MaterialComparison)."""
        # Material comparison doesn't use API calls, but included for standard conformance
        return ""
    
    def _post_process(self, similar_materials: List[Dict[str, Any]]) -> str:
        """Format similar materials into markdown comparison."""
        if not similar_materials:
            return ""
        
        # Create comparison section
        comparison = ["## Similar Materials", ""]
        comparison.append("Materials with similar properties include:")
        comparison.append("")
        
        # Add each similar material with key properties
        for material in similar_materials:
            name = material["name"].capitalize()
            similarity = material["similarity"]
            data = material["data"]
            
            comparison.append(f"### {name}")
            comparison.append(f"*Similarity score: {similarity:.2f}*")
            comparison.append("")
            
            # Add key properties if available
            properties = data.get("properties", {})
            if properties:
                comparison.append("**Key properties:**")
                comparison.append("")
                properties_list = [f"- **{k}**: {v}" for k, v in properties.items()]
                comparison.append("\n".join(properties_list[:5]))  # Limit to top 5 properties
            
            # Add a link to the material page
            comparison.append("")
            comparison.append(f"[Learn more about {name}]({name.lower()}.html)")
            comparison.append("")
        
        return "\n".join(comparison)
    
    def _extract_frontmatter(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from markdown file."""
        return BaseComponent.extract_frontmatter_from_file(file_path)
    
    def _calculate_similarity(self, material1: Dict[str, Any], material2: Dict[str, Any]) -> float:
        """Calculate similarity score between two materials."""
        score = 0.0
        
        # Compare properties if available
        properties1 = material1.get("properties", {})
        properties2 = material2.get("properties", {})
        
        if properties1 and properties2:
            # Find common properties
            common_properties = set(properties1.keys()) & set(properties2.keys())
            
            if common_properties:
                # Increment score for each common property
                score += len(common_properties) * 0.2
        
        # Compare applications if available
        apps1 = material1.get("applications", [])
        apps2 = material2.get("applications", [])
        
        if apps1 and apps2:
            # Find common applications
            common_apps = set(apps1) & set(apps2)
            
            if common_apps:
                # Increment score for each common application
                score += len(common_apps) * 0.3
        
        # Compare technical specifications if available
        specs1 = material1.get("technicalSpecifications", {})
        specs2 = material2.get("technicalSpecifications", {})
        
        if specs1 and specs2:
            # Find common specifications
            common_specs = set(specs1.keys()) & set(specs2.keys())
            
            if common_specs:
                # Increment score for each common specification
                score += len(common_specs) * 0.2
        
        return score