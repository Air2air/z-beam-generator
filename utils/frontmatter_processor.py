import logging


class FrontmatterProcessor:
    """Centralized processor for frontmatter data."""
    
    @staticmethod
    def parse(text):
        """Parse frontmatter from text."""
        if not text.startswith("---"):
            return {}, text
            
        # Find the end of frontmatter
        end_index = text.find("---", 3)
        if end_index == -1:
            return {}, text
            
        # Extract and parse frontmatter
        frontmatter_text = text[3:end_index].strip()
        content = text[end_index+3:].strip()
        
        try:
            import yaml
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter, content
        except Exception as e:
            logging.error(f"Failed to parse frontmatter: {str(e)}")
            return {}, text
            
    @staticmethod
    def serialize(frontmatter):
        """Convert frontmatter dict to YAML format."""
        try:
            import yaml
            frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            return f"---\n{frontmatter_yaml}---\n"
        except Exception as e:
            logging.error(f"Failed to serialize frontmatter: {str(e)}")
            return "---\n---\n"