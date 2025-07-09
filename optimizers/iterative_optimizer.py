#!/usr/bin/env python3
"""
Content Optimizer - Handles iterative and writing sample optimization
"""
import difflib
import re
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class IterativeOptimizer:
    """Optimizes text sections using iterative methods"""
    
    def __init__(self, config, api_client):
        self.config = config
        self.api_client = api_client
    
    def optimize_sections(self, sections, material, metadata):
        """Updated interface to match generator expectations"""
        logger.info(f"🔄 ITERATIVE OPTIMIZATION STARTED for {material}")
        logger.info(f"📊 Input sections: {len(sections)}")
        
        # Convert sections format for your existing method
        text_sections = []
        for section in sections:
            text_sections.append({
                'name': section.get('title', '').lower().replace(' ', '_'),
                'title': section.get('title', 'Untitled'),
                'content': section.get('content', '')
            })
        
        # Get author data from metadata (if needed)
        author_data = {
            'name': metadata.get('authorName', ''),
            'slug': metadata.get('authorSlug', ''),
            'id': metadata.get('authorId', '')
        }
        
        # Use your existing optimization logic
        optimized_result = self.optimize_sections_original(text_sections, author_data, material)
        
        # Convert back to expected format
        optimized_sections = []
        for section in optimized_result:
            optimized_sections.append({
                'title': section.get('title', 'Optimized Content'),
                'content': section.get('content', '')
            })
        
        logger.info(f"✅ ITERATIVE OPTIMIZATION COMPLETED - {len(optimized_sections)} sections")
        return optimized_sections
    
    def optimize_sections_original(self, text_sections, author_data, material=None):
        """Your existing optimize_sections method (renamed to avoid conflict)"""
        optimization_method = self.config["optimization_method"]
        logger.info(f"🔧 Starting optimization: {optimization_method}")
        
        if optimization_method == "iterative":
            return self._apply_iterative_optimization(text_sections, material)
        elif optimization_method == "writing_sample":
            return self._apply_writing_sample_optimization(text_sections, author_data)
        else:
            raise ValueError(f"Unknown optimization method: {optimization_method}")
    
    def _count_words(self, text):
        """Simple word count"""
        return len(text.split())
    
    def _calculate_text_similarity(self, text1, text2):
        """Calculate similarity between two texts (0-1 scale)"""
        # Remove extra whitespace and normalize
        text1_clean = re.sub(r'\s+', ' ', text1.strip())
        text2_clean = re.sub(r'\s+', ' ', text2.strip())
        
        # Calculate similarity using difflib
        similarity = difflib.SequenceMatcher(None, text1_clean, text2_clean).ratio()
        return similarity
    
    def _calculate_word_change_percentage(self, text1, text2):
        """Calculate percentage of words changed between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        total_words = len(words1.union(words2))
        if total_words == 0:
            return 0
        
        changed_words = len(words1.symmetric_difference(words2))
        return (changed_words / total_words) * 100

    def _apply_iterative_optimization(self, text_sections, material):
        """Apply iterative optimization steps to the full article"""
        logger.info("🔄 APPLYING ITERATIVE OPTIMIZATION")
        
        # Load iterative steps
        iterative_steps = self._load_iterative_config()
        logger.info(f"🔄 Found {len(iterative_steps)} optimization steps")
        
        # Combine all sections into one article
        full_article = self._combine_sections(text_sections)
        original_content = full_article
        original_word_count = self._count_words(full_article)
        logger.info(f"📊 Original total word count: {original_word_count}")
        
        # Apply each step sequentially to the full article
        content = full_article
        for step_idx, step in enumerate(iterative_steps, 1):
            logger.info(f"🔧 [{step_idx}/{len(iterative_steps)}] Step: {step['name']} (Full Article)")
            
            try:
                # Store content before this step
                content_before_step = content
                
                # Prepare all possible template variables from config
                template_vars = {
                    'material': material or self.config.get('default_material', 'titanium'),
                    'content': content,
                    'max_total_words': self.config.get('max_total_words'),
                    'target_words': self.config.get('target_section_words'),
                    'max_section_words': self.config.get('max_section_words')
                }
                
                # Format prompt with all variables
                prompt = step['prompt'].format(**template_vars)
                
                # Log the word limits being applied (from config)
                logger.info(f"📏 Word limits: target={template_vars['target_words']}, max={template_vars['max_section_words']}, total_max={template_vars['max_total_words']}")
                
                optimized_content = self.api_client.call(prompt, f"optimize-full-article-{step['name']}")
                
                # CALCULATE DELTA AFTER THIS STEP
                if self.config.get('debug_deltas', False):
                    similarity = self._calculate_text_similarity(content_before_step, optimized_content)
                    word_change_pct = self._calculate_word_change_percentage(content_before_step, optimized_content)
                    
                    logger.info(f"📊 STEP DELTA ANALYSIS:")
                    logger.info(f"   • Text similarity: {similarity:.3f} (1.0 = identical)")
                    logger.info(f"   • Word change: {word_change_pct:.1f}% of vocabulary")
                    logger.info(f"   • Word count: {self._count_words(content_before_step)} → {self._count_words(optimized_content)}")
                    
                    # Use configurable thresholds for similarity warnings
                    high_similarity_threshold = self.config.get('high_similarity_threshold', 0.95)
                    low_similarity_threshold = self.config.get('low_similarity_threshold', 0.7)
                    
                    if similarity > high_similarity_threshold:
                        logger.warning(f"⚠️  Very little change in step '{step['name']}' (similarity: {similarity:.3f})")
                    elif similarity < low_similarity_threshold:
                        logger.info(f"✅ Significant transformation in step '{step['name']}' (similarity: {similarity:.3f})")
            
                # Update content for next step
                content = optimized_content
                word_count = self._count_words(content)
                logger.info(f"✅ Step {step['name']} completed - {len(content)} chars, {word_count} words")
                
            except KeyError as e:
                logger.error(f"❌ Step {step['name']} failed - missing template variable: {e}")
                logger.error(f"❌ Available variables: {list(template_vars.keys())}")
                raise  # NO FALLBACK - fail fast
            except Exception as e:
                logger.error(f"❌ Step {step['name']} failed: {e}")
                raise  # NO FALLBACK - fail fast
        
        # FINAL DELTA ANALYSIS (original vs final)
        if self.config.get('debug_deltas', False):
            final_similarity = self._calculate_text_similarity(original_content, content)
            final_word_change = self._calculate_word_change_percentage(original_content, content)
            final_word_count = self._count_words(content)
            
            logger.info(f"📊 FINAL ARTICLE ANALYSIS:")
            logger.info(f"   • Overall similarity: {final_similarity:.3f}")
            logger.info(f"   • Overall word change: {final_word_change:.1f}%")
            logger.info(f"   • Word count change: {original_word_count} → {final_word_count}")
            logger.info(f"   • Target: {self.config.get('max_total_words')} words")
            
            # Use configurable threshold for final similarity check
            final_similarity_threshold = self.config.get('final_similarity_threshold', 0.85)
            
            if final_similarity > final_similarity_threshold:
                logger.warning(f"⚠️  Article may still appear AI-generated (similarity: {final_similarity:.3f})")
            else:
                logger.info(f"✅ Article significantly transformed (similarity: {final_similarity:.3f})")
        
        # NEW: Split optimized content back into sections for orchestrator
        logger.info("🔧 Splitting optimized full article back into sections")
        return self._split_optimized_content(content, text_sections)

    def _combine_sections(self, text_sections):
        """Combine sections into a single article"""
        combined = []
        for section in text_sections:
            combined.append(f"## {section['title']}")
            combined.append(section['content'])
            combined.append("")  # Empty line between sections
        return "\n".join(combined)

    def _split_optimized_content(self, optimized_content, original_sections):
        """Split optimized full article back into individual sections"""
        logger.info("🔧 Splitting optimized content back into sections")
        
        # Split by markdown headers (## Section Title)
        sections = re.split(r'\n## ', optimized_content)
        
        # Remove empty first element and add back header markers
        if sections and not sections[0].strip():
            sections = sections[1:]
        
        # Add back the ## markers (except for first section)
        for i in range(1, len(sections)):
            sections[i] = "## " + sections[i]
        
        logger.info(f"📊 Split into {len(sections)} sections from optimized content")
        
        # Match sections back to original structure
        optimized_sections = []
        
        for i, original_section in enumerate(original_sections):
            if i < len(sections):
                section_content = sections[i].strip()
                
                # Extract title and content
                lines = section_content.split('\n', 1)
                if len(lines) >= 2:
                    # Remove ## from title
                    title = lines[0].replace('##', '').strip()
                    content = lines[1].strip()
                else:
                    title = original_section['title']
                    content = section_content
                
                optimized_sections.append({
                    'name': original_section['name'],
                    'title': title,
                    'content': content
                })
                
                logger.info(f"✅ Section '{title}' extracted: {len(content)} chars")
            else:
                # Fallback if section missing
                logger.warning(f"⚠️ Section '{original_section['title']}' not found in optimized content, using original")
                optimized_sections.append(original_section)
        
        # Validate we have the right number of sections
        if len(optimized_sections) != len(original_sections):
            logger.warning(f"⚠️ Section count mismatch: expected {len(original_sections)}, got {len(optimized_sections)}")
        
        return optimized_sections

    def _load_iterative_config(self):
        """Load iterative optimization steps - FAIL FAST if missing"""
        iterative_file = Path(self.config["prompts_dir"]) / "optimizations" / "iterative.json"
        
        if not iterative_file.exists():
            raise FileNotFoundError(f"Iterative config not found: {iterative_file}")
        
        with open(iterative_file, 'r') as f:
            data = json.load(f)
        
        # Handle your specific structure - convert object to array sorted by order
        if isinstance(data, dict):
            steps = []
            for key, value in data.items():
                if isinstance(value, dict) and "prompt" in value:
                    step = {
                        "name": value.get("name", key),
                        "prompt": value["prompt"],
                        "order": value.get("order", 0)
                    }
                    steps.append(step)
            
            # Sort by order
            steps.sort(key=lambda x: x["order"])
            return steps
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Invalid iterative config structure in {iterative_file}")

    def _apply_writing_sample_optimization(self, text_sections, author_data):
        """Apply writing sample optimization (if needed)"""
        # Placeholder for writing sample optimization
        return text_sections