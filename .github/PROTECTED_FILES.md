# Protected Files - DO NOT MODIFY Without Explicit Permission

**Purpose**: These files are critical to system operation and have been carefully tuned. AI assistants must ASK before modifying any file on this list.

## 🔒 TIER 1: Absolutely Critical (Never Touch)

### Persona Files
- `shared/voice/profiles/taiwan.yaml` - Yi-Chun Lin persona (Mandarin EFL)
- `shared/voice/profiles/united-states.yaml` - Todd Dunning persona (American native)
- `shared/voice/profiles/italy.yaml` - Alessandro Moretti persona (Italian EFL)
- `shared/voice/profiles/indonesia.yaml` - Ikmanda Roswati persona (Bahasa EFL)

**Why**: Contains carefully crafted linguistic patterns, cultural nuances, voice characteristics. Modifications break author authenticity.

### Domain Prompt Templates
- `domains/settings/prompts/settings_description.txt` - Settings generation template
- `domains/materials/prompts/*.txt` - Material generation templates

**Why**: These define content structure and formatting. Currently not loading due to bug, but registered and will be used once fixed.

### Generation Core
- `generation/core/evaluated_generator.py` - Main generation orchestrator (complex 25KB+ file)
- `generation/core/generator.py` - Core generation logic
- `shared/text/utils/prompt_builder.py` - Prompt assembly (has known bug, needs surgical fix only)

**Why**: Working production code with complex logic. Changes require deep understanding and comprehensive testing.

## 🟡 TIER 2: Modify With Caution (Ask First)

### Configuration Files
- `generation/config.yaml` - Generation settings (word counts, thresholds, etc.)
- `domains/settings/config.yaml` - Settings domain config
- `domains/materials/config.yaml` - Materials domain config
- `shared/config/settings.py` - API provider configuration

**Why**: System-wide impact. Changes affect all generation operations.

### Data Files
- `data/materials/Materials.yaml` - Single source of truth for material data
- `data/settings/Settings.yaml` - Machine settings data
- `data/contaminants/Contaminants.yaml` - Contamination patterns

**Why**: Primary data storage. Corruption breaks entire system.

### Learning System
- `learning/*.py` - All learning system files
- `generation/learning/*.py` - Learning integrations

**Why**: Complex algorithms with tuned parameters. Changes require understanding of learning architecture.

## 🟢 TIER 3: Safe With Tests (Verify Before Claiming Success)

### Coordinators & Adapters
- `domains/materials/coordinator.py` - Materials coordination
- `shared/text/adapters/*.py` - Domain adapters

**Why**: Integration points. Changes must be tested across all components.

### Utilities
- `domains/*/data_loader.py` - Data loading utilities
- `domains/*/modules/*.py` - Domain modules

**Why**: Widely used. Verify no regressions after changes.

---

## 🚨 AI Assistant Protocol

### Before Modifying ANY Protected File:

**TIER 1 (Never Touch)**:
```
❌ STOP - File is TIER 1 protected
✅ ASK: "This file is protected. I believe it needs X change because Y. 
   Can I proceed, or should I explore alternatives?"
```

**TIER 2 (Ask First)**:
```
⚠️ CAUTION - File is TIER 2 protected
✅ EXPLAIN: "This configuration change would affect X. 
   Impact: Y. Should I proceed?"
```

**TIER 3 (Verify)**:
```
✅ SAFE to modify with testing
✅ VERIFY: Test after change, report results before claiming success
```

### Common Scenarios

**User says**: "The prompt isn't working right"
```
❌ DON'T: Rewrite prompt file
✅ DO: Ask which specific part isn't working, suggest minimal targeted change
```

**User says**: "Generation is slow"
```
❌ DON'T: Modify generator.py
✅ DO: Check configuration first, investigate bottlenecks, suggest config changes
```

**User says**: "Fix the template loading bug"
```
❌ DON'T: Rewrite prompt_builder.py
✅ DO: Make surgical 3-line fix to _load_component_template() method only
```

**User says**: "Voice isn't distinct enough"
```
❌ DON'T: Modify persona files
✅ DO: This is an LLM behavior issue. Explain limitations, suggest alternatives 
   (post-processing validation, switching models, examples in prompts)
```

---

## Known Issues & Accepted Architecture

### Template Loading Bug
**Location**: `shared/text/utils/prompt_builder.py` line 228-243
**Issue**: Hardcoded path doesn't use ComponentRegistry
**Fix**: Surgical change to use `ComponentRegistry.get_spec(component_type).prompt_template_file`
**Status**: Documented, waiting for fix

### Voice Distinctiveness
**Issue**: Both Grok and Claude produce generic output despite detailed personas
**Grades**: Grok D+ (3/10), Claude C+ (5/10)
**Root Cause**: LLM behavior (prioritizes coherence over subtle linguistic patterns)
**Status**: Accepted limitation. Consider post-processing or model switching.

---

## Protection Enforcement

### Manual Review
- All changes to protected files reviewed by human before deployment
- AI assistants must provide justification for any TIER 1/2 modifications

### Git Protection (Recommended)
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check for modifications to protected files
PROTECTED_FILES=(
    "shared/voice/profiles/*.yaml"
    "domains/*/prompts/*.txt"
    "generation/core/evaluated_generator.py"
)

for pattern in "${PROTECTED_FILES[@]}"; do
    if git diff --cached --name-only | grep -q "$pattern"; then
        echo "⚠️  WARNING: Modifying protected file matching: $pattern"
        echo "Are you sure? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
done
```

### Testing Requirements
Any change to TIER 2/3 files must include:
1. Import verification test
2. Functionality test
3. Regression test for related components
4. Evidence of success (terminal output, test results)

---

## Last Updated
December 6, 2025 - After domain cleanup removed 18 unused files

## Version History
- v1.0 (Dec 6, 2025) - Initial protected files list after cleanup
