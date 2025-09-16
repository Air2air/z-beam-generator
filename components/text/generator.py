#!/usr/bin/env python3
"""
Text Component Generator

Lightweight wrapper for ComponentGeneratorFactory integration.
Provides a clean interface to the fail_fast_generator.py text generation system.
"""

import logging
from typing import Dict, Optional, Any

from generators.component_generators import APIComponentGenerator, ComponentResult
from components.text.localization import validate_localization_support

logger = logging.getLogger(__name__)


class TextComponentGenerator(APIComponentGenerator):
    """
    Text component generator that wraps the fail_fast_generator.

    This is a lightweight wrapper that integrates with ComponentGeneratorFactory
    while delegating the actual text generation to fail_fast_generator.py.
    """

    def __init__(self):
        """Initialize the text component generator."""
        super().__init__("text")

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "text",
            "description": "Technical content generation for laser cleaning articles",
            "version": "3.0.0",
            "requires_api": True,
            "type": "dynamic",
        }

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
        enhancement_flags: Optional[Dict[str, bool]] = None,
    ) -> ComponentResult:
        """
        Generate text content using frontmatter data as primary source.

        FAIL-FAST: Requires counterpart frontmatter file to exist. Will not generate
        frontmatter itself - must be pre-generated.

        Args:
            material_name: Name of the material
            material_data: Raw material data from materials.yaml (fallback)
            api_client: API client for text generation
            author_info: Author information
            frontmatter_data: Processed frontmatter data (primary source)
            schema_fields: Schema fields (not used for text)
            enhancement_flags: Optional enhancement flags for AI detection optimization

        Returns:
            ComponentResult with generated content
        """
        try:
            # FAIL-FAST: Text component requires counterpart frontmatter file
            if not frontmatter_data:
                from pathlib import Path
                safe_material = material_name.lower().replace(" ", "-").replace("/", "-")
                frontmatter_path = Path("content") / "components" / "frontmatter" / f"{safe_material}-laser-cleaning.md"

                if not frontmatter_path.exists():
                    error_msg = f"Counterpart frontmatter file not found: {frontmatter_path}. Text component requires pre-generated frontmatter data."
                    logger.error(f"❌ {error_msg}")
                    return ComponentResult(
                        component_type="text",
                        content="",
                        success=False,
                        error_message=error_msg,
                    )
                else:
                    # Try to load existing frontmatter data
                    try:
                        from utils.file_ops.frontmatter_loader import load_frontmatter_data
                        frontmatter_data = load_frontmatter_data(material_name)
                        if not frontmatter_data:
                            error_msg = f"Failed to load frontmatter data from existing file: {frontmatter_path}"
                            logger.error(f"❌ {error_msg}")
                            return ComponentResult(
                                component_type="text",
                                content="",
                                success=False,
                                error_message=error_msg,
                            )
                        # Convert datetime objects to strings for JSON serialization
                        import datetime
                        def convert_datetimes(obj):
                            if isinstance(obj, dict):
                                return {k: convert_datetimes(v) for k, v in obj.items()}
                            elif isinstance(obj, list):
                                return [convert_datetimes(item) for item in obj]
                            elif isinstance(obj, datetime.datetime):
                                return obj.isoformat()
                            elif isinstance(obj, datetime.date):
                                return obj.isoformat()
                            else:
                                return obj
                        frontmatter_data = convert_datetimes(frontmatter_data)
                    except Exception as e:
                        error_msg = f"Error loading frontmatter data: {e}"
                        logger.error(f"❌ {error_msg}")
                        return ComponentResult(
                            component_type="text",
                            content="",
                            success=False,
                            error_message=error_msg,
                        )

            # Import the fail_fast_generator
            from .generators.fail_fast_generator import create_fail_fast_generator

            logger.info(
                f"📝 Generating text for {material_name} using simplified approach"
            )

            # Create generator with settings optimized for test vs production
            # Use faster retry delays in test mode to speed up test execution
            # Test mode detection using environment variables directly
            import os
            is_test_mode = any([
                os.getenv("TEST_MODE", "").lower() in ("true", "1", "yes"),
                os.getenv("PYTEST_CURRENT_TEST", "") != "",
                "pytest" in os.getenv("_", "").lower(),
            ])
            
            retry_delay = 0.1 if is_test_mode else 1.0
            
            generator = create_fail_fast_generator(
                max_retries=3,
                retry_delay=retry_delay,
                enable_scoring=False,  # Disable scoring for basic text generation
                skip_ai_detection=True,  # No AI detection in basic text component
            )

            # Generate content with provided author info
            if not author_info:
                raise ValueError("Author information is required for text generation")

            # CRITICAL: Validate localization support before generation
            author_country = author_info.get('country', 'USA')
            if not validate_localization_support(author_country):
                error_msg = f"Localization not supported for country '{author_country}'. Localization is mandatory for all text generation."
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)

            # Use frontmatter_data as primary source, fall back to material_data
            primary_data = frontmatter_data if frontmatter_data else material_data

            # Simple text generation
            result = generator.generate(
                material_name=material_name,
                material_data=primary_data,  # Use frontmatter data as primary source
                api_client=api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data,
                enhancement_flags=enhancement_flags,  # Pass enhancement flags for optimization
            )

            if not result.success:
                logger.warning(
                    f"❌ Text generation failed for {material_name}: {result.error_message}"
                )
                return ComponentResult(
                    component_type="text",
                    content="",
                    success=False,
                    error_message=result.error_message,
                )

            # Apply content humanization for better AI detection scores
            try:
                from scripts.tools.quick_content_humanizer import QuickContentHumanizer
                humanizer = QuickContentHumanizer()
                humanized_content = humanizer.humanize_content(result.content)
                logger.info(f"✨ Applied content humanization for {material_name}")
            except Exception as e:
                logger.warning(f"⚠️ Content humanization failed, using original content: {e}")
                humanized_content = result.content

            # Format content with frontmatter at the bottom
            try:
                formatted_content = self._format_content_with_frontmatter(
                    humanized_content, material_name, author_info, frontmatter_data
                )
            except ValueError as e:
                # Re-raise ValueError for missing required dependencies (fail-fast)
                logger.error(f"Validation error in content formatting: {e}")
                raise

            # Apply centralized version stamping (will prepend to any existing legacy stamps)
            from versioning import stamp_component_output

            final_content = stamp_component_output("text", formatted_content)

            return ComponentResult(
                component_type="text",
                content=final_content,
                success=True,
                error_message=None,
            )

        except ValueError as e:
            # Re-raise ValueError for missing required dependencies (fail-fast)
            logger.error(f"Validation error in text generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return ComponentResult(
                component_type="text", content="", success=False, error_message=str(e)
            )

    def _format_content_with_frontmatter(
        self,
        content: str,
        material_name: str,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
    ) -> str:
        """
        Format content with frontmatter, removing any preamble text before the actual content.

        This removes common AI-generated preambles like:
        - "Of course. Here is a comprehensive..."
        - "Certainly. Here is a technical..."
        - Any introductory text before the first substantial paragraph

        Args:
            content: Generated text content
            material_name: Name of the material
            author_info: Author information from generation
            frontmatter_data: Frontmatter data from counterpart component

        Returns:
            Formatted content with proper structure
        """
        import time

        # Extract author information - prioritize author_info over frontmatter  
        # This ensures the correct author is used even if frontmatter has old data
        if author_info and "name" in author_info:
            author_name = author_info["name"]
        elif frontmatter_data and "author" in frontmatter_data:
            author_name = frontmatter_data["author"]
        else:
            raise ValueError("Author information is required for content formatting")

        # Clean content by removing preamble text before actual content
        clean_content = self._remove_preamble_text(content.strip())
        
        # Remove any existing frontmatter from content (but preserve version logs)
        clean_content = self._remove_existing_frontmatter(clean_content)

        # Build the formatted content
        result_parts = []
        
        # Add clean content at top
        result_parts.append(clean_content)
        result_parts.append("")  # Empty line separator
        
        # Add basic author frontmatter
        result_parts.append("---")
        result_parts.append(f"author: {author_name}")
        result_parts.append(f"material: {material_name}")
        result_parts.append("component: text")
        result_parts.append(f"generated: {time.strftime('%Y-%m-%d')}")
        result_parts.append("source: text")
        result_parts.append("---")

        return '\n'.join(result_parts)

    def _remove_preamble_text(self, content: str) -> str:
        """
        Remove headers, metadata, abstracts, and preambles to start directly with the main content paragraph.
        
        Based on user formatting preferences:
        - Removes main headings (# Laser Cleaning of...)
        - Removes author bylines and metadata
        - Removes Abstract sections completely
        - Removes preambles like "Of course. Here is..."
        - Starts with the first substantial technical paragraph
        
        Args:
            content: Raw content with headers and metadata
            
        Returns:
            Content starting directly with the main technical paragraph
        """
        lines = content.split('\n')
        content_start_index = -1
        i = 0
        
        # First, skip all preambles, headers, metadata, and abstract sections
        while i < len(lines):
            line_stripped = lines[i].strip()
            
            # Skip empty lines
            if not line_stripped:
                i += 1
                continue
            
            # Skip preamble phrases
            if any(phrase in line_stripped for phrase in [
                "Of course.", "Here is", "Here's", "Below is", "This is", "I'll provide"
            ]):
                i += 1
                continue
            
            # Skip separators like ***
            if line_stripped in ['***', '---', '___']:
                i += 1
                continue
                
            # Skip all headers (# and ##)
            if line_stripped.startswith('#'):
                # If this is an Abstract header, skip until next section
                if 'abstract' in line_stripped.lower():
                    i += 1
                    # Skip all lines until we find another header or substantial content
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if next_line.startswith('#') and 'abstract' not in next_line.lower():
                            break  # Found next section
                        i += 1
                    continue
                else:
                    i += 1
                    continue
                    
            # Skip author/metadata lines
            if any(pattern in line_stripped for pattern in [
                "**Author:**", "**Material:**", "**Date:**", "**Affiliation:**", "**Expertise:**",
                "*Generated:", "*Italy*", "*Indonesia*", "*Taiwan*", "*USA*"
            ]):
                i += 1
                continue
                
            # This should be a substantial technical paragraph
            # Look for paragraphs that:
            # - Are longer than 100 characters (substantial content)
            # - Contain periods (complete sentences)
            # - Don't end with colons (not section labels)
            # - Start with a capital letter or material name
            if (len(line_stripped) > 100 and 
                '.' in line_stripped and 
                not line_stripped.endswith(':') and
                (line_stripped[0].isupper() or 
                 any(material in line_stripped[:50] for material in [
                     'Alumina', 'Porcelain', 'Silicon Nitride', 'Aluminum', 'Steel'
                 ]))):
                content_start_index = i
                break
            
            i += 1
        
        # If we found a good starting point, use it
        if content_start_index >= 0:
            return '\n'.join(lines[content_start_index:]).strip()
        
        # Fallback: remove obvious preambles and return the rest
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped and not any(pattern in line_stripped for pattern in [
                "Of course.", "Here is", "**Author:**", "**Material:**", "# ", "## Abstract"
            ]):
                return '\n'.join(lines[i:]).strip()
        
        return content.strip()
    
    def _remove_existing_frontmatter(self, content: str) -> str:
        """
        Remove any existing frontmatter blocks from content while preserving version logs.
        
        Args:
            content: Content that may contain frontmatter
            
        Returns:
            Content with frontmatter removed but version logs preserved
        """
        lines = content.split('\n')
        result_lines = []
        in_frontmatter = False
        in_version_log = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect frontmatter boundaries
            if stripped == '---':
                if not in_frontmatter and not in_version_log:
                    # Check if next lines look like frontmatter or version log
                    in_frontmatter = True
                    continue
                else:
                    # End of frontmatter or version log
                    in_frontmatter = False
                    in_version_log = False
                    continue
            
            # Detect version logs (preserve these)
            if stripped.startswith('Version Log -'):
                in_version_log = True
                result_lines.append(line)
                continue
                
            # Skip frontmatter lines but preserve version log lines
            if in_frontmatter and not in_version_log:
                continue
                
            # Add all other lines
            result_lines.append(line)
        
        return '\n'.join(result_lines).strip()
