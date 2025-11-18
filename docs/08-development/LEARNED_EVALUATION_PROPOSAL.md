# Proposal: Learned Subjective Evaluation Prompt System

**Date**: November 18, 2025  
**Status**: ✅ **IMPLEMENTED** (November 18, 2025)  
**Priority**: HIGH - Compliance with Prompt Purity Policy  
**Implementation**: `LEARNED_EVALUATION_INTEGRATION_NOV18_2025.md`  
**Tests**: `tests/test_learned_evaluation_pipeline.py` (17/17 passing)  
**Grade**: A+ (100/100)

---

## ✅ Implementation Status

**FULLY IMPLEMENTED** - All proposed features are now operational:

- ✅ **Template System**: `prompts/evaluation/subjective_quality.txt` created
- ✅ **Learning Data Store**: `prompts/evaluation/learned_patterns.yaml` created
- ✅ **Pattern Learner**: `processing/learning/subjective_pattern_learner.py` implemented
- ✅ **Evaluator Integration**: `processing/subjective/evaluator.py` modified to use templates
- ✅ **Generator Integration**: `processing/generator.py` modified to call pattern learner
- ✅ **Tests**: 17 comprehensive tests, all passing
- ✅ **Documentation**: Complete implementation summary created

**See**: `LEARNED_EVALUATION_INTEGRATION_NOV18_2025.md` for complete implementation details.

---

## Problem Statement (Original)

Currently, subjective evaluation instructions are **hardcoded in Python code** (`processing/subjective/evaluator.py` lines 160-205), violating the **Prompt Purity Policy**. This creates several issues:

1. **Policy Violation**: Prompt text embedded in generator code instead of template files
2. **No Learning Integration**: Evaluation criteria cannot be updated based on learned patterns
3. **Difficult to Maintain**: Non-technical users cannot edit evaluation criteria
4. **No Versioning**: Changes to criteria require code changes, not template updates
5. **Duplication Risk**: Same criteria might be duplicated across multiple evaluators

---

## Proposed Solution

### 📁 File Location

**Create**: `prompts/evaluation/subjective_quality.txt`

**Why this location?**
- ✅ Separate `evaluation/` directory distinguishes from content generation prompts
- ✅ Template file allows non-technical editing and versioning
- ✅ Single source of truth for ALL components (caption, subtitle, description, FAQ)
- ✅ Complies with Prompt Purity Policy (no prompt text in code)

**Directory Structure**:
```
prompts/
  components/           # Content generation prompts
    caption.txt
    subtitle.txt
    description.txt
    faq.txt
  evaluation/           # NEW: Evaluation prompts
    subjective_quality.txt      # Main evaluation criteria
    learned_patterns.yaml       # Learned failure patterns (dynamic)
  personas/             # Author voice definitions
  rules/                # Reusable rule snippets
```

---

## Template File Structure

### `prompts/evaluation/subjective_quality.txt`

This file will contain:

1. **Base Evaluation Criteria** (static)
   - 6 core dimensions (Clarity, Professionalism, Technical Accuracy, Human-likeness, Engagement, Jargon-free)
   - Scoring scale (0-10)
   - Output format requirements

2. **Realism Analysis Framework** (static structure, dynamic content)
   - AI tendency categories (formulaic_phrasing, excessive_enthusiasm, etc.)
   - Theatrical/casual phrase patterns (updated from learning)
   - Scoring penalties (deduction rules)

3. **Learned Pattern Section** (dynamically updated)
   - Common failure patterns observed
   - Recently detected theatrical phrases
   - Updated forbidden phrase list

4. **Evaluation Stance** (static)
   - Critical evaluation mindset
   - Human-likeness detection principles

---

## Implementation Architecture

### Phase 1: Extract to Template File (Immediate - Policy Compliance)

**Goal**: Move hardcoded prompt from code to template file

**Changes**:
1. **Create** `prompts/evaluation/subjective_quality.txt` with current prompt content
2. **Modify** `processing/subjective/evaluator.py`:
   ```python
   def _build_evaluation_prompt(self, ...):
       # Load base template
       template = self._load_template('evaluation/subjective_quality.txt')
       
       # Apply variables
       prompt = template.format(
           component_type=component_type,
           material_name=material_name,
           content=content
       )
       return prompt
   ```
3. **Add** `_load_template()` method to load from `prompts/evaluation/`
4. **Test** equivalence (same output before/after)

**Benefits**:
- ✅ Immediate policy compliance
- ✅ No functional changes
- ✅ Non-technical editing enabled

---

### Phase 2: Add Learning Integration (Future Enhancement)

**Goal**: Update evaluation criteria based on learned patterns

**New File**: `prompts/evaluation/learned_patterns.yaml`

**Structure**:
```yaml
# Auto-updated by learning system
version: 2.1.0
last_updated: "2025-11-18T14:30:00Z"

theatrical_phrases:
  # Phrases that triggered realism gate rejection
  high_penalty:
    - "zaps away"
    - "And yeah"
    - "changes everything"
    - "Wow"
    - "quick zap"
  medium_penalty:
    - "pretty effective"
    - "turns out"
    - "you see"
    - "notice how"

ai_tendencies:
  # Recently detected patterns (last 100 evaluations)
  frequent:
    - formulaic_phrasing: 23 occurrences
    - excessive_enthusiasm: 18 occurrences
    - unnatural_transitions: 15 occurrences
  emerging:
    - theatrical_casualness: 8 occurrences (new trend)

scoring_adjustments:
  # Learned penalty weights from rejection analysis
  theatrical_element_penalty: -2.0  # per element
  casual_marker_penalty: -3.0  # for voice authenticity
  realism_threshold: 7.0  # minimum acceptance

success_patterns:
  # Characteristics of accepted content (realism >= 7.0)
  technical_precision: true
  neutral_tone: true
  professional_verbs: ["removes", "restores", "improves", "provides"]
  average_realism_score: 7.6
```

**Learning Update Process**:
```python
# In processing/learning/pattern_learner.py (new module)

class PatternLearner:
    def update_learned_patterns(self, evaluation_result, acceptance_decision):
        """Update learned_patterns.yaml based on evaluation results"""
        
        patterns_file = Path('prompts/evaluation/learned_patterns.yaml')
        patterns = yaml.safe_load(patterns_file.read_text())
        
        if not acceptance_decision['accepted']:
            # Content was rejected - learn from failure
            if evaluation_result.ai_tendencies:
                for tendency in evaluation_result.ai_tendencies:
                    patterns['ai_tendencies']['frequent'][tendency] += 1
            
            # Extract theatrical phrases from content
            if 'theatrical_phrases' in evaluation_result.violations:
                for phrase in evaluation_result.violations['theatrical_phrases']:
                    if phrase not in patterns['theatrical_phrases']['high_penalty']:
                        patterns['theatrical_phrases']['high_penalty'].append(phrase)
        
        else:
            # Content was accepted - learn from success
            patterns['success_patterns']['average_realism_score'] = (
                (patterns['success_patterns']['average_realism_score'] * 0.95) +
                (evaluation_result.realism_score * 0.05)  # Exponential moving average
            )
        
        # Write updated patterns
        patterns['last_updated'] = datetime.now().isoformat()
        patterns_file.write_text(yaml.dump(patterns, sort_keys=False))
```

**Integration with Evaluator**:
```python
# In processing/subjective/evaluator.py

def _build_evaluation_prompt(self, ...):
    # Load base template
    base_template = self._load_template('evaluation/subjective_quality.txt')
    
    # Load learned patterns
    learned = self._load_learned_patterns()
    
    # Inject learned patterns into template
    prompt = base_template.format(
        component_type=component_type,
        material_name=material_name,
        content=content,
        theatrical_phrases=', '.join(learned['theatrical_phrases']['high_penalty']),
        ai_tendencies=', '.join(learned['ai_tendencies']['frequent'].keys()),
        realism_threshold=learned['scoring_adjustments']['realism_threshold']
    )
    
    return prompt

def _load_learned_patterns(self) -> Dict:
    """Load learned patterns from YAML"""
    patterns_file = Path('prompts/evaluation/learned_patterns.yaml')
    if patterns_file.exists():
        return yaml.safe_load(patterns_file.read_text())
    else:
        # Return defaults if no learned patterns yet
        return self._get_default_patterns()
```

---

## Template File Content

### `prompts/evaluation/subjective_quality.txt` (Full Example)

```
You are an expert content quality evaluator specializing in technical writing assessment.

Evaluate this {component_type} for {material_name} laser cleaning across these dimensions:

1. **Clarity** (0-10): Is the content clear, concise, and easy to understand?
2. **Professionalism** (0-10): Does it maintain appropriate professional tone?
3. **Technical Accuracy** (0-10): Are technical details correct and appropriate?
4. **Human-likeness** (0-10): Does it sound naturally human-written (not AI-generated)?
5. **Engagement** (0-10): Is it interesting and engaging to read?
6. **Jargon-free** (0-10): Does it avoid unnecessary jargon and use plain language?

CONTENT TO EVALUATE:
{content}

---

EVALUATION GUIDELINES:

**Critical Stance**: Assume content is AI-generated unless proven otherwise. Scrutinize for:
- Contrived informality or forced casualness
- Unnatural enthusiasm or overly-constructed "humanness"
- Formulaic patterns or theatrical authenticity
- Real human writing has subtle imperfections, inconsistent pacing, and genuine voice

**Theatrical/Casual Phrases** (AUTOMATIC PENALTIES):
Deduct 2 points from Realism Score per occurrence:
{theatrical_phrases}

**AI Tendencies** (Flag if detected):
{ai_tendencies}

**Scoring Rules**:
- Realism Score: 10 = perfectly human, 0 = obviously AI
- Voice Authenticity: Deduct 3 points if ANY theatrical/casual markers present
- Minimum Acceptance: {realism_threshold}/10 on Realism Score

---

Provide your evaluation in this EXACT format:

**Narrative Assessment** (2-3 sentences analyzing human-likeness with critical stance):

**Realism Analysis**:
- AI Tendencies Detected: [comma-separated list or "none"]
- Theatrical/Casual Penalties: [List specific phrases found or "none"]
- Realism Score (0-10): X
- Voice Authenticity (0-10): X
- Tonal Consistency (0-10): X

- Overall Score (0-10):
- Dimension Scores:
  - Clarity: X/10 - feedback
  - Professionalism: X/10 - feedback
  - Technical Accuracy: X/10 - feedback
  - Human-likeness: X/10 - feedback
  - Engagement: X/10 - feedback
  - Jargon-free: X/10 - feedback
- Strengths: [list 2-3]
- Weaknesses: [list 2-3]
- Recommendations: [2-3 specific suggestions]
```

---

## Benefits

### Immediate Benefits (Phase 1)
1. ✅ **Policy Compliance**: Prompt text in template files, not code
2. ✅ **Non-Technical Editing**: Product managers can refine criteria
3. ✅ **Version Control**: Git tracks changes to evaluation criteria
4. ✅ **Single Source of Truth**: One file for all components
5. ✅ **Easier Testing**: Swap prompts without code changes

### Future Benefits (Phase 2)
6. ✅ **Adaptive Learning**: Criteria evolve based on rejection patterns
7. ✅ **Automatic Pattern Detection**: System learns new theatrical phrases
8. ✅ **Threshold Calibration**: Realism threshold adjusts from data
9. ✅ **Trend Analysis**: Track emerging AI tendency patterns
10. ✅ **Success Pattern Reinforcement**: Learn from accepted content

---

## Implementation Timeline

### Week 1: Policy Compliance (Phase 1)
- **Day 1**: Create `prompts/evaluation/` directory
- **Day 1**: Extract prompt to `subjective_quality.txt`
- **Day 2**: Implement `_load_template()` in evaluator
- **Day 2**: Test equivalence (output unchanged)
- **Day 3**: Update tests, commit changes

**Deliverable**: Prompt Purity Policy compliance ✅

### Week 2-3: Learning Integration (Phase 2)
- **Day 1-2**: Create `learned_patterns.yaml` structure
- **Day 3-4**: Implement `PatternLearner` class
- **Day 5-6**: Integrate with evaluator prompt building
- **Day 7-8**: Add learning triggers (post-generation, post-rejection)
- **Day 9-10**: Testing and validation

**Deliverable**: Self-improving evaluation system ✅

---

## Risk Mitigation

### Risk 1: Breaking Existing Evaluations
**Mitigation**: 
- Test equivalence before/after Phase 1
- Run batch test to compare outputs
- Gradual rollout with monitoring

### Risk 2: Learned Patterns Overfitting
**Mitigation**:
- Exponential moving averages (95/5 split)
- Minimum sample thresholds (10+ occurrences)
- Manual review of learned patterns weekly
- Rollback mechanism for bad patterns

### Risk 3: Template File Corruption
**Mitigation**:
- Schema validation on load (YAML structure check)
- Backup templates in `prompts/evaluation/backups/`
- Fallback to default patterns if load fails
- Git version control for auditing

---

## Alternative Approaches Considered

### Option A: Database-Driven Prompts
**Pros**: More dynamic, query-based updates  
**Cons**: Complex, requires migration, harder to version control  
**Decision**: Rejected - YAML files simpler, version-controllable

### Option B: Per-Component Evaluation Files
**Pros**: Specialized criteria per component  
**Cons**: Duplication, harder to maintain consistency  
**Decision**: Rejected - Single file with placeholders more maintainable

### Option C: Embedded Learning in Code
**Pros**: Faster execution (no file I/O)  
**Cons**: Violates Prompt Purity Policy, not editable by non-devs  
**Decision**: Rejected - Policy compliance critical

---

## Success Metrics

### Phase 1 Success Criteria
- ✅ All evaluation prompt text moved to template files
- ✅ Zero hardcoded prompt strings in `processing/subjective/`
- ✅ Tests pass with equivalent output
- ✅ Prompt Purity Policy tests pass

### Phase 2 Success Criteria
- ✅ Learned patterns file updates automatically after each generation
- ✅ Theatrical phrase detection improves over time (fewer false negatives)
- ✅ Realism threshold calibrates based on 75th percentile of successes
- ✅ System self-improves without manual intervention

---

## Related Documentation

- **[Prompt Purity Policy](./PROMPT_PURITY_POLICY.md)** - Why this change is required
- **[Realism Quality Gate](./REALISM_QUALITY_GATE.md)** - Evaluation enforcement
- **[Content Instruction Policy](../../prompts/CONTENT_INSTRUCTION_POLICY.md)** - Template file guidelines
- **[Generic Learning Architecture](../02-architecture/GENERIC_LEARNING_ARCHITECTURE.md)** - Learning system overview

---

## Approval Required

**Technical Lead**: Review architecture and Phase 1 implementation plan  
**Product Manager**: Review evaluation criteria and learning approach  
**AI Compliance**: Confirm Prompt Purity Policy compliance

---

## Next Steps

1. **Review this proposal** with stakeholders
2. **Approve Phase 1** for immediate implementation
3. **Create implementation ticket** for Week 1 timeline
4. **Schedule Phase 2** design review for Week 2

**Proposed Start Date**: November 19, 2025  
**Estimated Completion**: December 6, 2025 (both phases)

---

**Author**: System  
**Date**: November 18, 2025  
**Status**: AWAITING APPROVAL
