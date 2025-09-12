#!/usr/bin/env python3
"""
AI Detection Prompt Chain System

This module provides AI detection prompt chaining that works independently from
localization prompts. AI detection prompts are applied FIRST, followed by 
localization prompts.

ARCHITECTURE: AI Detection → Localization → Base Content
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class AIDetectionPromptChain:
    """
    AI Detection prompt chaining system.
    
    This class provides AI detection prompts that are dynamically adapted
    based on Winston AI analysis and enhancement flags.
    """
    
    def __init__(self):
        self.prompts_path = "components/text/prompts"
        self.ai_detection_file = f"{self.prompts_path}/ai_detection_core.yaml"
        
        # Enhancement flags for dynamic adaptation
        self.enhancement_flags = {
            'natural_language_patterns': False,
            'sentence_variability': False,
            'paragraph_structure': False,
            'cultural_adaptation': False,
            'lexical_diversity': False,
            'emotional_depth': False,
            'conversational_boost': False,
            'human_error_simulation': False,
            'rhetorical_devices': False,
            'personal_anecdotes': False,
            'cognitive_variability': False,
            'mid_thought_interruptions': False,
            'uncertainty_expressions': False,
            'ai_detection_focus': False
        }
    
    def get_ai_detection_chain(self, enhancement_flags: Optional[Dict[str, bool]] = None) -> str:
        """
        Get AI detection prompt chain with dynamic enhancement flags.
        
        Args:
            enhancement_flags: Dictionary of enhancement flags to enable/disable
            
        Returns:
            Complete AI detection prompt chain
        """
        try:
            # Load base AI detection prompts
            ai_detection_prompts = self._load_ai_detection_prompts()
            
            # Apply enhancement flags if provided
            if enhancement_flags:
                self.enhancement_flags.update(enhancement_flags)
            
            # Build AI detection prompt chain
            return self._build_ai_detection_chain(ai_detection_prompts)
            
        except Exception as e:
            print(f"Warning: Could not load AI detection prompts: {e}")
            return self._get_fallback_ai_detection_prompt()
    
    def _load_ai_detection_prompts(self) -> Dict[str, Any]:
        """Load AI detection prompts from YAML file."""
        try:
            if os.path.exists(self.ai_detection_file):
                with open(self.ai_detection_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                print(f"Warning: AI detection prompts file not found: {self.ai_detection_file}")
                return {}
        except Exception as e:
            print(f"Error loading AI detection prompts: {e}")
            return {}
    
    def _build_ai_detection_chain(self, prompts: Dict[str, Any]) -> str:
        """Build the complete AI detection prompt chain."""
        sections = []
        
        # Add dynamic enhancement instructions based on flags
        enabled_enhancements = [flag for flag, enabled in self.enhancement_flags.items() if enabled]
        
        if enabled_enhancements:
            sections.append("=== AI DETECTION OPTIMIZATION (DYNAMIC) ===")
            sections.append(f"ENABLED ENHANCEMENTS: {', '.join(enabled_enhancements)}")
            sections.append("")
            
            # Add specific instructions for enabled enhancements
            for enhancement in enabled_enhancements:
                if enhancement in prompts:
                    instructions = prompts[enhancement]
                    if isinstance(instructions, list):
                        sections.append(f"{enhancement.upper().replace('_', ' ')}:")
                        for instruction in instructions:
                            sections.append(f"- {instruction}")
                        sections.append("")
            
            sections.append("=== END AI DETECTION OPTIMIZATION ===")
        else:
            # Add basic AI detection guidance
            sections.append("=== AI DETECTION GUIDANCE ===")
            sections.append("Write in a natural, human-like style that avoids AI detection patterns.")
            sections.append("Use varied sentence structures and authentic language patterns.")
            sections.append("=== END AI DETECTION GUIDANCE ===")
        
        return "\n".join(sections)
    
    def _get_fallback_ai_detection_prompt(self) -> str:
        """Provide fallback AI detection prompt if files are unavailable."""
        return """=== AI DETECTION GUIDANCE (FALLBACK) ===
Write content that appears naturally human-written:
- Use varied sentence structures and lengths
- Include natural language patterns and flow
- Avoid repetitive or predictable phrasing
- Add authentic human-like characteristics
=== END AI DETECTION GUIDANCE ==="""
    
    def update_enhancement_flags(self, new_flags: Dict[str, bool]) -> None:
        """Update enhancement flags for dynamic adaptation."""
        self.enhancement_flags.update(new_flags)
    
    def get_current_flags(self) -> Dict[str, bool]:
        """Get current enhancement flags."""
        return self.enhancement_flags.copy()


# Global instance for use throughout the system
ai_detection_chain = AIDetectionPromptChain()


def get_ai_detection_prompt(enhancement_flags: Optional[Dict[str, bool]] = None) -> str:
    """
    Get AI detection prompt chain (global function).
    
    Args:
        enhancement_flags: Optional enhancement flags for dynamic adaptation
        
    Returns:
        AI detection prompt chain string
    """
    return ai_detection_chain.get_ai_detection_chain(enhancement_flags)


def update_ai_detection_flags(enhancement_flags: Dict[str, bool]) -> None:
    """
    Update global AI detection enhancement flags.
    
    Args:
        enhancement_flags: New enhancement flags to apply
    """
    ai_detection_chain.update_enhancement_flags(enhancement_flags)


def validate_ai_detection_support() -> bool:
    """
    Validate that AI detection prompts are available.
    
    Returns:
        True if AI detection prompts are supported, False otherwise
    """
    try:
        prompt = get_ai_detection_prompt()
        return len(prompt) > 0
    except Exception:
        return False
