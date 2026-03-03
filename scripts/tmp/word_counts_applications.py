import re
from pathlib import Path

import yaml

FILE_PATH = "/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/applications/defense-laser-cleaning-applications.yaml"
TEXT_FIELD_CONFIG = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/generation/text_field_config.yaml"


def word_count(value: str) -> int:
    return len(re.findall(r"\b\w+\b", value))


def get_nested(data, path):
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_text_values(data):
    targets = {
        "pageTitle": data.get("pageTitle"),
        "pageDescription": data.get("pageDescription"),
        "relatedMaterialsTitle": data.get("relatedMaterialsTitle"),
        "contaminatedByTitle": data.get("contaminatedByTitle"),
        "relationships.discovery.relatedMaterials._section.sectionDescription": get_nested(
            data,
            ["relationships", "discovery", "relatedMaterials", "_section", "sectionDescription"],
        ),
        "relationships.interactions.contaminatedBy._section.sectionDescription": get_nested(
            data,
            ["relationships", "interactions", "contaminatedBy", "_section", "sectionDescription"],
        ),
    }

    faq_items = (
        data.get("faq", {}).get("items")
        if isinstance(data.get("faq"), dict)
        else None
    )
    if isinstance(faq_items, list):
        for idx, item in enumerate(faq_items, start=1):
            title = item.get("title") if isinstance(item, dict) else None
            content = item.get("content") if isinstance(item, dict) else None
            targets[f"faq.items[{idx}].title"] = title
            targets[f"faq.items[{idx}].content"] = content

    return targets


def main():
    data = yaml.safe_load(Path(FILE_PATH).read_text())
    text_config = yaml.safe_load(Path(TEXT_FIELD_CONFIG).read_text())

    base_length_multiplier = text_config["defaults"]["base_length_multiplier"]
    rand_min = text_config["randomization_range"]["min_factor"]
    rand_max = text_config["randomization_range"]["max_factor"]
    base_lengths = {
        key: value.get("base_length")
        for key, value in text_config.get("fields", {}).items()
        if isinstance(value, dict) and "base_length" in value
    }

    targets = collect_text_values(data)
    print("Word counts and guidance (text_field_config.yaml):")
    for key, value in targets.items():
        if not value:
            print(f"- {key}: MISSING")
            continue
        wc = word_count(str(value))
        base_key = key.split(".")[-1]
        base_length = base_lengths.get(base_key)
        if key.startswith("faq.items["):
            base_length = base_lengths.get("faqAnswer") if key.endswith(".content") else base_lengths.get("faqQuestion")
        if base_length is None:
            print(f"- {key}: {wc} words (no configured base length)")
            continue
        low = base_length * base_length_multiplier * rand_min
        high = base_length * base_length_multiplier * rand_max
        status = "OK"
        if wc < low:
            status = f"UNDER ({wc} < {low:.1f})"
        elif wc > high:
            status = f"OVER ({wc} > {high:.1f})"
        print(f"- {key}: {wc} words -> {status}")


if __name__ == "__main__":
    main()
