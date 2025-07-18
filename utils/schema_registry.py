"""Schema Registry optimized for scientific/technical content."""

class SchemaRegistry:
    """Registry for schema.org type mappings with scientific focus."""
    
    # Default schema.org type mappings - SCIENTIFIC FOCUS
    TYPE_MAPPINGS = {
        # Basic content types
        "article": "ScholarlyArticle",
        "blog": "BlogPosting",
        "news": "NewsArticle",
        "technical": "TechnicalArticle",
        "case_study": "ScholarlyArticle",
        
        # Scientific/Technical types
        "material": "ChemicalSubstance",  # Scientific focus for materials
        "substance": "ChemicalSubstance",
        "element": "ChemicalSubstance",
        "compound": "ChemicalSubstance",
        "alloy": "ChemicalSubstance",
        "wood": "ChemicalSubstance",  # For materials like maple wood
        
        # Equipment types (still products but research-focused)
        "equipment": "Product",
        "instrument": "Product",
        "device": "Product",
        "tool": "Product",
        "software": "SoftwareApplication",
        
        # Process/Method types
        "technique": "HowTo",
        "method": "HowTo",
        "procedure": "HowTo",
        "protocol": "HowTo",
        
        # Research types
        "research": "ScholarlyArticle",
        "study": "ScholarlyArticle",
        "analysis": "ScholarlyArticle",
        "theory": "ScholarlyArticle",
        
        # Location types
        "region": "Place",
        "facility": "Place",  # Research facility, not business
        "laboratory": "Place",
        
        # Special content types
        "guide": "HowTo",
        "faq": "FAQPage",
        "comparison": "ScholarlyArticle",
        "specification": "TechnicalArticle",
        
        # Default fallback
        "default": "ScholarlyArticle"  # Scientific default
    }
    
    # Special field handlers for specific schema types
    SPECIAL_FIELD_HANDLERS = {
        # For materials - scientific properties
        "ChemicalSubstance": {
            "properties_field": "additionalProperty",
            "property_type": "PropertyValue",
            "dimensions_handling": "separate_properties"
        },
        # For techniques/methods - steps and requirements
        "HowTo": {
            "steps_field": "step",
            "steps_type": "HowToStep",
            "requirements_field": "supply",
            "tools_field": "tool"
        },
        # For research equipment
        "Product": {
            "properties_field": "additionalProperty",
            "property_type": "PropertyValue",
            "research_application": "applicationCategory"
        },
        # For research articles
        "ScholarlyArticle": {
            "citations_field": "citation",
            "references_field": "citation",
            "authors_field": "author",
            "keywords_field": "keywords"
        }
    }
    
    @classmethod
    def get_schema_type(cls, article_type, content=None):
        """Get the appropriate schema.org type with scientific focus."""
        article_type = article_type.lower()
        
        # Special handling for material types
        if article_type == "material":
            if content and "name" in content:
                material_name = content["name"].lower()
                
                # Wood-specific materials use more specific type
                if any(wood in material_name for wood in ["wood", "timber", "oak", "maple", "cedar"]):
                    return "ChemicalSubstance"  # Best match in schema.org
                
                # Metals and alloys
                if any(metal in material_name for metal in ["steel", "aluminum", "titanium", "alloy"]):
                    return "ChemicalSubstance"
                    
                # Polymers and plastics
                if any(polymer in material_name for polymer in ["polymer", "plastic", "resin"]):
                    return "ChemicalSubstance"
        
        # Direct lookup
        if article_type in cls.TYPE_MAPPINGS:
            schema_type = cls.TYPE_MAPPINGS[article_type]
        else:
            # Try to find a partial match
            for key, value in cls.TYPE_MAPPINGS.items():
                if key in article_type:
                    schema_type = value
                    break
            else:
                # Use default if no match found
                schema_type = cls.TYPE_MAPPINGS["default"]
        
        # Content-based overrides
        if content:
            # For materials with educational focus
            if "purpose" in content and "educational" in content["purpose"]:
                schema_type = "ScholarlyArticle"
                
            # For materials with technical specifications, still use ChemicalSubstance
            if "technicalSpecifications" in content and isinstance(content["technicalSpecifications"], dict):
                if article_type == "material":
                    schema_type = "ChemicalSubstance"
            
            # For content with experimental procedures
            if "procedure" in content and isinstance(content["procedure"], list):
                schema_type = "HowTo"
                
            # For content with extensive citations
            if "references" in content and isinstance(content["references"], list) and len(content["references"]) > 3:
                schema_type = "ScholarlyArticle"
        
        return schema_type
    
    @classmethod
    def get_field_handlers(cls, schema_type):
        """Get special field handlers for a schema type."""
        return cls.SPECIAL_FIELD_HANDLERS.get(schema_type, {})
    
    @classmethod
    def is_material_type(cls, schema_type):
        """Check if a schema type is material-related."""
        return schema_type in ["ChemicalSubstance"]
    
    @classmethod
    def is_article_type(cls, schema_type):
        """Check if a schema type is academic article-like."""
        return schema_type in ["ScholarlyArticle", "TechnicalArticle"]
    
    @classmethod
    def is_method_type(cls, schema_type):
        """Check if a schema type is method-related."""
        return schema_type in ["HowTo"]