# JSON Payload Monitoring System

**Adaptive prompt guidance and conformity tracking for AI-generated JSON responses**

## Overview

The JSON Payload Monitoring System tracks JSON parsing successes and failures during the research phase, providing adaptive prompt guidance to prevent recurring issues. It works in tandem with progressive JSON repair strategies to minimize malformed responses from AI research calls.

## Problem Statement

AI models (Grok, Claude, GPT-4) occasionally generate malformed JSON despite explicit formatting instructions:

- **Unterminated strings** - Missing closing quotes in values
- **Missing values** - Incomplete key-value pairs
- **Invalid property names** - Incorrect quote usage in keys
- **Extra data** - Text outside JSON structure
- **Trailing commas** - Extra commas after last items

Manual prompt refinement can't anticipate all failure modes, and hardcoded validation only catches errors **after** they occur.

## Solution

The PayloadMonitor provides:

1. **Real-time tracking** - Records every parse attempt (success/failure)
2. **Failure categorization** - Identifies specific JSON issues
3. **Adaptive guidance** - Generates targeted prompt additions based on patterns
4. **Schema validation** - Verifies structure matches expected format
5. **Historical analysis** - Tracks failure rates over time (last 100 attempts)

## Features

### ✅ Conformity Tracking
- Success/failure rates with rolling history
- Categorized failure types (5 categories)
- Recent failure window (last 100 attempts)
- Persistent storage across sessions

### 🎯 Adaptive Prompt Guidance
- Activates at >10% failure rate
- Top 3 failure patterns with specific fixes
- Simplification requirements at >50% failure
- Material-specific recommendations

### 🔍 Schema Validation
- Expected structure checking
- Required field verification
- Type validation (lists, objects, strings)
- Detailed mismatch reporting

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│         CategoryContaminationResearcher                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Build Prompt                                     │  │
│  │     ↓                                                 │  │
│  │  2. Check PayloadMonitor for Adaptive Guidance      │  │
│  │     ↓                                                 │  │
│  │  3. Append Guidance if Failures Detected            │  │
│  │     ↓                                                 │  │
│  │  4. Call Grok API                                    │  │
│  │     ↓                                                 │  │
│  │  5. Progressive JSON Repair (3 strategies)          │  │
│  │     ↓                                                 │  │
│  │  6. Parse JSON                                       │  │
│  │     ├─ Success → validate_schema() → record success │  │
│  │     └─ Failure → record failure → retry              │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       PayloadMonitor (Global Singleton)              │  │
│  │                                                       │  │
│  │  • record_parse_attempt()                            │  │
│  │  • get_adaptive_prompt_guidance()                    │  │
│  │  • validate_schema()                                 │  │
│  │  • get_monitoring_report()                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Persistent Storage: domains/cache/payload_monitoring│ │
│  │    - parse_attempts.json                             │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

## Usage

### Basic Integration

```python
from domains.materials.image.prompts.payload_monitor import get_payload_monitor

# Get global monitor instance
monitor = get_payload_monitor()

# Check for adaptive guidance before API call
guidance = monitor.get_adaptive_prompt_guidance()
if guidance:
    prompt += f"\n\n{guidance}"

# After parsing attempt
try:
    data = json.loads(response)
    
    # Validate schema
    is_valid, errors = monitor.validate_schema(data, "contamination_research")
    if not is_valid:
        raise ValueError(f"Schema validation failed: {errors}")
    
    # Record success
    monitor.record_parse_attempt(
        success=True,
        attempt_number=1,
        cleaning_strategy="none"
    )
except json.JSONDecodeError as e:
    # Record failure with error details
    monitor.record_parse_attempt(
        success=False,
        attempt_number=1,
        cleaning_strategy="light",
        error_type="unterminated_string",
        error_details={'line': e.lineno, 'column': e.colno},
        raw_json=response if attempt == 3 else None  # Save on final attempt
    )
```

### Progressive JSON Repair Integration

```python
def parse_with_progressive_repair(text, attempt_number):
    """Parse JSON with attempt-based repair strategy."""
    
    # Choose strategy based on attempt
    if attempt_number == 0:
        strategy = "light"  # Just trailing commas
        cleaned = repair_light(text)
    elif attempt_number == 1:
        strategy = "moderate"  # Newlines in strings + trailing commas
        cleaned = repair_moderate(text)
    else:
        strategy = "aggressive"  # Char-by-char parsing
        cleaned = repair_aggressive(text)
    
    try:
        data = json.loads(cleaned)
        
        # Validate and record success
        is_valid, errors = monitor.validate_schema(data, "contamination_research")
        if is_valid:
            monitor.record_parse_attempt(
                success=True,
                attempt_number=attempt_number,
                cleaning_strategy=strategy
            )
            return data
        else:
            raise ValueError(f"Invalid schema: {errors}")
            
    except json.JSONDecodeError as e:
        # Categorize error
        error_type = categorize_json_error(e, text)
        
        monitor.record_parse_attempt(
            success=False,
            attempt_number=attempt_number,
            cleaning_strategy=strategy,
            error_type=error_type,
            error_details={'line': e.lineno, 'column': e.colno, 'msg': e.msg}
        )
        raise
```

## Failure Types

### 1. Unterminated String
**Symptom**: Missing closing quote on string value
```json
{
  "pattern_name": "rust spots",
  "description": "Orange-brown oxidation without closing quote
}
```

**Adaptive Guidance**:
```
⚠️ CRITICAL: UNTERMINATED STRING ERRORS detected
• ALWAYS close ALL string values with matching quotes
• Check: "description": "text here" ← needs closing quote
```

### 2. Missing Value
**Symptom**: Key without value or incomplete pair
```json
{
  "pattern_name": "rust spots",
  "description":
}
```

**Adaptive Guidance**:
```
⚠️ CRITICAL: MISSING VALUE ERRORS detected
• ENSURE every key has a complete value
• Check: "key": value ← value cannot be empty/missing
```

### 3. Invalid Property Name
**Symptom**: Unquoted or improperly quoted key
```json
{
  pattern_name: "rust spots",
  "description": "text"
}
```

**Adaptive Guidance**:
```
⚠️ CRITICAL: INVALID PROPERTY NAME ERRORS detected
• ALL property names MUST have double quotes
• Check: "property_name": value ← key needs quotes
```

### 4. Extra Data
**Symptom**: Text outside JSON structure
```json
Here are the results:
{
  "patterns": [...]
}
That's all the data.
```

**Adaptive Guidance**:
```
⚠️ CRITICAL: EXTRA DATA ERRORS detected
• Return ONLY the JSON object, no extra text
• NO explanations or commentary before/after JSON
```

### 5. Other
**Symptom**: Trailing commas, syntax errors, nested issues
```json
{
  "patterns": [
    {"name": "rust"},
  ]
}
```

**Adaptive Guidance**:
```
⚠️ CRITICAL: JSON SYNTAX ERRORS detected
• NO trailing commas after last array/object items
• Validate all brackets/braces match
```

## Schema Validation

### Expected Schemas

#### Contamination Research Schema
```python
{
    "material_name": str,
    "patterns": [
        {
            "pattern_name": str,
            "appearance": str,
            "physics": str,
            "distribution": str,
            "photo_reference_urls": [str, ...]  # ≥2 URLs
        },
        ...  # ≥5 patterns
    ]
}
```

### Validation Rules
- `patterns` must be list with ≥5 items
- Each pattern must be dict with required keys
- Each `photo_reference_urls` must be list with ≥2 URLs
- All string fields must be non-empty

### Validation Example
```python
monitor = get_payload_monitor()

is_valid, errors = monitor.validate_schema(data, "contamination_research")

if not is_valid:
    print("Schema validation failed:")
    for error in errors:
        print(f"  - {error}")
    # Example errors:
    # - Missing required field: patterns
    # - patterns must be a list, got <class 'dict'>
    # - Pattern 0 missing required field: pattern_name
    # - Pattern 2 has fewer than 2 photo_reference_urls (found 1)
```

## Adaptive Prompt Guidance

### Activation Threshold
Guidance is generated when failure rate exceeds **10%** (>10 failures in last 100 attempts).

### Guidance Structure
```
⚠️ CRITICAL JSON FORMATTING (Recent issues detected):

• UNTERMINATED STRING ERRORS (5 recent)
  → ALWAYS close ALL string values with matching quotes
  → Check: "description": "text here" ← needs closing quote

• MISSING VALUE ERRORS (3 recent)
  → ENSURE every key has a complete value
  → Check: "key": value ← value cannot be empty/missing

• INVALID PROPERTY NAME ERRORS (2 recent)
  → ALL property names MUST have double quotes
  → Check: "property_name": value ← key needs quotes

⚠️ SIMPLIFY: You're producing too many errors (50%+ failure rate)
   → Use shorter strings, fewer nested structures
   → Focus on correctness over detail
```

### Integration Point
```python
# Before API call
guidance = monitor.get_adaptive_prompt_guidance()
if guidance:
    prompt += f"\n\n{guidance}"
    print("📝 Appended adaptive JSON guidance based on failure patterns")
```

## Monitoring Reports

### Example Report
```
================================================================================
📊 JSON PAYLOAD CONFORMITY REPORT
================================================================================

✅ Success Rate: 78.0% (78/100)
⚠️  Recent Failures: 22


🚨 Failure Patterns (last 100 attempts):
   • unterminated_string: 10 (45.5%)
   • missing_value: 6 (27.3%)
   • invalid_property_name: 4 (18.2%)
   • other: 2 (9.1%)


📈 Recent Trend (last 20 attempts):
   • Successes: 14 (70.0%)
   • Failures: 6 (30.0%)
   • Status: ⚠️  ELEVATED (above 10% threshold)


🔧 Cleaning Strategy Effectiveness:
   • none: 45% success (20/45)
   • light: 80% success (24/30)
   • moderate: 95% success (19/20)
   • aggressive: 100% success (5/5)

================================================================================
```

### Report Usage
```python
# After multiple research calls
print(monitor.get_monitoring_report())
```

## Performance

- **Memory**: ~10KB per 100 attempts (typical: <50KB)
- **Disk**: ~20KB JSON file
- **Overhead**: <2ms per operation
- **Persistence**: Async writes, non-blocking

## Data Persistence

All monitoring data is automatically persisted to:
- **Location**: `domains/cache/payload_monitoring/parse_attempts.json`
- **Format**: JSON with timestamps
- **Contents**:
  - Total success/failure counts
  - Recent attempts (last 100)
  - Failure categorization
  - Cleaning strategy effectiveness

Data survives system restarts and is loaded automatically on next use.

## Testing

Test the monitoring system:

```python
from domains.materials.image.prompts.payload_monitor import get_payload_monitor

monitor = get_payload_monitor()

# Simulate failures
monitor.record_parse_attempt(
    success=False,
    attempt_number=1,
    cleaning_strategy="light",
    error_type="unterminated_string"
)

# Check guidance activation
guidance = monitor.get_adaptive_prompt_guidance()
print(guidance)  # Should show guidance after enough failures

# View report
print(monitor.get_monitoring_report())
```

## Best Practices

1. **Always check guidance before API calls** - Proactive prevention
2. **Record all parse attempts** - Both successes and failures
3. **Use schema validation** - Catch structural issues early
4. **Review reports periodically** - Identify systemic issues
5. **Escalate repair strategies** - Progressive cleaning across retries
6. **Save raw JSON on final failure** - Debugging reference

## Integration Checklist

- [x] Import `get_payload_monitor()` in researcher
- [x] Check guidance before API call
- [x] Record successes with schema validation
- [x] Record failures with error categorization
- [x] Save raw JSON on final attempt
- [x] Display monitoring report on final failure
- [x] Use progressive repair strategies

## See Also

- `image_pipeline_monitor.py` - Comprehensive pipeline monitoring
- `category_contamination_researcher.py` - Full integration example
- `PIPELINE_MONITORING.md` - End-to-end monitoring documentation
- `test_image_pipeline_monitoring.py` - Test suite
