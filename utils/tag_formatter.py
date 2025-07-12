"""
Tag formatting utilities for Z-Beam Generator
"""
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("zbeam.tag_formatter")

def format_tags(tags: List[str]) -> List[str]:
    """
    Simple tag formatter: lowercase, strip, deduplicate.
    Returns a sorted list of tags.
    """
    logger.info("Formatting tags: %s", tags)
    formatted = sorted({str(tag).strip().lower() for tag in tags if tag})
    logger.info("Formatted tags: %s", formatted)
    return formatted

class TagFormatter:
    """Format tags according to configuration"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("tag_formatting", {})

    def format_tags(self, tags: List[str]) -> str:
        logger.info("Formatting tags with config: %s", self.config)
        formatted = list({str(tag).strip().lower() for tag in tags if tag})
        formatted_tags = [self._format_case(tag) for tag in formatted]
        if self.config.get("sort_tags", True):
            formatted_tags.sort()
        style = self.config.get("style", "hashtag")
        if style == "hashtag":
            return self._format_hashtag_style(formatted_tags)
        elif style == "plain":
            return self._format_plain_style(formatted_tags)
        elif style == "bullet":
            return self._format_bullet_style(formatted_tags)
        elif style == "numbered":
            return self._format_numbered_style(formatted_tags)
        else:
            return self._format_hashtag_style(formatted_tags)

    def _format_case(self, tag: str) -> str:
        case_format = self.config.get("case_format", "title")
        if case_format == "title":
            return tag.title()
        elif case_format == "lower":
            return tag.lower()
        elif case_format == "upper":
            return tag.upper()
        elif case_format == "camel":
            return self._to_camel_case(tag)
        else:
            return tag

    def _to_camel_case(self, text: str) -> str:
        words = re.split(r'[\s\-_]+', text)
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    def _format_hashtag_style(self, tags: List[str]) -> str:
        prefix = self.config.get("prefix", "#")
        suffix = self.config.get("suffix", "")
        remove_spaces = self.config.get("remove_spaces", True)
        separator = self.config.get("separator", ", ")
        max_per_line = self.config.get("max_tags_per_line", 6)
        formatted = []
        for tag in tags:
            clean_tag = tag.replace(" ", "") if remove_spaces else tag
            formatted.append(f"{prefix}{clean_tag}{suffix}")
        if max_per_line and len(formatted) > max_per_line:
            lines = []
            for i in range(0, len(formatted), max_per_line):
                line_tags = formatted[i:i+max_per_line]
                lines.append(separator.join(line_tags))
            return "\n".join(lines)
        else:
            return separator.join(formatted)

    def _format_plain_style(self, tags: List[str]) -> str:
        separator = self.config.get("separator", ", ")
        return separator.join(tags)

    def _format_bullet_style(self, tags: List[str]) -> str:
        return "\n".join([f"• {tag}" for tag in tags])

    def _format_numbered_style(self, tags: List[str]) -> str:
        return "\n".join([f"{i+1}. {tag}" for i, tag in enumerate(tags)])

def format_tags_for_article(tags: List[str], config: Dict[str, Any]) -> str:
    """Format tags for article output using TagFormatter"""
    formatter = TagFormatter(config)
    return formatter.format_tags(tags)