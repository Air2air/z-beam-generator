"""
Caption generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Caption structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class CaptionGenerator(BaseComponent):
    """Generator for image caption content."""
    
    def generate(self) -> str:
        """Generate caption content.
        
        Returns:
            str: The generated caption
        """
        try:
            # 1. Prepare data for prompt
            data = self._prepare_data()
            
            # 2. Format prompt
            prompt = self._format_prompt(data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for caption generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Add caption constraints
        data.update({
            "results_word_count_max": self.get_component_config("results_word_count_max", 120),
            "equipment_word_count_max": self.get_component_config("equipment_word_count_max", 60),
            "shape": self.get_component_config("shape", "component")
        })
        
        # Get frontmatter data and include ALL available structured data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Include all frontmatter data dynamically
            for key, value in frontmatter.items():
                if value:  # Only include non-empty values
                    data[key] = value
            
            # Store list of available keys for template iteration
            data["available_keys"] = [k for k, v in frontmatter.items() if v]
            
            # Also provide the complete frontmatter as formatted YAML
            import yaml
            data["all_frontmatter"] = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            
            # Extract material name from frontmatter or subject
            if "name" in frontmatter:
                data["material"] = frontmatter["name"].lower()
            else:
                data["material"] = self.subject.lower()
                
            # Extract shape from frontmatter if available
            if "shape" in frontmatter:
                data["shape"] = frontmatter["shape"]
            elif "applications" in frontmatter and frontmatter["applications"]:
                # Try to infer shape from applications
                first_app = frontmatter["applications"][0] if isinstance(frontmatter["applications"], list) else frontmatter["applications"]
                if isinstance(first_app, dict) and "name" in first_app:
                    # Use a generic shape based on application type
                    app_name = first_app["name"].lower()
                    if any(word in app_name for word in ["blade", "turbine"]):
                        data["shape"] = "blade"
                    elif any(word in app_name for word in ["panel", "sheet"]):
                        data["shape"] = "panel"
                    elif any(word in app_name for word in ["pipe", "tube"]):
                        data["shape"] = "pipe"
                    else:
                        data["shape"] = "component"
        else:
            data["all_frontmatter"] = "No frontmatter data available"
            data["material"] = self.subject.lower()
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the caption content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed caption
        """
        # Apply standard processing
        processed = super()._post_process(content)
        
        # Ensure content has a heading
        if not processed.lstrip().startswith("#"):
            processed = f"## Caption for {self.subject.capitalize()}\n\n{processed}"
        
        # Clean up any extra markdown formatting that's not appropriate for captions
        lines = processed.split("\n")
        result = []
        in_caption = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result.append(line)
            elif stripped.startswith("#"):
                result.append(line)
                in_caption = True
            elif in_caption:
                # Remove bullet points and extra formatting from caption text
                if stripped.startswith("- ") or stripped.startswith("* "):
                    stripped = stripped[2:]
                result.append(stripped)
            else:
                result.append(line)
        
        return "\n".join(result)
