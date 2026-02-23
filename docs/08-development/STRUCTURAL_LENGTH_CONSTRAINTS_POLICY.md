# Structural Length Constraints Policy
**Version**: 1.0  
**Date**: December 14, 2025  
**Status**: MANDATORY  
**Applies To**: All domain prompt templates

---

## Policy Statement

**ALL domain prompt templates MUST include explicit structural length constraints in the first line of the prompt.**

Structural constraints (sentence counts) provide superior word count control compared to numerical word targets or humanness guidelines.

---

## Core Principle

**Structural Constraints > Word Count Suggestions**

✅ **CORRECT**: `Write a concise technical description (2-3 sentences) about...`  
❌ **WRONG**: `Write approximately 120 words about...`  
❌ **WRONG**: `LENGTH: 55 words` (removed in Dec 2025 cleanup)  
❌ **INSUFFICIENT**: Humanness guideline `~120 words (approximate target, not strict)`

---

## Requirements

### 1. First Line Placement (MANDATORY)

The structural constraint MUST appear in the **first line** of the prompt template.

**Rationale**: LLMs prioritize instructions that appear early in the prompt.

**Example**:
```
Write a concise technical description (2-3 sentences) about {material} for laser cleaning applications.

Author: {author} from {country}
...
```

### 2. Concrete Structural Units (MANDATORY)

Use **countable structural units**, not abstract numerical targets.

**Approved Units**:
- Sentences: `(1-2 sentences)`, `(2-3 sentences)`, `(3-5 sentences)`
- Paragraphs: `(single paragraph)`, `(2 short paragraphs)`

**Prohibited Units**:
- Words: `(50 words)`, `(100-150 words)` - LLMs ignore these
- Characters: `(500 characters)` - Not natural writing units
- Approximate ranges: `(~120 words)` - "Approximate" = ignorable

### 3. Component-Specific Constraints

Each component type should have appropriate constraints based on content depth:

| Component | Recommended Constraint | Expected Words |
|-----------|----------------------|----------------|
| description | (1-2 sentences) | 30-50 words |
| contaminant description | (2-3 sentences) | 70-90 words |
| description | (1-2 sentences) | 30-50 words |
| micro (before/after) | (2 short paragraphs) | 60-80 words |
| faq answer | (2-4 sentences) | 40-80 words |

### 4. Language Precision (MANDATORY)

**Required Terms**:
- "concise" - Signals brevity
- "technical" - Defines tone
- "(N-M sentences)" - Concrete limit

**Prohibited Terms**:
- "approximately" - Makes constraint optional
- "around" - Vague guidance
- "guideline" - Suggests flexibility
- "not strict" - Invites violation

---

## Implementation Pattern

### Standard Template Structure

```
Write a concise technical description (N-M sentences) about {item} for laser cleaning applications.

[Optional: Focus areas]

Author: {author} from {country}

CONTEXT:
[Context data...]

CONTENT REQUIREMENTS (WHAT to say):
[Content guidelines...]

{voice_instruction}
```

### Domain-Specific Examples

**Materials Domain** (prompt catalog `catalog.byPath: prompts/materials/description.txt`):
```
Write a concise technical description (1-2 sentences) about {material} for laser cleaning applications.
```

**Contaminants Domain** (prompt catalog `catalog.byPath: prompts/contaminants/description.txt`):
```
Write a concise technical description (2-3 sentences) about {identifier} contamination for laser cleaning applications.
```

**Settings Domain** (prompt catalog `catalog.byPath: prompts/settings/description.txt`):
```
Write a concise technical description (1-2 sentences) about {setting} for laser cleaning applications.
```

---

## Why This Works

### 1. LLM Behavior with Structural Constraints

**Structural units are concrete and countable**:
- LLM can count sentences as it generates
- Cannot write 10 sentences when instructed "2-3"
- Physical constraint vs abstract target

**Word counts are abstract**:
- LLM doesn't count words during generation
- "120 words" is post-hoc measurement, not real-time constraint
- Easily ignored when LLM focuses on content completeness

### 2. Evidence from Testing

**Materials (with structural constraint)**:
- Instruction: `(1-2 sentences)`
- Result: 30-52 words, ±20% variance
- Grade: A+ control

**Contaminants (before fix - no constraint)**:
- Instruction: None (removed during cleanup)
- Result: 70-269 words, ±120% variance
- Grade: F (uncontrolled)

**Contaminants (after fix - structural constraint)**:
- Instruction: `(2-3 sentences)`
- Result: 74-91 words, ±21.6% variance
- Grade: A+ control

### 3. Position Matters

**First line** (high priority):
```
Write a concise technical description (2-3 sentences)...
[LLM sees this immediately and respects it]
```

**Buried at end** (low priority):
```
[Long content requirements...]
📏 LENGTH GUIDELINE: ~120 words (approximate target)
[LLM ignores this after reading content list]
```

---

## Enforcement

### Automated Testing

**Required Test**: `tests/test_structural_length_constraints.py`

Verifies:
1. All domain prompts have structural constraint in first line
2. Constraint uses approved structural units (sentences/paragraphs)
3. No prohibited terms ("approximately", "around", "guideline")
4. Constraint appears before content requirements

### Code Review Checklist

Before merging any prompt template changes:
- [ ] Does first line include structural constraint?
- [ ] Is constraint using countable units (sentences)?
- [ ] Are prohibited terms absent?
- [ ] Does constraint match component type recommendations?

---

## Migration Guide

### Updating Existing Prompts

**Step 1: Identify Current State**
```bash
# Check for structural constraint in the prompt catalog
grep -n "sentence" prompts/registry/prompt_catalog.yaml
```

**Step 2: Add Constraint (if missing)**
```diff
- Author: {author} from {country}
- Topic: {item}
+ Write a concise technical description (2-3 sentences) about {item} for laser cleaning applications.
+ 
+ Author: {author} from {country}
```

**Step 3: Test Generation**
```bash
# Generate 5 test items
python3 run.py --postprocess --domain <domain> --field <field> --item "<test-item>"
```

**Step 4: Verify Word Count**
```python
import yaml
with open('data/<domain>/<file>.yaml') as f:
    data = yaml.safe_load(f)
    item = data['<root_key>']['<test-item>']
    words = len(item['<field>'].split())
    print(f'{words} words')  # Should be in expected range
```

### Common Mistakes

❌ **Mistake 1: Keeping old LENGTH line**
```
LENGTH: 55 words
Write a concise technical description (2-3 sentences)...
```
**Fix**: Remove old LENGTH line entirely.

❌ **Mistake 2: Adding "approximately"**
```
Write approximately 2-3 sentences about...
```
**Fix**: Use concrete language - remove "approximately".

❌ **Mistake 3: Placing constraint after content**
```
CONTENT REQUIREMENTS:
[Long list...]

Write 2-3 sentences.
```
**Fix**: Move constraint to first line.

---

## Relationship to Other Systems

### Humanness Optimizer

**Humanness provides**:
- Structural variation (rhythm, opening styles)
- Voice diversity (personality, quirks)
- Length guideline (informational only)

**Humanness does NOT provide**:
- Enforceable length limits
- Primary word count control

**Separation of Concerns**:
- Prompt template: Structural constraint (enforceable)
- Humanness optimizer: Variation within constraint (informational)

### Base Configuration

**Config provides**:
- Base word count targets (for token calculation)
- Variation ranges (for diversity)

**Config does NOT provide**:
- Length instructions to LLM
- Prompt content

**Separation of Concerns**:
- Config: Technical parameters (tokens, variation)
- Prompt: Content instructions (what to generate)

---

## Historical Context

### December 2025 Cleanup

**Problem**: Contradictory word count instructions
- Config: `150-250 words`
- Prompt: `LENGTH: 55 words`
- LLM: Confused, ignored both

**Action**: "Remove ALL word count specifications from config files" (commit c9dddb05)
- ✅ Config cleaned
- ❌ Prompt line removed without replacement

**Result**: Contaminants had ZERO length guidance

### Root Cause Analysis

**Symptoms**:
- Uncontrolled word counts (70-269 words)
- High variance (±120%)
- Inconsistent outputs

**Root Cause**: Missing structural constraint in prompt template

**Solution**: Add `(2-3 sentences)` to first line of prompt

**Outcome**: 
- Controlled word counts (74-91 words)
- Low variance (±21.6%)
- A+ consistency

---

## Best Practices

### 1. Choose Appropriate Constraint

**Short content** (30-50 words):
```
Write a concise technical description (1-2 sentences)...
```

**Medium content** (70-90 words):
```
Write a concise technical description (2-3 sentences)...
```

**Long content** (120-180 words):
```
Write a focused technical description (3-5 sentences)...
```

### 2. Match Content Requirements

If asking for 5 distinct points, allow enough sentences:
```
Write a concise technical description (3-5 sentences) covering:
1. What it is
2. Characteristics
3. Behaviors
4. Challenges
5. Why laser works
```

### 3. Test Before Batch Operations

Generate 3-5 test items before committing to full batch regeneration.

**Verification**:
- Check word count range
- Verify sentence count matches constraint
- Confirm variance is acceptable (< 40% for A+ grade)

### 4. Document Changes

Update relevant documentation when changing constraints:
- This policy document
- Component-specific guides
- Test expectations

---

## Exceptions

### When Structural Constraints May Not Apply

**Poetry/Creative Content**: If generating creative content where structure varies wildly.

**User-Provided Content**: If incorporating user text that may not follow constraints.

**Multi-Component Responses**: If generating complex multi-part content.

**Current Domains**: None - all domains should use structural constraints.

---

## Maintenance

### Quarterly Review

Every 3 months, review:
1. Are all domains compliant?
2. Are word count ranges still appropriate?
3. Have any new domains been added without constraints?
4. Are test results showing good variance control?

### Update Triggers

Re-evaluate constraints when:
- Adding new domain
- Changing component types
- User feedback indicates length issues
- Quality scores drop due to overly restrictive constraints

---

## Compliance Checklist

### For New Domains
- [ ] Structural constraint in first line of all prompts
- [ ] Constraint uses countable units (sentences/paragraphs)
- [ ] No prohibited vague terms
- [ ] Test generation shows expected word counts
- [ ] Variance under 40% (A+ grade)

### For Prompt Updates
- [ ] Structural constraint preserved or improved
- [ ] First line position maintained
- [ ] Test regeneration before merging
- [ ] Documentation updated

### For Quality Issues
- [ ] Check if constraint too restrictive
- [ ] Verify constraint still in place (not deleted)
- [ ] Test variance is acceptable
- [ ] Confirm LLM respecting constraint

---

## References

**Related Documentation**:
- `docs/QUICK_REFERENCE.md` - Quick lookup for common patterns
- `docs/prompts/CONTENT_INSTRUCTION_POLICY.md` - What belongs in prompts
- `docs/architecture/TEMPLATE_ONLY_POLICY.md` - Template-only architecture

**Test Files**:
- `tests/test_structural_length_constraints.py` - Automated verification
- `tests/test_prompt_template_compliance.py` - Prompt structure validation

**Analysis Documents**:
- `WORD_COUNT_CONTROL_ROOT_CAUSE_DEC14_2025.md` - Root cause analysis
- `WORD_COUNT_FIX_RESULTS_DEC14_2025.md` - Implementation validation

---

## Summary

**Policy**: ALL prompts MUST have structural constraints in first line.

**Format**: `Write a concise technical description (N-M sentences) about {item}...`

**Why**: Structural units (sentences) are concrete and enforceable, unlike word counts.

**Evidence**: Materials (A+ control) → Contaminants fixed (A+ control after adding constraint).

**Enforcement**: Automated tests + code review checklist.

**Grade**: MANDATORY compliance - violations block merge.
