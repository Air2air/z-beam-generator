# Legacy Runtime Cleanup Proposal

Date: 2026-03-12
Status: Proposed
Scope: `z-beam-generator` legacy orchestration and compatibility surfaces only

## Goal

Reduce the remaining mixed-architecture surfaces in the legacy Python runtime without rewriting working generation/export code. The target is a smaller compatibility layer around the Grok-first Pipeline 2 control surface, not a new framework.

## Current State

The repository now has two overlapping architectural stories:

1. Canonical Grok-first policy is defined in `schemas/pipeline_2_policy.yaml`, `governance/`, `aggregates/`, `voices/`, and `frontmatter-templates/`.
2. The live Python runtime still presents a legacy orchestration path centered on `run.py`, `legacy/run.py`, `shared/text/utils/prompt_builder.py`, and older exporter/orchestrator documentation.

The result is not a single large "legacy subsystem." It is a small number of still-live compatibility seams that continue to make the repo look Python-pipeline-first even though policy has moved to Grok-first inputs.

## Confirmed Legacy Seams

### 1. Root CLI is already only a compatibility wrapper

- `run.py` only delegates to `legacy.run.main`.
- This is good news: the root command contract is already isolated.
- Cleanup should preserve the command surface and reduce the internals behind `legacy/run.py`, not change user-facing commands first.

### 2. `legacy/run.py` still acts as a mixed control plane

- It contains provider config, component config, CLI parsing, bootstrap validation, postprocess execution, export coordination, and backfill discovery.
- That makes one file responsible for too many unrelated concerns.
- It is the clearest remaining place where compatibility logic and current runtime logic are still fused.

### 3. Export has a practical canonical path, but not a fully retired old path

- `export/core/frontmatter_exporter.py` is the real center of export behavior.
- `export/core/orchestrator.py` declares itself deprecated in favor of `FrontmatterExporter`.
- Despite that, `FrontmatterOrchestrator` still has active references in docs, tests, scripts, and workflow code.
- This means the exporter consolidation is structurally correct, but caller migration is incomplete.

### 4. Author and voice handling still crosses canonical and compatibility layers

- Policy points to canonical voice files in `voices/*.yaml`.
- Legacy runtime still performs prompt-time voice injection in `shared/text/utils/prompt_builder.py`.
- `export/utils/author_manager.py` is only a shim into shared author-management code, but multiple callers still import through the export path.
- This is a classic compatibility seam: the logic is mostly centralized, but the import surface still communicates the old architecture.

### 5. Architecture documentation still overstates the legacy pipeline

- `docs/02-architecture/processing-pipeline.md` still describes the Python processing pipeline as the universal requirement for all text generation.
- `schemas/pipeline_2_policy.yaml` and Grok governance docs now define a different canonical picture: Grok-first direct generation with compatibility paths retained temporarily.
- This drift is now an architecture problem, not only a documentation wording problem, because it obscures which surfaces are safe to simplify.

## What Should Not Be Rewritten

This proposal explicitly does not recommend:

- rewriting `FrontmatterExporter`
- rewriting `domains/data_orchestrator.py`
- rewriting generator core logic only because policy moved first
- removing compatibility paths before callers are migrated
- changing source-of-truth rules around aggregate/source YAMLs and frontmatter export

Those areas may evolve later, but they are not the highest-value cleanup targets right now.

## Recommended Target State

The repo should converge on this model:

1. Grok-first policy and canonical inputs remain the source of truth for direct generation.
2. The Python runtime becomes an explicitly named compatibility/runtime services layer.
3. Export flows converge on `FrontmatterExporter` as the only supported export coordinator.
4. Author/voice resolution is exposed through one canonical service surface, with temporary shims only where still needed.
5. Architecture docs describe both realities honestly: canonical Grok-first generation and compatibility Python runtime services.

## Staged Cleanup Plan

### Phase 1: Clarify and isolate compatibility surfaces

Objective: make remaining legacy paths obvious and narrow without behavior change.

Actions:

- Extract `API_PROVIDERS` and other static CLI/runtime config out of `legacy/run.py` into a focused runtime config module.
- Split `legacy/run.py` into smaller command-oriented functions or modules while preserving the current CLI flags and behavior.
- Add explicit module docstrings that say whether a file is canonical, compatibility, or deprecated.

Why first:

- Low behavioral risk.
- Makes later deletions and migrations measurable.
- Reduces confusion without touching data contracts.

### Phase 2: Retire `FrontmatterOrchestrator` as an active path

Objective: finish the export consolidation that is already mostly complete.

Actions:

- Inventory and migrate active callers of `FrontmatterOrchestrator` in:
  - `scripts/tools/run.py`
  - `shared/commands/workflow.py`
  - `tests/test_normalized_exports.py`
- Replace orchestration use cases with either:
  - direct `FrontmatterExporter` usage, or
  - a much smaller transitional adapter dedicated to the remaining workflow need
- Update `export/README.md`, `README.md`, and architecture docs so they stop presenting the orchestrator as a current architecture pillar.

Exit condition:

- No production/runtime caller depends on `FrontmatterOrchestrator`.
- Remaining references are either removed or explicitly documented as compatibility-only.

### Phase 3: Collapse author/voice import drift

Objective: keep one live author/voice service surface while preserving behavior.

Actions:

- Standardize callers on shared author-management imports instead of `export.utils.author_manager`.
- Document the contract between `authorId`, author registry resolution, and voice profile selection in one canonical place.
- Keep the export-layer author-manager shim temporarily, but demote it to a compatibility artifact with a caller-count target for removal.

Non-goal:

- Do not replace prompt-time voice injection until Grok-first direct generation completely displaces that runtime path.

### Phase 4: Repair architecture truthfulness

Objective: remove the gap between canonical policy and architecture documentation.

Actions:

- Reframe `docs/02-architecture/processing-pipeline.md` so it describes the legacy Python runtime path accurately instead of presenting it as the only valid generation model.
- Add a short architecture bridge doc that states:
  - canonical Grok-first control surface
  - compatibility Python runtime services still in use
  - current source of truth for voice, exports, and frontmatter validation
- Update navigation surfaces that still point readers to an outdated "universal pipeline" story.

Why last:

- Documentation should reflect the post-migration reality, not a temporary midpoint.
- Some wording can be corrected immediately, but the stronger cleanup value comes after Phase 1 and Phase 2 land.

## Low-Risk First Batch

If the goal is to start with a surgical implementation batch, this is the highest-confidence sequence:

1. Extract config/constants from `legacy/run.py` into a runtime config module.
2. Migrate the known non-core imports of `export.utils.author_manager` to shared author-manager paths.
3. Audit `FrontmatterOrchestrator` callers and convert one low-risk caller first, ideally a script or test before shared workflow code.
4. Update the docs that currently present `FrontmatterOrchestrator` as a primary architecture component.

This batch would reduce architectural drift materially without changing core export behavior.

## Validation Requirements For Cleanup Batches

Each implementation batch should verify all of the following before completion:

- root CLI still works for scoped commands that currently depend on `legacy/run.py`
- scoped export still works through `FrontmatterExporter`
- author resolution still succeeds for representative source items with assigned `authorId`
- no docs claim a surface is canonical if the repo treats it as deprecated or compatibility-only

Recommended scoped checks:

- grep for `FrontmatterOrchestrator` after caller migrations
- grep for `export.utils.author_manager` after import cleanup
- run a scoped export command for one domain/item
- run the touched tests only, not the entire suite by default

## Decision Summary

The correct cleanup is not a rewrite of the generator. It is a narrowing exercise:

- keep the working exporter
- shrink the live compatibility CLI/control plane
- retire the deprecated orchestrator path
- standardize author/voice service imports
- update architecture docs so they describe the actual mixed-state transition honestly

That sequence gives the repo a cleaner path toward Grok-first operation without destabilizing the production export/data pipeline.