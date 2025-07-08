#!/usr/bin/env python3
"""
Content Generator - Main coordinator for content generation
"""

import logging
from .health_checker import APIHealthChecker
from .section_generator import SectionGenerator
from .sections_loader import SectionsLoader
from .article_composer import ArticleComposer
from modules.optimization.orchestrator import OptimizationOrchestrator

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Main coordinator for content generation with optimization pipeline"""
    
    def __init__(self, config):
        self.config = config
        
        # Initialize components
        self.health_checker = APIHealthChecker(config)
        self.section_generator = SectionGenerator(config)
        self.sections_loader = SectionsLoader(config)
        self.article_composer = ArticleComposer()
        
        # Initialize optimization orchestrator
        self.optimizer = OptimizationOrchestrator(config)
        
        # Load E-A-T requirements from optimization pipeline
        self.eat_requirements = self._load_eat_requirements()
        if self.eat_requirements:
            logger.info(f"📋 Loaded E-A-T requirements for generation enhancement")
        else:
            logger.info(f"📋 No E-A-T requirements found - using standard generation")
    
    def _load_eat_requirements(self):
        """Load E-A-T requirements from optimization pipeline"""
        try:
            # Reuse pipeline manager to avoid duplication
            from modules.optimization.pipeline_manager import OptimizationPipelineManager
            pipeline_manager = OptimizationPipelineManager(self.config)
            steps = pipeline_manager.load_optimization_pipeline()
            
            # Find step with requirements
            for step in steps:
                config = step['config']
                if 'requirements' in config:
                    logger.info(f"📋 Found E-A-T requirements in step: {config.get('name', step['key'])}")
                    return config.get('requirements', '')
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load E-A-T requirements: {e}")
            return None
    
    def generate_article(self, material):
        """Generate complete article for specified material"""
        logger.info(f"🚀 Starting article generation for material: {material}")
        
        # Load sections configuration
        sections = self.sections_loader.load_sections()
        material_sections = self.sections_loader.get_material_sections(sections, material)
        
        # Health check API before generation
        self.health_checker.check_api_health()
        
        # Generate each section
        generated_sections = []
        
        for section in material_sections:
            section_name = section['name']
            section_title = section['title']
            section_type = section.get('section_type', 'TEXT')
            
            logger.info(f"🔧 Generating section: {section_name} ({section_title})")
            
            # Generate base content
            if self.eat_requirements:
                content = self.section_generator.generate_section_with_enhancement(
                    section, material, self.eat_requirements
                )
            else:
                content = self.section_generator.generate_section_standard(section, material)
            
            if not content or not content.strip():
                raise RuntimeError(f"Failed to generate content for section: {section_name}")
            
            logger.info(f"✅ Generated {len(content.split())} words for: {section_name}")
            
            # Apply optimization pipeline if enabled
            if section.get('ai_detect', True):
                try:
                    optimized_content = self.optimizer.optimize_section(
                        content=content,
                        section_name=section_name,
                        section_type=section_title,
                        material=material
                    )
                    content = optimized_content
                except Exception as e:
                    raise RuntimeError(f"Optimization failed for section {section_name}: {e}")
            
            # Format section
            formatted_section = self.article_composer.format_section(
                section_name, section_title, content, section_type
            )
            generated_sections.append(formatted_section)
        
        # Combine all sections
        article = self.article_composer.combine_sections(generated_sections, material)
        
        logger.info(f"🎉 Article generation complete for {material}")
        logger.info(f"📊 Total article length: {len(article.split())} words")
        
        return article
