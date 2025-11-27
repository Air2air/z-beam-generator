# Pipeline Stage Verification Guide

This document describes how to verify that each generation goes through all required pipeline stages.

## Pipeline Stages Overview

Every content generation goes through these stages:

1. **Humanness Layer Generation** - Generate 1428-char dynamic instructions
2. **Content Generation** - Create material-specific content with quality-gated retries
3. **Winston AI Detection** - Check human vs AI score (69%+ human threshold)
4. **Subjective Evaluation** - Assess realism score (7.0/10 minimum)
5. **Readability Check** - Validate readability metrics
6. **Database Logging** - Record parameters, scores, feedback
7. **Sweet Spot Learning** - Update optimal parameter recommendations

## Verification Methods

### Method 1: Real-Time Logging (Recommended)

Watch generation output in real-time by filtering stdout for stage markers:

```bash
python3 run.py --caption "Aluminum" --skip-integrity-check 2>&1 | \
  grep -E "Stage|Attempt|🎯|✅ Generated|Winston Score|Realism Score|Humanness|Quality Gate|saved to|GENERATION COMPLETE"
```

**Output shows:**
```
✅ HumannessOptimizer initialized (Winston DB: z-beam.db)
Threshold: 5.5/10 | Max Attempts: 5
✅ Generated 1428 character instruction block
🎯 Target: 38 words (range: 30-120)
🎯 Max tokens: 418, Temperature: 0.815
✅ Generated: 302 chars, 45 words
Winston Score: 85.2% human ✅ PASS
Realism Score: 7.5/10 ✅ PASS
Quality Gate: ✅ PASS
✅ Caption generated and saved to Materials.yaml
📊 GENERATION COMPLETE REPORT
```

**Stage Markers:**
- `✅ HumannessOptimizer initialized` = Stage 1 (Humanness Layer)
- `✅ Generated 1428 character instruction block` = Instructions loaded
- `🎯 Target` = Word count calculation
- `🎯 Max tokens, Temperature` = Dynamic parameter calculation
- `✅ Generated: X chars` = Content generation attempt
- `Winston Score: X% human` = Stage 3 (AI Detection)
- `Realism Score: X/10` = Stage 4 (Subjective Evaluation)
- `Quality Gate: PASS/FAIL` = Overall quality check
- `✅ saved to Materials.yaml` = Persistence confirmation
- `📊 GENERATION COMPLETE REPORT` = Final report

### Method 2: Database Queries

Use the verification script to check all stages in database:

```bash
python3 scripts/verify_pipeline_stages.py
```

**Output shows:**
```
🔍 PIPELINE STAGE VERIFICATION
==============================

✅ Database found at z-beam.db

📊 DATABASE TABLES:
   • ai_patterns
   • detection_results
   • generation_parameters
   • subjective_evaluations
   • sweet_spot_recommendations

🔎 STAGE 1: Winston AI Detection
   ✅ Found 5 recent detections
   • Aluminum/caption: 85.2% human, 14.8% AI ✅ PASS

🎨 STAGE 2: Subjective Evaluation (Realism)
   ✅ Found 5 recent evaluations
   • Aluminum/caption: 7.5/10 ✅ PASS

⚙️  STAGE 3: Generation Parameters
   ✅ Found 5 parameter records
   • Aluminum/caption: temp=0.815, attempt=1

🎯 STAGE 4: Sweet Spot Learning
   ✅ Found recommendations for 1 component types
   • caption: 15 samples, confidence: high

🔗 STAGE 5: End-to-End Pipeline Verification
   📍 Latest generation: Aluminum/caption
   ✅ Stage 1 (Winston): PASS
   ✅ Stage 2 (Subjective): 7.5/10 PASS
   ✅ Stage 3 (Parameters): temp=0.815, attempt=1
   ✅ Stage 4 (Sweet Spot): 15 recommendations exist
   
   📊 Pipeline Status:
   4/4 stages verified in database

🧠 STAGE 6: Humanness Layer Integration
   ✅ Winston patterns: 11 stored
   ✅ Humanness template: shared/text/templates/system/humanness_layer.txt
   ✅ Subjective patterns: shared/text/templates/evaluation/learned_patterns.yaml
```

### Method 3: Direct Database Inspection

Query database tables directly to see stage data:

```bash
# Check Winston AI detection results
sqlite3 z-beam.db "SELECT material, component_type, human_score, ai_score, success FROM detection_results ORDER BY timestamp DESC LIMIT 5;"

# Check subjective evaluations
sqlite3 z-beam.db "SELECT topic, component_type, overall_score, passes_quality_gate FROM subjective_evaluations ORDER BY timestamp DESC LIMIT 5;"

# Check generation parameters
sqlite3 z-beam.db "SELECT material, component_type, temperature, attempt_number FROM generation_parameters ORDER BY timestamp DESC LIMIT 5;"

# Check sweet spot recommendations
sqlite3 z-beam.db "SELECT component_type, sample_count, confidence_level FROM sweet_spot_recommendations;"

# Check Winston patterns learned
sqlite3 z-beam.db "SELECT COUNT(*) FROM ai_patterns;"
```

### Method 4: Integrity Checks (Full Validation)

Run generation WITH integrity checks enabled to see comprehensive validation:

```bash
python3 run.py --caption "Aluminum"
```

**Shows additional verification:**
```
🔍 Integrity Checks:
   ✅ Database Exists: z-beam.db
   ✅ Detection Logged: Aluminum/caption
   ✅ Evaluation Logged: Aluminum/caption
   ✅ Parameters Logged: Aluminum/caption
   ✅ Sweet Spot Updated: caption
   ✅ Humanness Layer Active: 1428 chars
   ✅ All Stages Complete
```

### Method 5: Filtering Full Output

For deep debugging, capture full output and filter for specific patterns:

```bash
# Capture full generation log
python3 run.py --description "Aluminum" > /tmp/generation.log 2>&1

# Extract humanness instructions
grep -A 50 "🧠 Humanness Instructions" /tmp/generation.log

# Extract all generation attempts
grep "Attempt [0-9]" /tmp/generation.log

# Extract quality scores
grep -E "Winston Score|Realism Score|Readability" /tmp/generation.log

# Extract learning updates
grep -E "Sweet Spot|Learning|Correlation" /tmp/generation.log
```

## Stage-by-Stage Verification Checklist

### ✅ Stage 1: Humanness Layer Generation

**What to verify:**
- HumannessOptimizer initializes
- Loads Winston patterns from database
- Loads Subjective patterns from YAML
- Generates 1428-character instruction block
- Strictness level progresses (1-5) across retry attempts

**Verification commands:**
```bash
# Check template exists
ls -lh shared/text/templates/system/humanness_layer.txt

# Check patterns file exists
ls -lh prompts/evaluation/learned_patterns.yaml

# Check database has patterns
sqlite3 z-beam.db "SELECT COUNT(*) FROM ai_patterns;"

# Watch generation for humanness markers
python3 run.py --caption "Material" 2>&1 | grep -i humanness
```

**Expected output markers:**
```
✅ HumannessOptimizer initialized (Winston DB: z-beam.db)
✅ Generated 1428 character instruction block
Strictness Level: 1 (Lenient)  # First attempt
Strictness Level: 3 (Moderate) # Retry attempt
```

### ✅ Stage 2: Content Generation

**What to verify:**
- Dynamic parameter calculation (temperature, max_tokens, penalties)
- Word count targeting
- Quality-gated retries (up to 5 attempts)
- Content saved to Materials.yaml

**Verification commands:**
```bash
# Watch parameter calculation
python3 run.py --caption "Material" 2>&1 | grep "🎯"

# Check generation attempts
python3 run.py --caption "Material" 2>&1 | grep "Attempt"

# Verify content saved
python3 -c "import yaml; data=yaml.safe_load(open('data/materials/Materials.yaml')); print(data['Aluminum']['caption'])"
```

**Expected output markers:**
```
🎯 Target: 38 words (range: 30-120)
🎯 Max tokens: 418, Temperature: 0.815
Attempt 1/5
✅ Generated: 302 chars, 45 words
Attempt 2/5
✅ Generated: 285 chars, 42 words
✅ Caption generated and saved to Materials.yaml
```

### ✅ Stage 3: Winston AI Detection

**What to verify:**
- Winston API called for each generation
- Human score meets threshold (69%+ default)
- Results logged to database
- Feedback used for learning

**Verification commands:**
```bash
# Watch Winston scoring
python3 run.py --caption "Material" 2>&1 | grep -i winston

# Check database for recent results
sqlite3 z-beam.db "SELECT material, component_type, human_score, ai_score FROM detection_results ORDER BY timestamp DESC LIMIT 5;"

# Verify patterns learned
sqlite3 z-beam.db "SELECT pattern_type, phrase, penalty_weight FROM ai_patterns LIMIT 10;"
```

**Expected output markers:**
```
Winston Score: 85.2% human (threshold: 69%) ✅ PASS
Winston Feedback: ["avoid passive voice", "reduce technical jargon"]
✅ Detection logged to database
```

### ✅ Stage 4: Subjective Evaluation (Realism)

**What to verify:**
- Grok evaluates generated content
- Realism score meets threshold (7.0/10 default)
- Dimensional scores calculated (clarity, professionalism, accuracy, likeness, engagement)
- Results logged to database
- AI tendencies extracted for learning

**Verification commands:**
```bash
# Watch subjective scoring
python3 run.py --caption "Material" 2>&1 | grep -i "realism\|subjective"

# Check database for evaluations
sqlite3 z-beam.db "SELECT topic, component_type, overall_score, passes_quality_gate FROM subjective_evaluations ORDER BY timestamp DESC LIMIT 5;"

# Check learned patterns
cat shared/text/templates/evaluation/learned_patterns.yaml
```

**Expected output markers:**
```
Realism Score: 7.5/10 (threshold: 7.0) ✅ PASS
  • Clarity: 8/10
  • Professionalism: 7/10
  • Technical Accuracy: 9/10
  • Human Likeness: 7/10
  • Engagement: 6/10
✅ Evaluation logged to database
AI Tendencies: ["formulaic structure", "technical tone"]
```

### ✅ Stage 5: Readability Check

**What to verify:**
- Readability metrics calculated
- Meets min/max thresholds
- Results included in final report

**Verification commands:**
```bash
# Watch readability scoring
python3 run.py --caption "Material" 2>&1 | grep -i readability

# Check readability in generation report
python3 run.py --caption "Material" 2>&1 | grep -A 5 "GENERATION COMPLETE"
```

**Expected output markers:**
```
Readability: ✅ PASS (Flesch-Kincaid: 65.3)
```

### ✅ Stage 6: Database Logging

**What to verify:**
- All stages logged to database
- Detection results recorded
- Subjective evaluations stored
- Generation parameters saved
- Sweet spot recommendations updated

**Verification commands:**
```bash
# Run full pipeline verification
python3 scripts/verify_pipeline_stages.py

# Check all tables have recent data
sqlite3 z-beam.db "SELECT name, (SELECT COUNT(*) FROM sqlite_master sm WHERE sm.name = t.name) as count FROM sqlite_master t WHERE type='table';"
```

**Expected database state:**
```
✅ detection_results: 150+ rows
✅ subjective_evaluations: 100+ rows
✅ generation_parameters: 200+ rows
✅ ai_patterns: 10+ patterns
✅ sweet_spot_recommendations: 5+ component types
```

### ✅ Stage 7: Sweet Spot Learning

**What to verify:**
- Parameter correlations calculated
- Sweet spot recommendations updated
- Confidence levels computed (high/medium/low)
- Sample count increases over time

**Verification commands:**
```bash
# Check sweet spot recommendations
sqlite3 z-beam.db "SELECT component_type, sample_count, confidence_level FROM sweet_spot_recommendations;"

# Watch learning updates
python3 run.py --caption "Material" 2>&1 | grep -i "sweet spot\|learning\|correlation"
```

**Expected output markers:**
```
🎯 Sweet Spot Learning:
   • Temperature: 0.815 (correlation: 0.45)
   • Frequency Penalty: 0.3 (correlation: -0.12)
   • Sample Count: 25
   • Confidence: high
✅ Sweet spot updated for caption
```

## Troubleshooting

### Problem: No output during generation

**Solution:** Remove output redirection:
```bash
# ❌ Wrong: Output hidden
python3 run.py --caption "Material" > /dev/null 2>&1

# ✅ Right: Full output visible
python3 run.py --caption "Material" 2>&1
```

### Problem: Database shows no recent records

**Solution:** Check if `--skip-integrity-check` was used:
```bash
# ❌ Skips some database logging
python3 run.py --caption "Material" --skip-integrity-check

# ✅ Full logging enabled
python3 run.py --caption "Material"
```

### Problem: Stage markers not appearing

**Solution:** Check logging level and ensure terminal output enabled:
```bash
# Check if generation is actually running
ps aux | grep "python3 run.py"

# Run with full verbosity
python3 run.py --caption "Material" -v 2>&1
```

### Problem: Quality gate keeps failing

**Solution:** Check current thresholds and recent feedback:
```bash
# Check Winston threshold
grep "detection_threshold" generation/config.yaml

# Check realism threshold
grep "realism_threshold" generation/config.yaml

# View recent failures
sqlite3 z-beam.db "SELECT material, component_type, human_score FROM detection_results WHERE success=0 ORDER BY timestamp DESC LIMIT 10;"
```

## Summary

**Primary Verification Method**: Real-time logging with grep filtering

```bash
python3 run.py --caption "Material" 2>&1 | grep -E "✅|🎯|Quality Gate"
```

**Comprehensive Verification**: Database inspection script

```bash
python3 scripts/verify_pipeline_stages.py
```

**Deep Debugging**: Full output capture and manual analysis

```bash
python3 run.py --caption "Material" > /tmp/gen.log 2>&1
grep -E "Stage|Attempt|Score|Quality" /tmp/gen.log
```

All verification methods confirm the Universal Humanness Layer v2.0 is fully operational with dual-feedback learning, quality-gated generation, and comprehensive stage logging.
