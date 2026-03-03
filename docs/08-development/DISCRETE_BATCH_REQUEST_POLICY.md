# Discrete Batch Request Policy

**Policy Established**: 2026-03-01  
**Status**: MANDATORY - Grade F if violated

## Policy Statement

All batch flows MUST execute as a sequence of individual, discrete requests per item/field.

- ✅ Allowed: looping through items and issuing one generation request per item for a field
- ✅ Allowed: looping through multiple fields and issuing one request per field per item
- ❌ Forbidden: single combined prompt that asks for multiple items in one generation response
- ❌ Forbidden: marker-based extraction from one combined multi-item model response

## Scope

This applies to:

- `run.py --batch-generate`
- `generation/core/batch_generator.py`
- Any domain orchestrator that performs generation for multiple items and/or fields

## Rationale

- Improves traceability of failures (one request maps to one item/field)
- Prevents extraction/marker parsing brittleness
- Aligns runtime prompt auditing with exact per-field prompts
- Keeps retry/quality decisions isolated per item and field

## Enforcement Requirements

1. Batch orchestration code MUST call generation in a loop (`for item`, `for field`) using one request per step.
2. Legacy helpers that construct combined multi-item prompts MUST be disabled or fail fast.
3. Validation/gating SHOULD run per generated item/field result, not on concatenated cross-item text.
4. New batch code must include logs showing discrete per-item/per-field processing.

## Violation Examples

### ❌ Non-compliant

- Building one prompt: "Generate pageDescription for Aluminum, Steel, Copper"
- Parsing `[MATERIAL: ...]` blocks from one response

### ✅ Compliant

- Request 1: `Aluminum.pageDescription`
- Request 2: `Steel.pageDescription`
- Request 3: `Copper.pageDescription`

For multi-field generation:

- Request 1: `Aluminum.pageTitle`
- Request 2: `Aluminum.pageDescription`
- Request 3: `Aluminum.faq`
- Request 4: `Steel.pageTitle`
- ...

## Related Policies

- `docs/08-development/TERMINAL_LOGGING_POLICY.md`
- `docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md`
- `.github/copilot-instructions.md`
