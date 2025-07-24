import re
from typing import Dict, Any

class SlugManager:
    """Manages slug generation for Z-Beam articles."""
    
    @classmethod
    def generate_slug(cls, subject: str, article_type: str) -> str:
        """Generate a slug based on subject and article_type.
        
        Args:
            subject: The subject name
            article_type: The article type (material, application, region, thesaurus)
            
        Returns:
            str: The generated slug
        """
        # Normalize the subject (lowercase, replace spaces with hyphens)
        normalized = subject.lower()
        normalized = re.sub(r'[^a-z0-9]+', '-', normalized)
        normalized = normalized.strip('-')
        
        # Generate slug based on article type
        if article_type == "material":
            return f"{normalized}-laser-cleaning"
        elif article_type == "application":
            return f"{normalized}-laser-cleaning"
        elif article_type == "region":
            return f"{normalized}-laser-cleaning"
        elif article_type == "thesaurus":
            return f"{normalized}"
        else:
            return normalized
    
    @classmethod
    def get_output_filename(cls, context: Dict[str, Any]) -> str:
        """Get the output filename based on subject and article_type.
        
        Args:
            context: The article context dictionary
            
        Returns:
            str: The output filename
        """
        subject = context.get("subject", "")
        article_type = context.get("article_type", "material")
        output_dir = context.get("output_dir", "output")
        
        # Generate slug
        slug = cls.generate_slug(subject, article_type)
        
        # Return full path
        return f"{output_dir}/{slug}.md"