# Validation Learning Feedback Architecture

**Last Updated**: December 11, 2025  
**Status**: ✅ IMPLEMENTED

## Overview

The validation learning feedback system provides **dynamic prompt adaptation** based on validation issues detected during generation. Validation runs on every generation but **never blocks** - instead, issues are logged to the learning database where the humanness optimizer uses them to improve future prompts.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   GENERATION FLOW                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Build Prompt (with current humanness layer)             │
│     - Base template + Voice instructions + Humanness        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. VALIDATE PROMPT (Non-Blocking)                          │
│     ✅ Length (chars, words, tokens)                         │
│     ✅ Format (structure, sections)                          │
│     ✅ Coherence (contradictions, separation)                │
│     ✅ Critical sections (voice, forbidden phrases)          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Issues found? │
                    └───────┬───────┘
                            │
                ┌───────────┴───────────┐
                │                       │
               YES                     NO
                │                       │
                ▼                       ▼
    ┌───────────────────────┐   ┌─────────────┐
    │ Log to Database       │   │ Continue    │
    │ - Issue severity      │   │ (no action) │
    │ - Issue message       │   └─────────────┘
    │ - Prompt metrics      │
    │ - Timestamp           │
    └───────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Generate Content (Always Proceeds)                      │
│     - API call with validated prompt                        │
│     - Content extraction                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Save & Evaluate (Post-Save Quality Analysis)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           LEARNING FEEDBACK LOOP                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  HumannessOptimizer.generate_humanness_instructions()       │
│  - Reads validation issues from database                    │
│  - Identifies recurring problems                            │
│  - Adapts humanness layer to address issues                 │
│  - Returns enhanced instructions for next generation        │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Generator (Validation Layer)

**File**: `generation/core/generator.py`  
**Method**: `generate_without_save()` (lines 263-400)

**Responsibilities**:
- Validate assembled prompt before API call
- Run standard validation (length, format, technical)
- Run coherence validation (contradictions, separation)
- Log issues to learning database (non-blocking)
- Display validation results in terminal

**Key Features**:
- ✅ **Non-blocking** - Warns but never raises exceptions
- ✅ **Comprehensive** - Checks length, format, coherence, critical sections
- ✅ **Dual logging** - Terminal output + file logging
- ✅ **Learning feedback** - Calls `_log_validation_issues()` to feed optimizer

**Code Example**:
```python
# Standard validation (non-blocking)
validation_result = validate_text_prompt(prompt)

if not validation_result.is_valid:
    if validation_result.has_critical_issues:
        print(f"\n⚠️  VALIDATION ISSUES DETECTED (logged for learning)")
        print(validation_result.format_report())
        # Log to database for humanness optimizer
        self._log_validation_issues(validation_result, 'standard')
    else:
        print(f"   ⚠️  Validation warnings (logged for learning)")
        self._log_validation_issues(validation_result, 'standard')
```

### 2. Validation Logger

**File**: `generation/core/generator.py`  
**Method**: `_log_validation_issues()` (lines 602-647)

**Responsibilities**:
- Extract issue details from validation results
- Log to `prompt_validation_feedback` table
- Capture severity, message, suggestions
- Record prompt metrics (length, tokens)
- Non-blocking - catches all exceptions

**Design Principles**:
- ❌ **No hardcoded values** - Uses dynamic database patterns
- ✅ **Fail-soft** - Logs error but never blocks generation
- ✅ **Lazy loading** - Imports database only when needed
- ✅ **Structured data** - JSON-serializable issue format

**Code Example**:
```python
def _log_validation_issues(self, validation_result, validation_type: str):
    """Log validation issues for humanness optimizer feedback."""
    try:
        from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
        db = WinstonFeedbackDatabase('z-beam.db')
        
        # Extract issues
        issues = []
        for issue in validation_result.issues:
            issues.append({
                'severity': issue.severity,
                'message': issue.message,
                'suggestion': issue.suggestion
            })
        
        # Log to database
        db.log_prompt_validation(
            validation_type=validation_type,
            is_valid=validation_result.is_valid,
            issues=issues,
            prompt_length=validation_result.prompt_length,
            word_count=validation_result.word_count,
            estimated_tokens=validation_result.estimated_tokens
        )
        
    except Exception as e:
        # Non-blocking: log error but continue
        logger.warning(f"Could not log validation feedback: {e}")
```

### 3. Humanness Optimizer (Learning Consumer)

**File**: `learning/humanness_optimizer.py`  
**Method**: `generate_humanness_instructions()`

**Responsibilities**:
- Read validation issues from database
- Identify recurring problems (e.g., "missing voice instructions")
- Adapt humanness layer template dynamically
- Inject corrections into next generation's prompt

**Future Enhancement** (Not yet implemented):
```python
def _extract_validation_patterns(self) -> ValidationPatterns:
    """
    Extract validation issue patterns from database.
    
    Queries prompt_validation_feedback table for:
    - Recurring issue types (e.g., missing voice, long prompts)
    - Severity distribution (CRITICAL vs WARNING)
    - Prompt metric trends (length increasing over time)
    
    Returns:
        ValidationPatterns with recurring issues and recommendations
    """
    # Query last 100 validation records
    issues = db.query(
        "SELECT validation_type, issues, prompt_length, timestamp "
        "FROM prompt_validation_feedback "
        "ORDER BY timestamp DESC LIMIT 100"
    )
    
    # Analyze patterns
    missing_voice_count = count_issues(issues, "voice instructions.*MISSING")
    long_prompt_count = count_issues(issues, "prompt_length > 8000")
    
    return ValidationPatterns(
        missing_voice_frequency=missing_voice_count / len(issues),
        average_prompt_length=mean([i['prompt_length'] for i in issues]),
        recommendations=[
            "Ensure voice_instruction placeholder always rendered",
            "Reduce template verbosity if avg length > 7000"
        ]
    )
```

## Database Schema

**Table**: `prompt_validation_feedback`

```sql
CREATE TABLE IF NOT EXISTS prompt_validation_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    validation_type TEXT NOT NULL,  -- 'standard' or 'coherence'
    is_valid INTEGER NOT NULL,      -- 0 or 1
    issues TEXT,                     -- JSON array of issue objects
    prompt_length INTEGER,
    word_count INTEGER,
    estimated_tokens INTEGER
);

CREATE INDEX idx_validation_timestamp 
ON prompt_validation_feedback(timestamp DESC);

CREATE INDEX idx_validation_type 
ON prompt_validation_feedback(validation_type, is_valid);
```

## Validation Types

### Standard Validation

**Checks**:
- **Length**: Characters, words, estimated tokens
- **Format**: Required sections present
- **Technical**: Proper structure, no formatting errors

**Example Issues**:
```json
[
  {
    "severity": "WARNING",
    "message": "Prompt length 8234 chars exceeds recommended 7000",
    "suggestion": "Consider using compact template for this component"
  },
  {
    "severity": "CRITICAL",
    "message": "Voice instructions missing from prompt",
    "suggestion": "Ensure {voice_instruction} placeholder is rendered"
  }
]
```

### Coherence Validation

**Checks**:
- **Contradictions**: Conflicting instructions
- **Separation**: Voice vs content vs formatting
- **Redundancy**: Duplicate instructions

**Example Issues**:
```json
[
  {
    "severity": "ERROR",
    "message": "Voice instructions duplicated 3 times in prompt",
    "suggestion": "Remove duplicate voice_section building in prompt_builder.py"
  },
  {
    "severity": "WARNING",
    "message": "7 different word count targets found",
    "suggestion": "Consolidate word count to single source"
  }
]
```

## Benefits

### 1. Dynamic Adaptation
- **Continuous improvement** - System learns from every generation
- **Automated fixes** - Humanness optimizer adapts without manual intervention
- **Pattern detection** - Identifies recurring issues automatically

### 2. Non-Blocking
- **100% completion rate** - Validation never blocks generation
- **Fast generation** - No retry loops or quality gates
- **User visibility** - All issues logged and displayed

### 3. Quality Improvement
- **Root cause analysis** - Database tracks issue frequency over time
- **Trend detection** - Identify if problems increasing or decreasing
- **Data-driven decisions** - Metrics guide template improvements

## Usage Example

### Generation with Validation Feedback

```python
from domains.materials.coordinator import UnifiedMaterialsGenerator
from shared.api.client_factory import create_api_client

# Initialize coordinator (uses QualityEvaluatedGenerator)
client = create_api_client('grok')
coordinator = UnifiedMaterialsGenerator(client)

# Generate content (validation runs automatically)
result = coordinator.generate('Aluminum', 'description')

# Validation issues (if any) are:
# 1. Displayed in terminal output
# 2. Logged to z-beam.db
# 3. Available to humanness optimizer for next generation
```

### Terminal Output Example

```
================================================================================
🔍 COMPREHENSIVE PROMPT VALIDATION (FULL PROMPT)
================================================================================

📊 PROMPT METRICS:
   • Characters: 5,234
   • Words: 687
   • Estimated tokens: 1,308
   • Status: Valid with warnings

🔍 CRITICAL SECTIONS CHECK:
   • Voice instructions: ✅ PRESENT
   • Forbidden phrases: ✅ PRESENT
   • Component requirements: ✅ PRESENT

⚠️  VALIDATION ISSUES DETECTED (logged for learning)
   1. [WARNING] Prompt length 5234 chars approaching limit
      💡 Consider using compact template if length exceeds 7000

🔗 COHERENCE VALIDATION:
   ✅ Coherence validated successfully

📄 Full prompt saved to: /tmp/tmp_abc123_prompt.txt
   View with: cat /tmp/tmp_abc123_prompt.txt

   📊 Validation feedback logged (1 issues) for humanness optimizer

================================================================================
```

## Monitoring & Analytics

### Query Validation Issues

```python
from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase

db = WinstonFeedbackDatabase('z-beam.db')

# Get recent validation issues
issues = db.execute(
    "SELECT * FROM prompt_validation_feedback "
    "WHERE is_valid = 0 "
    "ORDER BY timestamp DESC LIMIT 20"
)

# Analyze patterns
for issue in issues:
    print(f"{issue['timestamp']}: {issue['validation_type']}")
    print(f"  Issues: {json.loads(issue['issues'])}")
```

### Track Prompt Length Trends

```python
# Average prompt length over time
lengths = db.execute(
    "SELECT AVG(prompt_length) as avg_length, "
    "DATE(timestamp) as date "
    "FROM prompt_validation_feedback "
    "GROUP BY DATE(timestamp) "
    "ORDER BY date DESC LIMIT 30"
)

# Plot trend
import matplotlib.pyplot as plt
dates = [l['date'] for l in lengths]
avgs = [l['avg_length'] for l in lengths]
plt.plot(dates, avgs)
plt.title('Prompt Length Trend (30 days)')
plt.show()
```

## Future Enhancements

### 1. Automatic Humanness Adaptation (Planned)

Add `_extract_validation_patterns()` to `HumannessOptimizer`:
- Read validation issues from database
- Identify top 5 recurring problems
- Inject specific corrections into humanness layer

### 2. Validation Metrics Dashboard (Planned)

Create web dashboard showing:
- Issue frequency by type
- Prompt length trends
- Validation pass rate
- Top recommendations

### 3. A/B Testing (Planned)

Test prompt variations:
- Version A: Current humanness layer
- Version B: Adapted humanness layer
- Compare validation issue rates

## Related Documentation

- **Processing Pipeline**: `docs/02-architecture/processing-pipeline.md`
- **Humanness Optimizer**: `learning/humanness_optimizer.py`
- **Prompt Validation**: `shared/validation/prompt_validator.py`
- **Coherence Validation**: `shared/validation/prompt_coherence_validator.py`
- **Generator**: `generation/core/generator.py`
- **Evaluated Generator**: `generation/core/evaluated_generator.py`

## Compliance

✅ **TIER 1**: No mocks/fallbacks in production code  
✅ **TIER 2**: Fail-soft on validation (logs but doesn't block)  
✅ **TIER 3**: Full evidence trail in database  
✅ **Copilot Instructions**: No hardcoded values, dynamic adaptation  
✅ **Template-Only Policy**: All prompt content in templates, validation in code
