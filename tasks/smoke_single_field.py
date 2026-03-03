#!/usr/bin/env python3
from __future__ import annotations

import argparse

from generation.field_router import FieldRouter
from shared.api.client_factory import create_api_client


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True)
    parser.add_argument("--field", default="pageDescription")
    parser.add_argument("--item", required=True)
    parser.add_argument("--provider", default="grok")
    args = parser.parse_args()

    client = create_api_client(args.provider)
    result = FieldRouter.generate_field(
        domain=args.domain,
        field=args.field,
        item_name=args.item,
        api_client=client,
        dry_run=True,
        skip_learning_evaluation=True,
    )

    success = bool(getattr(result, "success", False))
    skipped = bool(getattr(result, "skipped", False))
    message = getattr(result, "message", "")
    print(f"domain={args.domain} item={args.item} field={args.field} success={success} skipped={skipped} message={message}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
