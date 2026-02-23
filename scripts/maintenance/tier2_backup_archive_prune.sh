#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

MODE="dry-run"
if [[ "${1:-}" == "--apply" ]]; then
  MODE="apply"
fi

STAMP="$(date +%Y-%m-%d_%H%M%S)"
ARCHIVE_BASE="docs/archive/cleanup-backups/$STAMP"

FILES=()
while IFS= read -r line; do
  FILES+=("$line")
done < <(
  find data export domains -type f \( -name '*.backup*' -o -name '*.bak*' -o -name '*.test' \) \
    ! -path '*/__pycache__/*' \
    | sort
)

COUNT="${#FILES[@]}"
if [[ "$COUNT" -eq 0 ]]; then
  echo "No backup/test snapshot files matched."
  exit 0
fi

TOTAL_SIZE="$(printf '%s\0' "${FILES[@]}" | xargs -0 du -ch 2>/dev/null | tail -1 | awk '{print $1}')"

echo "Mode: $MODE"
echo "Matched files: $COUNT"
echo "Total size: $TOTAL_SIZE"
echo "Archive target: $ARCHIVE_BASE"
echo

echo "Top 20 largest candidates:"
printf '%s\0' "${FILES[@]}" | xargs -0 du -h 2>/dev/null | sort -hr | head -20

echo
if [[ "$MODE" == "dry-run" ]]; then
  echo "Dry-run only. Re-run with --apply to move files into archive."
  exit 0
fi

for file in "${FILES[@]}"; do
  dest="$ARCHIVE_BASE/$file"
  mkdir -p "$(dirname "$dest")"
  mv "$file" "$dest"
done

echo
echo "Archive complete."
echo "Moved $COUNT files to: $ARCHIVE_BASE"
