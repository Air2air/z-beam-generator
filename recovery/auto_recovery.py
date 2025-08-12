"""
Intelligent auto-recovery system for Z-Beam content formatting.
Provides Claude with specific fixes and automatically retries failed operations.
"""

import logging
import re
import json
import yaml
from typing import Dict, List, Tuple, Optional, Callable

logger = logging.getLogger(__name__)

class ContentAutoRecovery:
    """Intelligent content recovery with Claude-specific fix instructions."""
    
    def __init__(self, max_retries: int = 3):
        """Initialize auto-recovery system.
        
        Args:
            max_retries: Maximum number of automatic retry attempts
        """
        self.max_retries = max_retries
        self.recovery_patterns = self._build_recovery_patterns()
    
    def _build_recovery_patterns(self) -> List[Dict]:
        """Build comprehensive recovery patterns with Claude instructions."""
        return [
            {
                "error_pattern": r"yaml.*error.*line (\d+).*column (\d+)",
                "error_type": "yaml_syntax",
                "claude_instruction": "Fix YAML syntax error at line {0}, column {1}",
                "fix_function": self._fix_yaml_syntax,
                "priority": "critical"
            },
            {
                "error_pattern": r"mapping values are not allowed here",
                "error_type": "yaml_mapping",
                "claude_instruction": "Fix YAML mapping - likely missing quotes around values with colons",
                "fix_function": self._fix_yaml_mapping,
                "priority": "critical"
            },
            {
                "error_pattern": r"json.*error.*line (\d+)",
                "error_type": "json_syntax",
                "claude_instruction": "Fix JSON syntax error at line {0}",
                "fix_function": self._fix_json_syntax,
                "priority": "critical"
            },
            {
                "error_pattern": r"unterminated string",
                "error_type": "unterminated_string",
                "claude_instruction": "Fix unterminated strings - add missing quotes",
                "fix_function": self._fix_unterminated_strings,
                "priority": "high"
            },
            {
                "error_pattern": r"code.*block|```",
                "error_type": "code_blocks",
                "claude_instruction": "Remove or fix malformed code blocks in YAML/JSON content",
                "fix_function": self._fix_code_blocks,
                "priority": "medium"
            },
            {
                "error_pattern": r"could not determine.*constructor|unknown.*tag",
                "error_type": "yaml_constructor",
                "claude_instruction": "Fix YAML constructor issues - likely code blocks or invalid syntax",
                "fix_function": self._fix_code_blocks,
                "priority": "high"
            }
        ]
    
    def recover_content(self, content: str, error: Exception, component: str, 
                       generator_func: Optional[Callable] = None) -> Tuple[bool, str, List[str]]:
        """
        Attempt to recover content with intelligent fixes.
        
        Args:
            content: Original content that failed
            error: The exception that occurred
            component: Component name for context
            generator_func: Function to regenerate content if needed
            
        Returns:
            (success, fixed_content, applied_fixes)
        """
        # Store component for use in fix functions
        self._current_component = component
        
        error_str = str(error).lower()
        applied_fixes = []
        
        logger.info(f"🔧 AUTO-RECOVERY: Attempting to fix {component} content")
        logger.info(f"   Original error: {str(error)}")
        logger.info(f"   Content length: {len(content) if content else 0} chars")
        
        # Find matching recovery patterns
        matching_patterns = []
        for pattern_info in self.recovery_patterns:
            if re.search(pattern_info["error_pattern"], error_str):
                matching_patterns.append(pattern_info)
        
        if not matching_patterns:
            logger.warning(f"   No recovery patterns match error: {error_str}")
            return False, content, []
        
        # Sort by priority and apply fixes
        matching_patterns.sort(key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x["priority"]])
        
        current_content = content
        
        for attempt in range(self.max_retries):
            logger.info(f"   🔄 Recovery attempt {attempt + 1}/{self.max_retries}")
            
            for pattern_info in matching_patterns:
                try:
                    # Generate Claude instruction
                    match = re.search(pattern_info["error_pattern"], error_str)
                    if match:
                        instruction = pattern_info["claude_instruction"].format(*match.groups())
                    else:
                        instruction = pattern_info["claude_instruction"]
                    
                    logger.info(f"   🤖 CLAUDE ACTION: {instruction}")
                    
                    # Apply fix
                    fixed_content = pattern_info["fix_function"](current_content, error_str)
                    
                    if fixed_content != current_content:
                        applied_fixes.append(f"{pattern_info['error_type']}: {instruction}")
                        current_content = fixed_content
                        logger.info(f"   ✅ Applied fix: {pattern_info['error_type']}")
                        
                        # Test the fix
                        if self._validate_fix(current_content, component):
                            logger.info(f"   🎉 Recovery successful after {len(applied_fixes)} fixes")
                            return True, current_content, applied_fixes
                    
                except Exception as fix_error:
                    logger.warning(f"   ⚠️ Fix failed for {pattern_info['error_type']}: {fix_error}")
                    continue
        
        # If automatic fixes failed, try regeneration
        if generator_func and len(applied_fixes) == 0:
            logger.info("   🔄 Automatic fixes failed, attempting content regeneration")
            try:
                regenerated_content = generator_func()
                if regenerated_content and regenerated_content.strip():
                    if self._validate_fix(regenerated_content, component):
                        applied_fixes.append("content_regeneration: Generated new content")
                        logger.info("   🎉 Recovery successful via regeneration")
                        return True, regenerated_content, applied_fixes
            except Exception as regen_error:
                logger.warning(f"   ⚠️ Regeneration failed: {regen_error}")
        
        logger.error(f"   ❌ Recovery failed after {self.max_retries} attempts")
        return False, current_content, applied_fixes
    
    def _fix_yaml_syntax(self, content: str, error_str: str) -> str:
        """Fix specific YAML syntax issues without creating fallbacks."""
        if not content or not content.strip():
            raise ValueError("Cannot fix YAML syntax on empty content")
        
        fixed = content
        
        # Fix unquoted values with colons (most common issue)
        # Only fix obvious cases where colons appear in values
        fixed = re.sub(r'^(\s*\w+):\s*([^"\'\n]*:[^"\'\n]*)$', r'\1: "\2"', fixed, flags=re.MULTILINE)
        
        # Fix URLs that aren't quoted
        fixed = re.sub(r'^(\s*\w+):\s*(https?://[^\s\n]+)$', r'\1: "\2"', fixed, flags=re.MULTILINE)
        
        # Remove any accidental YAML document separators that cause multi-document errors
        fixed = re.sub(r'^---\s*$', '', fixed, flags=re.MULTILINE)
        fixed = re.sub(r'^\.\.\.\s*$', '', fixed, flags=re.MULTILINE)
        
        # Clean up any resulting empty lines
        fixed = re.sub(r'\n\s*\n', '\n', fixed)
        
        # Only return if we actually made changes and content is still substantial
        if fixed != content and fixed.strip():
            return fixed.strip()
        
        # If no changes made or content became empty, fail fast
        raise ValueError("Could not apply YAML syntax fixes to content")
    
    def _fix_yaml_mapping(self, content: str, error_str: str) -> str:
        """Fix YAML mapping value issues - focus on colon problems."""
        if not content or not content.strip():
            raise ValueError("Cannot fix YAML mapping on empty content")
        
        # Specifically target the "mapping values are not allowed here" error
        # This usually means unquoted values containing colons
        
        fixed = content
        original_fixed = fixed
        
        # Quote values that contain colons but aren't already quoted
        fixed = re.sub(r'^(\s*\w+):\s*([^"\'\n]*:[^"\'\n]*)$', r'\1: "\2"', fixed, flags=re.MULTILINE)
        
        # Quote values that look like URLs or file paths
        fixed = re.sub(r'^(\s*\w+):\s*((?:https?://|[A-Za-z]:[/\\])[^\s\n]+)$', r'\1: "\2"', fixed, flags=re.MULTILINE)
        
        # Only return if we made meaningful changes
        if fixed != original_fixed and fixed.strip():
            return fixed
        
        raise ValueError("Could not fix YAML mapping issues")
    
    def _fix_json_syntax(self, content: str, error_str: str) -> str:
        """Fix specific JSON syntax issues without fallbacks."""
        if not content or not content.strip():
            raise ValueError("Cannot fix JSON syntax on empty content")
        
        fixed = content
        original_fixed = fixed
        
        # Fix trailing commas (most common JSON issue)
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # Fix single quotes to double quotes (only if they look like JSON strings)
        fixed = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', fixed)  # Keys
        fixed = re.sub(r":\s*'([^']*)'", r': "\1"', fixed)    # Values
        
        # Fix common boolean/null value casing
        fixed = re.sub(r':\s*True\b', ': true', fixed)
        fixed = re.sub(r':\s*False\b', ': false', fixed)
        fixed = re.sub(r':\s*None\b', ': null', fixed)
        
        # Only return if we made changes and content is still valid-looking
        if fixed != original_fixed and '{' in fixed and '}' in fixed:
            return fixed
        
        raise ValueError("Could not apply meaningful JSON fixes")
    
    def _fix_unterminated_strings(self, content: str, error_str: str) -> str:
        """Fix unterminated string issues by balancing quotes."""
        if not content or not content.strip():
            raise ValueError("Cannot fix unterminated strings on empty content")
        
        lines = content.split('\n')
        fixed_lines = []
        made_changes = False
        
        for line in lines:
            # Count double quotes and balance them
            quote_count = line.count('"')
            if quote_count % 2 != 0:  # Odd number of quotes
                # Only add quote at the end if line doesn't already end with one
                if not line.rstrip().endswith('"'):
                    line = line.rstrip() + '"'
                    made_changes = True
            
            fixed_lines.append(line)
        
        if made_changes:
            return '\n'.join(fixed_lines)
        
        raise ValueError("No unterminated string issues found to fix")
    
    def _fix_empty_content(self, content: str, error_str: str) -> str:
        """Handle empty content - fail fast, no placeholders."""
        if not content or not content.strip():
            # Don't create placeholder content - this should trigger regeneration
            # or be handled by the retry mechanism at a higher level
            raise ValueError("Content is empty and cannot be automatically fixed - requires regeneration")
        
        return content
    
    def _fix_code_blocks(self, content: str, error_str: str) -> str:
        """Remove code block markers that don't belong in YAML/JSON."""
        if not content or not content.strip():
            raise ValueError("Cannot fix code blocks on empty content")
        
        fixed = content
        original_fixed = fixed
        
        # Remove code block markers (``` with optional language)
        fixed = re.sub(r'```\w*\n?', '', fixed)
        fixed = re.sub(r'```\n?', '', fixed)
        
        # Remove any remaining triple backticks
        fixed = fixed.replace('```', '')
        
        # Clean up resulting empty lines but preserve structure
        fixed = re.sub(r'\n\s*\n\s*\n', '\n\n', fixed)  # Max 2 consecutive newlines
        fixed = fixed.strip()
        
        # Only return if we made changes and content is still substantial
        if fixed != original_fixed and len(fixed.strip()) > 10:
            return fixed
        
        raise ValueError("Could not meaningfully fix code block issues")
    
    def _validate_fix(self, content: str, component: str) -> bool:
        """Validate that the fix actually works."""
        if not content or not content.strip():
            return False
        
        try:
            # Try to parse based on component type
            if component in ['frontmatter', 'content']:
                yaml.safe_load(content)
                return True
            elif component in ['jsonld']:
                json.loads(content)
                return True
            else:
                # For other components, just check it's not empty
                return len(content.strip()) > 0
        except Exception:
            return False
    
    def generate_claude_recovery_report(self, component: str, original_error: str, 
                                      applied_fixes: List[str], success: bool) -> str:
        """Generate a comprehensive recovery report for Claude analysis."""
        
        report = f"🔧 AUTO-RECOVERY REPORT: {component}\n"
        report += "=" * 50 + "\n\n"
        
        report += "📋 ORIGINAL ISSUE:\n"
        report += f"   {original_error}\n\n"
        
        if applied_fixes:
            report += f"🛠️  FIXES APPLIED ({len(applied_fixes)}):\n"
            for i, fix in enumerate(applied_fixes, 1):
                report += f"   {i}. {fix}\n"
            report += "\n"
        
        if success:
            report += "✅ RECOVERY STATUS: SUCCESS\n"
            report += "   Content has been automatically fixed and validated.\n\n"
            report += "🤖 CLAUDE NEXT STEPS:\n"
            report += "   1. Review the applied fixes to prevent future occurrences\n"
            report += "   2. Consider updating prompts to avoid these issues\n"
            report += "   3. Document successful patterns for future use\n"
        else:
            report += "❌ RECOVERY STATUS: FAILED\n"
            report += "   Automatic recovery was unsuccessful.\n\n"
            report += "🤖 CLAUDE REQUIRED ACTIONS:\n"
            report += "   1. Manual intervention needed for this error type\n"
            report += "   2. Analyze the original content and error pattern\n"
            report += "   3. Develop new recovery patterns if applicable\n"
            report += "   4. Consider prompt engineering improvements\n"
        
        report += "\n🎯 PREVENTION RECOMMENDATIONS:\n"
        
        # Generate specific recommendations based on error patterns
        if "yaml" in original_error.lower():
            report += "   - Add YAML validation to prompts\n"
            report += "   - Include examples of proper YAML structure\n"
            report += "   - Emphasize proper indentation (2 spaces)\n"
        
        if "json" in original_error.lower():
            report += "   - Add JSON validation requirements to prompts\n"
            report += "   - Include valid JSON examples\n"
            report += "   - Specify double quotes for all strings\n"
        
        if "empty" in original_error.lower():
            report += "   - Make prompts more specific and detailed\n"
            report += "   - Add fallback content requirements\n"
            report += "   - Include minimum content length expectations\n"
        
        return report

# Global instance for easy access
auto_recovery = ContentAutoRecovery()
