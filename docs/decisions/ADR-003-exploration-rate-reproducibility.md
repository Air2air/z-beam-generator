# ADR-003: Exploration Rate and Reproducibility

**Status**: Accepted (November 18, 2025)

## Context

The system uses parameter exploration to discover better generation settings:
- Randomly adjusts temperature, voice parameters, enrichment
- Helps learning system find sweet spots
- But causes non-deterministic behavior

Problem discovered: Batch tests failing inconsistently
- Interactive mode: 0.9% AI detection → ✅ PASS
- Subprocess mode: 74.6% AI detection → ❌ FAIL
- Same material, different results each time

## Root Cause Analysis

Investigation revealed the issue was NOT:
- ❌ Cache differences between processes
- ❌ Subprocess isolation issues
- ❌ Winston API inconsistency

The issue WAS:
- ✅ High exploration rate (15%) caused excessive randomness
- ✅ Time-based variation seeds made each run different
- ✅ Each subprocess generated genuinely different content

## Decision

### 1. Reduce Exploration Rate: 15% → 5%

**Previous**: 15% of attempts used random parameter exploration
**New**: 5% exploration rate for better consistency

**Rationale**:
- 15% was too aggressive - every 7th attempt was random
- 5% provides enough learning opportunities without chaos
- Still allows discovery of better parameters
- Produces more consistent baseline quality

**Results**:
- Before: 0/4 batch tests passed
- After: 2/3 tests passed (67% success rate)
- 3x improvement in consistency

### 2. Add Random Seed Support

**Added**: `random_seed` parameter to `DynamicGenerator.__init__`

**Usage**:
```python
# For reproducible batch testing
generator = DynamicGenerator(api_client, random_seed=42)

# For normal interactive use (exploration enabled)
generator = DynamicGenerator(api_client)  # random_seed=None
```

**Behavior when seed is set**:
- `random.seed(random_seed)` called for reproducibility
- Variation seeds derived from `random_seed + attempt` (not time-based)
- Exploration mode DISABLED (no random variations)

**Behavior when seed is None**:
- Normal exploration enabled (5% rate)
- Time-based variation seeds
- Learning from exploration allowed

### 3. Consistent Variation Seeds

**Previous**:
```python
variation_seed = int(time.time() * 1000) + attempt  # Always time-based
```

**New**:
```python
if self.random_seed is not None:
    variation_seed = self.random_seed + attempt  # Consistent
else:
    variation_seed = int(time.time() * 1000) + attempt  # Time-based
```

## Consequences

### Positive
- ✅ Batch tests reproducible when seed provided
- ✅ More consistent quality across runs (5% vs 15% variation)
- ✅ Still allows learning through controlled exploration
- ✅ Interactive mode unchanged (no seed = full exploration)

### Negative
- ⚠️ Must remember to set seed for batch testing
- ⚠️ Reduced exploration may slow discovery of new sweet spots

### Mitigation
- Document when to use seed vs when not to
- Interactive development: no seed (learning enabled)
- Batch testing: use seed (reproducibility)
- Production: no seed (quality + learning)

## The Trade-off: Learning vs Consistency

| Aspect | High Exploration (15%) | Low Exploration (5%) | With Seed |
|--------|----------------------|---------------------|-----------|
| **Consistency** | Low - random variations | Higher - stable baseline | Highest - deterministic |
| **Learning** | Fast - tries many options | Slower - fewer experiments | None - no exploration |
| **Quality** | Unpredictable | More reliable | Reproducible |
| **Use Case** | Early development | Production | Testing/debugging |

## When to Use Each Mode

### No Seed (Exploration Enabled) - DEFAULT
**Use for**:
- Interactive development
- Normal content generation
- Learning new patterns
- Discovering better parameters

**Characteristics**:
- 5% exploration rate
- Time-based seeds (different each run)
- Quality varies slightly
- System learns over time

### With Seed (Exploration Disabled)
**Use for**:
- Batch testing
- Debugging issues
- Comparing approaches
- Reproducible demonstrations

**Characteristics**:
- 0% exploration (disabled)
- Consistent seeds (same each run)
- Identical output for same inputs
- No learning during session

## Alternatives Considered

### Alternative 1: Eliminate Exploration Completely
**Rejected because**:
- System couldn't learn from experiments
- Sweet spot discovery would stagnate
- No way to escape local optima
- Learning database wouldn't improve

### Alternative 2: Keep 15% Exploration
**Rejected because**:
- Proved too inconsistent in testing
- Batch tests failing unpredictably
- User experience degraded
- 5% provides enough learning

### Alternative 3: Adaptive Exploration Rate
**Rejected because**:
- Added complexity without clear benefit
- Harder to reason about system behavior
- 5% fixed rate working well
- Can reconsider if needed later

### Alternative 4: Separate Test Mode Flag
**Rejected because**:
- Seed parameter achieves same goal
- One mechanism simpler than two
- Seed is more explicit (clear intent)
- Test mode could be forgotten/misused

## Implementation Details

### In processing/generator.py

```python
def __init__(self, api_client, adapter=None, random_seed=None):
    self.random_seed = random_seed
    
    if random_seed is not None:
        random.seed(random_seed)
        self.logger.info(f"🎲 Random seed set to {random_seed}")

# In parameter adaptation:
exploration_enabled = self.random_seed is None
if exploration_enabled and attempt > 1 and random.random() < 0.05:
    # Apply random variations
```

## Related Decisions

- [WINSTON_CONSISTENCY_FIXES_NOV18_2025.md](../../WINSTON_CONSISTENCY_FIXES_NOV18_2025.md) - Full context

## For AI Assistants

**When you see exploration code**:
1. ✅ This is intentional for learning
2. ✅ 5% rate is correct (don't increase without reason)
3. ❌ Don't remove exploration - system needs it
4. ❌ Don't suggest increasing rate for "better learning"

**When suggesting batch testing**:
1. ✅ Recommend using random_seed parameter
2. ✅ Example: `generator = DynamicGenerator(client, random_seed=42)`
3. ✅ Explain this gives reproducible results

**When debugging inconsistent quality**:
1. ✅ Check if exploration is causing variations
2. ✅ Suggest using seed to isolate other issues
3. ✅ Don't assume it's a bug - might be expected variation
