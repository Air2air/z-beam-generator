import logging
import os
import sys
import random
from typing import Dict, Any, List, Optional

# Add parent directory to Python path to allow importing sibling packages
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
from api_client import APIClient

# Import refactored components
from content.utils.config_loader import ConfigLoader
from content.utils.retry_handler import RetryHandler
from content.formatters.data_formatter import DataFormatter
from content.prompts.section_prompts import SectionPromptBuilder
from content.prompts.context_builder import ContextBuilder
from content.randomizers.title_randomizer import TitleRandomizer
from content.randomizers.order_randomizer import OrderRandomizer
from content.randomizers.style_randomizer import StyleRandomizer

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates highly randomized content based on frontmatter data and configuration options."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.options = {}
        self.frontmatter = {}
        
        # Load templates and prompts
        self.prompt_template = ConfigLoader.load_prompt_template()
        self.section_prompts = ConfigLoader.load_section_prompts()
        
        logger.info(f"ContentGenerator initialized for {context['article_type']}: {context['subject']}")

    def set_frontmatter(self, frontmatter: Dict[str, Any]) -> 'ContentGenerator':
        """Set frontmatter data for content generation."""
        self.frontmatter = frontmatter or {}
        return self

    def set_options(self, options: Dict[str, Any]) -> 'ContentGenerator':
        """Set component-specific options from component_config.content."""
        self.options = options or {}
        return self
    
    def generate(self) -> str:
        """Generate highly randomized content based on schema and options from component_config.content."""
        article_type = self.context['article_type']
        subject = self.context['subject']
        
        # Get configuration exclusively from component_config.content
        min_words = self.options.get("min_words", 300)
        max_words = self.options.get("max_words", 1000)
        target_paragraphs = self.options.get("paragraphs", 5)
        use_dynamic_sections = self.options.get("use_dynamic_sections", False)
        randomize_sections = self.options.get("randomize_sections", False)
        max_attempts = self.options.get("max_attempts", 3)
        
        # Randomize the total word count if randomization is enabled
        if randomize_sections:
            # Apply variance to the overall content length
            variation_factor = random.uniform(0.8, 1.2)  # ±20% variation
            max_words = int(max_words * variation_factor)
            min_words = int(min_words * variation_factor)
            logger.info(f"Randomized content length target: {min_words}-{max_words} words")
            
            # Randomize paragraph count
            target_paragraphs = max(3, int(target_paragraphs * random.uniform(0.7, 1.3)))
            logger.info(f"Randomized paragraph count: ~{target_paragraphs}")
        
        # Determine sections to generate based on configuration
        sections_to_generate = self._determine_sections_to_generate(use_dynamic_sections, randomize_sections)
        
        # Randomly limit the number of sections if randomization is enabled
        if randomize_sections and len(sections_to_generate) > 3:
            # 40% chance to use fewer sections for more content variety
            if random.random() < 0.4:
                # Keep between 60-90% of sections
                keep_ratio = random.uniform(0.6, 0.9)
                num_to_keep = max(3, int(len(sections_to_generate) * keep_ratio))
                sections_to_generate = random.sample(sections_to_generate, num_to_keep)
                logger.info(f"Randomly limited to {num_to_keep} sections for content variety")
        
        if not sections_to_generate:
            logger.error("No valid sections to generate content for")
            return ""
            
        # Get section names for logging
        section_names = [section["title"] for section in sections_to_generate]
        logger.info(f"Generating content for sections: {', '.join(section_names)}")
        
        # Calculate words per section (base value before per-section randomization)
        words_per_section = max(50, int(max_words / len(sections_to_generate)))
        
        # Build section prompts text
        section_prompts_text = self._build_section_prompts(sections_to_generate, subject, words_per_section)
    
        # Format the main prompt with all sections
        frontmatter_context = ContextBuilder.extract_frontmatter_context(
            self.frontmatter, 
            article_type
        )
        
        # Randomly vary the main prompt format if randomization is enabled
        if randomize_sections:
            # 30% chance to change the voice/style of the content
            if random.random() < 0.3:
                writing_styles = [
                    "Write in a highly technical and detailed style with precise terminology",
                    "Use an educational tone that explains concepts clearly while maintaining technical accuracy",
                    "Write from an expert consultant perspective with actionable insights",
                    "Use a scientific style with emphasis on methodology and quantifiable results",
                    "Write with an engineering focus on practical implementation details"
                ]
                style_instruction = random.choice(writing_styles)
                frontmatter_context = f"{style_instruction}\n\n{frontmatter_context}"
        
        formatted_prompt = self.prompt_template.format(
            article_type=article_type,
            subject=subject,
            min_words=min_words,
            max_words=max_words,
            paragraphs=target_paragraphs,
            num_sections=len(sections_to_generate),
            sections=", ".join(section_names),
            section_prompts=section_prompts_text,
            frontmatter_context=frontmatter_context
        )
        
        # Generate content using AI provider with retry logic
        client = APIClient(self.ai_provider)
        
        # Create a lambda function that will be passed to the retry handler
        generate_func = lambda prompt, tokens: client.generate(prompt, tokens)
        
        content = RetryHandler.generate_with_retry(
            generate_func,
            formatted_prompt,
            min_words,
            max_words,
            max_attempts
        )
        
        # Debug logging to verify randomization
        try:
            with open("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/randomization_debug.log", "w") as f:
                f.write(f"Randomization enabled: {randomize_sections}\n")
                f.write(f"Final sections used: {[s['title'] for s in sections_to_generate]}\n")
                f.write(f"Section lengths: {[s.get('target_length', words_per_section) for s in sections_to_generate]}\n")
        except Exception as e:
            logger.error(f"Failed to write debug log: {e}")

        # Write the final prompt to a markdown file for debugging
        try:
            with open("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/final_prompt_debug.md", "w") as f:
                f.write(formatted_prompt)
        except Exception as e:
            logger.error(f"Failed to write final prompt debug file: {e}")
        
        return content
    
    def _determine_sections_to_generate(self, use_dynamic_sections: bool, randomize_sections: bool) -> List[Dict[str, Any]]:
        """Determine which sections to generate based on configuration and frontmatter."""
        if use_dynamic_sections:
            # Get sections from frontmatter
            sections_to_generate = self._detect_content_sections(randomize_sections)
            
            if sections_to_generate:
                return sections_to_generate
            
            logger.warning("No sections detected from frontmatter, falling back to default sections")
            
        # Use explicitly requested sections or fall back to all available sections
        requested_sections = self.options.get("sections", [])
        available_sections = list(self.section_prompts.keys())
        
        # If randomizing and no specific sections requested, consider using a random subset
        if randomize_sections and not requested_sections and len(available_sections) > 3:
            # 50% chance to use a subset of available sections
            if random.random() < 0.5:
                # Use between 60-90% of available sections
                num_sections = max(3, int(len(available_sections) * random.uniform(0.6, 0.9)))
                requested_sections = random.sample(available_sections, num_sections)
                logger.info(f"Randomly selected {num_sections} sections from available options")
        
        sections_to_generate = []
        
        if not requested_sections:
            # If no specific sections requested, use all available sections
            for section_name in available_sections:
                sections_to_generate.append({
                    "id": section_name,
                    "title": TitleRandomizer.get_title(section_name, randomize_sections),
                    "frontmatter_field": section_name
                })
        else:
            # Use only requested sections that exist
            for section_name in requested_sections:
                if section_name in available_sections:
                    sections_to_generate.append({
                        "id": section_name,
                        "title": TitleRandomizer.get_title(section_name, randomize_sections),
                        "frontmatter_field": section_name
                    })
                else:
                    logger.warning(f"Requested section '{section_name}' not found, skipping")
        
        # Apply aggressive randomization if requested
        if randomize_sections and sections_to_generate:
            # Set keep_overview_first to false 40% of the time for more randomization
            keep_overview_first = random.random() >= 0.4
            sections_to_generate = OrderRandomizer.randomize_sections(
                sections_to_generate, 
                keep_overview_first=keep_overview_first
            )
            
        return sections_to_generate
    
    def _detect_content_sections(self, randomize_order: bool = False) -> List[Dict[str, Any]]:
        """
        Detect which frontmatter fields can be used as content sections.
        """
        if not self.frontmatter:
            return []
            
        # Map frontmatter fields to section names
        section_mapping = {
            "description": "overview",
            "applications": "applications", 
            "technicalSpecifications": "technicalSpecifications",
            "facilities": "facilities",
            "regulatoryStandards": "regulations",
            "challenges": "challenges",
            "outcomes": "outcomes",
            "qualityStandards": "qualityStandards",
            "benefits": "benefits",
            "properties": "specifications"
        }
        
        # Find valid sections based on available frontmatter
        sections = []
        for field, section_id in section_mapping.items():
            if field in self.frontmatter and self.frontmatter[field]:
                sections.append({
                    "id": section_id,
                    "title": TitleRandomizer.get_title(section_id, randomize_order),
                    "frontmatter_field": field
                })
        
        # Randomize sections if requested
        if randomize_order and sections:
            # Set keep_overview_first to false 40% of the time for more randomization
            keep_overview_first = random.random() >= 0.4
            sections = OrderRandomizer.randomize_sections(sections, keep_overview_first=keep_overview_first)
            
        return sections
    
    def _build_section_prompts(self, sections: List[Dict], subject: str, words_per_section: int) -> str:
        """Build prompts for all sections with randomized section lengths."""
        section_prompts_text = ""
        randomize = self.options.get("randomize_sections", False)
        
        for section in sections:
            section_id = section["id"]
            frontmatter_field = section["frontmatter_field"]
            
            # Get data for this section
            if frontmatter_field in self.frontmatter:
                field_data = self.frontmatter[frontmatter_field]
                formatted_data = DataFormatter.format_section_data(frontmatter_field, field_data, randomize)
            else:
                # For sections without direct frontmatter data, use section prompt
                section_prompt = self.section_prompts.get(section_id, "")
                if not section_prompt:
                    logger.warning(f"No prompt found for section {section_id}")
                    continue
                    
                # Format with subject
                try:
                    formatted_data = section_prompt.format(subject=subject)
                except KeyError as e:
                    logger.warning(f"Missing format key for section '{section_id}': {e}")
                    formatted_data = section_prompt
            
            # Create prompt for this section
            prompt = SectionPromptBuilder.create_section_prompt(
                section, 
                subject, 
                formatted_data, 
                words_per_section,
                randomize
            )
            section_prompts_text += prompt + "\n\n"
            
        return section_prompts_text