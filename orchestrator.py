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
    
    def orchestrate_article(self, optimized_sections, metadata, author_data):
        """Orchestrate final article"""
        logger.info("🎼 ORCHESTRATING FINAL ARTICLE")
        
        article_parts = []
        
        # Add YAML frontmatter
        logger.info("🎼 Adding YAML frontmatter...")
        article_parts.append("---")
        for key, value in metadata.items():
            if key == "tags" and isinstance(value, list):
                tags_str = "[" + ", ".join(f"'{tag}'" for tag in value) + "]"
                article_parts.append(f'{key}: {tags_str}')
            else:
                article_parts.append(f'{key}: "{value}"')
        article_parts.append("---")
        article_parts.append("")
        
        # Add main title
        article_parts.append(f"# {metadata['title']}")
        article_parts.append("")
        
        # Handle single optimized article
        if len(optimized_sections) == 1 and optimized_sections[0]['name'] == 'optimized_article':
            logger.info("🎼 Using single optimized article")
            article_parts.append(optimized_sections[0]['content'])
        else:
            # Multiple sections - assemble normally
            logger.info(f"🎼 Adding {len(optimized_sections)} sections...")
            for section in optimized_sections:
                article_parts.append(f"## {section['title']}")
                article_parts.append("")
                article_parts.append(section['content'])
                article_parts.append("")
        
        final_article = "\n".join(article_parts)
        logger.info(f"✅ Article orchestrated - {len(final_article)} chars")
        
        return final_article