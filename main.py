#!/usr/bin/env python3
"""
Simplified Z-Beam Content Generator

Single-file implementation following anti-bloat and anti-hardcoding rules.
All configuration via GlobalConfigManager, no abstractions, maximum simplicity.
"""

import sys
import logging
from typing import Optional
from pathlib import Path

# ADD MISSING IMPORTS
from config.global_config import GlobalConfigManager
from modules.content_generator import generate_content_for_material

# Initialize logger
logger = logging.getLogger(__name__)

def main():
    """Main execution with fail-fast error handling"""
    
    try:
        # Load configuration
        config = GlobalConfigManager.get_instance()
        
        # Get user config
        material = config.get('material')
        provider = config.get('generator_provider')
        file_name = config.get('file_name')
        
        logger.info(f"🚀 Starting generation: {material} using {provider}")
        
        # GENERATE CONTENT - FAIL FAST ON ANY ERROR
        article_content = generate_content_for_material(
            material=material,
            provider=provider,
            max_tokens=config.get('max_tokens', 4096),
            temperature=config.get('temperature', 0.7)
        )
        
        # SAVE CONTENT - FAIL IF SAVE FAILS
        if not save_article(article_content, file_name, config):
            logger.error(f"❌ GENERATION FAILED: Could not save article to {file_name}")
            raise RuntimeError(f"Failed to save article: {file_name}")
        
        logger.info(f"✅ GENERATION COMPLETE: {file_name}")
        print(f"✅ Article generated successfully: {file_name}")
        
    except Exception as e:
        logger.error(f"💀 GENERATION FAILED: {e}")
        print(f"❌ Article generation failed: {e}")
        raise  # Re-raise to ensure non-zero exit code

def save_article(content: str, file_name: str, config) -> bool:
    """Save article content to output file"""
    
    try:
        # Get output directory from config
        output_dir_name = config.get('output_directory', 'output')
        
        # Create output directory
        output_dir = Path(output_dir_name)
        output_dir.mkdir(exist_ok=True)
        
        # Write content
        output_path = output_dir / file_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"📄 Article saved to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save article: {e}")
        return False

def generate_content_simple(config) -> Optional[str]:
    """
    Simple content generation using direct API calls.
    No abstractions, no service layers, maximum simplicity.
    """
    try:
        # Get configuration values from GlobalConfigManager
        material = config.get_material()
        provider = config.get_generator_provider()
        max_tokens = config.get_max_tokens()
        temperature = config.get_content_temperature()
        
        print(f"🎯 Generating content for {material} using {provider}")
        print(f"⚙️ Settings: {max_tokens} tokens, {temperature} temperature")
        
        # Simple content generation call
        content = generate_content_for_material(
            material=material,
            provider=provider,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if content:
            # Save to output file
            output_path = save_content_simple(config, content)
            return output_path
        else:
            raise RuntimeError("Empty content returned from generator")
            
    except Exception as e:
        print(f"❌ Content generation error: {e}")
        return None

def save_content_simple(config, content: str) -> str:
    """Save content to output file using simple direct approach."""
    try:
        # Get ALL values from config - NO HARDCODING
        file_name = config.get('file_name')
        output_dir_name = config.get('output_directory', 'output')  # From config
        
        # Create output directory
        output_dir = Path(output_dir_name)
        output_dir.mkdir(exist_ok=True)
        
        # Write content
        output_path = output_dir / file_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return str(output_path)
        
    except Exception as e:
        raise RuntimeError(f"Failed to save content: {e}")

if __name__ == "__main__":
    main()
