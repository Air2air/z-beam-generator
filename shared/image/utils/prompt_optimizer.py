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
IMAGEN_OPTIMAL_TARGET = 2400  # Aggressive target - leaves room for corrections
IMAGEN_WARNING_THRESHOLD = 3000  # Warn earlier


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
        
        # Strategy 4: Aggressive section trimming if still over target
        if len(optimized) > self.target_length:
            optimized = self._aggressive_trim(optimized)
        
        # Strategy 5: Section pruning if still significantly over target (but under hard limit)
        # This removes lower-priority sections to get closer to target
        if len(optimized) > self.target_length * 1.3:  # More than 30% over target
            optimized = self._prune_sections(optimized)
        
        # Strategy 6: Truncate lowest priority sections if still over hard limit
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
        condensed = condensed.replace("CRITICAL: ", "")  # Keep content, remove label
        condensed = condensed.replace("MANDATORY: ", "")
        condensed = condensed.replace("IMPORTANT: ", "")
        
        # Simplify connecting phrases (case-insensitive)
        condensed = condensed.replace("In order to", "To")
        condensed = condensed.replace("in order to", "to")
        condensed = condensed.replace("Due to the fact that", "Because")
        condensed = condensed.replace("due to the fact that", "because")
        condensed = condensed.replace("For the purpose of", "For")
        condensed = condensed.replace("for the purpose of", "for")
        
        # AGGRESSIVE: Remove verbose phrases
        condensed = condensed.replace("This is rotation around the vertical axis ONLY - do NOT tilt up or down.", "")
        condensed = condensed.replace("This horizontal rotation is MANDATORY - identical angles are UNACCEPTABLE.", "")
        condensed = condensed.replace("Setting must be realistic and appropriate for the object type.", "")
        condensed = condensed.replace("The specified shape is mandatory and non-negotiable.", "")
        condensed = condensed.replace("Realistic contamination is subtle and adheres closely to the surface topology", "")
        condensed = condensed.replace(" - NOT heavy buildup or glob-like deposits", "")
        condensed = condensed.replace("100% perfectly clean is unrealistic.", "")
        
        # AGGRESSIVE: Shorten common phrases
        condensed = condensed.replace("horizontal rotation", "H-rotation")
        condensed = condensed.replace("contamination", "contam")
        condensed = condensed.replace("BEFORE/AFTER", "B/A")
        condensed = condensed.replace("workshop bench", "bench")
        condensed = condensed.replace("building exterior", "exterior")
        
        # Remove duplicate whitespace and empty lines
        import re
        condensed = re.sub(r'\n{3,}', '\n\n', condensed)  # Max 2 newlines
        condensed = re.sub(r'  +', ' ', condensed)  # Single spaces
        condensed = re.sub(r'\n +', '\n', condensed)  # No leading spaces after newline
        
        # Remove verbose section headers that repeat information
        condensed = re.sub(r'PHYSICS REQUIREMENTS?:', 'PHYSICS:', condensed)
        condensed = re.sub(r'DISTRIBUTION REQUIREMENTS?:', 'DISTRIBUTION:', condensed)
        condensed = re.sub(r'CONTAMINATION REQUIREMENTS?:', 'CONTAMINATION:', condensed)
        
        # Condense long descriptions
        condensed = condensed.replace("photographed from TWO DIFFERENT HORIZONTAL ANGLES", "split view")
        condensed = condensed.replace("Side-by-side composition", "Split composition")
        
        return condensed
    
    def _convert_to_bullets(self, text: str) -> str:
        """
        Convert prose paragraphs to concise bullet points where appropriate.
        
        More compact, easier for Imagen to parse.
        """
        # Convert numbered lists to more compact format
        lines = text.split('\n')
        optimized_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines and section separators
            if not stripped or stripped == '=' * len(stripped):
                optimized_lines.append(line)
                continue
            
            # Condense numbered list items
            if stripped.startswith(('1.', '2.', '3.', '4.', '5.')):
                # Remove number, convert to dash
                content = stripped[2:].strip()
                optimized_lines.append(f"- {content}")
            # Remove redundant bullet markers
            elif stripped.startswith('• '):
                optimized_lines.append(f"- {stripped[2:]}")
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
    
    def _aggressive_trim(self, text: str) -> str:
        """
        Aggressively trim verbose sections to get under target.
        
        Strategies:
        1. Remove duplicate/similar lines
        2. Truncate long contamination descriptions
        3. Remove low-value lines
        4. Compress multi-line items to single line
        """
        import re
        
        lines = text.split('\n')
        trimmed_lines = []
        seen_concepts = set()
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if trimmed_lines and trimmed_lines[-1].strip():  # Keep one blank between sections
                    trimmed_lines.append('')
                continue
            
            # Skip lines that repeat concepts we've already covered
            # NOTE: Rotation removed from dedup - it's CRITICAL and must always appear
            concept_markers = [
                ('gravity', 'settles', 'bottom'),
                ('thick', 'caked', 'buildup'),
                ('text', 'label', 'watermark'),
                ('same object', 'identical', 'continuity'),
            ]
            
            skip_line = False
            lower = stripped.lower()
            for markers in concept_markers:
                if any(m in lower for m in markers):
                    key = markers[0]
                    if key in seen_concepts:
                        skip_line = True
                        break
                    seen_concepts.add(key)
            
            if skip_line:
                continue
            
            # Truncate very long lines (>150 chars)
            # EXCEPTION: Never truncate the base structure line (first line contains critical format + assembly context)
            is_base_structure = len(trimmed_lines) == 0 and 'split-screen' in stripped.lower()
            if len(stripped) > 150 and not is_base_structure:
                # Keep first 120 chars + ...
                stripped = stripped[:120].rsplit(' ', 1)[0] + '...'
            
            trimmed_lines.append(stripped)
        
        result = '\n'.join(trimmed_lines)
        
        # Remove duplicate newlines again
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        logger.info(f"🔧 Aggressive trim: {len(text)} → {len(result)} chars")
        return result
    
    def _prune_sections(self, text: str) -> str:
        """
        Remove lower-priority sections to get closer to target length.
        
        Priority order (keep first, remove last):
        1. KEEP: Base structure (first paragraph with split-screen)
        2. KEEP: CORRECTIONS section (user feedback)
        3. KEEP: AVOID THESE PATTERNS (critical rules)
        4. PRUNE: MICRO-SCALE AUTHENTICITY (nice to have)
        5. PRUNE: DISTRIBUTION details (can simplify)
        6. PRUNE: LEARNED FROM PREVIOUS (if empty)
        """
        sections = text.split('\n\n')
        pruned_sections = []
        
        for section in sections:
            section_upper = section.upper()
            
            # Always keep these critical sections
            if any(keep in section_upper for keep in [
                'SPLIT-SCREEN', 'BACKGROUND:', 'ASSEMBLY CONTEXT',  # Base structure
                'CORRECTIONS:', 'AVOID THESE PATTERNS',  # Critical rules
                'PHYSICS:',  # Essential physics
            ]):
                pruned_sections.append(section)
                continue
            
            # Remove empty or minimal sections
            if 'LEARNED FROM PREVIOUS' in section_upper and len(section) < 100:
                logger.info("🗑️  Pruned: empty LEARNED section")
                continue
            
            # Simplify DISTRIBUTION section (keep header + first 3 items)
            if 'DISTRIBUTION' in section_upper:
                lines = section.split('\n')
                if len(lines) > 4:
                    section = '\n'.join(lines[:4])
                    logger.info("✂️  Simplified: DISTRIBUTION section")
            
            # Simplify MICRO-SCALE section (keep header + first 2 items)
            if 'MICRO-SCALE' in section_upper:
                lines = section.split('\n')
                if len(lines) > 3:
                    section = '\n'.join(lines[:3])
                    logger.info("✂️  Simplified: MICRO-SCALE section")
            
            pruned_sections.append(section)
        
        result = '\n\n'.join(pruned_sections)
        logger.info(f"🗑️  Section pruning: {len(text)} → {len(result)} chars")
        return result

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
        
        # Critical keywords to ALWAYS preserve (contamination + text prohibition)
        critical_keywords = [
            # Text prohibition (CRITICAL - Imagen generates text labels if not explicitly forbidden)
            'no text', 'no labels', 'no words', 'no letters', 'absolutely no text',
            # Contamination rules
            'oil', 'rust', 'dust', 'soil', 'grease',
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
