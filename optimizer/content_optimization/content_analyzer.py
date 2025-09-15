"""
Content Analyzer Module

Handles content analysis, author extraction, and content formatting
for optimization workflows.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def extract_target_content_only(file_content: str) -> str:
    """
    Extract only the target text content from a file, excluding all logging metadata.
    
    This is critical for optimization - we must only analyze the actual content,
    not the embedded version logs, AI analysis data, or iteration metadata.
    
    Supports two extraction methods:
    1. NEW: Global Metadata Delimiting Standard (HTML-style comments)
    2. LEGACY: Pattern-based extraction for files not yet migrated
    
    Args:
        file_content: Full file content including potential logging data
        
    Returns:
        Clean text content without logging, version logs, or analysis metadata
    """
    logger.info("🔧 Extracting clean target content from file with embedded logging")
    
    original_size = len(file_content)
    
    # METHOD 1: Try Global Metadata Delimiting Standard (HTML-style comments)
    content_start_marker = "<!-- CONTENT START -->"
    content_end_marker = "<!-- CONTENT END -->"
    
    if content_start_marker in file_content and content_end_marker in file_content:
        logger.info("   🎯 Using Global Metadata Delimiting Standard extraction")
        
        # Extract content between delimiters
        content_pattern = rf'{re.escape(content_start_marker)}\s*\n(.*?)\n\s*{re.escape(content_end_marker)}'
        match = re.search(content_pattern, file_content, re.DOTALL)
        
        if match:
            clean_content = match.group(1).strip()
            clean_size = len(clean_content)
            reduction_percent = ((original_size - clean_size) / original_size * 100) if original_size > 0 else 0
            
            logger.info(f"   📏 Delimited extraction: {original_size:,} → {clean_size:,} chars ({reduction_percent:.1f}% reduction)")
            
            # Validate clean extraction
            if "Version Log" in clean_content or "ai_detection_analysis" in clean_content:
                logger.warning("   ⚠️  Logging artifacts still present in delimited content")
            else:
                logger.info("   ✅ Clean delimited extraction successful - no logging artifacts detected")
            
            return clean_content
        else:
            logger.warning("   ⚠️  Found delimiters but could not extract content - falling back to legacy method")
    
    # METHOD 2: Legacy pattern-based extraction for files not yet migrated
    logger.info("   🔄 Using legacy pattern-based extraction")
    
    # Define clear markers for content boundaries
    version_log_pattern = r'\n\n\nVersion Log - Generated:'
    ai_detection_pattern = r'\n\n---\nai_detection_analysis:'
    quality_analysis_pattern = r'\nquality_analysis:'
    
    # First pass: Find content section without any YAML sections
    lines = file_content.split('\n')
    clean_lines = []
    in_yaml = False
    
    for line in lines:
        if line.strip() == '---':
            in_yaml = not in_yaml
            continue
        
        if not in_yaml:
            # Check for logging markers
            if any(marker in line for marker in ['Version Log - Generated', 'ai_detection_analysis', 'quality_analysis']):
                break
            clean_lines.append(line)
    
    # Join and clean the content
    content = '\n'.join(clean_lines).strip()
    
    # Find the first occurrence of any logging marker in the cleaned content
    markers = [
        (version_log_pattern, version_log_pattern),
        (ai_detection_pattern, ai_detection_pattern),
        (quality_analysis_pattern, quality_analysis_pattern)
    ]
    
    earliest_marker_pos = len(content)
    
    for pattern, _ in markers:
        match = re.search(pattern, content)
        if match:
            earliest_marker_pos = min(earliest_marker_pos, match.start())
    
    # Extract content up to the first logging marker
    if earliest_marker_pos < len(content):
        clean_content = content[:earliest_marker_pos].strip()
    else:
        clean_content = content.strip()
    
    # Additional cleanup: remove any remaining metadata patterns that may be embedded
    clean_content = re.sub(r"'length': \d+, 'score': [\d.]+, 'text': '.*?'", '', clean_content)
    clean_content = re.sub(r"sentences: \[.*?\]", '', clean_content, flags=re.DOTALL)
    clean_content = re.sub(r"failing_sentences_count: \d+", '', clean_content)
    clean_content = re.sub(r"provider: \"winston\"", '', clean_content)
    clean_content = re.sub(r"credits_used: \d+", '', clean_content)
    clean_content = re.sub(r"classification: \"[^\"]*\"", '', clean_content)
    clean_content = re.sub(r"confidence: [\d.]+", '', clean_content)
    clean_content = re.sub(r"processing_time: [\d.]+", '', clean_content)
    
    # Clean up any excessive whitespace
    clean_content = re.sub(r'\n{3,}', '\n\n', clean_content)
    clean_content = clean_content.strip()
    
    clean_size = len(clean_content)
    reduction_percent = ((original_size - clean_size) / original_size * 100) if original_size > 0 else 0
    
    logger.info(f"   📏 Legacy extraction: {original_size:,} → {clean_size:,} chars ({reduction_percent:.1f}% reduction)")
    
    # Validate that we extracted actual content
    if clean_size < 100:
        logger.warning(f"   ⚠️  Extracted content is very short ({clean_size} chars) - may indicate extraction issues")
    
    if "Version Log" in clean_content or "ai_detection_analysis" in clean_content:
        logger.warning("   ⚠️  Logging artifacts still present in extracted content")
    else:
        logger.info("   ✅ Clean legacy extraction successful - no logging artifacts detected")
    
    return clean_content


def update_content_with_ai_analysis(content: str, ai_result, material_name: str) -> str:
    """Update content with AI detection analysis preserving Global Metadata Delimiting Standard.
    
    Maintains the structure:
    <!-- CONTENT START -->
    [clean content]
    [author frontmatter]
    <!-- CONTENT END -->
    
    <!-- METADATA START -->
    [AI analysis and logs]
    <!-- METADATA END -->
    """
    try:
        # Check if content uses Global Metadata Delimiting Standard
        content_start_marker = "<!-- CONTENT START -->"
        content_end_marker = "<!-- CONTENT END -->"
        metadata_start_marker = "<!-- METADATA START -->"
        metadata_end_marker = "<!-- METADATA END -->"
        
        has_delimiters = all(marker in content for marker in [
            content_start_marker, content_end_marker, 
            metadata_start_marker, metadata_end_marker
        ])
        
        if has_delimiters:
            logger.info("🏷️ Preserving Global Metadata Delimiting Standard during optimization")
            
            # Extract content and metadata sections
            content_start_idx = content.find(content_start_marker) + len(content_start_marker)
            content_end_idx = content.find(content_end_marker)
            
            if content_start_idx < len(content_start_marker) or content_end_idx == -1:
                logger.warning("⚠️ Invalid content delimiters, falling back to legacy format")
                return _update_content_legacy_format(content, ai_result, material_name)
            
            # Extract clean content section (between delimiters)
            content_section = content[content_start_idx:content_end_idx].strip()
            
            # Extract author frontmatter from content section or existing metadata
            content_lines = content_section.split("\n")
            clean_content_lines = []
            author_frontmatter_lines = []
            
            # First, extract any author frontmatter that might be in content section
            in_frontmatter = False
            for line in content_lines:
                if line.strip() == "---":
                    if not in_frontmatter:
                        in_frontmatter = True
                        continue
                    else:
                        # End of frontmatter
                        in_frontmatter = False
                        continue
                
                if in_frontmatter:
                    author_frontmatter_lines.append(line)
                elif not in_frontmatter and line.strip():
                    clean_content_lines.append(line)
            
            # Also check for author frontmatter outside content delimiters
            if not author_frontmatter_lines:
                # Look for author frontmatter between <!-- CONTENT END --> and <!-- METADATA START -->
                content_end_pos = content.find(content_end_marker) + len(content_end_marker)
                metadata_start_pos = content.find(metadata_start_marker)
                
                if content_end_pos < len(content) and metadata_start_pos > content_end_pos:
                    between_section = content[content_end_pos:metadata_start_pos].strip()
                    if between_section:
                        between_lines = between_section.split("\n")
                        in_frontmatter = False
                        for line in between_lines:
                            if line.strip() == "---":
                                if not in_frontmatter:
                                    in_frontmatter = True
                                    continue
                                else:
                                    in_frontmatter = False
                                    break
                            
                            if in_frontmatter:
                                author_frontmatter_lines.append(line)
            
            # Clean up content lines
            while clean_content_lines and clean_content_lines[-1].strip() == "":
                clean_content_lines.pop()
            
            # Build new content section (pure content only, no frontmatter)
            new_content_lines = []
            new_content_lines.extend(clean_content_lines)
            
            # Build author frontmatter section (goes between content and metadata)
            author_section_lines = []
            author_section_lines.append("")
            author_section_lines.append("---")
            if author_frontmatter_lines:
                author_section_lines.extend(author_frontmatter_lines)
            else:
                # Extract author info or use defaults
                author_info = extract_author_info_from_content(content)
                if author_info:
                    author_section_lines.append(f"author: {author_info.get('name', 'AI Assistant')}")
                    author_section_lines.append(f"material: {material_name}")
                    author_section_lines.append("component: text")
                    author_section_lines.append("generated: 2025-09-13")
                    author_section_lines.append("source: text")
            author_section_lines.append("---")
            
            # Build metadata section with AI analysis
            metadata_lines = []
            metadata_lines.append("---")
            metadata_lines.append("ai_detection_analysis:")
            metadata_lines.append(f"  score: {ai_result.score:.6f}")
            metadata_lines.append(f"  confidence: {ai_result.confidence:.6f}")
            metadata_lines.append(f'  classification: "{ai_result.classification}"')
            metadata_lines.append(f'  provider: "{ai_result.provider}"')
            metadata_lines.append(f"  processing_time: {ai_result.processing_time:.6f}")
            
            # Add optimization iteration count if available
            if hasattr(ai_result, 'optimization_iterations'):
                metadata_lines.append(f"  optimization_iterations: {ai_result.optimization_iterations}")
            
            # Add quality analysis if available
            if hasattr(ai_result, 'quality_analysis') and ai_result.quality_analysis:
                metadata_lines.append("")
                metadata_lines.append("quality_analysis:")
                quality = ai_result.quality_analysis
                metadata_lines.append(f"  overall_score: {quality.get('overall_score', 0):.6f}")
                metadata_lines.append(f"  formatting_score: {quality.get('formatting_score', 0):.6f}")
                metadata_lines.append(f"  technical_score: {quality.get('technical_score', 0):.6f}")
                metadata_lines.append(f"  authenticity_score: {quality.get('authenticity_score', 0):.6f}")
                metadata_lines.append(f"  readability_score: {quality.get('readability_score', 0):.6f}")
                metadata_lines.append(f"  believability_score: {quality.get('believability_score', 0):.6f}")
                metadata_lines.append(f"  word_count: {quality.get('word_count', 0)}")
                if 'author_country' in quality:
                    metadata_lines.append(f'  author_country: "{quality["author_country"]}"')
                
                # Add detailed analysis if available
                if 'details' in quality:
                    metadata_lines.append("  details:")
                    _add_nested_dict_to_lines(metadata_lines, quality['details'], "    ")
            
            metadata_lines.append("---")
            
            # Combine everything with Global Metadata Delimiting Standard
            result_lines = []
            result_lines.append(content_start_marker)
            result_lines.extend(new_content_lines)
            result_lines.append(content_end_marker)
            
            # Add author frontmatter between content and metadata
            result_lines.extend(author_section_lines)
            
            result_lines.append("")
            result_lines.append(metadata_start_marker)
            result_lines.extend(metadata_lines)
            result_lines.append(metadata_end_marker)
            
            return "\n".join(result_lines)
        
        else:
            # Fall back to legacy format if no delimiters found
            logger.info("🔄 Using legacy format (no Global Metadata Delimiting Standard found)")
            return _update_content_legacy_format(content, ai_result, material_name)
            
    except Exception as e:
        logger.error(f"Error updating content with AI analysis for {material_name}: {e}")
        return content


def _add_nested_dict_to_lines(lines: list, data: dict, indent: str):
    """Helper function to add nested dictionary data to YAML lines."""
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{indent}{key}:")
            _add_nested_dict_to_lines(lines, value, indent + "  ")
        elif isinstance(value, list):
            lines.append(f"{indent}{key}: {value}")
        elif isinstance(value, str):
            lines.append(f'{indent}{key}: "{value}"')
        elif isinstance(value, (int, float)):
            if isinstance(value, float):
                lines.append(f"{indent}{key}: {value:.6f}")
            else:
                lines.append(f"{indent}{key}: {value}")
        else:
            lines.append(f"{indent}{key}: {value}")


def _update_content_legacy_format(content: str, ai_result, material_name: str) -> str:
    """Legacy content update format for files without Global Metadata Delimiting Standard."""
    lines = content.split("\n")
    
    # Extract different sections
    clean_content_lines = []
    author_frontmatter_lines = []
    existing_logs = []
    
    # Find yaml sections marked with ---
    yaml_sections = []
    current_yaml = []
    in_yaml = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.strip() == "---":
            if not in_yaml:
                # Start of YAML section
                in_yaml = True
                i += 1
                continue
            else:
                # End of YAML section
                yaml_sections.append(current_yaml.copy())
                current_yaml = []
                in_yaml = False
                i += 1
                continue
        
        if in_yaml:
            current_yaml.append(line)
        else:
            clean_content_lines.append(line)
            
        i += 1
    
    # Handle any unclosed YAML section
    if current_yaml and in_yaml:
        yaml_sections.append(current_yaml)
    
    # Classify YAML sections
    for yaml_section in yaml_sections:
        section_text = "\n".join(yaml_section)
        
        # Check if this is author frontmatter (contains author, material, component)
        if any(line.strip().startswith("author:") for line in yaml_section):
            author_frontmatter_lines = yaml_section
        # Check if this is existing analysis logs
        elif any(line.strip().startswith(("ai_detection_analysis:", "existing_analysis:", "score:", "confidence:")) for line in yaml_section):
            existing_logs = yaml_section
    
    # Clean up content lines (remove empty lines at end)
    while clean_content_lines and clean_content_lines[-1].strip() == "":
        clean_content_lines.pop()
    
    # Build the target format
    result_lines = []
    
    # 1. Clean markdown content at top
    result_lines.extend(clean_content_lines)
    result_lines.append("")
    
    # 2. Basic author frontmatter in middle
    result_lines.append("---")
    if author_frontmatter_lines:
        result_lines.extend(author_frontmatter_lines)
    else:
        # Extract author info from content if available
        author_info = extract_author_info_from_content(content)
        if author_info:
            result_lines.append(f"author: {author_info.get('name', 'AI Assistant')}")
            result_lines.append(f"material: {material_name}")
            result_lines.append("component: text")
            result_lines.append("generated: 2025-09-13")
            result_lines.append("source: text")
    result_lines.append("---")
    result_lines.append("")
    
    # 3. AI analysis logs at bottom
    result_lines.append("---")
    result_lines.append("ai_detection_analysis:")
    result_lines.append(f"  score: {ai_result.score:.6f}")
    result_lines.append(f"  confidence: {ai_result.confidence:.6f}")
    result_lines.append(f'  classification: "{ai_result.classification}"')
    result_lines.append(f'  provider: "{ai_result.provider}"')
    result_lines.append(f"  processing_time: {ai_result.processing_time:.6f}")
    
    if ai_result.details:
        result_lines.append("  details:")
        for key, value in ai_result.details.items():
            if isinstance(value, dict):
                result_lines.append(f"    {key}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        result_lines.append(f'      {sub_key}: "{sub_value}"')
                    elif isinstance(sub_value, (int, float)):
                        if isinstance(sub_value, float):
                            result_lines.append(f"      {sub_key}: {sub_value:.6f}")
                        else:
                            result_lines.append(f"      {sub_key}: {sub_value}")
                    else:
                        result_lines.append(f"      {sub_key}: {sub_value}")
            else:
                if isinstance(value, str):
                    result_lines.append(f'    {key}: "{value}"')
                elif isinstance(value, (int, float)):
                    if isinstance(value, float):
                        result_lines.append(f"    {key}: {value:.6f}")
                    else:
                        result_lines.append(f"    {key}: {value}")
                else:
                    result_lines.append(f"    {key}: {value}")
    
    result_lines.append("---")
    
    return "\n".join(result_lines)


def extract_author_info_from_content(content: str) -> Optional[Dict[str, Any]]:
    """Extract author information from content frontmatter."""
    try:
        lines = content.split("\n")
        in_frontmatter = False
        author_info = {}

        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
                continue

            if in_frontmatter and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"')

                if key == "author":
                    author_info["name"] = value
                elif key == "persona_country":
                    author_info["country"] = value.lower()
                elif key == "author_id":
                    author_info["id"] = int(value) if value.isdigit() else 1

        if author_info:
            # FAIL-FAST: Author information must be complete - no defaults allowed
            if "id" not in author_info:
                raise ValueError("Author ID must be provided explicitly - no defaults allowed in fail-fast architecture")
            if "country" not in author_info:
                raise ValueError("Author country must be provided explicitly - no defaults allowed in fail-fast architecture")
            return author_info

    except Exception as e:
        logger.warning(f"Error extracting author info: {e}")

    return None


def extract_author_info_from_frontmatter_file(material_name: str) -> Optional[Dict[str, Any]]:
    """Extract author information by looking up material in materials.yaml and finding author in authors.json."""
    try:
        from .data_finder import find_material_data
        
        # Load materials data to get author_id
        materials_path = Path("data/materials.yaml")
        if not materials_path.exists():
            logger.warning(f"Materials file not found: {materials_path}")
            return None
            
        with open(materials_path, "r", encoding="utf-8") as f:
            import yaml
            materials_data = yaml.safe_load(f)
        
        # Find the material to get its author_id
        material_data = find_material_data(material_name, materials_data.get("materials", {}))
        if not material_data or "author_id" not in material_data:
            logger.warning(f"No author_id found for material: {material_name}")
            return None
            
        author_id = material_data["author_id"]
        
        # Load authors data
        authors_path = Path("components/author/authors.json")
        if not authors_path.exists():
            logger.warning(f"Authors file not found: {authors_path}")
            return None
            
        with open(authors_path, "r", encoding="utf-8") as f:
            authors_data = json.load(f)
        
        # Find the author by ID
        for author in authors_data.get("authors", []):
            if author.get("id") == author_id:
                return {
                    "name": author.get("name"),
                    "country": author.get("country", "").lower(),
                    "id": author.get("id"),
                    "title": author.get("title"),
                    "expertise": author.get("expertise")
                }
        
        logger.warning(f"Author with ID {author_id} not found")
        return None

    except Exception as e:
        logger.error(f"Error extracting author info from frontmatter file: {e}")
        return None


def update_content_with_comprehensive_analysis(
    content: str, ai_result, quality_result, material_name: str, iterations: int
) -> str:
    """Update content with comprehensive analysis using Global Metadata Delimiting Standard:
    
    Structure:
    <!-- CONTENT START -->
    [Clean markdown content]
    <!-- CONTENT END -->
    
    <!-- METADATA START -->
    ---
    [Basic author frontmatter]
    ---
    ---
    [Comprehensive optimization logs]
    ---
    <!-- METADATA END -->
    """
    try:
        # Extract only the clean content using our delimiter-aware function
        clean_content = extract_target_content_only(content)
        
        if not clean_content:
            logger.warning(f"No clean content extracted for {material_name}, using original")
            clean_content = content
        
        # Extract author frontmatter from original content
        author_frontmatter_lines = []
        lines = content.split("\n")
        
        # Look for existing frontmatter between --- delimiters
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            if in_frontmatter:
                author_frontmatter_lines.append(line)
        
        # If no frontmatter found, create basic author info
        if not author_frontmatter_lines:
            author_info = extract_author_info_from_content(content)
            if author_info:
                author_frontmatter_lines.append(f"author: {author_info.get('name', 'AI Assistant')}")
            else:
                author_frontmatter_lines.append("author: AI Assistant")
            author_frontmatter_lines.append(f"material: {material_name}")
            author_frontmatter_lines.append("component: text")
            author_frontmatter_lines.append("generated: 2025-09-13")
            author_frontmatter_lines.append("source: text")
        
        # Build content with Global Metadata Delimiting Standard
        result_lines = []
        
        # Content section with delimiters
        result_lines.append("<!-- CONTENT START -->")
        result_lines.append(clean_content)
        result_lines.append("<!-- CONTENT END -->")
        result_lines.append("")
        
        # Metadata section with delimiters
        result_lines.append("<!-- METADATA START -->")
        result_lines.append("---")
        result_lines.extend(author_frontmatter_lines)
        result_lines.append("---")
        result_lines.append("---")
        result_lines.append("---")
        
        # Add comprehensive optimization logs
        result_lines.append("ai_detection_analysis:")
        result_lines.append(f"  score: {ai_result.score:.6f}")
        result_lines.append(f"  confidence: {ai_result.confidence:.6f}")
        result_lines.append(f'  classification: "{ai_result.classification}"')
        result_lines.append(f'  provider: "{ai_result.provider}"')
        result_lines.append(f"  processing_time: {ai_result.processing_time:.6f}")
        result_lines.append(f"  optimization_iterations: {iterations}")
        result_lines.append("")
        
        result_lines.append("quality_analysis:")
        result_lines.append(f"  overall_score: {quality_result.overall_score:.6f}")
        result_lines.append(f"  formatting_score: {quality_result.formatting_score:.6f}")
        result_lines.append(f"  technical_score: {quality_result.technical_score:.6f}")
        result_lines.append(f"  authenticity_score: {quality_result.authenticity_score:.6f}")
        result_lines.append(f"  readability_score: {quality_result.readability_score:.6f}")
        result_lines.append(f"  believability_score: {quality_result.believability_score:.6f}")
        result_lines.append(f"  word_count: {quality_result.details.get('word_count', 0)}")
        result_lines.append(f'  author_country: "{quality_result.details.get("author_country", "")}"')
        
        # Add AI result details
        if ai_result.details:
            result_lines.append("  details:")
            for key, value in ai_result.details.items():
                if isinstance(value, dict):
                    result_lines.append(f"    {key}:")
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            result_lines.append(f'      {sub_key}: "{sub_value}"')
                        elif isinstance(sub_value, (int, float)):
                            if isinstance(sub_value, float):
                                result_lines.append(f"      {sub_key}: {sub_value:.6f}")
                            else:
                                result_lines.append(f"      {sub_key}: {sub_value}")
                        else:
                            result_lines.append(f"      {sub_key}: {sub_value}")
                else:
                    if isinstance(value, str):
                        result_lines.append(f'    {key}: "{value}"')
                    elif isinstance(value, (int, float)):
                        if isinstance(value, float):
                            result_lines.append(f"    {key}: {value:.6f}")
                        else:
                            result_lines.append(f"    {key}: {value}")
                    else:
                        result_lines.append(f"    {key}: {value}")
        
        result_lines.append("---")
        result_lines.append("<!-- METADATA END -->")
        
        return "\n".join(result_lines)

    except Exception as e:
        logger.error(f"Error updating comprehensive analysis with Global Metadata Delimiting Standard for {material_name}: {e}")
        return content
