"""
Writing Samples Optimizer - Rewrites content to match author's writing style
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WritingSamplesOptimizer:
    """Optimizer that rewrites content to match specific author writing styles"""
    
    def __init__(self, config: Dict[str, Any], context: Dict[str, Any], api_client):
        self.config = config
        self.context = context
        self.api_client = api_client
        self.prompts_dir = Path(config["prompts_dir"])
        
        # Load authors data
        self.authors = self._load_authors()
        
        logger.info(f"📝 WritingSamplesOptimizer initialized for author_id: {context.get('author_id')}")
    
    def optimize_sections(self, text_sections, author_data):
        """Optimize text sections by rewriting to match author's style"""
        logger.info("🎨 WRITING SAMPLES OPTIMIZATION STARTED")
        logger.info(f"📊 Input sections: {len(text_sections)}")
        
        # Log input sections
        for i, section in enumerate(text_sections):
            logger.info(f"📄 Section {i+1}: {section.get('name', 'unnamed')} - {len(section.get('content', ''))} chars")
        
        author_id = self.context.get("author_id")
        
        if not author_id:
            logger.error("❌ No author_id provided in context")
            return text_sections
        
        # Load writing sample
        writing_sample = self._load_writing_sample(author_id)
        
        if not writing_sample:
            logger.error(f"❌ Could not load writing sample for author {author_id}")
            return text_sections
        
        # Get author info for logging
        author = self.authors.get(author_id)
        author_name = author.get("name", f"Author {author_id}") if author else f"Author {author_id}"
        
        logger.info(f"🎨 REWRITING CONTENT using {author_name}'s writing style")
        logger.info(f"📝 Writing sample length: {len(writing_sample)} chars")
        
        # Combine all sections into one article
        combined_content = self._combine_sections(text_sections)
        logger.info(f"📄 Combined content length: {len(combined_content)} chars")
        
        # Show sample of original content
        logger.info(f"📖 ORIGINAL CONTENT SAMPLE (first 200 chars):")
        logger.info(f"'{combined_content[:200]}...'")
        
        # Optimize the full content
        optimized_content = self.optimize_content(combined_content, writing_sample)
        logger.info(f"📄 Optimized content length: {len(optimized_content)} chars")
        
        # Show sample of optimized content
        logger.info(f"📖 OPTIMIZED CONTENT SAMPLE (first 200 chars):")
        logger.info(f"'{optimized_content[:200]}...'")
        
        # Calculate change percentage
        change_ratio = len(optimized_content) / len(combined_content) if combined_content else 0
        logger.info(f"📊 Content length change: {change_ratio:.2f}x")
        
        # Return as single optimized section
        result = [{
            'name': 'optimized_article',
            'title': 'Optimized Content',
            'content': optimized_content
        }]
        
        logger.info("✅ WRITING SAMPLES OPTIMIZATION COMPLETED")
        return result
    
    def optimize_content(self, content: str, writing_sample: str) -> str:
        """Optimize content by rewriting to match author's style"""
        logger.info("🔄 Starting API call for content optimization...")
        
        # Log original content details
        logger.info(f"📊 ORIGINAL CONTENT ANALYSIS:")
        logger.info(f"   Length: {len(content)} chars")
        logger.info(f"   Words: {len(content.split())} words")
        logger.info(f"   Sentences: {content.count('.')}")
        logger.info(f"   Paragraphs: {content.count('\\n\\n')}")
        
        # Show original content sample
        logger.info(f"📖 ORIGINAL CONTENT SAMPLE (first 300 chars):")
        logger.info(f"'{content[:300]}...'")
        
        # Create the optimization prompt
        prompt = self._create_optimization_prompt(content, writing_sample)
        
        # Log prompt details
        logger.info(f"📝 Prompt length: {len(prompt)} chars")
        logger.info(f"📝 OPTIMIZATION PROMPT SAMPLE (first 500 chars):")
        logger.info(f"'{prompt[:500]}...'")
        
        # Call API
        try:
            logger.info("🌐 Sending optimization request to API...")
            optimized_content = self.api_client.call(prompt, "writing_sample_optimization")
            
            if optimized_content:
                optimized_content = optimized_content.strip()
                
                # Log optimized content details
                logger.info(f"📊 OPTIMIZED CONTENT ANALYSIS:")
                logger.info(f"   Length: {len(optimized_content)} chars")
                logger.info(f"   Words: {len(optimized_content.split())} words")
                logger.info(f"   Sentences: {optimized_content.count('.')}")
                logger.info(f"   Paragraphs: {optimized_content.count('\\n\\n')}")
                
                # Show optimized content sample
                logger.info(f"📖 OPTIMIZED CONTENT SAMPLE (first 300 chars):")
                logger.info(f"'{optimized_content[:300]}...'")
                
                # Calculate and log differences
                length_change = len(optimized_content) - len(content)
                word_change = len(optimized_content.split()) - len(content.split())
                length_ratio = len(optimized_content) / len(content) if content else 0
                
                logger.info(f"📈 OPTIMIZATION DELTA:")
                logger.info(f"   Length change: {length_change:+d} chars ({length_ratio:.2f}x)")
                logger.info(f"   Word change: {word_change:+d} words")
                
                # Check for significant changes
                if abs(length_change) > 100:
                    logger.info(f"📊 SIGNIFICANT LENGTH CHANGE detected: {length_change:+d} chars")
                
                # Look for style indicators
                original_italics = content.count('*')
                optimized_italics = optimized_content.count('*')
                
                if original_italics != optimized_italics:
                    logger.info(f"🎨 STYLE CHANGES: Italics {original_italics} → {optimized_italics}")
                
                # Check for cultural expressions (example for Italian)
                cultural_indicators = ['mamma', 'madonna', 'perfetto', 'bene', 'che', 'la ', 'il ']
                original_cultural = sum(content.lower().count(word) for word in cultural_indicators)
                optimized_cultural = sum(optimized_content.lower().count(word) for word in cultural_indicators)
                
                if original_cultural != optimized_cultural:
                    logger.info(f"🌍 CULTURAL ELEMENTS: {original_cultural} → {optimized_cultural}")
                
                # Sample key phrases that changed
                original_lines = content.split('\\n')[:5]
                optimized_lines = optimized_content.split('\\n')[:5]
                
                logger.info(f"📝 STYLE TRANSFORMATION EXAMPLES:")
                for i, (orig, opt) in enumerate(zip(original_lines, optimized_lines)):
                    if orig.strip() != opt.strip():
                        logger.info(f"   Line {i+1}:")
                        logger.info(f"     BEFORE: {orig.strip()[:100]}...")
                        logger.info(f"     AFTER:  {opt.strip()[:100]}...")
                
                logger.info(f"✅ API optimization successful")
                return optimized_content
                
            else:
                logger.error("❌ API returned empty response")
                return content
                
        except Exception as e:
            logger.error(f"❌ Error during writing sample optimization: {e}")
            return content
    
    def _combine_sections(self, text_sections):
        """Combine sections into a single article"""
        logger.info("🔗 Combining sections into single article...")
        
        combined = []
        for section in text_sections:
            section_title = section.get('title', 'Untitled Section')
            section_content = section.get('content', '')
            
            logger.info(f"📄 Adding section: {section_title} ({len(section_content)} chars)")
            
            combined.append(f"## {section_title}")
            combined.append(section_content)
            combined.append("")  # Empty line between sections
        
        result = "\n".join(combined)
        logger.info(f"✅ Combined article: {len(result)} chars")
        return result
    
    def _load_authors(self) -> Dict[int, Dict[str, Any]]:
        """Load authors configuration"""
        authors_file = Path(self.config["authors_file"])
        logger.info(f"📚 Loading authors from: {authors_file}")
        
        if not authors_file.exists():
            logger.error(f"❌ Authors file not found: {authors_file}")
            return {}
        
        try:
            with open(authors_file, 'r', encoding='utf-8') as f:
                authors_list = json.load(f)
            
            # Convert to dict keyed by id
            authors_dict = {author["id"]: author for author in authors_list}
            logger.info(f"✅ Loaded {len(authors_dict)} authors")
            
            # Log available authors
            for author_id, author in authors_dict.items():
                logger.info(f"👤 Author {author_id}: {author.get('name', 'Unknown')}")
            
            return authors_dict
            
        except Exception as e:
            logger.error(f"❌ Error loading authors: {e}")
            return {}
    
    def _load_writing_sample(self, author_id: int) -> Optional[str]:
        """Load writing sample for specific author"""
        logger.info(f"📖 Loading writing sample for author_id: {author_id}")
        
        author = self.authors.get(author_id)
        
        if not author:
            logger.error(f"❌ Author not found: {author_id}")
            return None
        
        logger.info(f"👤 Found author: {author.get('name', 'Unknown')}")
        
        # Get writing sample file path
        writing_sample_file = author.get("writing_sample_file")
        if not writing_sample_file:
            logger.error(f"❌ No writing_sample_file specified for author {author_id}")
            logger.error(f"📋 Available keys: {list(author.keys())}")
            return None
        
        logger.info(f"📁 Writing sample file: {writing_sample_file}")
        
        # Load the writing sample - FIX: Don't double the path
        sample_path = Path(writing_sample_file)  # Use the full path from authors.json
        logger.info(f"📂 Full sample path: {sample_path}")
        
        if not sample_path.exists():
            logger.error(f"❌ Writing sample file not found: {sample_path}")
            return None
        
        try:
            with open(sample_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            logger.info(f"✅ Loaded writing sample: {len(content)} chars")
            logger.info(f"📖 WRITING SAMPLE PREVIEW (first 200 chars):")
            logger.info(f"'{content[:200]}...'")
            return content
            
        except Exception as e:
            logger.error(f"❌ Error loading writing sample: {e}")
            return None
    
    def _create_optimization_prompt(self, content: str, writing_sample: str) -> str:
        """Create the optimization prompt using external prompt file"""
        
        # Load the rewrite prompt template
        prompt_file = self.prompts_dir / "optimizations" / "writing_samples" / "rewrite_prompt.md"
        
        if prompt_file.exists():
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_template = f.read().strip()
                logger.info(f"✅ Loaded prompt template: {len(prompt_template)} chars")
            except Exception as e:
                logger.error(f"❌ Error loading prompt template: {e}")
                prompt_template = self._get_default_prompt()
        else:
            logger.warning(f"⚠️ Prompt file not found: {prompt_file}")
            prompt_template = self._get_default_prompt()
        
        # Combine template with content and writing sample
        full_prompt = f"""{prompt_template}

TARGET CONTENT TO REWRITE:
{content}

WRITING STYLE SAMPLE:
{writing_sample}

Now rewrite the target content in Mario's authentic Italian style, making it engaging and personal while keeping all technical information accurate."""
        
        return full_prompt

    def _get_default_prompt(self) -> str:
        """Fallback prompt if file not found"""
        return """You are Mario Jordan, a passionate Italian laser applications engineer. 
        Rewrite this technical content in your authentic voice - enthusiastic, personal, 
        with Italian expressions and cooking analogies. Make it engaging while keeping 
        all technical accuracy."""