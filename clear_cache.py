#!/usr/bin/env python3
"""
Cache clearing script for content generator testing

Clears the LRU cache in fail_fast_generator to force reloading of updated prompts
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.content.generators.fail_fast_generator import FailFastContentGenerator

def clear_content_generator_cache():
    """Clear all LRU caches in the content generator"""
    print("🧹 Clearing content generator cache...")
    
    # Clear class-level caches
    if hasattr(FailFastContentGenerator._load_base_content_prompt, 'cache_clear'):
        FailFastContentGenerator._load_base_content_prompt.cache_clear()
        print("✅ Cleared _load_base_content_prompt cache")
    
    if hasattr(FailFastContentGenerator._load_persona_prompt, 'cache_clear'):
        FailFastContentGenerator._load_persona_prompt.cache_clear() 
        print("✅ Cleared _load_persona_prompt cache")
        
    if hasattr(FailFastContentGenerator._load_formatting_prompt, 'cache_clear'):
        FailFastContentGenerator._load_formatting_prompt.cache_clear()
        print("✅ Cleared _load_formatting_prompt cache")
        
    if hasattr(FailFastContentGenerator._load_authors_data, 'cache_clear'):
        FailFastContentGenerator._load_authors_data.cache_clear()
        print("✅ Cleared _load_authors_data cache")
    
    print("🎉 Cache cleared! Updated prompts will be loaded on next generation.")

if __name__ == "__main__":
    clear_content_generator_cache()
