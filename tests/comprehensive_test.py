#!/usr/bin/env python3
"""
Comprehensive test for MDX validation patterns.
"""

from generator.modules.mdx_validator import validate_mdx_output


def test_comprehensive_patterns():
    """Test all the patterns we've implemented."""

    test_content = """---
title: "Test Article"
tags:
  - "- "material""
  - "silver"
keywords:
  - "image: "/images/test.jpg""
---

# Test Content

## Table with problematic patterns
<table>
  <tr>
    <td>Heat-Affected Zone</td>
    <td&lt;0.05 mm</td>
    <td>Critical</td>
  </tr>
  <tr>
    <td>Removal Rate</td>
    <td&gt;5-8 m²/hour</td>
    <td>Lower than tin</td>
  </tr>
  <tr>
    <td>Temperature</td>
    <td&amp;High temp</td>
    <td>Notes</td>
  </tr>
</table>

## Other problematic patterns
- Speed >10 mm/s is too fast
- Temperature <500°C is too low
- Pressure >=20 bar is recommended
- Flow <=5 L/min is optimal

## Text with unescaped symbols
The process uses {variable} substitution & other issues.
"""

    print("Testing comprehensive MDX validation...")
    print("=" * 60)

    fixed_content, issues = validate_mdx_output(test_content)

    print(f"Found and fixed {len(issues)} issues:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

    print("\n" + "=" * 60)
    print("FIXED CONTENT:")
    print("=" * 60)
    print(fixed_content)

    # Verify critical fixes
    print("\n" + "=" * 60)
    print("VERIFICATION:")
    print("=" * 60)

    checks = [
        ("<td&lt;", "<td>&lt;", "HTML entity in tag fixed"),
        ("<td&gt;", "<td>&gt;", "HTML entity in tag fixed"),
        ("<td&amp;", "<td>&amp;", "HTML entity in tag fixed"),
        ('"- "material""', '"material"', "YAML quote issue fixed"),
        (
            'image: "/images/test.jpg""',
            'image: "/images/test.jpg"',
            "YAML nested quote fixed",
        ),
    ]

    for original, expected, description in checks:
        if original in test_content and expected in fixed_content:
            print(f"✅ {description}")
        elif original not in test_content:
            print(f"ℹ️  {description} - original pattern not found")
        else:
            print(f"❌ {description} - fix may not have worked")


if __name__ == "__main__":
    test_comprehensive_patterns()
