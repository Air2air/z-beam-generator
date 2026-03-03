from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
domains = ("applications", "materials", "contaminants", "compounds", "settings")


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text()) or {}


def save_yaml(path: Path, payload):
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=120))


def expected_child(key: str) -> str:
    if key.endswith(".sectionTitle"):
        return "sectionTitle"
    if key.endswith(".sectionDescription"):
        return "sectionDescription"
    return "prompt"

for domain in domains:
    path = root / "domains" / domain / "prompts" / "text_prompt.yaml"
    payload = load_yaml(path)
    field_prompts = payload.get("field_prompts") or {}

    converted = {}
    for raw_key, raw_val in field_prompts.items():
        if not isinstance(raw_key, str) or not raw_key.strip():
            continue
        key = raw_key.strip()
        target_child = expected_child(key)

        text_val = None
        if isinstance(raw_val, dict):
            for candidate in (target_child, "prompt", "sectionDescription", "sectionTitle"):
                maybe = raw_val.get(candidate)
                if isinstance(maybe, str) and maybe.strip():
                    text_val = " ".join(maybe.strip().split())
                    break
        elif isinstance(raw_val, str) and raw_val.strip():
            text_val = " ".join(raw_val.strip().split())

        if isinstance(text_val, str) and text_val:
            converted[key] = {target_child: text_val}

    payload["field_prompts"] = dict(sorted(converted.items()))
    save_yaml(path, payload)
    print(f"converted {path.relative_to(root)} ({len(converted)})")
