# Terminal Output Logging Policy

**Status**: Active  
**Date**: November 18, 2025  
**Compliance**: Mandatory for all generation operations

---

## Policy Statement

**ALL generation operations MUST stream comprehensive output to terminal in real-time. Log files SHALL NOT be created or saved.**

This policy ensures:
- Complete user visibility into generation processes
- Real-time debugging capability
- Transparency of learning systems
- Verification of feedback loops

---

## Requirements

### 1. Stream to Terminal Only

**✅ REQUIRED**:
- Output to `stdout` and `stderr` using `print()` statements
- Real-time streaming (user sees output as it happens)
- No buffering that delays output visibility

**❌ FORBIDDEN**:
- Creating log files in `/tmp/`, `/var/log/`, or anywhere else
- Using `logging.FileHandler` or similar file-based logging
- Saving output to files via `tee`, redirection, or capture
- Silent execution with no terminal output

### 2. Required Output Elements

Every generation operation MUST display:

#### A. Attempt Progress
```
Attempt 2/5
```
- Current attempt number
- Total maximum attempts
- Displayed at start of each retry

#### B. Parameter Configuration
```
🌡️  Temperature: 1.200, Max tokens: 418
⚖️  Penalties: frequency=1.20, presence=1.20
```
- Temperature setting
- Token limits
- API penalties (frequency, presence)

#### C. Parameter Adjustments (Between Attempts)
```
📊 Applying feedback adjustments from attempt 1:
   🌡️  Temperature: 0.750 → 0.825
   📉 Frequency penalty: 0.20 → 0.30
   📉 Presence penalty: 0.10 → 0.15
   🎤 Voice formality: 0.5 → 0.6
```
- Before/after values with arrows
- Clear indication of what changed
- Emoji indicators for easy scanning

#### D. Quality Validation Results
```
Winston Score: 98.6% human (threshold: 69%) ✅ PASS
Realism Score: 5.0/10 (threshold: 5.5) ❌ FAIL
Subjective Language: ✅ PASS - No violations detected
Readability: ✅ PASS
```
- Each quality gate with score
- Threshold comparison (Winston threshold is dynamic based on humanness_intensity config)
- Pass/fail status with visual indicators

#### E. Learning Activity
```
🧠 Attempt 1: Prompt optimized with learned patterns:
   Confidence: high
   Patterns analyzed: 40
   Expected improvement: 30.3%
   + Added 5 risky pattern warnings
   + Added 3 success pattern examples
```
- Prompt optimization status
- Confidence level
- Expected improvement percentage
- Specific patterns added/removed

#### F. Final Report
```
================================================================================
📊 GENERATION COMPLETE REPORT
================================================================================

📝 GENERATED CONTENT:
────────────────────────────────────────────────────────────────────────────────
[Full generated text here]
────────────────────────────────────────────────────────────────────────────────

📈 QUALITY METRICS:
   • AI Detection Score: 0.245 (threshold: 0.303)
   • Realism Score: 9.0/10 (threshold: 7.0)
   • Status: ✅ PASS
   • Attempts: 2

📏 STATISTICS:
   • Length: 287 characters
   • Word count: 45 words

💾 STORAGE:
   • Location: data/materials/Materials.yaml
   • Component: caption
   • Material: Aluminum

================================================================================
```

---

## Implementation Guidelines

### For Generation Commands

**In `shared/commands/generation.py`**:
```python
# ✅ CORRECT: Stream to terminal
print(f"Attempt {attempt}/{max_attempts}")
print(f"🌡️  Temperature: {temp:.3f}")
print(f"Winston Score: {score}% human ✅ PASS")

# ❌ WRONG: Save to log file
logging.basicConfig(filename='/tmp/generation.log')
logger.info("Attempt 1/5")
```

### For Batch Tests

**In `run.py` batch test handler**:
```python
# ✅ CORRECT: Stream directly
result = subprocess.run(
    ['python3', 'scripts/batch_caption_test.py'],
    cwd=os.path.dirname(os.path.abspath(__file__))
)

# ❌ WRONG: Save to file with tee
tee_cmd = f"python3 scripts/batch_caption_test.py 2>&1 | tee {log_file}"
result = subprocess.run(tee_cmd, shell=True)
```

### For Processing Pipeline

**In `processing/generator.py`**:
```python
# ✅ CORRECT: Use self.logger (configured for console output)
self.logger.info(f"Attempt {attempt}/{max_attempts}")
self.logger.info(f"📊 Applying feedback adjustments from attempt {attempt-1}:")

# ❌ WRONG: Add file handlers
file_handler = logging.FileHandler('/tmp/generator.log')
self.logger.addHandler(file_handler)
```

---

## Rationale

### Why Stream-Only (No Log Files)?

1. **Immediate Visibility**: User sees what's happening in real-time
2. **Simplicity**: No file management, cleanup, or rotation needed
3. **Debugging**: Terminal output can be piped/redirected by user if needed
4. **CI/CD Friendly**: Output captured automatically in CI logs
5. **No Disk Waste**: Eliminates accumulation of log files

### Why Not Log Files?

Problems with log files:
- ❌ User doesn't see progress (requires tail -f or checking files)
- ❌ Files accumulate in `/tmp/` (require cleanup)
- ❌ Adds complexity (file rotation, permissions, paths)
- ❌ Makes debugging harder (need to find and open file)
- ❌ CI/CD requires separate log collection step

### User Can Still Save Logs

If users want to save output, they can:
```bash
# Save to file
python3 run.py --caption "Steel" 2>&1 | tee steel_generation.log

# Save and filter
python3 run.py --caption "Steel" 2>&1 | grep "Attempt" > attempts.log

# Analyze specific patterns
python3 run.py --batch-test 2>&1 | grep "Winston Score"
```

This gives users full control without imposing file management on the system.

---

## Testing Compliance

### Automated Test

**File**: `tests/test_terminal_output_policy.py`

```python
def test_no_log_files_created():
    """Verify generation does NOT create log files"""
    import tempfile
    import os
    
    # Track /tmp/ before
    tmp_files_before = set(os.listdir('/tmp'))
    
    # Run generation
    from shared.commands.generation import handle_caption_generation
    handle_caption_generation("Aluminum", skip_integrity_check=True)
    
    # Check /tmp/ after
    tmp_files_after = set(os.listdir('/tmp'))
    new_files = tmp_files_after - tmp_files_before
    
    # Filter for log files
    log_files = [f for f in new_files if f.endswith('.log') and 'generation' in f.lower()]
    
    assert len(log_files) == 0, f"Found log files created: {log_files}"


def test_output_streams_to_terminal(capsys):
    """Verify output appears on stdout/stderr"""
    from shared.commands.generation import handle_caption_generation
    
    handle_caption_generation("Aluminum", skip_integrity_check=True)
    
    captured = capsys.readouterr()
    output = captured.out + captured.err
    
    # Check for required output elements
    assert "Attempt" in output, "Missing attempt progress"
    assert "Temperature" in output, "Missing parameter info"
    assert "Winston" in output or "Realism" in output, "Missing quality checks"
```

### Manual Verification

```bash
# Should show streaming output in terminal
python3 run.py --caption "Steel"

# Should NOT create files in /tmp/
ls -lht /tmp/batch_run_*.log 2>/dev/null  # Should be empty after Nov 18, 2025

# Batch test should stream directly
python3 run.py --batch-test  # No "Logging to: /tmp/..." message
```

---

## Exceptions

**None**. This policy has no exceptions.

All generation operations stream to terminal only.

---

## References

- **Quick Reference**: `GROK_QUICK_REF.md` - Tier 2, Rule 8
- **Policy Updates**: `POLICY_UPDATES_NOV18_2025.md`
- **Implementation**: `shared/commands/generation.py`, `processing/generator.py`
- **Batch Tests**: `run.py` (--batch-test handler), `scripts/batch_caption_test.py`

---

## Compliance Checklist

- [ ] All `print()` statements for user-facing output (not `logger.info()` to files)
- [ ] No `logging.FileHandler` or file-based logging configured
- [ ] No log file creation in `/tmp/`, `/var/log/`, or elsewhere
- [ ] Subprocess calls inherit stdout/stderr (no `capture_output=True` for generation)
- [ ] Batch tests stream directly (no `tee` to save logs)
- [ ] All required output elements displayed (attempts, parameters, scores, etc.)
- [ ] Real-time streaming (no buffering delays)

---

**Last Updated**: November 18, 2025  
**Status**: Active and Enforced
