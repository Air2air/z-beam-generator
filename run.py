#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified with GlobalConfigManager
"""


def get_config():
    """Get configuration and context for generator"""

    # User settings
    context = {"material": "titanium", "author_id": 2, "article_type": "material"}

    # Initialize configuration
    config = {
        "provider": "OPENAI",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "metadata_temperature": 0.3,
        "max_tokens": 4000,
        "optimization_method": "iterative",
        "prompts_dir": "prompts",
        "output_dir": "output",
        "authors_file": "prompts/authors/authors.json",
        "sections_file": "prompts/text/sections.json",
        
        # Section length limits
        "max_section_words": 150,
        "target_section_words": 150,
        "max_total_words": 800,
        
        # Default material for fallback
        "default_material": "titanium",
        
        # Debug settings
        "debug_prompts": False,
        "debug_deltas": True,
        
        # Similarity thresholds for delta analysis
        "high_similarity_threshold": 0.95,  # Warn if step changes very little
        "low_similarity_threshold": 0.7,   # Success if step changes significantly
        "final_similarity_threshold": 0.85, # Warn if final text may still appear AI-generated
    }

    return config, context


def main():
    """Main function - can run generator or just return config"""
    config, context = get_config()

    #Optionally run the generator directly from here
    #Uncomment these lines if you want run.py to actually generate articles:

    from generator import ZBeamGenerator
    from pathlib import Path
    
    try:
        generator = ZBeamGenerator(config, context)
        article = generator.generate_article()
    
        # Save output
        output_dir = Path(config["output_dir"])
        output_dir.mkdir(exist_ok=True)
    
        output_file = output_dir / f"{context['material'].replace(' ', '_')}_laser_cleaning.md"
        with open(output_file, 'w') as f:
            f.write(article)
    
        print(f"✅ Article saved to: {output_file}")
    
    except Exception as e:
        print(f"❌ Generation failed: {e}")


if __name__ == "__main__":
    main()
