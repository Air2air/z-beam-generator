#!/usr/bin/env python3
"""
Article Orchestrator - Assembles final article
"""
import logging

logger = logging.getLogger(__name__)

class ArticleOrchestrator:
    """Orchestrates final article assembly"""
    
    def __init__(self, config):
        self.config = config
    
    def orchestrate_article(self, sections, metadata, tags):
        """Orchestrate final article assembly with separate tags input"""
        logger.info("🎼 Assembling final article with discrete components")
        
        # Add tags to metadata for YAML generation
        metadata_with_tags = metadata.copy()
        metadata_with_tags["tags"] = tags
        
        # Ensure proper data types for YAML output
        metadata_with_tags = self._ensure_proper_yaml_types(metadata_with_tags)
        
        # Create YAML frontmatter
        frontmatter = "---\n"
        for key, value in metadata_with_tags.items():
            if isinstance(value, list):
                frontmatter += f"{key}:\n"
                for item in value:
                    frontmatter += f"  - \"{item}\"\n"
            elif isinstance(value, dict):
                frontmatter += f"{key}:\n"
                for k, v in value.items():
                    frontmatter += f"  {k}: \"{v}\"\n"
            elif isinstance(value, str):
                frontmatter += f"{key}: \"{value}\"\n"
            else:
                frontmatter += f"{key}: {value}\n"
        frontmatter += "---\n\n"
        
        # Assemble article content
        article_content = frontmatter
        article_content += f"# {metadata['title']}\n\n"
        
        for section in sections:
            article_content += f"## {section['title']}\n"
            article_content += f"{section['content']}\n\n"
        
        logger.info("✅ Article orchestration completed with discrete tag integration")
        return article_content

    def _ensure_proper_yaml_types(self, metadata):
        """Ensure all metadata has proper types for YAML output"""
        import ast
        
        # Fields that should be arrays
        array_fields = ["processingChallenges", "alternativeMethods", "costFactors", "tags"]
        
        # Fields that should be objects
        object_fields = ["laserCleaningParameters", "performanceMetrics"]
        
        # Convert string arrays to actual arrays
        for field in array_fields:
            if field in metadata and isinstance(metadata[field], str):
                try:
                    metadata[field] = ast.literal_eval(metadata[field])
                    logger.info(f"✅ Converted {field} from string to array")
                except (ValueError, SyntaxError):
                    logger.warning(f"⚠️ Failed to convert {field} to array: {metadata[field]}")
        
        # Convert string objects to actual objects
        for field in object_fields:
            if field in metadata and isinstance(metadata[field], str):
                try:
                    metadata[field] = ast.literal_eval(metadata[field])
                    logger.info(f"✅ Converted {field} from string to object")
                except (ValueError, SyntaxError):
                    logger.warning(f"⚠️ Failed to convert {field} to object: {metadata[field]}")
        
        return metadata