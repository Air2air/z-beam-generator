#!/usr/bin/env python3
"""
Iterative Optimizer - Applies multiple optimization passes to content
"""
import difflib
import re
import json
from pathlib import Path
from typing import Dict, List, Any
from .base_optimizer import BaseOptimizer
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
        """Load optimization steps from iterative.json - NO FALLBACKS"""
        
        # Load from the JSON file
        json_path = Path("optimizers/iterative.json")
        
        if not json_path.exists():
            raise FileNotFoundError(f"❌ Required iterative steps file not found: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            steps_data = json.load(f)
        
        # Convert JSON structure to list of steps
        steps = []
        for key, step_config in steps_data.items():
            step = {
                "name": step_config.get("name", key),
                "description": step_config.get("description", ""),
                "order": step_config.get("order", 0),
                "prompt": step_config.get("prompt", ""),
                "type": step_config.get("type", "general")
            }
            steps.append(step)
        
        # Sort by order
        steps.sort(key=lambda x: x["order"])
        
        logger.info(f"✅ Loaded {len(steps)} optimization steps from iterative.json")
        for step in steps:
            logger.info(f"   📋 Step {step['order']}: {step['name']}")
        
        return steps
    
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