#!/usr/bin/env python3
"""
Mock Caption Component Generator for Testing
"""

from typing import Any, Dict, Optional

from utils.component_base import ComponentResult


class MockCaptionComponentGenerator:
    """Mock generator for caption component testing."""

    def __init__(self):
        self.call_count = 0

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate mock caption component content."""
        self.call_count += 1

        mock_content = f"**{material_name}** surface (left) before cleaning, showing contaminants.\n\n**After laser cleaning** (right) at 1064 nm, 10 W, 100 ns pulse duration, and 200 µm spot size, achieving complete contaminant removal."

        return ComponentResult(
            component_type="caption",
            content=mock_content,
            success=True,
        )
