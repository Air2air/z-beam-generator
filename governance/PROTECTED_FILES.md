# Critical File Guidance (No Tier Locks)

**Purpose**: This file is now advisory only. There are no tier-based edit restrictions in this repository.

## Policy Update

- Tier-based file protection has been removed.
- No file requires special “Tier 1/Tier 2” permission gates.
- All files can be modified when required to complete user-requested work.

## High-Impact Areas (Advisory)

These paths still have broad system impact and should receive targeted validation after edits:

- `generation/core/*.py`
- `shared/text/utils/*.py`
- `generation/config.yaml`
- `generation/backfill/config/*.yaml`
- `export/config/*.yaml`
- `data/*/*.yaml`
- `domains/*/prompts/*.yaml`
- `shared/voice/profiles/*.yaml`

## Expected Working Style

- Prefer minimal, source-level fixes over output patching.
- Validate changed behavior with focused tests or runtime checks.
- Document high-impact changes in `tasks/todo.md` and `tasks/lessons.md`.

## Last Updated
March 2, 2026 - Tier protections removed; advisory guidance retained.
