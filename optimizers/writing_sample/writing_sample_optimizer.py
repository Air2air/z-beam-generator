"""
Writing Sample Optimizer - Matches author writing style
"""
import logging
from typing import Dict, List, Any
from pathlib import Path

# Fix the import path - BaseOptimizer is one level up
from ..base_optimizer import BaseOptimizer

logger = logging.getLogger(__name__)

class WritingSampleOptimizer(BaseOptimizer):
    """Optimizer that rewrites content to match specific author writing styles"""
    
    def __init__(self, config, api_client):
        """Initialize with config and API client"""
        # Ensure parent class is properly initialized
        super().__init__(config, api_client)
        
        # Validate that authors were loaded properly
        if not hasattr(self, 'authors') or not self.authors:
            logger.error("❌ Authors not loaded in WritingSampleOptimizer")
            raise RuntimeError("Authors not loaded properly from BaseOptimizer")
        
        # Validate writing samples exist for all authors
        self._validate_writing_sample()
        
        logger.info(f"📝 WritingSampleOptimizer initialized with {len(self.authors)} authors")
    
    def _load_rewrite_prompt_template(self) -> str:
        """Load the rewrite prompt template from markdown file - NO FALLBACKS"""
        template_path = Path("optimizers/writing_sample/rewrite_prompt.md")
        
        if not template_path.exists():
            logger.error(f"❌ Required rewrite prompt template not found: {template_path}")
            raise FileNotFoundError(f"Required file missing: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read().strip()
                logger.info(f"✅ Loaded rewrite prompt template from {template_path}")
                return template
        except Exception as e:
            logger.error(f"❌ Error loading rewrite prompt template: {e}")
            raise RuntimeError(f"Failed to load rewrite prompt template: {e}")
    
    def optimize_sections(self, sections: List[Dict], context: Dict, config: Dict) -> List[Dict]:
        """Apply writing samples optimization to content sections - NO FALLBACKS"""
        logger.info(f"🎨 WRITING SAMPLES OPTIMIZATION STARTED for {context}")
        logger.info(f"📊 Input sections: {len(sections)}")
        
        # Get author ID from context - REQUIRED
        author_id = context.get('author_id')
        if not author_id:
            logger.error("❌ No author_id found in context")
            raise ValueError("author_id is required in context")
        
        logger.info(f"👤 Using author ID: {author_id}")
        
        # Get author info - REQUIRED
        author = self.get_author_by_id(author_id)
        if not author:
            logger.error(f"❌ Author not found for ID: {author_id}")
            raise ValueError(f"Author not found for ID: {author_id}")
        
        # Fix: Use 'country' instead of 'location'
        logger.info(f"✅ Found author: {author['name']} ({author['country']})")
        
        # Load writing samples - REQUIRED
        writing_sample = self._load_writing_sample(author_id)
        if not writing_sample:
            logger.error(f"❌ No writing samples found for author {author_id}")
            raise ValueError(f"No writing samples found for author {author_id}")
        
        logger.info(f"📚 Loaded {len(writing_sample)} writing samples")
        
        # Process each section
        optimized_sections = []
        
        for i, section in enumerate(sections):
            logger.info(f"🔄 Processing section {i+1}/{len(sections)}: {section['title']}")
            
            # Select writing samples for this section
            selected_samples = self._select_samples_for_section(writing_sample, section, config)
            
            # Generate optimization prompt - WILL FAIL IF TEMPLATE MISSING
            prompt = self._generate_writing_style_prompt(
                section, 
                selected_samples, 
                author, 
                context,
                config
            )
            
            # Apply writing style optimization
            optimized_content = self.api_client.call(
                prompt, 
                f"writing-samples-{section['title'].lower().replace(' ', '-')}"
            )
            
            # Create optimized section
            optimized_section = {
                'title': section['title'],
                'content': optimized_content,
                'order': section.get('order', i + 1)
            }
            
            optimized_sections.append(optimized_section)
            logger.info(f"✅ Optimized section '{section['title']}': {len(optimized_content)} chars")
        
        logger.info(f"✅ WRITING SAMPLES OPTIMIZATION COMPLETED")
        return optimized_sections
    
    def _optimize_content_with_sample(self, content: str, writing_sample: str, author_name: str) -> str:
        """Optimize content using writing sample with template - NO FALLBACKS"""
        logger.info(f"🔄 Optimizing content: {len(content)} chars")
        
        # Load the rewrite prompt template - WILL FAIL IF MISSING
        prompt_template = self._load_rewrite_prompt_template()
        
        # Replace the author name placeholder
        prompt_template = prompt_template.replace('{author_name}', author_name)
        
        # Build complete prompt
        prompt_parts = [
            prompt_template,
            "",
            "**WRITING SAMPLE**:",
            "",
            writing_sample.strip(),
            "",
            "**TARGET CONTENT TO REWRITE**:",
            "",
            content,
            "",
            "**REWRITTEN CONTENT**:"
        ]
        
        prompt = "\n".join(prompt_parts)
        
        # Call API to optimize content
        optimized_content = self.api_client.call(prompt, "writing-sample-optimization")
        
        logger.info(f"✅ Content optimized: {len(optimized_content)} chars")
        return optimized_content
    
    def _generate_writing_style_prompt(self, section: Dict, samples: List[str], author: Dict, context: Dict, config: Dict) -> str:
        """Generate prompt for writing style optimization using template - NO FALLBACKS"""
        
        # Load the rewrite prompt template - WILL FAIL IF MISSING
        prompt_template = self._load_rewrite_prompt_template()
        
        # Replace the author name placeholder
        prompt_template = prompt_template.replace('{author_name}', author['name'])
        
        # Validate we have writing samples
        if not samples:
            logger.error(f"❌ No writing samples provided for section '{section['title']}'")
            raise ValueError(f"No writing samples available for section '{section['title']}'")
        
        # Build the complete prompt - REMOVE TEMPLATE ARTIFACTS
        prompt_parts = [
            prompt_template,
            "",
            "**WRITING SAMPLE**:",
            "",
            samples[0].strip(),
            "",
            "**TARGET CONTENT TO REWRITE**:",
            "",
            section['content'],  # REMOVED: Section metadata lines
            "",
            "**INSTRUCTIONS**:",
            "- Rewrite in the author's exact style",
            "- Remove any template artifacts (Section:, Material: lines)",
            "- Start directly with the content",
            "- Maintain all technical information",
            "",
            "**REWRITTEN CONTENT**:"
        ]
        
        return "\n".join(prompt_parts)
    
    def _load_writing_sample(self, author_id: int) -> List[str]:
        """Load writing samples for specific author using writing_sample_file path"""
        
        # Get author info to find the writing sample file path
        author = self.get_author_by_id(author_id)
        if not author:
            raise ValueError(f"Author not found for ID: {author_id}")
        
        writing_sample_file = author.get('writing_sample_file')
        if not writing_sample_file:
            # Build the path manually if not specified
            nationality_map = {
                'Taiwan': 'taiwanese',
                'Italy': 'italian', 
                'United States': 'english',
                'Indonesia': 'indonesian'
            }
            
            nationality = author.get('nationality', author.get('country', ''))
            filename_suffix = nationality_map.get(nationality, nationality.lower())
            filename = f"style_{filename_suffix}.md"
            
            # Use the correct path - files are in writing_sample/ (singular)
            writing_sample_file = f"optimizers/writing_sample/{filename}"
        
        sample_path = Path(writing_sample_file)
        
        if not sample_path.exists():
            logger.error(f"❌ Writing sample file not found: {sample_path}")
            raise FileNotFoundError(f"Required writing sample file missing: {sample_path}")
        
        try:
            with open(sample_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                if not content:
                    logger.error(f"❌ Empty writing sample file: {sample_path}")
                    raise ValueError(f"Empty writing sample file: {sample_path}")
                
                # For markdown files, treat entire content as one sample
                # Could be enhanced to split on headers if needed
                samples = [content]
                
                logger.info(f"📚 Loaded writing sample from {sample_path} ({len(content)} chars)")
                return samples
        except Exception as e:
            logger.error(f"❌ Error loading writing sample from {sample_path}: {e}")
            raise RuntimeError(f"Failed to load writing sample: {e}")

    def _validate_writing_sample(self):
        """Validate that writing samples exist for all authors using writing_sample_file paths"""
        missing_authors = []
        
        for author in self.authors:
            author_id = author.get('id')
            author_name = author.get('name', 'Unknown')
            writing_sample_file = author.get('writing_sample_file')
            
            if not writing_sample_file:
                # If no writing_sample_file specified, build the path manually
                nationality_map = {
                    'Taiwan': 'taiwanese',
                    'Italy': 'italian', 
                    'United States': 'english',
                    'Indonesia': 'indonesian'
                }
                
                nationality = author.get('nationality', author.get('country', ''))
                filename_suffix = nationality_map.get(nationality, nationality.lower())
                filename = f"style_{filename_suffix}.md"
                
                # CORRECT PATH: Use writing_sample/ (singular) not writing_sample/ (plural)
                writing_sample_file = f"optimizers/writing_sample/{filename}"
            
            sample_path = Path(writing_sample_file)
            
            if not sample_path.exists():
                missing_authors.append(f"{author_name} (ID: {author_id}) - Missing: {writing_sample_file}")
            else:
                try:
                    with open(sample_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            missing_authors.append(f"{author_name} (ID: {author_id}) - Empty file: {writing_sample_file}")
                except Exception as e:
                    missing_authors.append(f"{author_name} (ID: {author_id}) - Error reading: {writing_sample_file} ({e})")
        
        if missing_authors:
            error_msg = f"Missing or invalid writing samples:\n" + "\n".join(f"  - {author}" for author in missing_authors)
            logger.error(f"❌ {error_msg}")
            raise FileNotFoundError(error_msg)
        
        logger.info(f"✅ Writing samples validated for all {len(self.authors)} authors")
    
    def _select_samples_for_section(self, writing_sample: List[str], section: Dict, config: Dict) -> List[str]:
        """Select appropriate writing samples for the current section"""
        # For now, return all samples. In the future, could implement smart selection
        # based on section type, content similarity, etc.
        max_samples = config.get('max_writing_sample', 1)  # Use 1 sample by default
        selected = writing_sample[:max_samples]
        logger.info(f"📋 Selected {len(selected)} samples for section '{section['title']}'")
        return selected

    # ADD the get_author_by_id method explicitly if inheritance is failing
    def get_author_by_id(self, author_id: int) -> Dict:
        """Get author information by ID"""
        if not hasattr(self, 'authors') or not self.authors:
            logger.error("❌ Authors not loaded")
            raise RuntimeError("Authors not available")
        
        for author in self.authors:
            if author.get('id') == author_id:
                logger.debug(f"✅ Found author: {author.get('name')} (ID: {author_id})")
                return author
        
        logger.warning(f"⚠️ Author not found for ID: {author_id}")
        return None
    
    def _get_writing_sample_path(self, author_id: int) -> Path:
        """Get the path to the writing sample file for an author"""
        author = self.authors.get(author_id)
        if not author:
            raise ValueError(f"Author ID {author_id} not found")
        
        # Map nationality to filename
        nationality_map = {
            'Taiwan': 'taiwanese',
            'Italy': 'italian', 
            'United States': 'english',
            'Indonesia': 'indonesian'
        }
        
        nationality = author['nationality']
        filename_suffix = nationality_map.get(nationality, nationality.lower())
        filename = f"style_{filename_suffix}.md"
        
        # Use the correct path - files are in the same directory as this optimizer
        return Path(__file__).parent / filename
    
    def optimize(self, content: str, metadata: Dict[str, Any]) -> str:
        """Apply author writing style (simplified)"""
        author_id = metadata.get("author_id", 1)
        
        # Simple style application
        style_prompt = f"""Rewrite this content in the writing style of author {author_id}.
        Keep it under 1200 words total, casual and human-like.
        Use contractions, personal observations, and natural flow.
        
        Content: {content}
        
        Return only the rewritten content."""
        
        return self.api_client.call(style_prompt, "style-application")