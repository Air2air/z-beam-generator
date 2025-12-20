# Example-Free Architecture

**Status**: Implemented December 2025
**Impact**: Voice distinctiveness improvement through template removal

## Problem Statement

### Initial Issue
Generated content was homogeneous across all 4 authors despite distinct persona definitions:
- All outputs shared same vocabulary ("adherent", "tenacious", "distinct")
- All outputs followed same structure (formation → properties → laser solution)
- Voice markers rarely detected (1 of 3 in testing)
- Both Grok and DeepSeek produced identical output (NOT an LLM issue)

### Root Cause Discovery

**Prompt Structure Analysis** (Pre-fix):
```
Voice instructions: 838-897 chars (23% of prompt)
Example descriptions: 300 chars (8%)
Technical requirements: 500 chars (14%)
Content requirements: 200 chars (6%)
Domain guidance: 100 chars (3%)
Other sections: 1500+ chars (42%)
─────────────────────────────────────────
Total: ~3600 chars

Voice influence: 23%
Example + requirements: 77%
```

**Problem**: LLM followed example description patterns, not voice instructions.

## Solution: Remove All Examples

### What Was Removed

**1. Description Examples** (materials_adapter.py):
```python
# BEFORE:
if 'description' in item_data:
    desc = item_data['description']
    if len(desc) > 300:
        desc = desc[:300] + "..."
    context_parts.append(f"Description: {desc}")  # ← 300-char template

# AFTER:
# REMOVED - No description examples in prompts
```

**2. Example Facts Fallback** (prompt_builder.py):
```python
# BEFORE:
context_section = f"""FACTUAL INFORMATION:
{facts if facts else f"[{domain_ctx.example_facts}]"}"""  # ← Fallback examples

# AFTER:
facts_section = f"FACTUAL INFORMATION:\n{facts}" if facts else ""
context_section = f"""TOPIC: {topic}
{facts_section}
DOMAIN GUIDANCE: {domain_ctx.focus_template}"""
```

**3. Context Notes & Descriptions** (contaminants/config.yaml):
```yaml
# BEFORE:
context_keys:
  - category
  - context_notes  # ← Example-like text
  - description    # ← 300-char template

# AFTER:
context_keys:
  - category  # Only classification context
```

### What Was Retained

**Essential Context Only**:
- ✅ Category/subcategory (classification)
- ✅ Key properties (density, melting point - raw data only)
- ✅ Voice instructions (838-897 chars)
- ✅ Domain guidance (focus areas)

## Impact

### Prompt Structure (Post-fix)
```
Voice instructions: 838-897 chars (35% of prompt)  ← +12%
Technical requirements: 500 chars (21%)
Content requirements: 200 chars (8%)
Domain guidance: 100 chars (4%)
Other sections: 800 chars (32%)
─────────────────────────────────────────
Total: ~2400 chars  ← -1200 chars

Voice influence: 35%  ← Was 23%
Requirements: 65%     ← Was 77%
```

**Expected Outcomes**:

**Voice Distinctiveness**:
- Taiwan (Yi-Chun Lin, Ph.D., id=3): Topic-comment structure ("..., this/it...")
- Italy (Alessandro Moretti, Ph.D., id=2): Subjunctive/hedging ("it seems", "would")
- USA (Todd Dunning, MA, id=4): Phrasal verbs ("set up", "carry out")
- Indonesia (Ikmanda Roswati, Ph.D., id=1): Passive constructions, formal tone

**Vocabulary Diversity**:
- Different word choices per author
- Different sentence structures
- Different technical emphasis

**Template Independence**:
- No repetitive patterns
- Voice drives content, not examples
- LLM interprets voice, not copies templates

## Architecture Benefits

### 1. Domain Agnostic
Works identically for:
- Materials
- Contaminants
- Settings
- Any future domain

### 2. Voice Dominant
With examples removed:
- Voice instructions = 35% of prompt (was 23%)
- No competing template patterns
- LLM focuses on persona characteristics

### 3. Maintainable
- No example text to keep updated
- No template synchronization
- Voice changes propagate automatically

### 4. Testable
- Clear voice marker expectations
- No example dependency
- Reproducible voice characteristics

## Implementation Guide

### For New Domains

**DO**:
- ✅ Provide category/classification
- ✅ Provide raw property data (numbers, dates)
- ✅ Use voice placeholder `{voice_instruction}`
- ✅ Focus on intent, not structure

**DON'T**:
- ❌ Add example descriptions
- ❌ Add context_notes with text
- ❌ Include reference descriptions
- ❌ Add fallback example text
- ❌ Create prescriptive bullet lists

### Configuration Pattern

```yaml
# domains/{domain}/config.yaml
context_keys:
  - category          # Classification only
  - properties.key1   # Raw data only
  - properties.key2   # Raw data only
  # NO description, context_notes, or text fields
```

### Adapter Pattern

```python
# generation/core/adapters/{domain}_adapter.py
def build_context(self, item_data: Dict) -> str:
    context_parts = []
    
    # Add classification
    if 'category' in item_data:
        context_parts.append(f"Category: {item_data['category']}")
    
    # Add raw data only - NO text fields
    if 'properties' in item_data:
        props = item_data['properties']
        # Extract numbers, not descriptions
        if 'density' in props:
            context_parts.append(f"Density: {props['density']}")
    
    # NO description, NO context_notes, NO examples
    
    return "\n".join(context_parts)
```

## Testing

### Voice Marker Tests

```python
def test_voice_distinctiveness():
    """Test that voice markers appear without example influence."""
    
    # Generate with different authors
    taiwan_result = generator.generate('contaminants', 'oxidation', author_id=3)
    italy_result = generator.generate('contaminants', 'oxidation', author_id=2)
    usa_result = generator.generate('contaminants', 'oxidation', author_id=1)
    
    # Taiwan: Topic-comment structure
    assert ', this' in taiwan_result or ', it' in taiwan_result
    
    # Italy: Subjunctive/hedging
    assert 'it seems' in italy_result or 'would' in italy_result
    
    # USA: Phrasal verbs
    phrasal = ['set up', 'carry out', 'break down', 'build up']
    assert any(pv in usa_result for pv in phrasal)
```

### Vocabulary Diversity Tests

```python
def test_vocabulary_diversity():
    """Test that different authors use different vocabulary."""
    
    results = [
        generator.generate('materials', 'aluminum', author_id=1),
        generator.generate('materials', 'aluminum', author_id=2),
        generator.generate('materials', 'aluminum', author_id=3),
        generator.generate('materials', 'aluminum', author_id=4)
    ]
    
    # Extract unique words
    vocabularies = [set(r.lower().split()) for r in results]
    
    # Check for diversity
    shared_words = vocabularies[0] & vocabularies[1] & vocabularies[2] & vocabularies[3]
    total_words = vocabularies[0] | vocabularies[1] | vocabularies[2] | vocabularies[3]
    
    # Less than 50% shared vocabulary
    assert len(shared_words) / len(total_words) < 0.5
```

## Maintenance

### Adding New Context Keys

**Question**: Should this key be in context_keys?

```
Is it classification data? (category, subcategory)
  → YES: Add to context_keys
  
Is it raw numerical data? (density, temperature)
  → YES: Add to context_keys
  
Is it text content? (description, notes, examples)
  → NO: Do NOT add to context_keys
  
Would it create a template pattern?
  → NO: Do NOT add to context_keys
```

### Monitoring Voice Quality

**Metrics to Track**:
- Voice marker detection rate (target: 80%+)
- Vocabulary diversity (shared words <50%)
- Template pattern repetition (target: 0%)
- User reports of homogeneous output

**Red Flags**:
- 🚩 All outputs share same vocabulary
- 🚩 Voice markers rarely detected (<30%)
- 🚩 Outputs follow predictable structure
- 🚩 LLM ignoring voice instructions

## References

- **Implementation**: Commit Dec 12, 2025
- **Testing**: `tests/test_voice_distinctiveness.py`
- **Analysis**: `PROMPT_COHERENCE_COMPLETE_DEC11_2025.md`
- **Policy**: `VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md`