# PROJECT_RULES.md
**Last updated:** 2026-02-23

## Project Overview
- Description: AI-powered laser cleaning content generation system with strict fail-fast architecture.
- Primary tech stack: Python 3.10+, YAML data, pytest, mypy/pyright, ruff.
- Target users / goal: Internal team generating and validating laser cleaning content and metadata.

## Architecture Decisions
- Routing: CLI entry points via run.py; domain-based generators.
- State management: File-backed data (YAML) is the source of truth; in-memory only during runs.
- Data fetching: Read from data/*.yaml; write back to source YAML and sync frontmatter.
- Folder structure: generation/ (core pipeline), export/ (frontmatter), domains/ (domain logic), data/ (source YAML).

## Coding Standards
- Language / linting: Python with type checking (mypy/pyright) and ruff linting.
- Component style: Reuse existing generators/factories; avoid rewrites.
- Naming conventions: Simplify naming; follow docs/08-development/NAMING_CONVENTIONS_POLICY.md.

## Always
- Fail fast on missing config, data, or dependencies.
- Use QualityEvaluatedGenerator pipeline for ALL text generation.
- Dual-write: source YAML plus frontmatter sync.
- Keep changes minimal and follow existing patterns.
- Run project commands with `python3` from the repo root (no venv for routine tasks).

## Never
- No mocks/fallbacks in production code.
- No hardcoded values/defaults in production code.
- No exporter-only fixes for frontmatter issues.
- No prompt text embedded in generators; use prompt catalog entries only.

## Preferred Libraries & Patterns
- UI: N/A (backend system).
- Validation: pytest; integrity and validation scripts in scripts/validation/.
- Dates: Standard library.
- Forms: N/A.
- Testing: pytest (tests/).

## Performance Rules
- Avoid unnecessary data scans; reuse loaders and cached configs where present.
- Keep export transformations lightweight (format only, no enrichment).

## Security Rules
- Never commit secrets; use .env and config files.
- Fail fast on missing API keys instead of fallback behavior.

## Deployment & CI
- Validation and tests required before release; use scripts/validation and pytest.
- Maintain terminal logging for generation operations.

## Team Preferences
- Minimal impact changes, surgical fixes only.
- Preserve working code; ask before major changes.
