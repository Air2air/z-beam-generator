"""
Subtitle Component - Discrete Component Pattern

Generates engaging 8-12 word subtitles with Author Voice integration.

Pattern: Single voice call with specific word count constraints.
Follows discrete component architecture (core/, prompts/, config/).
"""

from .core.subtitle_generator import SubtitleComponentGenerator

__all__ = ['SubtitleComponentGenerator']
