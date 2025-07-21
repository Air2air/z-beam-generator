class ConfigValidator:
    """Validates configuration against a schema."""
    
    @staticmethod
    def validate_context(context):
        """Validate the ARTICLE_CONTEXT."""
        errors = []
        
        # Check required fields
        required_fields = ["subject", "article_type", "ai_provider"]
        for field in required_fields:
            if field not in context:
                errors.append(f"Missing required field: {field}")
                
        # Check components
        if "components" not in context:
            errors.append("Missing components configuration")
        else:
            # Check required components
            required_components = ["frontmatter", "content"]
            for component in required_components:
                if component not in context["components"]:
                    errors.append(f"Missing required component: {component}")
                    
        # Return validation result
        if errors:
            return False, errors
        return True, []