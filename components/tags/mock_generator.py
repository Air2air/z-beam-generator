#!/usr/bin/env python3
"""
Mock Tags Component Generator for testing.
"""

from typing import Dict, Optional

from generators.component_generators import ComponentResult


class MockTagsComponentGenerator:
    """Mock implementation for tags component testing"""

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate mock tags for testing"""
        # Extract material info
        material_name_clean = material_name.lower().replace(" ", "-")
        category = material_data.get("category", "material")
        
        # Get author slug
        author_slug = "expert"
        if author_info:
            author_name = author_info.get("name", "").strip()
            if author_name:
                author_slug = author_name.lower().replace(" ", "-").replace("dr.", "").replace("prof.", "")
        
        # Generate deterministic mock tags
        mock_tags = [
            material_name_clean,
            "ablation", 
            "cleaning",
            "laser",
            category,
            "non-contact",
            "industrial",
            author_slug
        ]
        
        # Remove duplicates and ensure exactly 8 tags
        unique_tags = []
        for tag in mock_tags:
            if tag not in unique_tags:
                unique_tags.append(tag)
        
        # Fill to 8 tags if needed
        while len(unique_tags) < 8:
            unique_tags.append("precision")
        
        content = ", ".join(unique_tags[:8])
        
        return ComponentResult(
            component_type="tags",
            content=content,
            success=True
        )