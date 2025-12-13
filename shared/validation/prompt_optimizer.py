"""
Prompt Optimizer - Auto-Fix Critical Validation Issues

Automatically rewrites prompts to fix CRITICAL issues:
- Reduces size to fit API limits
- Optimizes whitespace and formatting
- Preserves essential content and instructions

Author: AI Assistant
Date: December 12, 2025
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def optimize_prompt(prompt: str, validation_result) -> str:
    """
    Optimize prompt to fix CRITICAL and WARNING validation issues.
    
    Applies multiple optimization strategies:
    1. Remove excessive whitespace (triple newlines → double)
    2. Condense repetitive instructions
    3. Trim verbose examples
    4. Remove redundant emphasis markers
    5. Shorten long lines
    6. Fix inconsistent length targets (keep only first occurrence)
    7. Resolve style contradictions (remove conflicting adjectives)
    8. Remove duplicate word count specifications
    
    Args:
        prompt: Original prompt text
        validation_result: ValidationResult with issues to fix
        
    Returns:
        Optimized prompt (may still have issues if unfixable)
    """
    original_length = len(prompt)
    optimized = prompt
    
    # Strategy 1: Remove excessive blank lines (6 triple-newlines → 2 double-newlines)
    optimized = re.sub(r'\n\n\n+', '\n\n', optimized)
    logger.info(f"Whitespace optimization: {original_length} → {len(optimized)} chars")
    
    # Strategy 2: Fix inconsistent length targets (WARNING fix)
    # Keep only the first LENGTH specification, remove duplicates
    length_patterns = [
        r'LENGTH:\s*\d+-\d+\s+words?',
        r'Write\s+\d+-\d+\s+words?',
        r'Target:\s*\d+-\d+\s+words?',
        r'Aim for\s+\d+-\d+\s+words?',
        r'\d+-\d+\s+words?\s+total',
        r'approximately\s+\d+-\d+\s+words?',
    ]
    
    first_length_found = False
    lines = optimized.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Check if this line contains a length specification
        has_length = any(re.search(pattern, line, re.IGNORECASE) for pattern in length_patterns)
        
        if has_length:
            if not first_length_found:
                # Keep the first length specification
                filtered_lines.append(line)
                first_length_found = True
                logger.info(f"Kept primary length target: {line.strip()[:60]}...")
            else:
                # Skip duplicate length specifications
                logger.info(f"Removed duplicate length target: {line.strip()[:60]}...")
                continue
        else:
            filtered_lines.append(line)
    
    optimized = '\n'.join(filtered_lines)
    
    # Strategy 3: Resolve style contradictions (WARNING fix)
    # Remove conflicting style adjectives
    contradictions = [
        (r'\btechnical\b.*?\bsimple\b', 'technical'),  # Keep technical, remove simple
        (r'\bsimple\b.*?\btechnical\b', 'technical'),  # Keep technical, remove simple
        (r'\bbrief\b.*?\bdetailed\b', 'detailed'),     # Keep detailed, remove brief
        (r'\bdetailed\b.*?\bbrief\b', 'detailed'),     # Keep detailed, remove brief
        (r'\bshort\b.*?\bcomprehensive\b', 'comprehensive'),
        (r'\bcomprehensive\b.*?\bshort\b', 'comprehensive'),
    ]
    
    for pattern, keep_word in contradictions:
        if re.search(pattern, optimized, re.IGNORECASE):
            # Found contradiction - remove the conflicting word
            opposite = pattern.split(r'\b')[1]  # Get first word in pattern
            if opposite != keep_word:
                # Remove the opposite word
                optimized = re.sub(rf'\b{opposite}\b', '', optimized, count=1, flags=re.IGNORECASE)
                logger.info(f"Resolved style contradiction: removed '{opposite}', kept '{keep_word}'")
    
    # Strategy 4: Remove redundant emphasis (keep first occurrence only)
    # Remove duplicate CRITICAL/IMPORTANT markers
    lines = optimized.split('\n')
    seen_emphasis = set()
    deduplicated_lines = []
    
    for line in lines:
        # Check if line is pure emphasis (CRITICAL:, IMPORTANT:, etc)
        emphasis_match = re.match(r'^\s*(CRITICAL|IMPORTANT|REQUIRED|MANDATORY|FORBIDDEN):', line, re.IGNORECASE)
        if emphasis_match:
            key = emphasis_match.group(1).upper()
            if key in seen_emphasis:
                continue  # Skip duplicate emphasis
            seen_emphasis.add(key)
        deduplicated_lines.append(line)
    
    optimized = '\n'.join(deduplicated_lines)
    logger.info(f"Emphasis deduplication: {len(lines)} → {len(deduplicated_lines)} lines")
    
    # Strategy 5: Condense verbose instructions
    # Replace wordy phrases with concise equivalents
    replacements = [
        (r'You must ensure that you', 'Ensure'),
        (r'It is important to note that', 'Note:'),
        (r'Please make sure to', 'Must'),
        (r'You should always remember to', 'Always'),
        (r'Do not forget to', 'Must'),
        (r'Be sure to pay attention to', 'Note'),
    ]
    
    for pattern, replacement in replacements:
        optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
    
    logger.info(f"Phrase condensation: {len(prompt.split())} → {len(optimized.split())} words")
    
    # Strategy 6: Remove redundant intensifiers
    optimized = re.sub(r'\b(very|really|extremely|absolutely|totally)\s+', '', optimized, flags=re.IGNORECASE)
    
    # Strategy 7: Trim overly long lines (break at 500 chars)
    lines = optimized.split('\n')
    trimmed_lines = []
    for line in lines:
        if len(line) > 500:
            # Find last period before 500 chars, break there
            truncate_at = line.rfind('.', 0, 500)
            if truncate_at > 0:
                trimmed_lines.append(line[:truncate_at+1])
                remaining = line[truncate_at+1:].strip()
                if remaining:
                    trimmed_lines.append(remaining)
            else:
                trimmed_lines.append(line)  # Can't break safely, keep as-is
        else:
            trimmed_lines.append(line)
    
    optimized = '\n'.join(trimmed_lines)
    
    reduction = original_length - len(optimized)
    reduction_pct = 100 * reduction / original_length if original_length > 0 else 0
    
    logger.info(f"Prompt optimization complete: {original_length} → {len(optimized)} chars ({reduction_pct:.1f}% reduction)")
    
    return optimized


def aggressive_optimize(prompt: str, target_length: int = 8000) -> str:
    """
    Aggressively optimize prompt to fit target length.
    
    Uses more destructive strategies:
    - Remove all examples
    - Keep only core instructions
    - Preserve voice and requirements sections
    
    Args:
        prompt: Original prompt
        target_length: Target character count
        
    Returns:
        Aggressively optimized prompt
    """
    if len(prompt) <= target_length:
        return prompt
    
    # Extract critical sections (preserve these)
    voice_section = ""
    requirements_section = ""
    task_section = ""
    
    lines = prompt.split('\n')
    current_section = None
    preserved_lines = []
    
    for line in lines:
        # Identify sections
        if 'VOICE:' in line.upper():
            current_section = 'voice'
        elif 'REQUIREMENTS:' in line.upper():
            current_section = 'requirements'
        elif 'TASK:' in line.upper():
            current_section = 'task'
        elif 'EXAMPLES:' in line.upper() or 'EXAMPLE:' in line.upper():
            current_section = 'examples'  # Skip examples
            continue
        elif line.strip().startswith('---') or line.strip().startswith('==='):
            current_section = None
        
        # Preserve critical sections, skip examples
        if current_section in ['voice', 'requirements', 'task']:
            preserved_lines.append(line)
        elif current_section != 'examples' and line.strip():
            # Keep non-example content
            preserved_lines.append(line)
    
    optimized = '\n'.join(preserved_lines)
    
    # If still too long, apply basic optimization
    if len(optimized) > target_length:
        optimized = optimize_prompt(optimized, None)
    
    # If STILL too long, truncate intelligently
    if len(optimized) > target_length:
        # Keep first 80% of target (preserve beginning)
        # Add note about truncation
        truncate_at = int(target_length * 0.95)
        optimized = optimized[:truncate_at]
        optimized += "\n\n[Prompt truncated to fit API limit]"
    
    logger.warning(f"Aggressive optimization: {len(prompt)} → {len(optimized)} chars")
    
    return optimized
