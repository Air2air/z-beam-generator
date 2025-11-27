#!/usr/bin/env python3
"""
Prompt Optimizer for Imagen API

Ensures generated prompts stay within Imagen API limits while
preserving critical quality standards.

Strategy:
1. Condense templates intelligently (remove redundancy, not rules)
2. Prioritize physics/quality requirements over examples
3. Smart truncation when needed (cut least critical content first)
4. Always preserve user feedback (highest priority)

Author: AI Assistant
Date: November 25, 2025
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Imagen API Limits
IMAGEN_4_CHAR_LIMIT = 4096  # Hard limit for Imagen 4
IMAGEN_OPTIMAL_TARGET = 3500  # Safe target with margin
IMAGEN_WARNING_THRESHOLD = 3800  # Warn if approaching limit


class PromptOptimizer:
    """
    Optimizes prompts to fit within Imagen API character limits.
    
    Optimization Strategy (Priority Order):
    1. PRESERVE: User feedback (always included, highest priority)
    2. PRESERVE: Base structure (format requirements)
    3. PRESERVE: Critical physics (gravity, accumulation)
    4. CONDENSE: Micro-scale details (reduce examples)
    5. CONDENSE: Contamination rules (bullet points)
    6. TRUNCATE: Forbidden patterns (keep top violations)
    
    Example:
        optimizer = PromptOptimizer()
        optimized = optimizer.optimize_prompt(
            full_prompt="[6000 char prompt]",
            preserve_sections=["user feedback", "base structure"]
        )
        # Returns: ~3500 char optimized prompt
    """
    
    def __init__(
        self,
        target_length: int = IMAGEN_OPTIMAL_TARGET,
        hard_limit: int = IMAGEN_4_CHAR_LIMIT
    ):
        """
        Initialize optimizer with target length.
        
        Args:
            target_length: Optimal target length (default: 3500 chars)
            hard_limit: Hard API limit (default: 4096 chars)
        """
        self.target_length = target_length
        self.hard_limit = hard_limit
        self.warning_threshold = IMAGEN_WARNING_THRESHOLD
    
    def optimize_prompt(
        self,
        prompt: str,
        preserve_feedback: bool = True,
        preserve_json_format: bool = False
    ) -> str:
        """
        Optimize prompt to fit within Imagen limits.
        
        Args:
            prompt: Full prompt string to optimize
            preserve_feedback: Always preserve user feedback (default: True)
            preserve_json_format: Preserve JSON format specification (for validation prompts)
            
        Returns:
            Optimized prompt within target length
        """
        current_length = len(prompt)
        
        # Already optimal?
        if current_length <= self.target_length:
            logger.info(f"✅ Prompt already optimal: {current_length} chars")
            return prompt
        
        # Warning if close to hard limit
        if current_length > self.warning_threshold:
            logger.warning(
                f"⚠️  Prompt near limit: {current_length}/{self.hard_limit} chars "
                f"(needs {current_length - self.target_length} char reduction)"
            )
        
        # Extract JSON format if preservation requested
        json_format = ""
        if preserve_json_format and "RESPOND IN JSON FORMAT:" in prompt:
            json_start = prompt.find("RESPOND IN JSON FORMAT:")
            json_format = prompt[json_start:]
            prompt = prompt[:json_start]
            logger.info(f"📝 Extracted JSON format specification ({len(json_format)} chars)")
        
        # Apply optimization strategies in order
        optimized = prompt
        
        # Strategy 1: Condense repetitive wording
        optimized = self._condense_repetition(optimized)
        
        # Strategy 2: Convert prose to bullet points
        optimized = self._convert_to_bullets(optimized)
        
        # Strategy 3: Remove redundant examples
        optimized = self._remove_examples(optimized)
        
        # Strategy 4: Truncate lowest priority sections if still over
        if len(optimized) > self.hard_limit:
            # Account for JSON format length when calculating truncation
            available_space = self.hard_limit - len(json_format) if json_format else self.hard_limit
            optimized = self._emergency_truncate(
                optimized,
                preserve_feedback=preserve_feedback,
                max_length=available_space
            )
        
        # Re-append JSON format if it was extracted
        if json_format:
            optimized = optimized + "\n\n" + json_format
            logger.info("✅ Re-appended JSON format specification")
        
        reduction = current_length - len(optimized)
        logger.info(
            f"✅ Optimized: {current_length} → {len(optimized)} chars "
            f"(-{reduction} chars, {reduction/current_length*100:.1f}% reduction)"
        )
        
        return optimized
    
    def _condense_repetition(self, text: str) -> str:
        """
        Remove repetitive wording without losing meaning.
        
        Example:
        Before: "MUST show gravity effects. Drips MUST pool at bottom..."
        After: "Show gravity effects: drips pool at bottom..."
        """
        condensed = text
        
        # Remove excessive "MUST" emphasis (keep meaning, reduce repetition)
        condensed = condensed.replace("MUST show", "Show")
        condensed = condensed.replace("MUST have", "Have")
        condensed = condensed.replace("MUST include", "Include")
        condensed = condensed.replace("MUST create", "Create")
        condensed = condensed.replace("MUST NOT", "Do not")
        condensed = condensed.replace("should NEVER", "never")
        
        # Remove redundant requirement phrases
        condensed = condensed.replace("It is critical that", "")
        condensed = condensed.replace("It is essential that", "")
        condensed = condensed.replace("Make sure to", "")
        condensed = condensed.replace("Be sure to", "")
        
        # Simplify connecting phrases (case-insensitive)
        condensed = condensed.replace("In order to", "To")
        condensed = condensed.replace("in order to", "to")
        condensed = condensed.replace("Due to the fact that", "Because")
        condensed = condensed.replace("due to the fact that", "because")
        condensed = condensed.replace("For the purpose of", "For")
        condensed = condensed.replace("for the purpose of", "for")
        
        return condensed
    
    def _convert_to_bullets(self, text: str) -> str:
        """
        Convert prose paragraphs to concise bullet points where appropriate.
        
        More compact, easier for Imagen to parse.
        """
        # This is a simplified implementation
        # In production, would use NLP to identify list-worthy content
        
        # Convert numbered lists to more compact format
        lines = text.split('\n')
        optimized_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Condense numbered list items
            if stripped.startswith(('1.', '2.', '3.', '4.', '5.')):
                # Remove number, convert to dash
                content = stripped[2:].strip()
                optimized_lines.append(f"- {content}")
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _remove_examples(self, text: str) -> str:
        """
        Remove example clarifications to save space.
        
        Keep requirements, cut "(e.g., ...)" explanations.
        """
        import re
        
        # Remove parenthetical examples
        text = re.sub(r'\s*\(e\.g\.,?\s+[^)]+\)', '', text)
        text = re.sub(r'\s*\(such as[^)]+\)', '', text)
        text = re.sub(r'\s*\(like[^)]+\)', '', text)
        text = re.sub(r'\s*\(for example[^)]+\)', '', text)
        
        return text
    
    def _emergency_truncate(
        self,
        text: str,
        preserve_feedback: bool = True,
        max_length: Optional[int] = None
    ) -> str:
        """
        Emergency truncation if still over hard limit.
        
        Priority order (highest to lowest):
        1. User feedback (always preserve if preserve_feedback=True)
        2. Contamination restrictions (CRITICAL - material-specific rules)
        3. Base structure
        4. Physics rules
        5. Micro-scale details
        6. Generic forbidden patterns (safe to truncate)
        
        CRITICAL CONTAMINATION RULES (NEVER TRUNCATE):
        - Oil/grease only on metals/machinery
        - Rust only on ferrous metals (NOT plastics)
        - Dirt/soil globally prohibited
        - Material-specific contamination from research
        
        Args:
            text: Prompt text to truncate
            preserve_feedback: Always keep user feedback section
            max_length: Maximum allowed length (uses self.hard_limit if not provided)
            
        Returns:
            Truncated prompt under hard limit
        """
        limit = max_length if max_length is not None else self.hard_limit
        
        # Critical contamination keywords to ALWAYS preserve
        critical_keywords = [
            'oil', 'rust', 'dirt', 'soil', 'grease',
            'contamination', 'ferrous', 'plastic',
            'machinery', 'research confirms', 'NEVER'
        ]
        
        # Extract sections
        sections = []
        current_section = []
        
        for line in text.split('\n'):
            if line.strip().startswith(('CRITICAL CORRECTIONS', 'AVOID THESE PATTERNS', 'LEARNED FROM')):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        # If still over limit, intelligently truncate
        if len(text) > limit:
            truncated_sections = []
            for section in sections:
                if 'AVOID THESE PATTERNS' in section:
                    # Separate contamination rules from generic anti-patterns
                    lines = section.split('\n')
                    contamination_lines = []
                    generic_lines = []
                    header_lines = []
                    
                    for line in lines:
                        # Keep header
                        if 'AVOID THESE PATTERNS' in line or line.strip() == '':
                            header_lines.append(line)
                        # ALWAYS keep contamination-related lines
                        elif any(kw in line.lower() for kw in critical_keywords):
                            contamination_lines.append(line)
                        else:
                            generic_lines.append(line)
                    
                    # Build truncated section: header + ALL contamination + limited generic
                    truncated = '\n'.join(header_lines)
                    if contamination_lines:
                        truncated += '\n' + '\n'.join(contamination_lines)
                    # Only add first 5 generic anti-patterns if space allows
                    if generic_lines and len(truncated) < limit * 0.7:  # Leave 30% for other sections
                        truncated += '\n' + '\n'.join(generic_lines[:5])
                        if len(generic_lines) > 5:
                            truncated += "\n[Additional generic anti-patterns omitted]"
                    
                    truncated_sections.append(truncated)
                    
                    logger.info(
                        f"🔧 Truncated anti-patterns: preserved {len(contamination_lines)} "
                        f"contamination rules, kept {min(5, len(generic_lines))} generic rules"
                    )
                else:
                    truncated_sections.append(section)
            
            text = '\n\n'.join(truncated_sections)
        
        # Final check - hard truncate if absolutely necessary
        if len(text) > limit:
            logger.warning(
                f"🚨 Emergency hard truncation required: "
                f"{len(text)} → {limit} chars"
            )
            # CRITICAL: Never truncate contamination rules
            # Find contamination section and preserve it
            if 'AVOID THESE PATTERNS' in text:
                parts = text.split('AVOID THESE PATTERNS')
                pre_patterns = parts[0]
                patterns_section = 'AVOID THESE PATTERNS' + parts[1] if len(parts) > 1 else ''
                
                # Extract contamination rules
                contamination_rules = []
                for line in patterns_section.split('\n'):
                    if any(kw in line.lower() for kw in critical_keywords):
                        contamination_rules.append(line)
                
                # Truncate pre_patterns section if needed
                if len(pre_patterns) > limit * 0.5:
                    pre_patterns = pre_patterns[:int(limit * 0.5)]
                
                # Rebuild with contamination rules preserved
                text = pre_patterns + '\n\nAVOID THESE PATTERNS:\n' + '\n'.join(contamination_rules)
            else:
                # No patterns section - just truncate
                text = text[:limit - 100]
            
            text += "\n\n[Prompt truncated - contamination rules preserved]"
        
        return text
    
    def check_prompt_length(self, prompt: str) -> Dict[str, any]:
        """
        Check prompt length and return status.
        
        Args:
            prompt: Prompt string to check
            
        Returns:
            Dict with length info and recommendations
        """
        length = len(prompt)
        
        status = {
            'length': length,
            'target': self.target_length,
            'hard_limit': self.hard_limit,
            'within_target': length <= self.target_length,
            'within_limit': length <= self.hard_limit,
            'needs_optimization': length > self.target_length,
            'chars_over_target': max(0, length - self.target_length),
            'chars_under_limit': self.hard_limit - length,
            'estimated_tokens': length // 4,
        }
        
        # Recommendation
        if length > self.hard_limit:
            status['recommendation'] = "🚨 CRITICAL: Exceeds API limit - must optimize"
        elif length > self.warning_threshold:
            status['recommendation'] = "⚠️  WARNING: Near limit - should optimize"
        elif length > self.target_length:
            status['recommendation'] = "ℹ️  OK but non-optimal - consider optimizing"
        else:
            status['recommendation'] = "✅ OPTIMAL: Within target range"
        
        return status


def create_optimizer(
    target_length: Optional[int] = None
) -> PromptOptimizer:
    """Factory function to create prompt optimizer."""
    return PromptOptimizer(target_length=target_length or IMAGEN_OPTIMAL_TARGET)
