"""
MDX output validation and sanitization module.
Ensures generated content is compatible with Next.js MDX parser.
"""

import re
from typing import List, Tuple, Optional
from generator.modules.logger import get_logger


class MDXValidator:
    """Validates and sani        # If all else fails, try to use current date as fallback
    try:
        return datetime.now().strftime('%Y-%m-%d')
    except Exception:
        return None MDX content for Next.js compatibility."""

    def __init__(self):
        self.logger = get_logger("mdx_validator")

        # Patterns that cause MDX parsing issues
        self.problematic_patterns = [
            # HTML entities immediately after opening tags (e.g., <td&gt; -> <td>&gt;)
            (
                r"<([a-zA-Z][a-zA-Z0-9]*)((?:&[a-zA-Z0-9]+;|&#[0-9]+;|&#x[0-9a-fA-F]+;))",
                r"<\1>\2",
            ),
            # Less than symbol followed by number (e.g., <0.05)
            (r"<(\d+\.?\d*)", r"&lt;\1"),
            # Greater than symbol followed by number (e.g., >5.0)
            (r">(\d+\.?\d*)", r"&gt;\1"),
            # Less than or equal to (e.g., <=10)
            (r"<=(\d+\.?\d*)", r"&le;\1"),
            # Greater than or equal to (e.g., >=20)
            (r">=(\d+\.?\d*)", r"&ge;\1"),
            # Unescaped angle brackets in table cells
            (r"<td>([^<]*)<([^>]*)</td>", r"<td>\1&lt;\2</td>"),
            (r"<td>([^<]*)>([^>]*)</td>", r"<td>\1&gt;\2</td>"),
        ]

        # Additional patterns for common issues
        self.html_escape_patterns = [
            # Ampersand (except already escaped entities) - simplified pattern
            (r"&(?![a-zA-Z0-9#]+;)", r"&amp;"),
        ]

    def validate_and_fix_content(self, content: str) -> Tuple[str, List[str]]:
        """
        Validate and fix MDX content for Next.js compatibility.

        Args:
            content: Raw MDX content string

        Returns:
            Tuple of (fixed_content, list_of_issues_found)
        """
        if not content:
            return content, []

        issues_found = []
        fixed_content = content

        # First, validate and fix YAML frontmatter
        fixed_content, yaml_issues = self.validate_yaml_frontmatter(fixed_content)
        issues_found.extend(yaml_issues)

        # Fix problematic patterns
        for pattern, replacement in self.problematic_patterns:
            matches = re.findall(pattern, fixed_content)
            if matches:
                issues_found.append(
                    f"Fixed pattern '{pattern}' - found {len(matches)} occurrences"
                )
                fixed_content = re.sub(pattern, replacement, fixed_content)

        # Fix HTML escape issues
        for pattern, replacement in self.html_escape_patterns:
            matches = re.findall(pattern, fixed_content)
            if matches:
                issues_found.append(
                    f"Fixed HTML escape pattern '{pattern}' - found {len(matches)} occurrences"
                )
                fixed_content = re.sub(pattern, replacement, fixed_content)

        # Check for common MDX issues
        additional_issues = self._check_additional_issues(fixed_content)
        issues_found.extend(additional_issues)

        if issues_found:
            self.logger.info(f"MDX validation fixed {len(issues_found)} issues")
            for issue in issues_found:
                self.logger.debug(f"  - {issue}")

        return fixed_content, issues_found

    def _check_additional_issues(self, content: str) -> List[str]:
        """Check for additional potential MDX issues."""
        issues = []

        # Check for unclosed tags in tables
        table_section = self._extract_table_sections(content)
        for table in table_section:
            if self._has_unclosed_tags(table):
                issues.append("Found potentially unclosed HTML tags in table")

        # Check for invalid JSX attribute names
        invalid_attrs = re.findall(r"<[a-zA-Z][^>]*\s(\d[a-zA-Z]*)\s*=", content)
        if invalid_attrs:
            issues.append(
                f"Found invalid JSX attributes starting with numbers: {invalid_attrs}"
            )

        # Check for unescaped curly braces outside of JSX
        unescaped_braces = re.findall(r"(?<!`){(?![a-zA-Z_$])", content)
        if unescaped_braces:
            issues.append(
                f"Found unescaped curly braces: {len(unescaped_braces)} occurrences"
            )

        return issues

    def _extract_table_sections(self, content: str) -> List[str]:
        """Extract table sections from content."""
        table_pattern = r"<table[^>]*>.*?</table>"
        return re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)

    def _has_unclosed_tags(self, html: str) -> bool:
        """Check if HTML has unclosed tags."""
        # Simple check for common unclosed tags
        tag_counts = {}

        # Find opening tags
        opening_tags = re.findall(r"<([a-zA-Z][a-zA-Z0-9]*)[^>]*(?<!/)>", html)
        for tag in opening_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Find closing tags
        closing_tags = re.findall(r"</([a-zA-Z][a-zA-Z0-9]*)>", html)
        for tag in closing_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) - 1

        # Check if any tags are unbalanced
        return any(count != 0 for count in tag_counts.values())

    def validate_frontmatter(self, frontmatter: str) -> Tuple[str, List[str]]:
        """
        Validate and fix YAML frontmatter.

        Args:
            frontmatter: YAML frontmatter string

        Returns:
            Tuple of (fixed_frontmatter, list_of_issues_found)
        """
        issues = []
        fixed_frontmatter = frontmatter

        # Fix common YAML issues
        # Ensure proper date format
        date_pattern = r'publishedAt:\s*"([^"]*)"'
        date_match = re.search(date_pattern, fixed_frontmatter)
        if date_match:
            date_value = date_match.group(1)
            if not self._is_valid_date_format(date_value):
                issues.append(f"Invalid date format: {date_value}")
                # Try to fix common date format issues
                fixed_date = self._fix_date_format(date_value)
                if fixed_date:
                    fixed_frontmatter = re.sub(
                        date_pattern, f'publishedAt: "{fixed_date}"', fixed_frontmatter
                    )
                    issues.append(f"Fixed date format to: {fixed_date}")

        # Ensure arrays are properly formatted
        array_fields = ["tags", "keywords", "industries"]
        for field in array_fields:
            pattern = rf"{field}:\s*([^\n]*)"
            match = re.search(pattern, fixed_frontmatter)
            if (
                match
                and match.group(1).strip()
                and not match.group(1).strip().startswith("[")
            ):
                # Fix non-array format
                value = match.group(1).strip()
                if value and value != "[]":
                    issues.append(f"Fixed {field} format from string to array")
                    fixed_frontmatter = re.sub(
                        pattern, f'{field}:\n  - "{value}"', fixed_frontmatter
                    )

        return fixed_frontmatter, issues

    def _is_valid_date_format(self, date_value: str) -> bool:
        """
        Check if a date string is in a valid ISO format.

        Args:
            date_value: The date string to validate

        Returns:
            True if the date is valid, False otherwise
        """
        # Common valid date formats
        valid_patterns = [
            r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?$",  # ISO 8601
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?[+-]\d{2}:\d{2}$",  # ISO with timezone
        ]

        for pattern in valid_patterns:
            if re.match(pattern, date_value):
                # Try to parse the date to ensure it's actually valid
                try:
                    from datetime import datetime

                    if "T" in date_value:
                        # Handle ISO format
                        date_part = date_value.split("T")[0]
                        datetime.strptime(date_part, "%Y-%m-%d")
                    else:
                        datetime.strptime(date_value, "%Y-%m-%d")
                    return True
                except ValueError:
                    continue

        return False

    def _fix_date_format(self, date_value: str) -> Optional[str]:
        """
        Attempt to fix common date format issues.

        Args:
            date_value: The problematic date string

        Returns:
            Fixed date string or None if cannot be fixed
        """
        from datetime import datetime

        # Common problematic patterns and their fixes
        fix_patterns = [
            # MM/DD/YYYY -> YYYY-MM-DD
            (r"^(\d{1,2})/(\d{1,2})/(\d{4})$", r"\3-\1-\2"),
            # DD/MM/YYYY -> YYYY-MM-DD (assume DD/MM format)
            (r"^(\d{1,2})/(\d{1,2})/(\d{4})$", r"\3-\2-\1"),
            # YYYY/MM/DD -> YYYY-MM-DD
            (r"^(\d{4})/(\d{1,2})/(\d{1,2})$", r"\1-\2-\3"),
            # Remove extra quotes or spaces
            (r'^[\"\s]*([^"]*?)[\"\s]*$', r"\1"),
        ]

        cleaned_date = date_value.strip()

        for pattern, replacement in fix_patterns:
            match = re.match(pattern, cleaned_date)
            if match:
                try:
                    # Try to create a properly formatted date
                    fixed = re.sub(pattern, replacement, cleaned_date)
                    # Ensure proper zero padding
                    parts = fixed.split("-")
                    if len(parts) == 3:
                        year, month, day = parts
                        formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        # Validate the result
                        datetime.strptime(formatted_date, "%Y-%m-%d")
                        return formatted_date
                except (ValueError, IndexError):
                    continue

        # If all else fails, try to use current date as fallback
        try:
            return datetime.now().strftime("%Y-%m-%d")
        except Exception:
            return None

    def validate_yaml_frontmatter(self, content: str) -> Tuple[str, List[str]]:
        """
        Validate and fix YAML frontmatter issues.

        Args:
            content: The full MDX content

        Returns:
            Tuple of (fixed_content, list_of_issues_found)
        """
        issues = []

        # Check if content starts with frontmatter
        if not content.startswith("---\n"):
            return content, issues

        # Find the end of frontmatter
        end_pos = content.find("\n---", 4)
        if end_pos == -1:
            issues.append("YAML frontmatter not properly closed with ---")
            return content, issues

        frontmatter = content[4:end_pos]
        rest_content = content[end_pos:]

        # Fix common YAML issues
        yaml_fixes = [
            # Fix malformed quotes in tags/lists (e.g., "- "material"" -> "material")
            (r'^\s*-\s*"-\s*"([^"]+)""', r'  - "\1"'),
            # Fix nested quotes in array items (e.g., "image: "..." " -> image: "...")
            (r'^\s*-\s*"([^:]+):\s*"([^"]+)""', r'\1: "\2"'),
            # Fix empty array items that should be on separate lines
            (r':\s*\n\s*-\s*"[^"]*"[^"]*"', lambda m: m.group(0).replace('""', '"')),
        ]

        fixed_frontmatter = frontmatter
        for pattern, replacement in yaml_fixes:
            old_frontmatter = fixed_frontmatter
            fixed_frontmatter = re.sub(
                pattern, replacement, fixed_frontmatter, flags=re.MULTILINE
            )
            if old_frontmatter != fixed_frontmatter:
                issues.append(f"Fixed YAML syntax issue with pattern: {pattern}")

        # Reconstruct content
        fixed_content = "---\n" + fixed_frontmatter + rest_content

        return fixed_content, issues


def validate_mdx_output(content: str) -> Tuple[str, List[str]]:
    """
    Convenience function to validate and fix MDX content.

    Args:
        content: Full MDX content including frontmatter

    Returns:
        Tuple of (fixed_content, list_of_issues_found)
    """
    validator = MDXValidator()

    # Split frontmatter and content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body_content = parts[2]

            # Validate frontmatter
            fixed_frontmatter, fm_issues = validator.validate_frontmatter(frontmatter)

            # Validate content
            fixed_content, content_issues = validator.validate_and_fix_content(
                body_content
            )

            # Reconstruct
            full_content = f"---{fixed_frontmatter}---{fixed_content}"
            all_issues = fm_issues + content_issues

            return full_content, all_issues

    # No frontmatter, just validate content
    return validator.validate_and_fix_content(content)
