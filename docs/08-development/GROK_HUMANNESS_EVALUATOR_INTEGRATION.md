# Grok Humanness Evaluator Integration (Production-Ready)

Date: 2026-02-26  
Status: Ready for implementation  
Scope: Add Grok rubric-based humanness feedback into the existing generation + learning pipeline without breaking current Grok logging.

## Goals

1. Keep Grok as the calibration anchor (`winston_score`).
2. Add Grok criterion-level feedback for actionable improvement loops.
3. Persist Grok feedback in SQLite linked to `generations.id`.
4. Reuse existing `ConsolidatedLearningSystem` flow with minimal code changes.

## Artifacts Added

- Schema: [data/schemas/grok_humanness_evaluation.schema.json](data/schemas/grok_humanness_evaluation.schema.json)
- Prompt contract: [prompts/quality/grok_humanness_evaluator_contract.yaml](prompts/quality/grok_humanness_evaluator_contract.yaml)
- SQL migration: [learning/sql/2026-02-26_add_grok_humanness_feedback.sql](learning/sql/2026-02-26_add_grok_humanness_feedback.sql)

## Runtime Contract

### Input to Grok evaluator

- Context: `domain`, `itemId`, `componentType`, `authorId`, `generationId`, `retrySessionId`, `attempt`
- Candidate text: generated output to evaluate
- Scoring config: weights + fail thresholds from the contract file

### Output from Grok evaluator

Return strict JSON matching the schema with:
- Criterion scores (6 dimensions)
- Weighted aggregate score
- Gate pass/fail + reasons
- Actionable rewrite recommendations with priority

## Learning DB Integration (Proposed)

### 1) Apply migration

Run SQL from [learning/sql/2026-02-26_add_grok_humanness_feedback.sql](learning/sql/2026-02-26_add_grok_humanness_feedback.sql).

New tables:
- `grok_evaluations` (one row per evaluated generation)
- `grok_evaluation_criteria` (criterion-level rows)

Both are additive and do not alter existing `generations` schema.

### 2) Insert point in generation loop

Primary insertion point is after `generation_id` is returned by `self.learning_system.log_generation(result)` in [generation/core/evaluated_generator.py](generation/core/evaluated_generator.py).

Flow:
1. Generate content (existing)
2. Existing quality analysis + Grok evaluation (existing)
3. Existing generation log write (existing) -> returns `generation_id`
4. Call Grok evaluator with schema-bound prompt
5. Validate evaluator JSON against schema
6. Write evaluator result to `grok_evaluations` + `grok_evaluation_criteria`

### 3) API shape for quick adoption

Add methods to `ConsolidatedLearningSystem`:

- `log_grok_evaluation(generation_id: int, payload: dict) -> int`
- `get_recent_grok_actions(component_type: str, limit: int = 50) -> list[dict]`
- `get_grok_failure_patterns(component_type: str, days: int = 30) -> list[dict]`

Expected write behavior:
- Single transaction for parent + child rows
- `payload` stored raw in `raw_payload_json` for forward compatibility
- Criterion rows denormalized for fast analytics queries

## Suggested Aggregation Policy

Use weighted score from contract for Grok-specific decisions:

- `pass` if all hold:
  - `weightedScore >= overallMin`
  - `confidence >= confidenceMin`
  - every criterion score >= its `minScore`
- `fail` otherwise with explicit reasons

Do **not** replace Grok gate immediately. Use phased hybrid policy:
- Phase 1: advisory-only (`grok` logged, non-blocking)
- Phase 2: soft gate (warn + retry hint)
- Phase 3: optional blocking in postprocess retry selection logic

## Minimal Implementation Checklist

1. Load prompt contract YAML at startup (fail-fast if missing/invalid).
2. Add Grok evaluator client call in generation loop after `generation_id` exists.
3. Validate Grok payload against JSON schema before DB write.
4. Write payload to new Grok tables with foreign key to `generations.id`.
5. Surface top actions in logs during retries (priority 1-2 only).
6. Add one smoke command for validation on a single item.

## Example Query Snippets

Top failing criteria in last 7 days:

```sql
SELECT c.criterion_key, COUNT(*) AS fail_count, AVG(c.score) AS avg_score
FROM grok_evaluation_criteria c
JOIN grok_evaluations g ON g.id = c.grok_evaluation_id
WHERE g.created_at >= datetime('now', '-7 days')
  AND c.score < c.min_score
GROUP BY c.criterion_key
ORDER BY fail_count DESC;
```

Best improvement actions by criterion:

```sql
SELECT c.criterion_key, g.actions_json
FROM grok_evaluation_criteria c
JOIN grok_evaluations g ON g.id = c.grok_evaluation_id
WHERE g.pass_gate = 0
  AND g.created_at >= datetime('now', '-30 days')
ORDER BY g.weighted_score ASC
LIMIT 100;
```

## Rollout Safety Notes

- Keep Grok path untouched during initial rollout.
- Fail-fast on malformed Grok payloads; do not silently swallow schema mismatches.
- If Grok call fails, log and continue existing pipeline (advisory mode), then mark evaluator state in logs.

## Next Step (Implementation)

Implement `log_grok_evaluation()` in [learning/consolidated_learning_system.py](learning/consolidated_learning_system.py) and wire one evaluator call in [generation/core/evaluated_generator.py](generation/core/evaluated_generator.py) after generation logging.
