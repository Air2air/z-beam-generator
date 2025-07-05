#!/usr/bin/env python3
"""Test the MDX validator fixes."""

import os
import sys

# Add the project root to the path first
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from generator.modules.mdx_validator import validate_mdx_output
    from generator.modules.logger import get_logger
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def test_mdx_validator():
    """Test the MDX validator with problematic content."""

    logger = get_logger("test_mdx_validator")

    # Test content with date issues and other problems
    test_content = """---
title: "Test Article"
publishedAt: "12/25/2023"
description: "Test description"
keywords: Electronics, Metal
---

# Test Content

This is a test with some <td><0.05 mm</td> problematic content.

And some &gt;5-8 m²/hour&lt; issues too.
"""

    print("=== Testing MDX Validator ===")
    print("Original content:")
    print(test_content)
    print("\n" + "=" * 50 + "\n")

    try:
        fixed_content, issues = validate_mdx_output(test_content)

        print("Fixed content:")
        print(fixed_content)
        print("\n" + "=" * 30 + "\n")

        print("Issues found and fixed:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")

        print(f"\nTotal issues fixed: {len(issues)}")

        logger.info("MDX validator test completed successfully")

    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"MDX validator test failed: {e}")


if __name__ == "__main__":
    test_mdx_validator()
