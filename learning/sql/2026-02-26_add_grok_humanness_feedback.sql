-- Grok evaluator feedback schema (additive, backward compatible)
-- Date: 2026-02-26
-- Scope: Attach criterion-level Grok feedback to existing generations rows.

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS grok_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generation_id INTEGER NOT NULL,
    schema_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    mode TEXT NOT NULL,
    model TEXT NOT NULL,

    weighted_score REAL NOT NULL,
    confidence REAL NOT NULL,
    score_band TEXT NOT NULL,
    pass_gate INTEGER NOT NULL,

    overall_min REAL NOT NULL,
    confidence_min REAL NOT NULL,

    fail_reasons_json TEXT,
    actions_json TEXT,
    raw_payload_json TEXT NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (generation_id) REFERENCES generations(id)
);

CREATE INDEX IF NOT EXISTS idx_grok_eval_generation
    ON grok_evaluations(generation_id);

CREATE INDEX IF NOT EXISTS idx_grok_eval_score
    ON grok_evaluations(weighted_score);

CREATE INDEX IF NOT EXISTS idx_grok_eval_pass
    ON grok_evaluations(pass_gate);

CREATE TABLE IF NOT EXISTS grok_evaluation_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grok_evaluation_id INTEGER NOT NULL,
    criterion_key TEXT NOT NULL,
    score REAL NOT NULL,
    weight REAL NOT NULL,
    min_score REAL NOT NULL,
    evidence_json TEXT,
    issues_json TEXT,

    FOREIGN KEY (grok_evaluation_id) REFERENCES grok_evaluations(id)
);

CREATE INDEX IF NOT EXISTS idx_grok_eval_criterion
    ON grok_evaluation_criteria(criterion_key, score);

COMMIT;
