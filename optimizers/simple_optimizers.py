"""
Simple, direct optimizers - no classes needed
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def apply_writing_style(content: str, context: Dict[str, Any], api_client) -> str:
    """Apply author writing style"""
    author_id = context.get("author_id", 1)
    material = context.get("material", "unknown")
    
    # Get author info (simplified)
    author_styles = {
        1: "formal, technical",
        2: "casual, Italian-influenced", 
        3: "conversational, American",
        4: "academic, detailed"
    }
    
    style = author_styles.get(author_id, "professional")
    
    prompt = f"""Rewrite this {material} laser cleaning article in a {style} writing style.
    Use contractions, personal observations, and natural flow.
    Keep all technical information but make it conversational.
    Stay under 1200 words.
    
    {content}
    
    Return only the rewritten content:"""
    
    result = api_client.call(prompt, "style-application")
    logger.info(f"✅ Applied {style} writing style")
    return result

def add_technical_depth(content: str, context: Dict[str, Any], api_client) -> str:
    """Add technical authenticity"""
    material = context.get("material", "unknown")
    
    prompt = f"""Add technical credibility to this {material} laser cleaning article:
    - Include 2-3 specific measurements (wavelengths, power densities, speeds)
    - Add 1-2 industry standards (ASTM, ISO, ANSI numbers)
    - Reference 1-2 real equipment manufacturers or models
    - Keep casual, readable tone
    - Stay under 1200 words
    
    {content}
    
    Return only the enhanced content:"""
    
    result = api_client.call(prompt, "technical-enhancement")
    logger.info(f"✅ Added technical depth")
    return result

def humanize_content(content: str, context: Dict[str, Any], api_client) -> str:
    """Make content sound more human-written"""
    material = context.get("material", "unknown")
    
    prompt = f"""Make this {material} laser cleaning article sound naturally human-written:
    - Add casual phrases and contractions
    - Use varied sentence lengths (mix short and long)
    - Include minor imperfections and conversational elements
    - Add personal observations and rhetorical questions
    - Keep technical accuracy but reduce formal language
    - Stay under 1200 words
    
    {content}
    
    Return only the improved content:"""
    
    result = api_client.call(prompt, "humanization")
    logger.info(f"✅ Humanized content")
    return result