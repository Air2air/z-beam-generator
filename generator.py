#!/usr/bin/env python3
"""
Z-Beam Generator - Main orchestrator for laser cleaning article generation

This is the primary entry point that coordinates the entire article generation pipeline:
1. GENERATION PHASE: Creates text sections and metadata 
2. OPTIMIZATION PHASE: Applies writing style optimization
3. ORCHESTRATION PHASE: Assembles final markdown article

The generator uses a modular architecture where each component has a single responsibility:
- ContentGenerator: Creates text sections and delegates metadata generation
- MetadataGenerator: Generates structured metadata without AI prompts  
- Optimizer: Applies writing style improvements (iterative or writing samples)
- ArticleOrchestrator: Assembles final markdown output

Configuration is provided via run.py and includes:
- API provider settings (OpenAI, XAI, Gemini, DeepSeek)
- Word limits and generation parameters
- Optimization method selection
- File paths and output settings
"""
import logging
from pathlib import Path
from setup_logging import setup_logging
from run import get_config
from api_client import APIClient
from content_generator import ContentGenerator
from orchestrator import ArticleOrchestrator

# Setup logging
logger = setup_logging()

class ZBeamGenerator:
    """
    Main generator class that orchestrates the complete article generation pipeline
    
    Architecture:
    - Uses context-driven generation (material, author_id, article_type from config)
    - Separates concerns: content generation, metadata creation, optimization, assembly
    - Supports multiple optimization methods: iterative refinement or writing samples
    - Generates structured metadata without AI prompts for consistency
    - Produces markdown articles with frontmatter metadata
    
    Pipeline Flow:
    1. Generate text sections using configured prompts and word limits
    2. Generate metadata using structured data (not AI prompts)  
    3. Load author data from authors.json
    4. Apply style optimization using selected method
    5. Orchestrate final article assembly with proper markdown formatting
    """
    
    def __init__(self, config, context):
        """
        Initialize generator with configuration and context
        
        Args:
            config (dict): Complete configuration from run.py including:
                - provider: API provider (OPENAI, XAI, GEMINI, DEEPSEEK)
                - model: Model name for the selected provider
                - optimization_method: "iterative" or "writing_samples"
                - word limits: max_section_words, target_section_words, max_total_words
                - file paths: prompts_dir, output_dir, authors_file, sections_file
            context (dict): Generation context containing:
                - material: Material to generate article about (e.g., "titanium")
                - author_id: Integer ID of author from authors.json
                - article_type: Type of article (e.g., "material")
        
        Raises:
            ValueError: If optimization_method is not "iterative" or "writing_samples"
        """
        self.config = config
        self.context = context
        
        # Initialize core components
        self.api_client = APIClient(config)
        self.content_generator = ContentGenerator(config, self.api_client)
        
        # Optimization method selection - FAIL FAST if invalid
        if config["optimization_method"] == "iterative":
            from iterative_optimizer import IterativeOptimizer
            self.optimizer = IterativeOptimizer(config, context, self.api_client)
        elif config["optimization_method"] == "writing_samples":
            from writing_samples_optimizer import WritingSamplesOptimizer
            self.optimizer = WritingSamplesOptimizer(config, context, self.api_client)
        else:
            raise ValueError(f"Invalid optimization_method: {config['optimization_method']}. Must be 'iterative' or 'writing_samples'")
        
        self.orchestrator = ArticleOrchestrator(config)
        
        logger.info(f"🔧 ZBeamGenerator initialized - {config['provider']}/{config['model']}")
        logger.info(f"🎯 Optimization method: {config['optimization_method']}")
    
    def generate_article(self):
        """
        Generate complete laser cleaning article using the configured pipeline
        
        This is the main method that executes the three-phase generation process:
        
        GENERATION PHASE:
        - Loads section prompts from sections.json
        - Generates text sections with word limit enforcement
        - Creates structured metadata using MetadataGenerator (no AI prompts)
        - Loads author data from authors.json
        
        OPTIMIZATION PHASE:
        - Applies selected optimization method to improve writing style
        - For "writing_samples": matches author's writing style using samples
        - For "iterative": refines content through multiple iterations
        
        ORCHESTRATION PHASE:
        - Assembles final markdown article with YAML frontmatter
        - Combines optimized sections with metadata
        - Formats according to article template
        
        Returns:
            str: Complete markdown article with frontmatter metadata
            
        The generated article includes:
        - YAML frontmatter with all metadata fields
        - Article title and sections
        - Proper markdown formatting
        - Author attribution and technical specifications
        """
        # Extract context for this generation
        material = self.context["material"]
        author_id = self.context["author_id"] 
        article_type = self.context["article_type"]
        
        logger.info("🚀 STARTING ARTICLE GENERATION")
        logger.info(f"📄 Material: {material} | Author: {author_id} | Type: {article_type}")
        
        # PHASE 1: GENERATION
        # Generate text content and structured metadata
        logger.info("🔥 GENERATION PHASE")
        
        # Generate text sections using prompts and word limits
        sections = self.content_generator.generate_text_sections(material, article_type)
        
        # Generate metadata using structured approach (no AI prompts)
        # This includes material properties, author data, and generated tags
        metadata = self.content_generator.generate_metadata(material, author_id, article_type)
        
        # Load author data for optimization phase
        author_data = self.content_generator.load_author_data(author_id)
        
        # PHASE 2: OPTIMIZATION
        # Apply writing style improvements using selected method
        logger.info("🔧 OPTIMIZATION PHASE")
        optimized_sections = self.optimizer.optimize_sections(sections, author_data)
        
        # PHASE 3: ORCHESTRATION  
        # Assemble final article with proper formatting
        logger.info("🎼 ORCHESTRATION PHASE")
        article = self.orchestrator.orchestrate_article(optimized_sections, metadata, author_data)
        
        logger.info("🎉 ARTICLE GENERATION COMPLETED")
        return article

def main():
    """
    Main entry point for the Z-Beam Generator application
    
    Workflow:
    1. Load configuration and context from run.py
    2. Initialize ZBeamGenerator with config
    3. Generate complete article
    4. Save article to output directory
    
    The output file is named based on the material:
    - Format: {material}_laser_cleaning.md
    - Location: config["output_dir"]
    - Example: titanium_laser_cleaning.md
    
    Configuration is loaded from run.py which includes:
    - User settings (material, author_id, article_type)
    - API configuration (provider, model, parameters)
    - Generation settings (word limits, optimization method)
    - File paths (prompts, output, authors, sections)
    """
    # Load configuration from run.py
    config, context = get_config()
    
    # Initialize and run generator
    generator = ZBeamGenerator(config, context)
    article = generator.generate_article()
    
    # Save output to file
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(exist_ok=True)
    
    # Create filename based on material name
    output_file = output_dir / f"{context['material'].replace(' ', '_')}_laser_cleaning.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(article)
    
    logger.info(f"✅ Article saved to: {output_file}")

if __name__ == "__main__":
    main()