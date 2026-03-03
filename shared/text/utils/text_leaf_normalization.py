"""Shared helpers for normalizing generated text leaf values.

Used by source save, frontmatter sync, backfill generation, and export tasks.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional


def normalize_text_output(content: Any) -> Any:
    """Normalize plain text output by removing common wrapper artifacts."""
    if not isinstance(content, str):
        return content

    text = content.strip()
    if not text:
        return text

    if text.startswith('{') and text.endswith('}'):
        try:
            payload = json.loads(text)
            extracted = (
                payload.get('sectionContent')
                or payload.get('sectionDescription')
                or payload.get('description')
            )
            if isinstance(extracted, str) and extracted.strip():
                text = extracted.strip()
        except Exception:
            pass

    inline_description = re.split(r"(?i)(?:^|\n)\s*(?:#{1,6}\s*)?description\s*:?[ \t]*", text, maxsplit=1)
    if len(inline_description) == 2 and inline_description[1].strip():
        text = inline_description[1].strip()

    inline_markdown_description = re.split(r"(?i)#{1,6}\s*description\s*:?[ \t]*", text, maxsplit=1)
    if len(inline_markdown_description) == 2 and inline_markdown_description[1].strip():
        text = inline_markdown_description[1].strip()

    text = re.sub(r"(?im)^\s*#{1,6}\s*title\s*:?[ \t]*", "", text)
    text = re.sub(r"(?im)^\s*#{1,6}\s*description\s*:?[ \t]*", "", text)
    text = re.sub(r"(?im)^\s*title\s*:?[ \t]*", "", text)
    text = re.sub(r"(?im)^\s*description\s*:?[ \t]*", "", text)

    inline_description_tail = re.split(r"(?i)\bdescription\s*:\s*", text, maxsplit=1)
    if (
        len(inline_description_tail) == 2
        and inline_description_tail[1].strip()
        and len(inline_description_tail[0].strip()) <= 120
    ):
        text = inline_description_tail[1].strip()

    text = re.sub(r"\A\s*#{1,6}\s*", "", text)
    text = re.sub(r"\A\s*(?:title|description)\s*:?[ \t]*", "", text, flags=re.IGNORECASE)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) >= 2:
        first = lines[0]
        if (
            len(first) <= 90
            and not re.search(r"[.!?]$", first)
            and (
                re.search(r"(?i)laser\s+cleaning", first)
                or re.search(r"(?i)overview|guide|summary", first)
            )
        ):
            lines = lines[1:]
    text = " ".join(lines)

    text = re.sub(
        r"^\s*(?:[A-Z][A-Za-z0-9()&/\-+,]*\s+){0,8}Laser\s+Cleaning(?:\s+(?:Overview|Guide|Description))?\s+",
        "",
        text,
    )

    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def coerce_text_leaf_value(value: Any, leaf_key: str, field_label: Optional[str] = None) -> str:
    """Coerce known text leaf payloads to normalized strings; fail fast on invalid content."""
    target = field_label or leaf_key

    if isinstance(value, dict):
        if leaf_key in {'sectionTitle', 'pageTitle', 'page_title'}:
            ordered_keys = ('sectionTitle', 'title', 'name', 'label')
        elif leaf_key in {'sectionDescription', 'pageDescription', 'page_description', 'description'}:
            ordered_keys = ('sectionDescription', 'description', 'sectionContent', 'content', 'text', 'summary')
        else:
            ordered_keys = ('sectionContent', 'sectionDescription', 'description', 'content', 'text', 'summary')

        extracted = None
        for key in ordered_keys:
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                extracted = candidate
                break

        if extracted is None:
            raise ValueError(
                f"Expected text for {target}, received object without extractable text keys"
            )
        value = extracted

    if not isinstance(value, str):
        raise ValueError(f"Expected string for {target}, received {type(value).__name__}")

    if leaf_key in {'pageTitle', 'page_title'}:
        title = value.strip()
        title = re.sub(r"\A\s*#{1,6}\s*", "", title)
        title = re.sub(r"\A\s*title\s*:?\s*", "", title, flags=re.IGNORECASE)
        title_lines = [line.strip() for line in title.splitlines() if line.strip()]
        return re.sub(r"\s{2,}", " ", " ".join(title_lines)).strip()

    normalized = normalize_text_output(value)
    if not isinstance(normalized, str):
        raise ValueError(f"Normalization failed for {target}: expected string output")

    if leaf_key in {'sectionDescription', 'pageDescription', 'page_description', 'description'}:
        normalized = re.sub(r"\s+(?:this|that|these|those|it)\.\s*$", "", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"[,:;]\s*$", ".", normalized)
        normalized = normalized.strip()
        if normalized and normalized[-1] not in '.!?':
            normalized += '.'

    return normalized
