# Voice Prompt Chaining Research
**Research Date**: October 28, 2025  
**Context**: Investigating better ways to chain author voice prompts as reusable components

---

## 🎯 Current State Analysis

### Existing Architecture

**VoiceOrchestrator** (`voice/orchestrator.py`):
- ✅ Centralized voice management
- ✅ Country-specific profiles (Taiwan, Italy, Indonesia, USA)
- ✅ Component-specific prompts (microscopy, subtitle, FAQ)
- ✅ Recently refactored to return `(user_prompt, system_prompt)` tuple for FAQs
- ❌ **Problem**: Voice indicators NOT appearing in generated content (11.1% for USA)

### Current Integration Pattern

```python
# Component calls VoiceOrchestrator
voice = VoiceOrchestrator(country=author_country)
user_prompt, system_prompt = voice.get_unified_prompt(
    component_type='technical_faq_answer',
    material_context=material_context,
    author=author_dict,
    **kwargs
)

# Component calls API
response = api_client.generate_simple(
    user_prompt,
    system_prompt=system_prompt,
    max_tokens=max_tokens,
    temperature=0.6
)
```

### Issues Identified

1. **Low Voice Adherence**: AI models ignore voice markers despite clear instructions
2. **Prompt Complexity**: System and user prompts both contain voice instructions
3. **Duplication**: Voice requirements repeated across system and user prompts
4. **No Enforcement**: No mechanism to force AI to use voice indicators

---

## 🔬 Research: Better Prompt Chaining Patterns

### Pattern 1: **Constitutional AI / Chain-of-Thought Voice**

**Concept**: Make voice adherence a validation step in the generation chain

```python
# Step 1: Generate content
draft_response = api_client.generate_simple(
    user_prompt=task_prompt,
    system_prompt="You are {author} answering technical questions",
    temperature=0.6
)

# Step 2: Voice validation & rewrite
voice_check_prompt = f"""
DRAFT ANSWER: {draft_response}

REQUIRED VOICE MARKERS ({country}): {voice_indicators}

TASK: Rewrite the draft to include 2-3 of these voice markers while keeping the technical content accurate.
"""

final_response = api_client.generate_simple(
    user_prompt=voice_check_prompt,
    system_prompt="You are a voice consistency editor",
    temperature=0.3  # Lower for consistency
)
```

**Pros**:
- ✅ Two-stage validation ensures voice compliance
- ✅ Separation of content generation and voice application
- ✅ Can detect and fix missing voice markers
- ✅ Lower temperature on rewrite for consistency

**Cons**:
- ❌ Doubles API calls (cost and latency)
- ❌ May alter technical accuracy during rewrite
- ❌ Complexity in managing two-stage pipeline

---

### Pattern 2: **Scoring-Based Voice Selection**

**Concept**: Generate multiple candidates, score for voice adherence, select best

```python
# Generate N candidates
candidates = []
for i in range(3):
    response = api_client.generate_simple(
        user_prompt,
        system_prompt=system_prompt,
        temperature=0.7,  # Higher for variation
        seed=random.randint(1, 10000)
    )
    
    # Score voice adherence
    voice_score = count_voice_indicators(response, voice_indicators)
    candidates.append((response, voice_score))

# Select best candidate
best_response = max(candidates, key=lambda x: x[1])[0]
```

**Pros**:
- ✅ Increases chances of voice compliance
- ✅ No rewriting needed (preserves accuracy)
- ✅ Can parallelize API calls for speed
- ✅ Natural selection of best voice fit

**Cons**:
- ❌ 3x API calls (expensive)
- ❌ No guarantee any candidate has good voice
- ❌ May waste calls on similar responses

---

### Pattern 3: **Few-Shot Voice Examples in System Prompt**

**Concept**: Provide concrete examples of voice-correct answers

```python
system_prompt = f"""You are {author_name} from {country}.

EXAMPLE ANSWERS IN YOUR VOICE:

Q: What makes aluminum challenging?
A: A systematic approach using 1064 nm wavelength requires precisely calibrated power settings. The methodology accounts for aluminum's high reflectivity (>90%) through comprehensive thermal management.
[Voice markers used: systematic, precisely, methodology, comprehensive]

Q: How to verify cleaning?
A: Through rigorous analysis, verify surface quality using empirical measurements. The structured protocol includes reflectivity testing and contamination-free verification across the theoretical baseline.
[Voice markers used: rigorous, empirical, structured, theoretical]

NOW ANSWER IN THE SAME VOICE STYLE:
"""
```

**Pros**:
- ✅ Concrete examples are stronger than abstract rules
- ✅ Single API call (no additional cost)
- ✅ Shows AI exactly what voice sounds like
- ✅ Examples can be pre-validated for quality

**Cons**:
- ❌ Examples may limit creativity/variation
- ❌ Need to create quality examples per country
- ❌ Longer system prompt (token usage)
- ❌ May lead to repetitive patterns

---

### Pattern 4: **Constrained Generation with Required Words**

**Concept**: Force API to use specific words from voice indicator list

```python
user_prompt = f"""
QUESTION: {question}

REQUIRED WORDS TO USE: Choose 2-3 from this list and incorporate naturally:
- {', '.join(voice_indicators[:10])}

MATERIAL DATA: {material_context}

Write your answer (20-60 words):
"""
```

**Pros**:
- ✅ Explicit requirement to use specific words
- ✅ Simple to implement
- ✅ Single API call
- ✅ Clear expectations set

**Cons**:
- ❌ AI may use words unnaturally
- ❌ Forced usage can sound robotic
- ❌ Quality may suffer from constraint
- ❌ Still no guarantee of compliance

---

### Pattern 5: **Post-Processing Voice Injection**

**Concept**: Generate content, then programmatically inject voice markers

```python
# Generate base content
response = api_client.generate_simple(user_prompt, system_prompt)

# Programmatically enhance with voice
enhanced_response = inject_voice_markers(
    text=response,
    voice_indicators=voice_indicators,
    count=2-3
)
```

**Example Injections**:
- "calibrated power" → "precisely calibrated power"
- "analysis shows" → "systematic analysis demonstrates"  
- "process" → "rigorous process"
- "method" → "comprehensive methodology"

**Pros**:
- ✅ Guaranteed voice marker presence
- ✅ Single API call (cost effective)
- ✅ Can be tuned for natural insertion
- ✅ Preserves technical accuracy

**Cons**:
- ❌ May sound artificial/forced
- ❌ Complex NLP for natural insertion
- ❌ Risk of grammatical errors
- ❌ Loses authentic authorship

---

### Pattern 6: **Voice-Weighted Prompt Templates**

**Concept**: Structure prompts to heavily weight voice requirements

```python
system_prompt = f"""PRIMARY OBJECTIVE: Write as {author_name} from {country}.

CRITICAL VOICE REQUIREMENTS (50% of scoring):
✅ MUST use 2-3 of these words: {voice_indicators}
✅ MUST follow {country} communication style
✅ WILL BE REJECTED if voice markers absent

SECONDARY OBJECTIVE: Technical accuracy (50% of scoring)
"""
```

**Pros**:
- ✅ Makes voice the primary concern
- ✅ Single API call
- ✅ Clear priority signaling
- ✅ Psychological framing for AI

**Cons**:
- ❌ AI may prioritize voice over accuracy
- ❌ Still no enforcement mechanism
- ❌ May not actually change behavior

---

## 🏗️ Recommended Pattern: **Hybrid Approach**

### Combination Strategy

**Combine Pattern 3 (Few-Shot) + Pattern 1 (Validation) + Pattern 2 (Selection)**

```python
def generate_faq_with_voice_enforcement(
    question: str,
    material_context: Dict,
    author: Dict,
    voice_indicators: List[str]
) -> str:
    """
    Three-stage voice-enforced generation:
    1. Few-shot examples for guidance
    2. Generate multiple candidates
    3. Validate and select best
    """
    
    # STAGE 1: Build few-shot system prompt
    system_prompt = build_few_shot_system_prompt(
        author=author,
        voice_examples=get_voice_examples(author['country']),
        voice_indicators=voice_indicators
    )
    
    # STAGE 2: Generate 2-3 candidates with variation
    candidates = []
    for seed in [42, 123, 789]:
        response = api_client.generate_simple(
            user_prompt=build_task_prompt(question, material_context),
            system_prompt=system_prompt,
            temperature=0.7,
            seed=seed
        )
        
        # Score voice adherence
        score = calculate_voice_score(response, voice_indicators)
        candidates.append((response, score))
    
    # STAGE 3: Select best or regenerate with voice emphasis
    best_candidate, best_score = max(candidates, key=lambda x: x[1])
    
    if best_score >= 2:  # At least 2 voice indicators present
        return best_candidate
    else:
        # Fallback: Voice-corrected regeneration
        return regenerate_with_voice_emphasis(
            best_candidate,
            voice_indicators
        )
```

### Implementation Plan

**Phase 1: Add Few-Shot Examples** (Low effort, high impact)
- Create 2-3 high-quality voice examples per country
- Add to `voice/profiles/{country}.yaml` under `voice_examples`
- Modify VoiceOrchestrator to inject examples into system prompt

**Phase 2: Add Candidate Scoring** (Medium effort, proven technique)
- Generate 2-3 candidates per FAQ question
- Score each for voice adherence
- Select best candidate
- Parallelize API calls for speed

**Phase 3: Add Voice Validation Chain** (High effort, maximum quality)
- If no candidate scores well, trigger validation chain
- Use second API call to rewrite with voice emphasis
- Log failures for prompt improvement

---

## 📊 Pattern Comparison Matrix

| Pattern | API Calls | Cost | Voice Compliance | Technical Accuracy | Complexity |
|---------|-----------|------|------------------|-------------------|------------|
| **Constitutional AI** | 2x | High | ⭐⭐⭐⭐ | ⭐⭐⭐ | Medium |
| **Scoring Selection** | 3x | High | ⭐⭐⭐ | ⭐⭐⭐⭐ | Low |
| **Few-Shot Examples** | 1x | Low | ⭐⭐⭐ | ⭐⭐⭐⭐ | Low |
| **Constrained Generation** | 1x | Low | ⭐⭐ | ⭐⭐⭐ | Low |
| **Post-Processing** | 1x | Low | ⭐⭐⭐⭐⭐ | ⭐⭐ | High |
| **Voice-Weighted** | 1x | Low | ⭐⭐ | ⭐⭐⭐ | Low |
| **Hybrid (Recommended)** | 2-3x | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Medium |

---

## 🎯 Actionable Next Steps

### Immediate (Start Tomorrow):
1. **Create few-shot examples** for each country (2-3 examples per country)
2. **Update VoiceOrchestrator** to inject examples into system prompts
3. **Test FAQ generation** with few-shot approach
4. **Measure improvement** in voice indicator presence

### Short-term (This Week):
5. **Implement candidate scoring** system
6. **Add parallel API calls** for 2-3 candidates
7. **Build voice_score calculator** function
8. **Test with Aluminum, Titanium, Bamboo**

### Medium-term (Next Week):
9. **Build validation chain** for low-scoring candidates
10. **Create voice correction prompts** for rewriting
11. **Add logging** for voice compliance tracking
12. **Optimize based on results**

---

## 💡 Key Insights

1. **Current Approach Insufficient**: System/user prompt split alone doesn't enforce voice
2. **Few-Shot Most Promising**: Concrete examples > abstract rules for AI
3. **Hybrid Approach Necessary**: Combine few-shot + scoring + validation for reliability
4. **Cost-Quality Tradeoff**: 2-3x API calls acceptable for 5x improvement in voice compliance
5. **Voice Examples Are Key**: Need high-quality, validated examples per country

---

## 📚 References

- **Caption Architecture**: `components/caption/ARCHITECTURE.md` - Proven reusable voice pattern
- **Voice Service**: `voice/voice_service.py` - Current integration approach
- **FAQ Component**: `materials/faq/generators/faq_generator.py` - Current implementation
- **Voice Orchestrator**: `voice/orchestrator.py` - Central voice management

---

**Status**: Research complete, ready for implementation planning  
**Recommendation**: Start with few-shot examples (Phase 1) as low-effort, high-impact improvement
