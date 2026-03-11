# Grok Tools and Thresholds

## Purpose

This note captures the canonical Grok-facing tool and confidence guidance referenced by the AI assistant instructions.

## Preferred Pipeline 2 Tooling

- Use `code_execution` first for local aggregate YAML inspection, lightweight parsing, and data sanity checks.
- Use `browse_page` for external fetches or citation checks when local repository sources are insufficient.
- Keep canonical local inputs first: `governance/`, `aggregates/`, `voices/`, `frontmatter-templates/`, and `schemas/pipeline_2_policy.yaml`.
- Fall back to legacy Python/runtime scripts only when Pipeline 2 cannot complete the task directly.

## Thresholds

- Confidence target: greater than 85% before presenting Pipeline 2 output as ready.
- Property accuracy target: 98.1% for governed property content.
- Quality weighting: Grok humanness 60%, subjective quality 30%, readability 10%.

## Operating Rules

- Fail fast on missing required data or broken contracts.
- Do not introduce mocks or silent fallbacks in production paths.
- Preserve YAML structure and update text fields only unless schema or configuration work is explicitly required.
- Re-run integrity validation after aggregate-source changes.
