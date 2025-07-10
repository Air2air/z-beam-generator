"""
Writing Samples Optimizer - Rewrites content to match author's writing style
"""
import logging
from typing import Dict, List
from .base_optimizer import BaseOptimizer

logger = logging.getLogger(__name__)

class WritingSamplesOptimizer(BaseOptimizer):
    """Optimizer that rewrites content to match specific author writing styles"""
    
    def __init__(self, config, api_client):
        """Initialize with config and API client"""
        super().__init__(config, api_client)
        
        # Validate writing samples exist for all authors
        self._validate_writing_samples()
        
        logger.info(f"📝 WritingSamplesOptimizer initialized with {len(self.authors)} authors")
    
    def optimize_sections(self, sections: List[Dict], material: str, metadata: Dict) -> List[Dict]:
        """Apply writing samples optimization to content"""
        logger.info(f"🎨 WRITING SAMPLES OPTIMIZATION STARTED for {material}")
        logger.info(f"📊 Input sections: {len(sections)}")
        logger.info(f"🔧 Optimization method: {self.config.get('optimization_method', 'writing_samples')}")
        
        # Validate input sections
        if not self._validate_sections(sections):
            raise ValueError("Invalid sections provided")
        
        # Get author_id from metadata
        author_id = metadata.get('authorId')
        if not author_id:
            logger.error("❌ No authorId found in metadata")
            raise ValueError("authorId is required in metadata")
        
        # Convert to int
        try:
            author_id = int(author_id)
        except (ValueError, TypeError):
            logger.error(f"❌ Invalid authorId format: {author_id}")
            raise ValueError(f"authorId must be a valid integer: {author_id}")
        
        logger.info(f"👤 Using author ID: {author_id}")
        
        # Load writing sample (inherited from BaseOptimizer)
        writing_sample = self._load_writing_sample(author_id)
        if not writing_sample:
            logger.error(f"❌ Could not load writing sample for author {author_id}")
            raise FileNotFoundError(f"Writing sample not found for author {author_id}")
        
        # Convert sections to internal format (inherited from BaseOptimizer)
        text_sections = self._convert_sections_to_internal(sections)
        self._log_section_details(text_sections, "Input")
        
        # Combine sections for optimization (inherited from BaseOptimizer)
        combined_content = self._combine_sections(text_sections)
        logger.info(f"📄 Combined content length: {len(combined_content)} chars")
        
        # Get author info for logging
        author = self.authors.get(author_id)
        author_name = author.get("name", f"Author {author_id}") if author else f"Author {author_id}"
        author_country = author.get("country", "Unknown") if author else "Unknown"
        writing_style = author.get("writing_sample_file", "Unknown") if author else "Unknown"
        
        logger.info(f"🎨 REWRITING CONTENT using {author_name}'s writing style")
        logger.info(f"🌍 Author country: {author_country}")
        logger.info(f"📝 Writing style file: {writing_style}")
        
        # Optimize the full content
        optimized_content = self._optimize_content_with_sample(combined_content, writing_sample)
        logger.info(f"📄 Optimized content length: {len(optimized_content)} chars")
        
        # Split back into sections (inherited from BaseOptimizer)
        optimized_sections = self._split_optimized_content(optimized_content, text_sections)
        self._log_section_details(optimized_sections, "Output")
        
        # Ensure word limits (inherited from BaseOptimizer)
        optimized_sections = self._ensure_word_limits(optimized_sections)
        
        # Convert to output format (inherited from BaseOptimizer)
        result = self._convert_sections_to_output(optimized_sections)
        
        logger.info("✅ WRITING SAMPLES OPTIMIZATION COMPLETED")
        logger.info(f"🔧 Optimization method used: {self.config.get('optimization_method', 'writing_samples')}")
        
        return result
    
    def _optimize_content_with_sample(self, content: str, writing_sample: str) -> str:
        """Optimize content using writing sample"""
        logger.info(f"🔄 Optimizing content: {len(content)} chars")
        
        # Create optimization prompt
        prompt = f"""Rewrite the following content to match the writing style of this sample:

WRITING STYLE SAMPLE:
{writing_sample}

CONTENT TO REWRITE:
{content}

Instructions:
- Maintain all technical accuracy and factual information
- Preserve the section structure and headers (## Section Title)
- Match the tone, vocabulary, and sentence structure of the sample
- Keep the same level of technical detail
- Ensure the content flows naturally
- Maintain approximately the same content length

Return only the rewritten content with proper markdown formatting."""
        
        # Call API to optimize content
        optimized_content = self.api_client.call(prompt, "writing-sample-optimization")
        
        logger.info(f"✅ Content optimized: {len(optimized_content)} chars")
        return optimized_content