# Structural Variation Quality Gate

**Created**: November 21, 2025  
**Status**: ✅ Active (5th Quality Gate)  
**Integration**: QualityGatedGenerator

## Overview

The Structural Variation Quality Gate is the 5th essential quality parameter, enforcing content diversity across batch generations while preserving individual author voice signatures. It prevents formulaic AI patterns that pass Winston detection but show obvious structural monotony.

## Purpose

**Problem**: Batch generations can achieve 96-99% Winston human scores but still show obvious AI patterns:
- 100% identical opening patterns ("When laser cleaning X, you'll want to...")
- 70% formulaic structure (opening → property dump → warning → recommendation)
- Minimal word count variation (<5%)
- Repeated linguistic patterns

**Solution**: Enforce structural diversity as a quality gate that **rejects and retries** content showing low variation, forcing the system to naturally diversify across batch.

## Quality Gate Requirements

Content must pass **ALL** criteria:

1. **Diversity Score**: ≥ 6.0/10
2. **Not Formulaic**: Structure must vary from template pattern
3. **Opening Uniqueness**: Pattern repeated <3 times in last 10 generations
4. **Word Count Variation**: ≥10% of configured `word_count_variation` (dynamic threshold)
5. **Author Voice Preserved**: ≥60% of author's signature traits present

**Note**: Word count threshold automatically adjusts based on `word_count_variation` config setting (0.50 default = 5% minimum variance).

## Architecture

### Component: `StructuralVariationChecker`

**Location**: `generation/validation/structural_variation_checker.py`

```python
checker = StructuralVariationChecker(
    db_path='data/winston_feedback.db',
    min_diversity_score=6.0
)

result = checker.check(
    content=generated_text,
    material_name="Aluminum",
    component_type="description",
    author_id=4  # For voice preservation
)
```

### Integration Flow

```
QualityGatedGenerator.generate()
  ├─ 1. Generate content (SimpleGenerator)
  ├─ 2. Check forbidden phrases (pre-flight)
  ├─ 3. Run subjective evaluation (Grok)
  ├─ 4. Run Winston AI detection
  ├─ 5. Check structural variation (NEW)
  │     ├─ Opening pattern analysis
  │     ├─ Word count variance check
  │     ├─ Linguistic pattern detection
  │     ├─ Property dump detection
  │     ├─ Formulaic structure check
  │     └─ Author voice preservation
  └─ 6. [All Pass? Save : Adjust & Retry]
```

## Analysis Dimensions

### 1. Opening Pattern Diversity

**Tracks**: First sentence structure across recent generations

**Detection**:
```python
# Extract opening (up to first period/semicolon)
opening = re.match(r'^([^.;]+[.;]?)', content)

# Normalize for comparison (remove material names)
normalized = re.sub(r'\b[A-Z][a-z]+\b', 'MATERIAL', opening)

# Compare first 5 words
similar = sum(1 for w1, w2 in zip(words1, words2) if w1 == w2) >= 4
```

**Penalty**: -1.0 per repetition (max -3.0)

### 2. Word Count Variation

**Tracks**: Content length compared to recent average

**Calculation**:
```python
recent_counts = [75, 91, 82, 124, 87]  # Last 5 word counts
avg_count = sum(recent_counts) / len(recent_counts)  # 91.8
current_count = 90

variance = abs(current_count - avg_count) / avg_count
# = abs(90 - 91.8) / 91.8 = 0.0196 = 1.96%
```

**Requirements**:
- **Dynamic Threshold**: Loaded from `generation/config.yaml`
  ```yaml
  word_count_variation: 0.50  # ±50% range (default)
  ```
- **Minimum Variance**: 10% of configured variation
  - Config 0.10 (±10%) → Requires ≥1% variance
  - Config 0.50 (±50%) → Requires ≥5% variance
  - Formula: `min_variance = word_count_variation × 0.10`
- **Penalty**: -1.5 if variance below threshold

**Note**: Same config variable controls prompt ranges (generation) AND validation thresholds (unified system).

### 3. Linguistic Pattern Detection

**Tracks**: 12+ linguistic patterns in content

**Patterns Detected**:

**Opening Types**:
- `when_opening`: "When laser cleaning..."
- `with_opening`: "With aluminum..."
- `key_opening`: "The key with..."
- `for_opening`: "For bronze..."
- `youll_opening`: "You'll find..."

**Connectors**:
- `unlike_connector`: "unlike most metals..."
- `but_watch_connector`: "but watch for..."
- `we_connector`: "we typically/recommend..."
- `this_connector`: "this makes/clears..."

**Sentence Structures**:
- `youll_want_structure`: "you'll want to..."
- `watch_warning`: "watch for/the/out..."
- `careful_warning`: "be careful..."

**Penalty**: -0.5 per repeated pattern (max -2.0)

### 4. Property Dump Detection

**Identifies**: 3+ properties with numbers listed sequentially

**Pattern**:
```regex
(at|of)\s+[\d.]+[^,;.]*[,;]\s*\w+\s+(at|of)\s+[\d.]+[^,;.]*[,;]\s*\w+\s+(at|of)\s+[\d.]+
```

**Example Violation**:
> "density at 2.7 g/cm³, reflectivity of 0.95, melting at 933 K"

**Penalty**: -3.0

### 5. Formulaic Structure Detection

**Identifies**: Opening → Property Dump → Warning → Recommendation

**Checks**:
```python
has_property_dump = _detect_property_dump(content)
has_warning = bool(re.search(r'(but watch|be careful|avoid|watch for)', content))
has_recommendation = bool(re.search(r'(we recommend|use \d|start with)', content))

is_formulaic = has_property_dump and has_warning and has_recommendation
```

**Penalty**: -2.0

### 6. Author Voice Preservation

**Purpose**: Ensure structural diversity doesn't erase author signature

**Author Signatures**:

**American (Todd Dunning, ID 4)**:
- Connectors: while, through, during, as, by
- Vocabulary: removes, restores, improves, clears
- Style: Direct, minimal subordination, front-loaded action

**Italian (Alessandro Moretti, ID 2)**:
- Connectors: as, which, since, and, thus
- Vocabulary: clears, restores, brings back, improves
- Style: Relative clauses, progressive structure, evidence-based

**Taiwan (Yi-Chun Lin, ID 3)**:
- Connectors: thus, and, as follows, since, with
- Vocabulary: measures, reaches, indicates, shows
- Style: Data-first, colon lists, simple parataxis

**Verification**:
```python
# Check for author's connectors
for connector in signature['connectors']:
    if connector in content_lower:
        matches += 1

# Check for vocabulary match (at least 1 characteristic verb)
vocab_matches = sum(1 for word in vocab if word in content_lower)
if vocab_matches >= 1:
    matches += 1

# Preserved if ≥60% signature traits present
preserved = (matches / expected) >= 0.6
```

**Requirement**: Must preserve author voice (no penalty if passed, fails quality gate if not)

## Diversity Scoring

**Starting Score**: 10.0

**Penalties Applied**:
```python
score = 10.0

if has_property_dump:
    score -= 3.0        # Most critical - kills narrative flow

if is_formulaic:
    score -= 2.0        # Template pattern detected

score -= min(repetition_count * 1.0, 3.0)  # Opening repetition

if word_count_variance < 0.05:
    score -= 1.5        # Uniform lengths

score -= min(linguistic_repetition * 0.5, 2.0)  # Pattern repetition

return max(0.0, score)  # Floor at 0.0
```

**Example Scores**:

| Content | Property Dump | Formulaic | Repetitions | WC Variance | Ling. Rep | Score |
|---------|--------------|-----------|-------------|-------------|-----------|-------|
| Varied  | No | No | 0 | 12% | 0 | 10.0/10 ✅ |
| Uniform | No | No | 2 | 3% | 1 | 5.0/10 ❌ |
| Template| Yes | Yes | 3 | 4% | 2 | 0.0/10 ❌ |

## Database Schema

**Table**: `structural_patterns`

```sql
CREATE TABLE structural_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_name TEXT NOT NULL,
    component_type TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER,                    -- NEW: Author voice tracking
    opening_pattern TEXT,
    structure_type TEXT,                  -- "formula", "varied", "unique"
    has_property_dump BOOLEAN,
    word_count INTEGER,                   -- NEW: Length tracking
    word_count_variance REAL,             -- NEW: % from average
    linguistic_patterns TEXT,             -- NEW: CSV of patterns
    author_voice_preserved BOOLEAN,       -- NEW: Voice check result
    diversity_score REAL,
    passed BOOLEAN
)
```

## Usage Examples

### Basic Check (No Author)

```python
from generation.validation.structural_variation_checker import StructuralVariationChecker

checker = StructuralVariationChecker(
    db_path='data/winston_feedback.db',
    min_diversity_score=6.0
)

result = checker.check(
    content="When laser cleaning aluminum...",
    material_name="Aluminum",
    component_type="description"
)

if result.passes:
    print(f"✅ Diversity: {result.diversity_score:.1f}/10")
else:
    print(f"❌ Failed: {', '.join(result.issues)}")
```

### With Author Voice Preservation

```python
# Get author from Materials.yaml
author_id = materials_data['materials']['Aluminum']['author']['id']

result = checker.check(
    content=generated_text,
    material_name="Aluminum",
    component_type="description",
    author_id=author_id  # Enable voice preservation
)

print(f"Voice Preserved: {result.author_voice_preserved}")
print(f"Author ID: {result.author_id}")
```

### Batch Analysis

```python
batch_materials = ['Aluminum', 'Copper', 'Steel', 'Bronze']

for material in batch_materials:
    desc = get_description(material)
    result = checker.check(desc, material, 'description')
    
    print(f"{material}: {result.diversity_score:.1f}/10 "
          f"({'✅' if result.passes else '❌'})")
```

### Get Statistics

```python
stats = checker.get_diversity_stats('description', window=20)

print(f"Average Diversity: {stats['avg_diversity_score']:.1f}/10")
print(f"Pass Rate: {stats['pass_rate']:.0f}%")
print(f"Property Dump Rate: {stats['property_dump_rate']:.0f}%")
print(f"Formulaic Rate: {stats['formulaic_rate']:.0f}%")
```

## Integration with QualityGatedGenerator

**Automatic Integration**: The structural variation checker is automatically initialized and used by `UnifiedMaterialsGenerator`:

```python
# In domains/materials/coordinator.py
from generation.validation.structural_variation_checker import StructuralVariationChecker

structural_checker = StructuralVariationChecker(
    db_path='data/winston_feedback.db',
    min_diversity_score=6.0
)

self.generator = QualityGatedGenerator(
    api_client=api_client,
    subjective_evaluator=subjective_evaluator,
    winston_client=winston_client,
    structural_variation_checker=structural_checker,  # 5th gate
    max_attempts=5,
    quality_threshold=7.0
)
```

**Quality Gate Enforcement**:

```python
# In quality_gated_generator.py generate() method
if (realism_score >= threshold 
    and not evaluation.ai_tendencies 
    and winston_passed 
    and structural_passed):  # NEW: 5th gate
    
    # Save content
    self._save_to_yaml(material_name, component_type, content)
else:
    # Reject and retry with adjusted parameters
    logger.warning("Quality gate failed - retrying")
```

## Prompt System Updates

### humanness_layer.txt Additions

**8 Diverse Opening Patterns** (not just 5):
```
1. "When laser cleaning [material], you'll want to..."
2. "With [material], the challenge is..."
3. "[Material] cleans best when..."
4. "You'll find [material] needs..."
5. "If you're cleaning [material], start by..."
6. "The key with [material] is..."
7. "For [material], we typically..."
8. "[Material] responds well to... but watch..."
```

**Structural Diversity Instructions**:
```
🗂️ STRUCTURAL DIVERSITY (CRITICAL FOR DESCRIPTIONS)

❌ NEVER FOLLOW THIS FORMULA: Opening → Property List → Warning → Recommendation
❌ DON'T dump 3-4 properties with numbers in a row

✅ VARY YOUR STRUCTURE - Choose ONE of these approaches:
1. Problem-Focused: Start with challenge, explain why, give solution
2. Contrast-Based: Compare to similar, highlight difference
3. Process-Focused: Walk through setup naturally
4. Experience-Based: Share what works, note what to avoid
5. Property-Driven: Lead with ONE unique property, explore deeply
```

### description.txt Additions

```
🎯 STRUCTURAL VARIATION:
- DON'T follow formula: opening → property dump → warning → recommendation
- DON'T list 3-4 properties with numbers in a row
- DO weave properties into natural explanation
- DO vary where warnings and recommendations appear
- DO use one of the 5 structural approaches from humanness layer
```

## Monitoring & Debugging

### Real-Time Logging

```
🔍 STRUCTURAL VARIATION CHECK: description
   Author: ID 4
   Opening: "When laser cleaning Cedar, you'll want to..."
   Word count: 104 words (variance: 3.2%)
   Linguistic patterns: when_opening, youll_want_structure, we_connector
   ⚠️  Word count lacks variation
   ⚠️  Opening pattern repeated 3 times
   ✅ Author voice preserved (2/3 signature traits)
   ⚠️  Formulaic structure detected
   📊 Diversity Score: 4.5/10.0
   ❌ FAIL (<6.0/10 or formulaic)
```

### Query Recent Patterns

```python
import sqlite3

conn = sqlite3.connect('data/winston_feedback.db')
cursor = conn.cursor()

# Recent diversity scores
cursor.execute('''
    SELECT material_name, diversity_score, passed, author_id
    FROM structural_patterns
    WHERE component_type = 'description'
    ORDER BY timestamp DESC
    LIMIT 10
''')

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]:.1f}/10 ({'✅' if row[2] else '❌'}) Author: {row[3]}")
```

## Known Issues & Limitations

### 1. First Generation Always Passes
**Issue**: No history to compare against, so first material scores 10/10  
**Impact**: Minimal - subsequent generations enforce variation  
**Mitigation**: None needed - system self-corrects after first material

### 2. Author Voice May Conflict with Diversity
**Issue**: If all recent generations by same author, diversity may be harder  
**Impact**: Low - authors have multiple valid patterns  
**Mitigation**: System prioritizes voice preservation (pass if ≥60%)

### 3. Formulaic Detection Needs Tuning
**Issue**: Current regex may miss some formula variations  
**Status**: Monitoring production data for refinement  
**Mitigation**: Property dump detection catches most cases

## Performance Metrics

### Expected Impact

**Before Implementation**:
- 70% formulaic structure rate
- 100% identical opening patterns
- <5% word count variance
- Grade C work (technically correct, structurally monotonous)

**After Implementation**:
- <20% formulaic rate (goal)
- <30% opening pattern repetition (goal)
- ≥5% word count variance (enforced)
- Grade A work (correct AND naturally varied)

### Current Results (Nov 21, 2025)

**Batch Analysis (10 materials)**:
- Average Diversity Score: 5.2/10
- Pass Rate: 0% (all failed - correctly identified issues)
- Property Dump Rate: 0% (no sequential dumps)
- Formulaic Rate: 0% (strict formula not detected)
- **Primary Issue**: Opening pattern repetition + word count uniformity

## Future Enhancements

1. **Adaptive Thresholds**: Learn optimal diversity score from high-quality samples
2. **Author-Specific Baselines**: Track diversity within author's historical patterns
3. **Semantic Similarity**: Use embeddings to detect deeper structural patterns
4. **Cross-Component Learning**: Apply patterns learned from captions to descriptions
5. **Real-Time Feedback**: Show diversity preview before generation complete

## Related Documentation

- **Quality Gates Overview**: `docs/06-ai-systems/QUALITY_GATES.md`
- **Winston AI Detection**: `docs/07-api/WINSTON_API.md`
- **Realism Scoring**: `docs/06-ai-systems/REALISM_EVALUATION.md`
- **Author Voice System**: `docs/06-ai-systems/AUTHOR_PERSONAS.md`
- **Humanness Layer**: `docs/06-ai-systems/HUMANNESS_OPTIMIZATION.md`

## See Also

- Implementation: `generation/validation/structural_variation_checker.py`
- Integration: `generation/core/quality_gated_generator.py`
- Coordinator: `domains/materials/coordinator.py`
- Tests: `tests/test_structural_variation_checker.py`
