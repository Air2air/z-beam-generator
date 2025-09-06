#!/usr/bin/env python3
"""
Frontmatter Component Post-Processor

Component-specific post-processing logic for frontmatter components.
"""

import logging
from typing import Any, Dict

import yaml

from .utils import (


        # Extract YAML content
        if not content.startswith("---"):
            return {"error": "Not valid frontmatter format"}

        yaml_end = content.find("---", 3)
        if yaml_end == -1:
            return {"error": "Frontmatter not properly closed"}

        yaml_content = content[3:yaml_end].strip()
        frontmatter_data = yaml.safe_load(yaml_content)

        if not frontmatter_data:
            return {"error": "Empty frontmatter data"}

        # Get completeness analysis
        completeness = validate_frontmatter_properties_completeness(frontmatter_data)

        # Add additional metrics
        summary = {
            "total_fields": len(frontmatter_data),
            "has_properties": "properties" in frontmatter_data,
            "has_chemical_props": "chemicalProperties" in frontmatter_data,
            "has_category": "category" in frontmatter_data,
            "completeness_score": completeness["completeness"],
            "missing_sections": completeness["missing_sections"],
            "missing_properties": completeness["missing_properties"],
            "recommendations": completeness["recommendations"],
        }

        return summary

    except Exception as e:
        return {"error": f"Analysis failed: {e}"}
