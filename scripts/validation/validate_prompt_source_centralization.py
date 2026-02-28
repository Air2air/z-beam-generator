#!/usr/bin/env python3
"""Validate prompt source centralization and emit canonical prompt source map.

Policy scope:
- Domain prompt contracts and domain content prompt registries must be accessed only via
  approved centralization paths.
- Legacy domain prompt template path references (prompts/<domain>/*.txt) are forbidden
  in production/runtime Python code.

Outputs:
- tasks/prompt_source_map.json
- tasks/prompt_source_map.md
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

CORE_DOMAINS = ("applications", "materials", "contaminants", "compounds", "settings")

DOMAIN_REGEX = "(" + "|".join(CORE_DOMAINS) + ")"

PATTERNS: dict[str, re.Pattern[str]] = {
    "domain_prompt_contract": re.compile(rf"domains/{DOMAIN_REGEX}/prompt\.yaml"),
    "domain_content_registry": re.compile(rf"prompts/{DOMAIN_REGEX}/content_prompts\.yaml"),
    "shared_section_inline": re.compile(r"prompts/shared/section_inline_prompts\.yaml"),
    "legacy_domain_txt": re.compile(rf"prompts/{DOMAIN_REGEX}/[^\"'\s]+\.txt"),
    "prompt_catalog": re.compile(r"prompts/registry/prompt_catalog\.yaml"),
    "quality_patterns": re.compile(r"prompts/quality/learned_patterns\.yaml"),
    "voice_profiles": re.compile(r"prompts/profiles/[^\"'\s]+\.ya?ml"),
    "system_prompts": re.compile(r"prompts/system/[^\"'\s]+\.txt"),
    "seo_prompts": re.compile(r"prompts/seo/[^\"'\s]+\.txt"),
}

ALLOWED_FILES_BY_KIND: dict[str, set[str]] = {
    "domain_prompt_contract": {
        "shared/text/utils/prompt_registry_service.py",
        "scripts/validation/validate_prompt_section_contract.py",
    },
    "domain_content_registry": {
        "shared/text/utils/prompt_registry_service.py",
        "scripts/validation/validate_prompt_section_contract.py",
    },
    "shared_section_inline": {
        "shared/text/utils/prompt_registry_service.py",
        "scripts/validation/validate_prompt_section_contract.py",
        "scripts/validation/validate_machine_settings_contract.py",
    },
}

SKIP_PATH_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".next",
    "coverage",
}


@dataclass
class Reference:
    kind: str
    file: str
    line: int
    value: str


def _iter_python_files(repo_root: Path) -> Iterable[Path]:
    for path in repo_root.rglob("*.py"):
        rel = path.relative_to(repo_root).as_posix()
        if any(part in SKIP_PATH_PARTS for part in path.parts):
            continue
        if rel.startswith("tests/"):
            continue
        yield path


def _extract_references(repo_root: Path) -> list[Reference]:
    references: list[Reference] = []

    for py_file in _iter_python_files(repo_root):
        rel = py_file.relative_to(repo_root).as_posix()
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            for kind, pattern in PATTERNS.items():
                for match in pattern.finditer(line):
                    references.append(
                        Reference(
                            kind=kind,
                            file=rel,
                            line=line_number,
                            value=match.group(0),
                        )
                    )
    return references


def _build_violations(references: list[Reference]) -> list[str]:
    violations: list[str] = []

    for ref in references:
        allowed = ALLOWED_FILES_BY_KIND.get(ref.kind)
        if allowed is not None and ref.file not in allowed:
            violations.append(
                f"{ref.file}:{ref.line} disallowed direct access to {ref.kind} ('{ref.value}')"
            )
            continue

        if ref.kind == "legacy_domain_txt":
            violations.append(
                f"{ref.file}:{ref.line} legacy domain prompt template reference is forbidden ('{ref.value}')"
            )

    return sorted(set(violations))


def _write_map(repo_root: Path, references: list[Reference], violations: list[str]) -> None:
    by_kind: dict[str, list[dict[str, object]]] = {}
    for ref in references:
        by_kind.setdefault(ref.kind, []).append(
            {
                "file": ref.file,
                "line": ref.line,
                "value": ref.value,
            }
        )

    for kind in by_kind:
        by_kind[kind].sort(key=lambda entry: (str(entry["file"]), int(entry["line"])))

    payload = {
        "summary": {
            "reference_count": len(references),
            "violation_count": len(violations),
            "kinds": {kind: len(entries) for kind, entries in sorted(by_kind.items())},
        },
        "references": by_kind,
        "violations": violations,
    }

    tasks_dir = repo_root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    json_path = tasks_dir / "prompt_source_map.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Prompt Source Map",
        "",
        f"- Total references: {len(references)}",
        f"- Violations: {len(violations)}",
        "",
        "## By Kind",
    ]

    for kind, entries in sorted(by_kind.items()):
        md_lines.append(f"- {kind}: {len(entries)}")

    md_lines.extend(["", "## Violations"])
    if violations:
        for violation in violations:
            md_lines.append(f"- {violation}")
    else:
        md_lines.append("- None")

    md_path = tasks_dir / "prompt_source_map.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    references = _extract_references(repo_root)
    violations = _build_violations(references)
    _write_map(repo_root, references, violations)

    if violations:
        print("❌ Prompt source centralization validation failed:")
        for violation in violations:
            print(f"  - {violation}")
        print("\n📄 Wrote prompt source map: tasks/prompt_source_map.json")
        print("📄 Wrote prompt source report: tasks/prompt_source_map.md")
        return 1

    print("✅ Prompt source centralization validation passed")
    print("📄 Wrote prompt source map: tasks/prompt_source_map.json")
    print("📄 Wrote prompt source report: tasks/prompt_source_map.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
