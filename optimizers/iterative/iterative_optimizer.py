#!/usr/bin/env python3
"""
Iterative Optimizer - Applies multiple iterative improvements
"""
import difflib
import re
import json
from pathlib import Path
from typing import Dict, List, Any
from ..base_optimizer import BaseOptimizer
import logging

logger = logging.getLogger(__name__)

class IterativeOptimizer(BaseOptimizer):
    """Iterative content optimizer using JSON-defined steps"""
    
    def __init__(self, config: Dict[str, Any], api_client):
        """Initialize iterative optimizer"""
        super().__init__(config, api_client)
        
        # Load optimization steps from JSON - NO FALLBACKS
        self.optimization_steps = self._load_optimization_steps()
        
        logger.info(f"🔧 IterativeOptimizer initialized with {len(self.optimization_steps)} steps")
    
    def _load_optimization_steps(self) -> List[Dict]:
        """Load optimization steps from JSON file"""
        # Fix the path - look for iterative.json in the same folder as this optimizer
        json_path = Path(__file__).parent / "iterative.json"  # ← Fixed path
        
        if not json_path.exists():
            raise FileNotFoundError(f"❌ Required iterative steps file not found: {json_path}")
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            steps = data.get("optimization_steps", [])
            if not steps:
                raise ValueError("❌ No optimization steps found in iterative.json")
            
            logger.info(f"📚 Loaded {len(steps)} optimization steps")
            return steps
            
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Invalid JSON in iterative steps file: {e}")
        except Exception as e:
            raise RuntimeError(f"❌ Failed to load iterative steps: {e}")
    
    def optimize_sections(self, sections: List[Dict], context: Dict, config: Dict) -> List[Dict]:
        """Apply iterative optimization to content sections"""
        logger.info(f"🎯 ITERATIVE OPTIMIZATION STARTED for {context.get('material', 'unknown')}")
        logger.info(f"📊 Input sections: {len(sections)}")
        logger.info(f"🔧 Optimization steps: {len(self.optimization_steps)}")
        
        # Combine all sections into single content for iterative processing
        combined_content = self._combine_sections(sections)
        logger.info(f"📄 Combined content length: {len(combined_content)} chars")
        
        # Apply each optimization step
        optimized_content = combined_content
        
        for i, step in enumerate(self.optimization_steps):
            logger.info(f"🔄 Applying step {i+1}/{len(self.optimization_steps)}: {step['name']}")
            
            # Format the prompt with current content and context
            formatted_prompt = self._format_prompt(step["prompt"], optimized_content, context, config)
            
            # Apply optimization step - NO ERROR HANDLING FALLBACK
            optimized_content = self.api_client.call(
                formatted_prompt, 
                f"iterative-step-{i+1}-{step['name'].lower().replace(' ', '-')}"
            )
            logger.info(f"✅ Step {i+1} completed: {len(optimized_content)} chars")
        
        # Split optimized content back into sections
        optimized_sections = self._split_content_into_sections(optimized_content, sections)
        
        # REMOVED: No word limits applied here - let optimization determine final length
        # final_sections = self._apply_word_limits(optimized_sections, config)
        
        logger.info(f"✅ ITERATIVE OPTIMIZATION COMPLETED")
        return optimized_sections
    
    def _format_prompt(self, prompt_template: str, content: str, context: Dict, config: Dict) -> str:
        """Format prompt template with variables"""
        return prompt_template.format(
            content=content,
            material=context.get('material', 'unknown'),
            target_words=config.get('target_section_words', 120),
            max_total_words=config.get('max_total_words', 1200)
        )
    
    def _combine_sections(self, sections: List[Dict]) -> str:
        """Combine sections into single content block"""
        combined_parts = []
        
        for section in sections:
            combined_parts.append(f"## {section['title']}")
            combined_parts.append(section['content'])
            combined_parts.append("")  # Empty line between sections
        
        return "\n".join(combined_parts)
    
    def _split_content_into_sections(self, content: str, original_sections: List[Dict]) -> List[Dict]:
        """Split optimized content back into sections with robust fallback"""
        logger.info(f"🔧 Splitting optimized content back into sections")
        
        # Method 1: Try to find section headers (## format)
        sections = self._try_split_by_headers(content)
        
        if sections:
            logger.info(f"✅ Split by headers into {len(sections)} sections")
            return sections
        
        # Method 2: Try to find section titles without ## prefix
        sections = self._try_split_by_titles(content, original_sections)
        
        if sections:
            logger.info(f"✅ Split by titles into {len(sections)} sections")
            return sections
        
        # Method 3: Split content evenly based on original section count
        sections = self._split_content_evenly(content, original_sections)
        
        logger.info(f"✅ Split evenly into {len(sections)} sections")
        return sections

    def _try_split_by_headers(self, content: str) -> List[Dict]:
        """Try to split content by ## headers"""
        lines = content.split('\n')
        current_section = None
        current_content = []
        sections = []
        
        for line in lines:
            if line.startswith('## '):
                # Save previous section
                if current_section and current_content:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'order': len(sections) + 1
                    })
                
                # Start new section
                current_section = line[3:].strip()  # Remove '## '
                current_content = []
            elif current_section:
                # Add to current section content
                if line.strip():  # Skip empty lines
                    current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip(),
                'order': len(sections) + 1
            })
        
        return sections if len(sections) > 0 else []

    def _try_split_by_titles(self, content: str, original_sections: List[Dict]) -> List[Dict]:
        """Try to split content by finding original section titles"""
        # Remove the redundant import here since re is already imported at module level
    
        # Get original section titles
        original_titles = [section['title'] for section in original_sections]
        
        # Try to find these titles in the content (case insensitive)
        sections = []
        content_lower = content.lower()
        
        for i, title in enumerate(original_titles):
            title_lower = title.lower()
            
            # Look for the title in various formats
            patterns = [
                rf'\b{re.escape(title_lower)}\b',
                rf'^{re.escape(title_lower)}',
                rf'{re.escape(title_lower)}:',
                rf'#{1,3}\s*{re.escape(title_lower)}'
            ]
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, content_lower, re.MULTILINE))
                if matches:
                    # Found the title, extract content
                    start_pos = matches[0].start()
                    
                    # Find end position (next section or end of content)
                    end_pos = len(content)
                    if i + 1 < len(original_titles):
                        next_title = original_titles[i + 1].lower()
                        for next_pattern in patterns:
                            next_pattern_formatted = next_pattern.replace(re.escape(title_lower), re.escape(next_title))
                            next_matches = list(re.finditer(next_pattern_formatted, content_lower, re.MULTILINE))
                            if next_matches:
                                end_pos = next_matches[0].start()
                                break
                
                    # Extract content
                    section_content = content[start_pos:end_pos].strip()
                    
                    # Clean up the content (remove title line)
                    lines = section_content.split('\n')
                    if lines:
                        # Remove first line if it contains the title
                        if title_lower in lines[0].lower():
                            lines = lines[1:]
                
                    clean_content = '\n'.join(lines).strip()
                    
                    if clean_content:
                        sections.append({
                            'title': title,
                            'content': clean_content,
                            'order': i + 1
                        })
                    break
        
        return sections if len(sections) == len(original_titles) else []

    def _split_content_evenly(self, content: str, original_sections: List[Dict]) -> List[Dict]:
        """Split content evenly based on original section count"""
        logger.info(f"🔄 Splitting content evenly into {len(original_sections)} sections")
        
        # Remove any remaining headers or formatting
        clean_content = re.sub(r'^#+\s*.*$', '', content, flags=re.MULTILINE)
        clean_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', clean_content)  # Remove excessive newlines
        clean_content = clean_content.strip()
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # If no paragraphs, split by sentences
            sentences = re.split(r'(?<=[.!?])\s+', clean_content)
            paragraphs = [s.strip() for s in sentences if s.strip()]
        
        # Distribute paragraphs evenly across sections
        sections = []
        paragraphs_per_section = max(1, len(paragraphs) // len(original_sections))
        
        for i, original_section in enumerate(original_sections):
            start_idx = i * paragraphs_per_section
            end_idx = start_idx + paragraphs_per_section
            
            # For the last section, include any remaining paragraphs
            if i == len(original_sections) - 1:
                end_idx = len(paragraphs)
            
            section_paragraphs = paragraphs[start_idx:end_idx]
            section_content = '\n\n'.join(section_paragraphs)
            
            if section_content:
                sections.append({
                    'title': original_section['title'],
                    'content': section_content,
                    'order': i + 1
                })
            else:
                # Fallback: use a portion of the entire content
                total_chars = len(clean_content)
                chars_per_section = total_chars // len(original_sections)
                start_char = i * chars_per_section
                end_char = start_char + chars_per_section
                
                if i == len(original_sections) - 1:
                    end_char = total_chars
                
                fallback_content = clean_content[start_char:end_char].strip()
                
                sections.append({
                    'title': original_section['title'],
                    'content': fallback_content,
                    'order': i + 1
                })
        
        return sections

    def _split_into_sections(self, content: str, target_sections: int) -> List[Dict]:
        """Split content into exactly target_sections - NO EXTRA SECTIONS"""
    
        # Use the configured required sections
        from config.constants import CONFIG
        required_sections = CONFIG.generation["required_sections"]
    
        if len(required_sections) != target_sections:
            logger.warning(f"⚠️ Required sections ({len(required_sections)}) != target ({target_sections})")
    
        # Force exact section count
        sections = []
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
        if len(paragraphs) < target_sections:
            logger.error(f"❌ Not enough content paragraphs ({len(paragraphs)}) for {target_sections} sections")
            raise ValueError(f"Insufficient content for {target_sections} sections")
    
        # Distribute paragraphs evenly across required sections
        paragraphs_per_section = len(paragraphs) // target_sections
        extra_paragraphs = len(paragraphs) % target_sections
    
        para_idx = 0
        for i, section_title in enumerate(required_sections[:target_sections]):
            # Calculate paragraphs for this section
            section_para_count = paragraphs_per_section + (1 if i < extra_paragraphs else 0)
            
            # Get paragraphs for this section
            section_paragraphs = paragraphs[para_idx:para_idx + section_para_count]
            para_idx += section_para_count
            
            sections.append({
                'title': section_title,
                'content': '\n\n'.join(section_paragraphs),
                'order': i + 1
            })
    
        logger.info(f"✅ Split content into exactly {len(sections)} sections as required")
        return sections

    def _enforce_word_limits(self, content: str, config: Dict) -> str:
        """Enforce word limits on content"""
        max_total = config.get("max_total_words", 1200)
        max_section = config.get("max_section_words", 250)
        
        # Count total words
        total_words = len(content.split())
        if total_words > max_total:
            logger.warning(f"⚠️ Content exceeds limit: {total_words}/{max_total} words")
            
            # Add word limit enforcement prompt
            trim_prompt = f"""Trim this content to under {max_total} words total, with each section under {max_section} words. Keep the most important technical information.

CONTENT TO TRIM:
{content}

Requirements:
- Total: under {max_total} words
- Each section: under {max_section} words  
- Keep technical accuracy
- Maintain section headers

Return ONLY the trimmed content."""
            
            trimmed_content = self.api_client.call(trim_prompt, "word-limit-enforcement")
            logger.info(f"✅ Content trimmed: {len(trimmed_content.split())} words")
            return trimmed_content
        
        return content