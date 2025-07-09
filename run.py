#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified with GlobalConfigManager
"""
import logging
from pathlib import Path

def setup_logging(config):
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"zbeam_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("setup_logging")
    logger.info(f"📝 Logging initialized - File: {log_file}")
    return logger

def get_config():
    """Get configuration and context for generator"""
    
    # User settings
    context = {
        "material": "titanium", 
        "author_id": 2, 
        "article_type": "material"
        }

    # Initialize configuration
    config = {
        "provider": "OPENAI",  # Options: OPENAI, XAI, GEMINI, DEEPSEEK
        "model": "gpt-4-turbo",
        "temperature": 0.3,  # Lower from 0.7 to reduce AI-sounding language
        "metadata_temperature": 0.3,
        "max_tokens": 4000,
        
        # Optimization settings
        "optimization_method": "writing_samples",  # or "iterative"
        "iterative_optimizer_file": "iterative_optimizer.py",
        "writing_samples_optimizer_file": "writing_samples_optimizer.py",
        
        "prompts_dir": "prompts",
        "output_dir": "output",
        "authors_file": "prompts/authors/authors.json",
        "sections_file": "prompts/text/sections.json",
        
        # Section length limits
        "max_section_words": 75,
        "target_section_words": 75,
        "max_total_words": 800,
        
        # AI Detection Settings - ADDED:
        "zerogpt_enabled": False,
        "target_ai_score": 30,
        "sapling_api_key": None,
        "winston_api_key": None,
        "contentatscale_api_key": None,
        
        # Default material for fallback
        "default_material": "titanium",
        
        # Debug settings
        "debug_prompts": True,
        "debug_responses": True,
        "debug_content_flow": True,
        
        # Similarity thresholds for delta analysis
        "high_similarity_threshold": 0.95,
        "low_similarity_threshold": 0.7,
        "final_similarity_threshold": 0.85,
        
        "providers": {
            "OPENAI": {
                "api_key_env": "OPENAI_API_KEY",
                "base_url": "https://api.openai.com/v1",
                "models": {
                    "gpt-4o": "gpt-4o",
                    "gpt-4o-mini": "gpt-4o-mini",
                    "gpt-4-turbo": "gpt-4-turbo",
                    "gpt-3.5-turbo": "gpt-3.5-turbo"
                }
            },
            "XAI": {
                "api_key_env": "XAI_API_KEY",
                "base_url": "https://api.x.ai/v1",
                "models": {
                    "grok-beta": "grok-beta",
                    "grok-vision-beta": "grok-vision-beta"
                }
            },
            "GEMINI": {
                "api_key_env": "GEMINI_API_KEY",
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "models": {
                    "gemini-1.5-pro": "gemini-1.5-pro",
                    "gemini-1.5-flash": "gemini-1.5-flash",
                    "gemini-1.5-pro-002": "gemini-1.5-pro-002",
                    "gemini-1.5-flash-002": "gemini-1.5-flash-002"
                }
            },
            "DEEPSEEK": {
                "api_key_env": "DEEPSEEK_API_KEY",
                "base_url": "https://api.deepseek.com/v1",
                "models": {
                    "deepseek-chat": "deepseek-chat",
                    "deepseek-coder": "deepseek-coder",
                    "deepseek-reasoner": "deepseek-reasoner"
                }
            }
        }
    }

    return config, context

def extract_content_from_markdown(article_content):
    """Extract main content from markdown, skipping frontmatter"""
    content = article_content.strip()
    
    # Skip frontmatter if present
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    return content

def main():
    """Main function with integrated AI detection"""
    config, context = get_config()
    
    # Initialize logging
    logger = setup_logging(config)
    logger.info(f"🔧 ZBeamGenerator initialized - {config['provider']}/{config['model']}")
    logger.info("🚀 STARTING ARTICLE GENERATION")
    logger.info(f"📄 Material: {context['material']} | Author: {context['author_id']} | Type: {context['article_type']}")
    
    # Generate article
    from generator import ZBeamGenerator
    
    generator = ZBeamGenerator(config, context)
    article = generator.generate_article()
    
    # Save output first
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{context['material'].replace(' ', '_')}_laser_cleaning.md"
    with open(output_file, 'w') as f:
        f.write(article)
    
    logger.info(f"✅ Article saved to: {output_file}")
    
    # Now run AI detection on the generated content
    print("\n" + "="*60)
    print("🤖 RUNNING AI DETECTION ANALYSIS")
    print("="*60)
    
    # Import and run AI detector
    from detectors import AIDetector
    
    # Extract content (skip frontmatter)
    content_to_test = extract_content_from_markdown(article)
    
    print(f"📖 Testing generated content")
    print(f"📊 Content length: {len(content_to_test)} characters, {len(content_to_test.split())} words")
    print()
    
    # Configure and run detector
    detector = AIDetector(config)
    results = detector.score_content(content_to_test)
    
    # Print detailed report
    detector.print_detailed_report(results)
    
    # Show content sample
    print("\n" + "="*60)
    print("📝 CONTENT SAMPLE (first 300 chars):")
    print("="*60)
    sample = content_to_test[:300] + "..." if len(content_to_test) > 300 else content_to_test
    print(sample)
    print("="*60)
    
    # Final summary
    summary = results.get("summary", {})
    if summary.get("services_count", 0) > 0:
        avg_score = summary.get("average_ai_score", 0)
        target = config["target_ai_score"]
        
        if summary.get("passed_threshold", False):
            print(f"🎉 SUCCESS: AI detection score {avg_score:.1f}% is below target {target}%")
        else:
            print(f"⚠️  NEEDS IMPROVEMENT: AI detection score {avg_score:.1f}% is above target {target}%")
            print("💡 Consider using more aggressive humanization in your optimization prompts")
    
    print(f"\n📁 Full article saved to: {output_file}")

if __name__ == "__main__":
    main()
