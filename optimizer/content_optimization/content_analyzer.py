"""
Content Analyzer Module

Handles content analysis, author extraction, and content formatting
for optimization workflows.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def update_content_with_ai_analysis(content: str, ai_result, material_name: str) -> str:
    """Update content with AI detection analysis in the target format:
    1. Clean markdown content at top
    2. Basic author frontmatter in middle
    3. AI analysis logs at bottom
    """
    try:
        lines = content.split("\n")
        
        # Extract different sections
        clean_content_lines = []
        author_frontmatter_lines = []
        existing_logs = []
        
        # Find sections in content
        in_frontmatter = False
        in_logs = False
        current_section = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for frontmatter delimiter
            if line.strip() == "---":
                if not in_frontmatter and not in_logs:
                    # First --- - could be start of author frontmatter or logs
                    in_frontmatter = True
                    i += 1
                    continue
                elif in_frontmatter:
                    # End of frontmatter
                    author_frontmatter_lines = current_section.copy()
                    current_section = []
                    in_frontmatter = False
                    i += 1
                    continue
                elif in_logs:
                    # End of logs
                    existing_logs = current_section.copy()
                    current_section = []
                    in_logs = False
                    i += 1
                    continue
            
            # Check for optimization logs start
            if line.strip().startswith("ai_detection_analysis:") or line.strip().startswith("# Optimization Analysis"):
                in_logs = True
                if current_section:
                    clean_content_lines.extend(current_section)
                current_section = [line]
                i += 1
                continue
            
            # Collect lines based on current section
            if in_frontmatter or in_logs:
                current_section.append(line)
            else:
                clean_content_lines.append(line)
            
            i += 1
        
        # Handle any remaining content
        if current_section and not in_frontmatter and not in_logs:
            clean_content_lines.extend(current_section)
        elif current_section and in_logs:
            existing_logs.extend(current_section)
        
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
            # Extract author info from AI result if available
            author_info = extract_author_info_from_content(content)
            if author_info:
                result_lines.append(f"author: {author_info.get('name', 'AI Assistant')}")
                result_lines.append(f"material: {material_name}")
                result_lines.append("component: text")
                result_lines.append("generated: 2025-09-11")
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

    except Exception as e:
        logger.error(f"Error updating content with target format for {material_name}: {e}")
        return content


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
    """Update content with comprehensive analysis in the target format:
    1. Clean markdown content at top
    2. Basic author frontmatter in middle  
    3. Comprehensive optimization logs at bottom
    """
    try:
        lines = content.split("\n")
        
        # Extract different sections
        clean_content_lines = []
        author_frontmatter_lines = []
        
        # Find sections in content
        in_frontmatter = False
        in_logs = False
        current_section = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for frontmatter delimiter
            if line.strip() == "---":
                if not in_frontmatter and not in_logs:
                    # First --- - could be start of author frontmatter or logs
                    in_frontmatter = True
                    i += 1
                    continue
                elif in_frontmatter:
                    # End of frontmatter
                    author_frontmatter_lines = current_section.copy()
                    current_section = []
                    in_frontmatter = False
                    i += 1
                    continue
                elif in_logs:
                    # End of logs - ignore existing logs
                    current_section = []
                    in_logs = False
                    i += 1
                    continue
            
            # Check for optimization logs start
            if (line.strip().startswith("ai_detection_analysis:") or 
                line.strip().startswith("# Optimization Analysis") or
                line.strip().startswith("quality_analysis:")):
                in_logs = True
                if current_section:
                    clean_content_lines.extend(current_section)
                current_section = []  # Start collecting logs to ignore
                i += 1
                continue
            
            # Collect lines based on current section
            if in_frontmatter:
                current_section.append(line)
            elif not in_logs:
                clean_content_lines.append(line)
            # Ignore lines in existing logs
            
            i += 1
        
        # Handle any remaining content
        if current_section and not in_frontmatter and not in_logs:
            clean_content_lines.extend(current_section)
        
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
            # Extract author info or use defaults
            author_info = extract_author_info_from_content(content)
            if author_info:
                result_lines.append(f"author: {author_info.get('name', 'AI Assistant')}")
            else:
                result_lines.append("author: AI Assistant")
            result_lines.append(f"material: {material_name}")
            result_lines.append("component: text")
            result_lines.append("generated: 2025-09-11")
            result_lines.append("source: text")
        result_lines.append("---")
        result_lines.append("")
        
        # 3. Comprehensive optimization logs at bottom
        result_lines.append("---")
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
        
        return "\n".join(result_lines)

    except Exception as e:
        logger.error(f"Error updating comprehensive analysis with target format for {material_name}: {e}")
        return content
