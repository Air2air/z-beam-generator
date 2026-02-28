# Prompts Location Investigation (2026-02-27)

## Question
Should `prompts/` move under `shared/` or `generation/`?

## Current State
- Canonical prompt assets live at repo root: `prompts/`.
- Domain prompt governance now lives in `domains/<domain>/prompt.yaml` and `domains/<domain>/catalog.yaml`.
- Domain prompt source files remain `prompts/<domain>/content_prompts.yaml`.

## Impact Scan (repo-wide)
- Files referencing `prompts/`: **83**
- Top-level reference distribution (all scanned text/code):
  - `docs`: 114
  - `prompts`: 74
  - `shared`: 36
  - `.github`: 29
  - `tests`: 26
  - `domains`: 26
  - `scripts`: 10
  - `generation`: 7

## Python Runtime/Tooling Impact
- Python files referencing `prompts/`: **30**
- Distribution:
  - `shared`: 33 references
  - `tests`: 26
  - `scripts`: 10
  - `learning`: 6
  - `generation`: 6
  - `postprocessing`: 3

## Assessment
A direct move of `prompts/` is **high-risk now** because path assumptions are widespread in runtime code, tooling, tests, CI docs, and architecture docs.

## Recommendation
1. **Do not physically move `prompts/` yet**.
2. Keep root `prompts/` as canonical path in current phase.
3. Keep governance ownership in `domains/<domain>/prompt.yaml` + `domains/<domain>/catalog.yaml`.
4. Enforce layout contract in validation/CI (implemented).

## If migration is still desired later (phased)
1. Introduce a single path resolver (for example `PROMPTS_ROOT`) used by all runtime loaders.
2. Refactor Python runtime references first (`shared/`, `generation/`, `learning/`, `scripts/`).
3. Update tests to use resolver (not hardcoded `prompts/`).
4. Update docs and `.github` guidance.
5. Move assets in one controlled PR after all references are resolver-based.
6. Keep temporary compatibility symlink only during transition window, then remove.

## Candidate Targets if/when moved
- `shared/prompts/` is a better conceptual fit than `generation/prompts/` because prompts are consumed by shared runtime services, validation, quality, research, and generation (not generation-only).
- Proposed future target: `shared/prompts/`.
