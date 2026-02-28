import json
import pathlib

import yaml


def shape(value):
    if value is None:
        return "missing"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "object"
    return "other"


source_path = pathlib.Path("data/applications/Applications.yaml")
frontmatter_dir = pathlib.Path("../z-beam/frontmatter/applications")

with source_path.open() as f:
    source_data = yaml.safe_load(f) or {}

apps = source_data.get("applications", {}) if isinstance(source_data, dict) else {}

source_counts = {
    "total": len(apps),
    "missing": 0,
    "string": 0,
    "list": 0,
    "object": 0,
    "other": 0,
}
source_examples = {"missing": [], "string": [], "list": [], "other": []}

for slug, record in apps.items():
    faq_value = record.get("faq") if isinstance(record, dict) else None
    faq_shape = shape(faq_value)
    source_counts[faq_shape] += 1
    if faq_shape in source_examples:
        source_examples[faq_shape].append(slug)

frontmatter_counts = {
    "files": 0,
    "missing": 0,
    "string": 0,
    "list": 0,
    "object": 0,
    "other": 0,
}
frontmatter_examples = {"missing": [], "string": [], "list": [], "other": []}

if frontmatter_dir.exists():
    for file_path in sorted(frontmatter_dir.glob("*.yaml")):
        frontmatter_counts["files"] += 1
        with file_path.open() as f:
            fm_data = yaml.safe_load(f) or {}
        faq_value = fm_data.get("faq") if isinstance(fm_data, dict) else None
        faq_shape = shape(faq_value)
        frontmatter_counts[faq_shape] += 1
        if faq_shape in frontmatter_examples:
            frontmatter_examples[faq_shape].append(file_path.stem)

print("SOURCE_COUNTS", json.dumps(source_counts, indent=2))
print("FRONTMATTER_COUNTS", json.dumps(frontmatter_counts, indent=2))
for key in ("string", "list", "missing", "other"):
    if source_examples[key]:
        print(f"SOURCE_{key.upper()}_EXAMPLES", ", ".join(source_examples[key][:20]))
for key in ("string", "list", "missing", "other"):
    if frontmatter_examples[key]:
        print(f"FRONTMATTER_{key.upper()}_EXAMPLES", ", ".join(frontmatter_examples[key][:20]))
