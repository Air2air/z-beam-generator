# ADR-001: Dual Voice Enforcement Architecture

**Status**: Accepted (November 18, 2025)

## Context

The system needs to generate technical content that:
1. Passes Winston AI detection (≤30% AI score)
2. Maintains objective technical voice (no theatrical phrases)
3. Achieves high realism scores (≥7.0/10)
4. Learns from feedback to improve quality

Initial approaches tried:
- **Voice in prompts only**: Generator guided but no quality enforcement → inconsistent quality
- **Voice in evaluator only**: Strong enforcement but generator produces non-compliant content → 100% failure rate

## The Problem

When voice requirements existed ONLY in the realism evaluator:
- Generator produced content without knowing target style
- All attempts failed realism checks (4.0-5.0/10 scores, below 7.0 threshold)
- Learning loop was ineffective (no target to aim for)
- 0/4 batch test success rate

**Root Cause**: Generator needs to know HOW to write, not just be punished for getting it wrong.

## Decision

**Voice requirements must exist in BOTH places:**

1. **Component Prompts** (`prompts/components/*.txt`)
   - Role: **Generation Guidance**
   - Contains: Voice & style section with key requirements
   - Purpose: Helps generator produce compliant content on first attempt
   - Example:
   ```
   VOICE & STYLE:
   - Objective technical documentation ONLY
   - Use precise technical verbs: removes, reduces, exposes
   - NO casual language: "clears away", "gets rid of"
   ```

2. **Realism Evaluator** (`prompts/evaluation/subjective_quality.txt`)
   - Role: **Quality Enforcement**
   - Contains: Critical voice requirements with strict pass/fail gate
   - Purpose: Rejects content violating requirements (≥7.0 realism threshold)
   - Example:
   ```
   CRITICAL VOICE REQUIREMENTS (content MUST follow these to pass):
   - Write as materials scientist with ZERO theatrical elements
   - FORBIDDEN: casual substitutes, enthusiasm markers
   - Overall Realism ≥7.0 to PASS
   ```

## Consequences

### Positive
- ✅ Generator produces higher quality initial content (knows target style)
- ✅ Fewer retry attempts needed (guidance prevents common mistakes)
- ✅ Learning loop effective (generator refines toward known target)
- ✅ System working with exit code 0 (improved from 0/4 to passing)

### Negative
- ⚠️ Voice requirements exist in two files (must keep synchronized)
- ⚠️ Changes to voice requirements require updating both locations

### Mitigation
- Document this pattern clearly in copilot-instructions.md
- When updating voice requirements, update BOTH files
- Evaluator requirements should be MORE STRICT than prompt guidance
- Prompt gives direction, evaluator enforces precision

## The Learning Loop Flow

```
1. Prompt Guidance → Generator produces content following voice guidance
2. Content Generation → Uses technical verbs, objective tone
3. Quality Gate → Evaluator checks against strict requirements
4. Pass/Fail → Realism ≥7.0 required
5. Feedback → If fail, parameters adjusted based on specific violations
6. Next Attempt → Generator refines approach toward known target
```

## Alternatives Considered

### Alternative 1: Voice Requirements ONLY in Prompts
**Rejected because**:
- No enforcement mechanism
- Quality inconsistent
- No feedback loop for learning

### Alternative 2: Voice Requirements ONLY in Evaluator
**Rejected because**:
- Tried November 18, 2025 - resulted in 100% failure
- Generator produces non-compliant content (doesn't know target)
- Realism scores 4.0-5.0/10 (below 7.0 threshold)
- Learning loop ineffective (just random attempts)

### Alternative 3: Dynamically Generate Voice Prompts from Evaluator Requirements
**Rejected because**:
- Adds complexity without solving synchronization
- Prompt needs to be concise (guidance), evaluator needs to be thorough (enforcement)
- Different purposes require different levels of detail

## Related Decisions

- [ADR-004: Content Instructions Location](./ADR-004-content-instructions-location.md) - Where content rules belong
- [WINSTON_CONSISTENCY_FIXES_NOV18_2025.md](../../WINSTON_CONSISTENCY_FIXES_NOV18_2025.md) - Full context of discovery

## For AI Assistants

**When working on prompts or evaluation**:
1. ✅ Voice guidance in component prompts helps generator
2. ✅ Voice requirements in evaluator enforce quality
3. ❌ DO NOT remove voice guidance from prompts (leads to 100% failure)
4. ❌ DO NOT remove requirements from evaluator (no quality enforcement)
5. ✅ Keep both synchronized when updating voice requirements
6. ✅ Evaluator can be more strict/detailed than prompt guidance
