"""Slug generation utilities."""

import re

def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    slug = text.lower().replace(" ", "-").replace("/", "-")
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    return slug