#!/usr/bin/env bash
set -euo pipefail

# Batch postprocess/regeneration runner
# Usage:
#   ./scripts/tools/batch_regenerate_fields.sh materials pageDescription micro faq
#   ./scripts/tools/batch_regenerate_fields.sh materials --preset core
#   ./scripts/tools/batch_regenerate_fields.sh materials --preset pure
#   ./scripts/tools/batch_regenerate_fields.sh materials --preset seo
#   ./scripts/tools/batch_regenerate_fields.sh materials --preset all-text-routed

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <domain> [--preset <core|pure|seo|all-text-routed>] <field1> [field2 ...]"
  echo "Examples:"
  echo "  $0 materials pageDescription micro faq"
  echo "  $0 materials --preset core"
  echo "  $0 materials --preset pure"
  echo "  $0 materials --preset seo"
  echo "  $0 materials --preset all-text-routed"
  exit 1
fi

DOMAIN="$1"
shift

PRESET=""
FIELDS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --preset)
      if [[ $# -lt 2 ]]; then
        echo "❌ Error: --preset requires a value (core|pure|seo|all-text-routed)"
        exit 1
      fi
      PRESET="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 <domain> [--preset <core|pure|seo|all-text-routed>] <field1> [field2 ...]"
      exit 0
      ;;
    *)
      FIELDS+=("$1")
      shift
      ;;
  esac
done

# Resolve preset-based fields if requested
if [[ -n "$PRESET" ]]; then
  case "$PRESET" in
    core)
      # Fast, commonly used text content refresh
      FIELDS=(pageDescription micro faq)
      ;;
    pure)
      # Pure prose-style content fields only
      FIELDS=(pageTitle pageDescription micro faq)
      ;;
    seo)
      # SEO-focused text fields
      FIELDS=(pageTitle pageDescription micro)
      ;;
    all-text-routed)
      # All text fields for the given domain, derived from FieldRouter
      while IFS= read -r field_name; do
        [[ -n "$field_name" ]] && FIELDS+=("$field_name")
      done < <(
        DOMAIN="$DOMAIN" python3 - <<'PY'
import os
from generation.field_router import FieldRouter

domain = os.environ["DOMAIN"]
domain_map = FieldRouter.FIELD_TYPES.get(domain)
if domain_map is None:
    raise SystemExit(f"Unknown domain: {domain}")

for field_name, field_type in domain_map.items():
    if field_type == 'text':
        print(field_name)
PY
      )
      ;;
    all)
      # Backward-compatible alias (deprecated)
      echo "⚠️  Preset 'all' is deprecated; use 'all-text-routed'"
      while IFS= read -r field_name; do
        [[ -n "$field_name" ]] && FIELDS+=("$field_name")
      done < <(
        DOMAIN="$DOMAIN" python3 - <<'PY'
import os
from generation.field_router import FieldRouter

domain = os.environ["DOMAIN"]
domain_map = FieldRouter.FIELD_TYPES.get(domain)
if domain_map is None:
    raise SystemExit(f"Unknown domain: {domain}")

for field_name, field_type in domain_map.items():
    if field_type == 'text':
        print(field_name)
PY
      )
      ;;
    *)
      echo "❌ Error: Unknown preset '$PRESET'. Use core|pure|seo|all-text-routed"
      exit 1
      ;;
  esac
fi

if [[ ${#FIELDS[@]} -eq 0 ]]; then
  echo "❌ Error: No fields resolved. Provide explicit fields or --preset core|pure|seo|all-text-routed"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "======================================================================"
echo "🚀 BATCH REGENERATE START"
echo "   Domain: $DOMAIN"
if [[ -n "$PRESET" ]]; then
  echo "   Preset: $PRESET"
fi
echo "   Fields: ${FIELDS[*]}"
echo "   Source updates: ENABLED (no dry-run)"
echo "======================================================================"

for field in "${FIELDS[@]}"; do
  echo
  echo "----------------------------------------------------------------------"
  echo "🧠 Running postprocess for field: $field"
  echo "----------------------------------------------------------------------"

  python3 run.py --postprocess --domain "$DOMAIN" --field "$field" --all

  echo "✅ Completed field: $field"
done

echo

echo "======================================================================"
echo "✅ BATCH REGENERATE COMPLETE"
echo "   Domain: $DOMAIN"
echo "   Fields processed: ${FIELDS[*]}"
echo "======================================================================"
