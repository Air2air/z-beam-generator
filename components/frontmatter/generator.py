#!/usr/bin/env python3
"""
Frontmatter Component Generator

Generates frontmatter YAML content with property enhancement.
"""

import logging
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)

class FrontmatterComponentGenerator(APIComponentGenerator):
    """API-based generator for frontmatter components"""
    
    def __init__(self):
        super().__init__("frontmatter")
    
    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate frontmatter using API"""
        try:
            if not api_client:
                logger.error("API client is required for frontmatter generation")
                return ComponentResult(
                    component_type="frontmatter",
                    content="",
                    success=False,
                    error_message="API client not provided"
                )
            
            # Create template variables
            template_vars = self._create_template_vars(
                material_name, material_data, author_info, 
                frontmatter_data, schema_fields
            )
            
            # Build API prompt
            prompt = self._build_api_prompt(template_vars, frontmatter_data)
            
            # Call API
            api_response = api_client.generate_simple(prompt)
            
            if api_response.success:
                content = api_response.content
                
                # Post-process the content with property enhancement
                enhanced_content = self._post_process_content(content, material_name, material_data)
                
                logger.info(f"Generated frontmatter for {material_name}")
                
                return ComponentResult(
                    component_type="frontmatter",
                    content=enhanced_content,
                    success=True
                )
            else:
                error_msg = api_response.error or 'API call failed'
                logger.error(f"API error for frontmatter generation: {error_msg}")
                return ComponentResult(
                    component_type="frontmatter",
                    content="",
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Error generating frontmatter for {material_name}: {e}")
            return ComponentResult(
                component_type="frontmatter",
                content="",
                success=False,
                error_message=str(e)
            )
    
    def _create_template_vars(self, material_name, material_data, author_info, 
                            frontmatter_data=None, schema_fields=None):
        """Create template variables for frontmatter generation."""
        subject_lowercase = material_name.lower()
        subject_slug = subject_lowercase.replace(" ", "-")
        
        # FAIL-FAST: Category is required for frontmatter generation
        if "category" not in material_data:
            raise Exception("Material data missing required 'category' field - fail-fast architecture requires complete material information")
        category = material_data["category"]
        
        # FAIL-FAST: Formula is required for frontmatter generation
        formula = None
        if "formula" in material_data and material_data["formula"]:
            formula = material_data["formula"]
        elif "data" in material_data and "formula" in material_data["data"] and material_data["data"]["formula"]:
            formula = material_data["data"]["formula"]
        else:
            raise Exception("Material data missing required 'formula' field - fail-fast architecture requires complete material information")
        
        # FAIL-FAST: Symbol is required for frontmatter generation
        symbol = None
        if "symbol" in material_data and material_data["symbol"]:
            symbol = material_data["symbol"]
        elif "data" in material_data and "symbol" in material_data["data"] and material_data["data"]["symbol"]:
            symbol = material_data["data"]["symbol"]
        else:
            raise Exception("Material data missing required 'symbol' field - fail-fast architecture requires complete material information")
        
        # FAIL-FAST: Author information is required
        if not author_info or 'name' not in author_info:
            # Try to extract author_id from material_data and resolve it
            author_id = None
            if 'author_id' in material_data:
                author_id = material_data['author_id']
            elif 'data' in material_data and 'author_id' in material_data['data']:
                author_id = material_data['data']['author_id']
            
            if author_id:
                try:
                    from utils.author_manager import get_author_by_id
                    author_data = get_author_by_id(author_id)
                    if author_data and 'name' in author_data:
                        author_name = author_data['name']
                        logger.info(f"Resolved author_id {author_id} to {author_name}")
                    else:
                        raise Exception(f"Author data for ID {author_id} missing required 'name' field - fail-fast architecture requires complete author information")
                except Exception as e:
                    raise Exception(f"Failed to resolve author_id {author_id}: {e} - fail-fast architecture requires valid author information")
            else:
                raise Exception("Author information with 'name' field is required for frontmatter generation - fail-fast architecture requires complete author information")
        else:
            author_name = author_info['name']
        
        return {
            "subject": material_name,
            "subject_lowercase": subject_lowercase,
            "subject_slug": subject_slug,
            "material_formula": formula,
            "material_symbol": symbol,
            "material_type": material_data.get("material_type") if "material_type" in material_data else category,
            "category": category,
            "author_name": author_name,
            "article_type": material_data.get("article_type") if "article_type" in material_data else "material"  # Keep this for schema compatibility
        }
        """Build API prompt using template variables"""
        
        if not self.prompt_config:
            raise ValueError("Prompt configuration not loaded")
        
        if 'template' not in self.prompt_config:
            raise ValueError("Prompt configuration missing required 'template' field - fail-fast architecture requires complete configuration")
        
        template = self.prompt_config['template']
        
        # Escape literal {} braces in template that should not be formatted
        # Replace {} with {{}} so they are treated as literal braces
        template_escaped = template.replace('{}', '{{}}')
        
        # Format the template with variables
        try:
            formatted_prompt = template_escaped.format(**template_vars)
            return formatted_prompt
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Missing template variable: {e}")
        except Exception as e:
            logger.error(f"Template formatting error: {e}")
            raise ValueError(f"Template formatting error: {e}")

    def _post_process_content(self, content: str, material_name: str, material_data: Dict) -> str:
        """Post-process frontmatter content with property enhancement"""
        try:
            # Try to use the property enhancer if available
            from utils.property_enhancer import enhance_generated_frontmatter
            # FAIL-FAST: Category is required for enhancement
            if 'category' not in material_data:
                raise Exception("Material data missing required 'category' field for frontmatter enhancement - fail-fast architecture requires complete material information")
            category = material_data['category']
            enhanced_content = enhance_generated_frontmatter(content, category)
            logger.info(f"Enhanced frontmatter for {material_name} with property context")
            return enhanced_content
        except Exception as e:
            logger.warning(f"Failed to enhance frontmatter for {material_name}: {e}")
            return content
