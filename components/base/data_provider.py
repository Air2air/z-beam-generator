"""
Data Provider for Z-Beam Generator Components.

Ensures only clean, validated, pre-formatted data flows from base component to generators.
Provides strict data isolation with validation and sanitization.
"""

import logging
from typing import Dict, Any
from components.base.utils.content_formatter import ContentFormatter
from components.base.services.material_service import formula_service
from components.base.utils.slug_utils import SlugUtils

logger = logging.getLogger(__name__)

class CleanDataProvider:
    """Provides only clean, validated data to component generators.
    
    This class acts as a strict boundary between the base component and generators,
    ensuring that generators receive only sanitized, pre-formatted data.
    """
    
    def __init__(self, subject: str, article_type: str, category: str, 
                 author_data: Dict[str, Any], schema: Dict[str, Any]):
        """Initialize with core data and validate it immediately.
        
        Args:
            subject: The subject being processed
            article_type: Type of article being generated
            category: Category classification
            author_data: Author information
            schema: Schema definition
            
        Raises:
            ValueError: If any required data is invalid
        """
        # Validate inputs immediately
        self._validate_inputs(subject, article_type, category, author_data, schema)
        
        # Store validated data
        self.subject = self._sanitize_string(subject)
        self.article_type = self._sanitize_string(article_type)
        self.category = self._sanitize_string(category)
        self.author_data = self._validate_author_data(author_data)
        self.schema = schema
        
        # Pre-compute all formatted data
        self._formatted_data = self._prepare_clean_data()
    
    def get_clean_data(self, component_name: str, component_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get clean, validated data for a specific component.
        
        Args:
            component_name: Name of the component requesting data
            component_config: Component-specific configuration
            
        Returns:
            Dict[str, Any]: Clean, validated template data
            
        Raises:
            ValueError: If component data cannot be prepared
        """
        try:
            # Start with base clean data
            clean_data = self._formatted_data.copy()
            
            # Add component-specific clean data
            component_data = self._get_component_clean_data(component_name, component_config)
            clean_data.update(component_data)
            
            # Final validation
            self._validate_clean_data(clean_data)
            
            logger.debug(f"Provided clean data for {component_name} with {len(clean_data)} fields")
            return clean_data
            
        except Exception as e:
            logger.error(f"Failed to prepare clean data for {component_name}: {e}")
            raise ValueError(f"Cannot provide clean data for {component_name}: {e}")
    
    def _validate_inputs(self, subject: str, article_type: str, category: str, 
                        author_data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate all input data.
        
        Args:
            subject: Subject to validate
            article_type: Article type to validate
            category: Category to validate
            author_data: Author data to validate
            schema: Schema to validate
            
        Raises:
            ValueError: If any input is invalid
        """
        if not subject or not isinstance(subject, str):
            raise ValueError("Subject must be a non-empty string")
        
        if not article_type or not isinstance(article_type, str):
            raise ValueError("Article type must be a non-empty string")
        
        if not isinstance(category, str):
            raise ValueError("Category must be a string")
        
        if not author_data or not isinstance(author_data, dict):
            raise ValueError("Author data must be a non-empty dictionary")
        
        if not schema or not isinstance(schema, dict):
            raise ValueError("Schema must be a non-empty dictionary")
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string input.
        
        Args:
            value: String to sanitize
            
        Returns:
            str: Sanitized string
        """
        if not value:
            return ""
        
        # Remove potentially dangerous characters and normalize
        sanitized = str(value).strip()
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        return sanitized
    
    def _validate_author_data(self, author_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean author data.
        
        Args:
            author_data: Raw author data
            
        Returns:
            Dict[str, Any]: Validated author data
            
        Raises:
            ValueError: If author data is invalid
        """
        required_fields = ["author_name", "author_country"]
        for field in required_fields:
            if field not in author_data:
                raise ValueError(f"Required author field '{field}' is missing")
            
            if not author_data[field] or not isinstance(author_data[field], str):
                raise ValueError(f"Author field '{field}' must be a non-empty string")
        
        # Clean and validate author data
        clean_author = {}
        clean_author["author_name"] = self._sanitize_string(author_data["author_name"])
        clean_author["author_country"] = self._sanitize_string(author_data["author_country"])
        clean_author["author_id"] = author_data.get("author_id", author_data.get("id", 1))
        
        return clean_author
    
    def _prepare_clean_data(self) -> Dict[str, Any]:
        """Prepare all clean, formatted data.
        
        Returns:
            Dict[str, Any]: Clean formatted data
        """
        # Get material data
        material_formula = formula_service.get_formula(self.subject)
        material_symbol = formula_service.get_symbol(self.subject)
        material_type = formula_service.get_material_type(self.subject)
        
        # Prepare clean base data
        clean_data = {
            # ===================================================================
            # CORE IDENTIFIERS - All sanitized and validated
            # ===================================================================
            "subject": self.subject,
            "article_type": self.article_type,
            "category": self.category,
            "author_name": self.author_data["author_name"],
            "author_country": self.author_data["author_country"],
            "author_id": self.author_data["author_id"],
            
            # ===================================================================
            # SCHEMA DATA - For components that need schema structure
            # ===================================================================
            "schema": str(self.schema),
            
            # ===================================================================
            # MATERIAL DATA - Clean and validated
            # ===================================================================
            "material_formula": material_formula or "N/A",
            "material_symbol": material_symbol or "N/A", 
            "material_type": material_type or "N/A",
            
            # ===================================================================
            # PRE-FORMATTED CONTENT - All formatting handled by Python utilities
            # ===================================================================
            "formatted_title": ContentFormatter.format_title(self.subject, self.article_type),
            "formatted_headline": ContentFormatter.format_headline(self.subject, self.category),
            "formatted_description": ContentFormatter.format_description(
                self.subject, 
                material_formula, 
                {"density": "N/A", "wavelength": "1064nm"}
            ),
            "formatted_keywords": ContentFormatter.format_keywords(
                self.subject, 
                self.category, 
                material_formula
            ),
            
            # ===================================================================
            # PRE-FORMATTED IMAGES - All URLs and alt text handled by Python
            # ===================================================================
            "formatted_images": ContentFormatter.format_images(self.subject),
            "hero_image_url": ContentFormatter.format_images(self.subject)["hero"]["url"],
            "hero_image_alt": ContentFormatter.format_images(self.subject)["hero"]["alt"],
            "closeup_image_url": ContentFormatter.format_images(self.subject)["closeup"]["url"],
            "closeup_image_alt": ContentFormatter.format_images(self.subject)["closeup"]["alt"],
            
            # ===================================================================
            # PRE-FORMATTED SPECIFICATIONS - All structure handled by Python
            # ===================================================================
            "formatted_technical_specs": ContentFormatter.format_technical_specifications(),
            "formatted_regulatory_standards": ContentFormatter.format_regulatory_standards(),
            "formatted_environmental_impact": ContentFormatter.format_environmental_impact(self.subject),
            "formatted_outcomes": ContentFormatter.format_outcomes(),
            "formatted_author": ContentFormatter.format_author_info(self.author_data),
            
            # ===================================================================
            # PRE-FORMATTED IDENTIFIERS - All slug generation handled by Python
            # ===================================================================
            "slug": SlugUtils.create_slug(self.subject),
            "subject_slug": SlugUtils.create_slug(self.subject),
            "category_slug": SlugUtils.create_slug(self.category),
            
            # ===================================================================
            # PRE-FORMATTED DATES - All date formatting handled by Python
            # ===================================================================
            "created_date": ContentFormatter.format_created_date(),
            "updated_date": ContentFormatter.format_updated_date(),
            "publish_date": ContentFormatter.format_publish_date(),
            "iso_date": ContentFormatter.format_iso_date(),
        }
        
        return clean_data
    
    def _get_component_clean_data(self, component_name: str, 
                                 component_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get clean, validated component-specific data.
        
        Args:
            component_name: Name of the component
            component_config: Component configuration
            
        Returns:
            Dict[str, Any]: Clean component-specific data
        """
        clean_component_data = {}
        
        # Content component - only validated config values
        if component_name == "content":
            clean_component_data["max_links"] = max(1, int(component_config.get("max_links", 5)))
            clean_component_data["audience"] = self._sanitize_string(component_config.get("audience", "technical"))
            clean_component_data["min_words"] = max(100, int(component_config.get("min_words", 800)))
            clean_component_data["max_words"] = max(500, int(component_config.get("max_words", 1500)))
        
        # Bullets component - only validated config values
        elif component_name == "bullets":
            clean_component_data["count"] = max(3, min(10, int(component_config.get("count", 5))))
        
        # Table component - only validated config values
        elif component_name == "table":
            table_keys = component_config.get("table_keys", ["Property", "Value", "Unit"])
            if isinstance(table_keys, list):
                clean_component_data["table_keys"] = [self._sanitize_string(str(key)) for key in table_keys]
            else:
                clean_component_data["table_keys"] = ["Property", "Value", "Unit"]
            
            clean_component_data["rows"] = max(3, min(20, int(component_config.get("rows", 5))))
        
        # Tags component - only validated config values
        elif component_name in ["tags", "metatags"]:
            clean_component_data["min_tags"] = max(3, int(component_config.get("min_tags", 5)))
            clean_component_data["max_tags"] = max(5, min(20, int(component_config.get("max_tags", 10))))
            
            tag_categories = component_config.get("tag_categories", [])
            if isinstance(tag_categories, list):
                clean_component_data["tag_categories"] = [self._sanitize_string(str(cat)) for cat in tag_categories]
            else:
                clean_component_data["tag_categories"] = []
        
        # Caption component - only validated config values
        elif component_name == "caption":
            clean_component_data["results_word_count_max"] = max(10, min(100, int(component_config.get("results_word_count_max", 40))))
            clean_component_data["equipment_word_count_max"] = max(10, min(100, int(component_config.get("equipment_word_count_max", 40))))
            clean_component_data["shape"] = self._sanitize_string(component_config.get("shape", "component"))
        
        return clean_component_data
    
    def _validate_clean_data(self, clean_data: Dict[str, Any]) -> None:
        """Final validation of clean data.
        
        Args:
            clean_data: Data to validate
            
        Raises:
            ValueError: If data is invalid
        """
        required_fields = [
            "subject", "article_type", "category", 
            "formatted_title", "formatted_description", 
            "material_formula", "material_symbol"
        ]
        
        for field in required_fields:
            if field not in clean_data:
                raise ValueError(f"Required field '{field}' missing from clean data")
        
        # Validate that formatted fields are not empty
        for field in ["formatted_title", "formatted_description", "formatted_keywords"]:
            if not clean_data.get(field):
                raise ValueError(f"Formatted field '{field}' is empty")
        
        logger.debug(f"Clean data validation passed for {len(clean_data)} fields")
