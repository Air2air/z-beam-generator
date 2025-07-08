#!/usr/bin/env python3
"""
Content Generator - Main coordinator for content generation
"""

import logging
from .health_checker import APIHealthChecker
from .section_generator import SectionGenerator
from .sections_loader import SectionsLoader
from .article_composer import ArticleComposer
from modules.pipeline_orchestrator import PipelineOrchestrator
from modules.api_client import APIClient
from modules.optimization.orchestrator import OptimizationOrchestrator

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Main coordinator for content generation with optimization pipeline"""
    
    def __init__(self, config):
        self.config = config
        self.api_client = APIClient(config)
        self.health_checker = APIHealthChecker(config)
        self.sections_loader = SectionsLoader(config)
        self.section_generator = SectionGenerator(config)
        self.article_composer = ArticleComposer()  # ✅ Remove (config) parameter
        self.optimization_orchestrator = OptimizationOrchestrator(config)
        
        # Initialize pipeline orchestrator for metadata
        self.orchestrator = PipelineOrchestrator(config)
        
        # Initialize optimization settings
        self.eat_requirements = config.get("eat_requirements", None)
        self.optimizer = self.optimization_orchestrator

    def generate_article(self, context):
        """Generate article with metadata and content"""
        logger.info("🚀 Starting article generation...")
        
        # Health check API FIRST - before any expensive operations
        logger.info("🏥 Performing API health check...")
        self.health_checker.check_api_health()
        
        # Execute pre-generation modules (metadata)
        pre_results = self.orchestrator.execute_stage("pre_generation", context)
        
        # Extract materialType for existing logic
        material = context["materialType"]
        
        # Load sections configuration
        sections = self.sections_loader.load_sections()
        material_sections = self.sections_loader.get_material_sections(sections, material)
        
        # Generate sections
        logger.info("📝 Generating article sections...")
        generated_sections = []
        
        for section in material_sections:
            logger.info(f"🔄 Generating section: {section['name']}")
            
            # Generate section content - USE THE CORRECT METHOD NAME
            if self.eat_requirements:
                content = self.section_generator.generate_section_with_enhancement(
                    section=section,
                    material=material,
                    eat_requirements=self.eat_requirements
                )
            else:
                content = self.section_generator.generate_section_standard(
                    section=section,
                    material=material
                )
            
            # Format the section
            formatted_section = self.article_composer.format_section(
                section_name=section["name"],
                section_title=section["title"],
                content=content
            )
            
            generated_sections.append(formatted_section)
        
        # Combine sections into final article
        logger.info("📋 Combining sections into final article...")
        article_body = self.article_composer.combine_sections(generated_sections, material)
        
        # Apply optimization if enabled
        if self.eat_requirements:
            logger.info("🎯 Applying optimization pipeline...")
            article_body = self.optimizer.optimize_content(article_body, self.eat_requirements)
        
        # Combine metadata and content
        if "metadata" in pre_results:
            metadata = pre_results["metadata"]
            final_article = f"{metadata}\n\n{article_body}"
        else:
            final_article = article_body
        
        logger.info("✅ Article generation completed successfully!")
        return final_article
    
    def _assemble_final_article(self, pre_results, optimized_content):
        """Combine metadata and optimized content"""
        final_article = ""
        
        # Add metadata if available
        if "metadata" in pre_results:
            final_article += pre_results["metadata"] + "\n\n"
        
        # Add optimized content
        final_article += optimized_content
        
        return final_article
