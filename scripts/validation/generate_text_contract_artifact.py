#!/usr/bin/env python3
"""Generate canonical text contract artifact from router/backfill sources."""

from __future__ import annotations

import json
from pathlib import Path

from text_contract_common import compute_text_contract  # pyright: ignore[reportMissingImports]

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    repo_root = REPO_ROOT
    tasks_dir = repo_root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    contract = compute_text_contract(repo_root)
    payload = {
        "source": {
            "router": "generation/config.yaml: field_router.field_types.*.text",
            "backfill": "generation/backfill/config/*.yaml: multi_field_text.fields",
        },
        "domains": contract,
    }

    out_path = tasks_dir / "text_contract_artifact.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote artifact: {out_path.relative_to(repo_root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
