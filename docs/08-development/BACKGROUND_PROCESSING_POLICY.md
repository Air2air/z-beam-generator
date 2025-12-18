# Background Processing Policy

**Status**: MANDATORY  
**Date**: December 13, 2025  
**Applies to**: All batch operations, postprocessing, generation tasks

---

## 🔴 **MANDATORY REQUIREMENT**

**ALL long-running batch operations MUST be executed in background mode with terminal status monitoring.**

---

## 📋 **POLICY RULES**

### Rule 1: Background Execution for Batch Operations
Any operation processing multiple items (>5) MUST use background execution:

```bash
# ✅ CORRECT - Background with nohup
nohup python3 run.py --postprocess --domain materials --field description --all > output/process.txt 2>&1 &
echo "Process started with PID: $!"

# ❌ WRONG - Foreground blocking
python3 run.py --postprocess --domain materials --field description --all
```

### Rule 2: Output Redirection Required
All background processes MUST redirect output to a file:

```bash
# ✅ CORRECT - Output captured
nohup python3 command.py > output/results.txt 2>&1 &

# ❌ WRONG - No output capture
nohup python3 command.py &
```

### Rule 3: PID Tracking
After starting background process, MUST capture and display PID:

```bash
# ✅ CORRECT - PID tracked
nohup python3 command.py > output/results.txt 2>&1 &
echo "Process started with PID: $!"

# Also save PID for later monitoring
echo $! > logs/process.pid
```

### Rule 4: Real-Time Terminal Updates REQUIRED
Background processes MUST stream progress updates to terminal output file:

```python
# ✅ CORRECT - Terminal status updates
print(f"📝 POSTPROCESSING: {item_name} - {field}")
print(f"📊 Progress: {count}/{total}")
print(f"📊 CHECKPOINT: {count}/{total} items processed")

# ❌ WRONG - Silent processing with no status
# (No print statements, no progress indicators)
```

**Requirements:**
- Progress updates for EVERY item processed
- Checkpoint summaries at regular intervals (batch_size)
- Clear indicators of current operation
- Final summary with success/failure counts

**Verification:**
```bash
# Monitor live updates
tail -f output/process.txt

# Check progress
grep "POSTPROCESSING:" output/process.txt | wc -l

# View checkpoints
grep "CHECKPOINT:" output/process.txt
```

### Rule 4: Status Monitoring
MUST provide commands to check status:

```bash
# Check if process is running
ps aux | grep "run.py --postprocess" | grep -v grep

# Monitor progress in real-time (REQUIRED for long operations)
tail -f output/postprocess_materials_all.txt

# Check last 100 lines
tail -100 output/postprocess_materials_all.txt

# Count processed items
grep "POSTPROCESSING:" output/postprocess_materials_all.txt | wc -l
```

### Rule 5: Progress Checkpoints

### Rule 6: Full Pipeline Usage (Mandatory) 🔥 **NEW (Dec 13, 2025)**
**ALL postprocessing operations MUST use the complete generation pipeline and its quality validation.**

**Requirements:**
- ✅ **Use pipeline's QualityAnalyzer** - Same validation as generation (overall score 0-100, AI patterns, voice authenticity)
- ✅ **Use generator.generate()** - Reuse existing pipeline for regeneration
- ✅ **Include ALL quality checks** - Humanness, voice, Winston, realism, diversity
- ✅ **Learning database logging** - All quality metrics logged for sweet spot analysis
- ✅ **Dual-write** - Data YAML + frontmatter sync (automatic via generator)
- ❌ **NO direct API calls** - No `api_client.generate_simple()` or bypassing pipeline
- ❌ **NO custom validation logic** - Use QualityAnalyzer from pipeline

**Implementation:**
```python
# ✅ CORRECT - Pipeline's QualityAnalyzer + Full regeneration
from shared.voice.quality_analyzer import QualityAnalyzer
analyzer = QualityAnalyzer(api_client, strict_mode=False)
quality_analysis = analyzer.analyze(text=existing_content, author=author_data)

if quality_analysis['overall_score'] >= 70:  # Pipeline's threshold
    return KEPT_ORIGINAL

result = self.generator.generator.generate(
    identifier=item_name,
    component_type=self.field,
    faq_count=None
)

# ❌ WRONG - Custom validation + Bypassing pipeline
if my_custom_check(content):
    response = self.api_client.generate_simple(
        prompt=prompt_text,
        temperature=0.7
    )
)
```

**Rationale**: Core Principle #0 (Universal Text Processing Pipeline) - ALL text must go through QualityEvaluatedGenerator for consistent quality, voice compliance, and learning.

**Tests**: `tests/test_postprocess_pipeline_compliance.py`
Batch operations MUST include checkpoints:

```bash
# ✅ CORRECT - Checkpoint every 5 items
python3 run.py --postprocess --domain materials --field micro --all --batch-size 5

# ❌ WRONG - No checkpoints
python3 run.py --postprocess --domain materials --field micro --all
```

---

## 🛠️ **IMPLEMENTATION PATTERNS**

### Standard Background Execution Pattern
```bash
#!/bin/bash

# 1. Start background process with terminal updates
nohup python3 run.py \
  --postprocess \
  --domain materials \
  --field description \
  --all \
  --batch-size 5 \
  > output/postprocess_materials_all.txt 2>&1 &

# 2. Capture PID
PID=$!
echo "Background process started with PID: $PID"

# 3. IMMEDIATELY start monitoring terminal updates
echo "Monitoring progress (Ctrl+C to stop monitoring):"
sleep 2
tail -f output/postprocess_materials_all.txt
echo $PID > logs/postprocess.pid

# 3. Wait a moment for startup
sleep 3

# 4. Verify process is running
if ps -p $PID > /dev/null; then
    echo "✅ Process running successfully"
else
    echo "❌ Process failed to start"
    exit 1
fi

# 5. Show initial output
echo "Initial output:"
head -20 output/postprocess_materials_all.txt

# 6. Provide monitoring commands
echo ""
echo "Monitor progress with:"
echo "  tail -f output/postprocess_materials_all.txt"
echo "  grep 'CHECKPOINT:' output/postprocess_materials_all.txt"
echo ""
echo "Check status with:"
echo "  ps -p $PID"
echo ""
echo "Stop process with:"
echo "  kill $PID"
```

### Monitoring Script Pattern
```bash
#!/bin/bash
# monitor_postprocess.sh

PID=$(cat logs/postprocess.pid 2>/dev/null)

if [ -z "$PID" ]; then
    echo "❌ No PID file found"
    exit 1
fi

if ps -p $PID > /dev/null; then
    echo "✅ Process $PID is running"
    
    # Show progress
    echo ""
    echo "📊 Progress:"
    TOTAL=$(ls frontmatter/materials/*.yaml | wc -l | tr -d ' ')
    PROCESSED=$(grep "POSTPROCESSING:" output/postprocess_materials_all.txt | wc -l | tr -d ' ')
    echo "   Processed: $PROCESSED / $TOTAL materials"
    
    # Show recent output
    echo ""
    echo "📄 Recent output:"
    tail -20 output/postprocess_materials_all.txt
else
    echo "⚠️  Process $PID has stopped"
    
    # Show final statistics
    echo ""
    echo "📊 Final statistics:"
    grep "FINAL SUMMARY" output/postprocess_materials_all.txt -A 10
fi
```

---

## 📊 **USE CASES**

### Postprocessing All Materials (153 items)
```bash
nohup python3 run.py --postprocess --domain materials --field description --all --batch-size 5 > output/postprocess_materials_all.txt 2>&1 &
echo "PID: $!"
```

### Generating Content for All Items
```bash
nohup python3 batch_generate.py --domain contaminants --all > output/batch_generate.txt 2>&1 &
echo "PID: $!"
```

### Export Operations
```bash
nohup python3 export/orchestrator.py --all > output/export_all.txt 2>&1 &
echo "PID: $!"
```

---

## 🚨 **VIOLATION CONSEQUENCES**

**Violations of this policy result in:**
- ❌ Terminal session blocking (user cannot work)
- ❌ No progress visibility (user cannot monitor)
- ❌ Risk of accidental termination (terminal close = process dies)
- ❌ No output capture (errors lost)
- ❌ Cannot run multiple operations in parallel
- ❌ **Silent processing without status updates** (no visibility into progress)

**Grade**: F violation for:
- Foreground execution of batch operations (>5 items)
- **Background execution without terminal status updates**

---

## ✅ **BENEFITS**

1. **Non-blocking**: User can continue working during long operations
2. **Progress visibility**: Real-time monitoring via `tail -f` with live updates
3. **Output capture**: All logs saved for debugging
4. **Process control**: Easy to check status, stop, or restart
5. **Parallel operations**: Run multiple batch jobs simultaneously
6. **Status transparency**: Always know what the system is doing
6. **Session independence**: Process survives terminal close (with nohup)

---

## 📋 **CHECKLIST**

Before running any batch operation (>5 items):

- [ ] Use `nohup` for session independence
- [ ] Redirect output to file: `> output/file.txt 2>&1`
- [ ] Run in background: `&` at end of command
- [ ] Capture PID: `echo $!`
- [ ] Verify process started: `ps -p $PID`
- [ ] **Start monitoring terminal updates: `tail -f output/file.txt`** 🔥 **NEW REQUIREMENT**
- [ ] Provide monitoring commands to user
- [ ] Include batch-size parameter for checkpoints
- [ ] **Verify status updates are streaming in real-time** 🔥 **NEW REQUIREMENT**
- [ ] Test status monitoring before walking away

**CRITICAL**: Never start a background task without immediately monitoring terminal updates.

---

## 🎯 **ENFORCEMENT**

**This policy is MANDATORY for:**
- All postprocessing operations (`run.py --postprocess --all`)
- All batch generation operations (>5 items)
- All export operations (`--all`)
- Any operation expected to take >2 minutes

**Terminal status updates are MANDATORY for:**
- Every background process must print progress indicators
- Must show current item being processed
- Must show checkpoint summaries
- Must have final summary with counts

**AI Assistants MUST:**
1. Use background execution pattern for qualifying operations
2. Provide PID tracking and status monitoring commands
3. Verify process started successfully before reporting completion
4. Include monitoring instructions in response to user

**Grade**: Operations using foreground execution for batch tasks receive automatic F grade

---

## 📖 **REFERENCES**

- Background process monitoring: `ps aux | grep <process>`
- Output monitoring: `tail -f <output_file>`
- Process control: `kill <PID>`, `killall python3`
- nohup documentation: `man nohup`

**Status**: MANDATORY - Non-negotiable for batch operations
