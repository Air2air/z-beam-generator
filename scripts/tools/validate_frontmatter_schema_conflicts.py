#!/usr/bin/env python3
"""Fail-fast validator for frontmatter schema property/patternProperties contradictions."""

import json
import re
import sys
from pathlib import Path


def main() -> int:
    schema_path = Path("data/schemas/frontmatter.json")
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return 1

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    properties = schema.get("properties", {})
    pattern_properties = schema.get("patternProperties", {})

    conflicts = []
    for prop_name in properties:
        for pattern, rule in pattern_properties.items():
            if re.match(pattern, prop_name):
                # Explicit allowed exception
                if prop_name == "page_description" and pattern == r"^(?!page_description$).*_description$":
                    continue
                if isinstance(rule, dict) and rule.get("not") == {}:
                    conflicts.append((prop_name, pattern))

    if conflicts:
        print("❌ Schema contradiction detected:")
        for prop, pattern in conflicts:
            print(f"   - property '{prop}' is forbidden by pattern '{pattern}'")
        return 1

    print("✅ No property/patternProperties contradictions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
