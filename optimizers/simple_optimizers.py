"""
Simple, direct optimizers
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def apply_writing_style(content: str, context: Dict[str, Any], api_client, config: Dict[str, Any] = None) -> str:
    """Apply author writing style"""
    author_id = context.get("author_id", 1)
    material = context.get("material", "unknown")
    
    # Get simple config
    simple_config = config.get("simple_config", {}) if config else {}
    word_limit = simple_config.get("word_limit", 1200)
    
    # Enhanced author styles
    styles = {
        1: "formal, methodical Taiwanese engineering style",
        2: "casual, expressive Italian style with passion", 
        3: "direct, pragmatic American style with 'here's the deal' and 'bottom line' phrases",
        4: "academic, thorough Indonesian style with detailed explanations"
    }
    
    style = styles.get(author_id, "professional")
    
    # Add debug logging
    logger.info(f"🎨 Applying {style} for author {author_id}")
    
    prompt = f"""Rewrite this {material} laser cleaning article in {style}.
    
    FOR AUTHOR {author_id} SPECIFICALLY:
    - Use contractions and personal observations
    - Include characteristic phrases like "here's the deal", "bottom line", "let me tell you"
    - Make it conversational but technically accurate
    - Stay under {word_limit} words
    
    {content}
    
    Return only the rewritten content with distinct author voice:"""
    
    result = api_client.call(prompt, "style-application")
    logger.info(f"✅ Applied {style} writing style")
    return result

def add_technical_depth(content: str, context: Dict[str, Any], api_client, config: Dict[str, Any] = None) -> str:
    """Add technical authenticity"""
    material = context.get("material", "unknown")
    simple_config = config.get("simple_config", {}) if config else {}
    word_limit = simple_config.get("word_limit", 1200)
    depth = simple_config.get("technical_depth", "moderate")
    
    # Simple depth instructions
    depth_instructions = {
        "light": "Add 1-2 basic technical details",
        "moderate": "Add 2-3 specific measurements and 1 industry standard",
        "deep": "Add detailed specifications, multiple standards, and equipment manufacturers"
    }
    
    instruction = depth_instructions.get(depth, depth_instructions["moderate"])
    
    prompt = f"""Add technical credibility to this {material} laser cleaning article:
    - {instruction}
    - Keep casual, readable tone
    - Stay under {word_limit} words
    
    {content}
    
    Return only the enhanced content:"""
    
    result = api_client.call(prompt, "technical-enhancement")
    logger.info(f"✅ Added {depth} technical depth")
    return result

def humanize_content(content: str, context: Dict[str, Any], api_client, config: Dict[str, Any] = None) -> str:
    """Make content sound more human-written"""
    material = context.get("material", "unknown")
    simple_config = config.get("simple_config", {}) if config else {}
    word_limit = simple_config.get("word_limit", 1200)
    intensity = simple_config.get("style_intensity", "moderate")
    
    # Simple intensity instructions
    intensity_instructions = {
        "light": "Add subtle contractions and casual phrases",
        "moderate": "Add contractions, personal observations, and rhetorical questions",
        "heavy": "Add heavy casual language, personal asides, and conversational elements"
    }
    
    instruction = intensity_instructions.get(intensity, intensity_instructions["moderate"])
    
    prompt = f"""Make this {material} laser cleaning article sound naturally human-written:
    - {instruction}
    - Keep technical accuracy
    - Stay under {word_limit} words
    
    {content}
    
    Return only the more human-sounding content:"""
    
    result = api_client.call(prompt, "humanization")
    logger.info(f"✅ Applied {intensity} humanization")
    return result