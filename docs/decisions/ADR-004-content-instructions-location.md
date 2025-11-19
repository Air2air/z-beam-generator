# ADR-004: Content Instructions Location

**Status**: Accepted (Established in Content Instruction Policy)

## Context

The system has content rules (voice, style, format) and technical mechanisms (generation, extraction, validation). Need clear boundaries: where do content instructions belong?

## The Confusion

Original docs said conflicting things:
- "Content instructions ONLY in prompts/*.txt files"
- "NO content instructions in /processing folder code"

But also:
- "Component prompts should be minimal"
- "Evaluator enforces voice requirements"

This led to questions:
- If prompts should be minimal, where do voice rules go?
- If evaluator enforces style, why do prompts need it?
- What counts as "content instruction" vs "technical mechanism"?

## Decision

**Content instructions have THREE locations, each with a specific role:**

### 1. Component Prompts (`prompts/components/*.txt`)

**Contains**:
- Task description (what to write)
- Format requirements (structure, length, punctuation)
- **Voice guidance** (how to write it)

**Purpose**: Guide generation toward compliant content

**Example** (caption.txt):
```
TASK: Write two caption paragraphs for {material}

VOICE & STYLE:
- Objective technical documentation
- Precise technical verbs: removes, reduces, exposes
- NO casual language

FORMATTING:
- Separate paragraphs with blank line
- Each paragraph: 1-3 sentences
```

**Key Point**: "Minimal" means concise, not empty. Voice guidance belongs here.

### 2. Realism Evaluator (`prompts/evaluation/subjective_quality.txt`)

**Contains**:
- **Critical voice requirements** (stricter than prompt)
- Forbidden elements with examples
- Pass/fail criteria (≥7.0 realism)
- Evaluation dimensions

**Purpose**: Enforce quality and reject violations

**Example**:
```
CRITICAL VOICE REQUIREMENTS (content MUST follow these to pass):
- Write as materials scientist with ZERO theatrical elements
- FORBIDDEN: "game-changer", "revolutionize", "quick zap"
- Use precise technical verbs: removes, restores, improves
- Overall Realism ≥7.0 to PASS
```

**Key Point**: More detailed and strict than prompt guidance.

### 3. Processing Code (`processing/`)

**Contains**: ZERO content instructions

**Contains ONLY**:
- Technical mechanisms (API calls, extraction, validation)
- Parameter calculations (temperature, penalties)
- Flow control (retry logic, error handling)
- Data transformations

**Example** (WRONG):
```python
# ❌ FORBIDDEN: Content instruction in code
prompt += "\nUse objective technical tone with no theatrical phrases"
```

**Example** (CORRECT):
```python
# ✅ CORRECT: Technical mechanism only
prompt = self._load_prompt_template('caption.txt')
prompt = prompt.format(material=material_name, context=context)
```

## The Three-Layer Separation

| Layer | File Location | Role | Contains |
|-------|---------------|------|----------|
| **Generation** | `prompts/components/` | Guidance | Voice guidance, format rules |
| **Enforcement** | `prompts/evaluation/` | Quality gate | Strict requirements, pass/fail |
| **Technical** | `processing/` | Mechanisms | API calls, extraction, flow |

## What Counts as "Content Instruction"?

### ✅ Content Instructions (belong in prompts/)
- Voice and tone requirements
- Style guidelines (formal, casual, technical)
- Forbidden phrases or patterns
- Required terminology
- Format specifications
- Structure requirements

### ❌ NOT Content Instructions (belong in code)
- API parameters (temperature, max_tokens)
- Retry logic and error handling
- Data extraction strategies
- Parameter adaptation algorithms
- Database logging
- Quality score calculations

## Why This Matters

### The Dual Enforcement Discovery (November 18, 2025)

**Attempted**: Voice requirements ONLY in evaluator (removed from prompts)

**Result**: 100% failure rate (0/4 batch tests passed)
- Realism scores: 4.0-5.0/10 (below 7.0 threshold)
- Generator had no guidance on HOW to write
- Learning loop ineffective (no target to aim for)

**Lesson**: Generator needs guidance (in prompt) AND enforcement (in evaluator)

## Consequences

### Positive
- ✅ Clear separation of concerns
- ✅ Content rules in text files (easy to modify)
- ✅ Processing code stays generic (reusable)
- ✅ Learning loop effective (guidance + enforcement)

### Negative
- ⚠️ Voice rules in TWO places (prompt + evaluator)
- ⚠️ Must keep synchronized when updating

### Mitigation
- Evaluator can be MORE strict than prompt
- Prompt gives direction, evaluator enforces precision
- Document this relationship clearly (ADR-001)

## Alternatives Considered

### Alternative 1: All Rules in Code
**Rejected because**:
- Hard to modify (requires code changes)
- Violates Template-Only Policy
- Not reusable across domains
- AI assistants tempted to hardcode rules

### Alternative 2: All Rules in Evaluator Only
**Rejected because**:
- Tried November 18, 2025 - caused 100% failure
- Generator produces non-compliant content
- Learning loop ineffective
- See ADR-001 for full details

### Alternative 3: Rules in Config Files
**Rejected because**:
- Config is for parameters, not instructions
- Natural language rules don't fit YAML well
- Harder to maintain than text files
- Prompt templates more flexible

## The Prompt Purity Policy

From `docs/08-development/PROMPT_PURITY_POLICY.md`:

**ZERO prompt text permitted in generator code. NO EXCEPTIONS.**

❌ **Forbidden**:
```python
system_prompt = "You are a professional technical writer..."
prompt += "\nCRITICAL RULE: Write ONLY..."
prompt.replace("text", "YOU MUST NOT...")
```

✅ **Correct**:
```python
prompt = self._load_prompt_template('caption.txt')
```

## Related Decisions

- [ADR-001: Dual Voice Enforcement](./ADR-001-dual-voice-enforcement.md) - Why voice in both places
- [PROMPT_PURITY_POLICY.md](../08-development/PROMPT_PURITY_POLICY.md) - Zero hardcoded prompts
- [CONTENT_INSTRUCTION_POLICY.md](../../docs/prompts/CONTENT_INSTRUCTION_POLICY.md) - Original policy

## For AI Assistants

**When working on prompts**:
1. ✅ Content instructions belong in prompt files
2. ✅ Voice guidance in component prompts helps generation
3. ✅ Voice requirements in evaluator enforce quality
4. ❌ Don't make prompts "minimal" by removing voice guidance
5. ✅ "Minimal" = concise, not empty

**When working on processing code**:
1. ✅ Load prompts from files (no hardcoded text)
2. ✅ Technical mechanisms only (parameters, extraction, flow)
3. ❌ Never add content instructions to code
4. ❌ Never inline prompt text in generators
5. ✅ Use `_load_prompt_template()` pattern

**When updating voice requirements**:
1. ✅ Update BOTH prompt and evaluator
2. ✅ Evaluator can be more strict/detailed
3. ✅ Prompt gives guidance, evaluator enforces
4. ✅ Test that changes don't break generation
