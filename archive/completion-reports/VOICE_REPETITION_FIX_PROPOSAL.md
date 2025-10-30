# Voice Repetition Fix - Architectural Proposal

**Date**: October 29, 2025  
**Issue**: Voice markers repeat excessively across FAQ answers (86-100% repetition rate)  
**Root Cause**: Per-answer enhancement without cross-answer context

---

## 🔍 Problem Analysis

### Current Architecture (BROKEN)

```
FAQ Generation Flow:
1. Generate 7 FAQ Q&A pairs (no voice)
2. FOR EACH answer (loop 7 times):
   └─> voice_processor.enhance(single_answer)
       └─> AI adds 2-3 markers to THIS answer
       └─> NO CONTEXT about other answers
       └─> NO TRACKING of used markers
3. Result: "meticulous" in 6/7 answers (86%)
```

### Why It Fails

- **Independent Enhancement**: Each answer enhanced in isolation
- **No Memory**: AI doesn't know what markers were used in previous answers
- **No Distribution Logic**: No mechanism to spread markers across answers
- **Prompt Limitations**: Repetition rules in prompt can't prevent cross-answer repetition

---

## 🎯 Proposed Solutions (3 Options)

### **Option 1: Batch Enhancement with Global Context** ⭐ RECOMMENDED

**Concept**: Enhance ALL answers in a single API call with marker distribution awareness.

**Architecture**:
```python
# BEFORE (Current - Per Answer)
for item in faq_items:
    item['answer'] = voice_processor.enhance(item['answer'], author)

# AFTER (Proposed - Batch)
enhanced_items = voice_processor.enhance_batch(
    faq_items=faq_items,
    author=author,
    marker_distribution='varied'  # Each answer uses DIFFERENT markers
)
```

**Implementation**:
```python
class VoicePostProcessor:
    def enhance_batch(
        self,
        faq_items: List[Dict],
        author: Dict,
        marker_distribution: str = 'varied'
    ) -> List[Dict]:
        """
        Enhance multiple FAQ answers with distributed voice markers.
        
        Args:
            faq_items: List of FAQ Q&A dicts
            author: Author info with country
            marker_distribution: 'varied' | 'balanced' | 'random'
                - varied: Different markers per answer
                - balanced: Each marker used ~once across all answers
                - random: Random selection (current behavior)
        
        Returns:
            Enhanced FAQ items with distributed voice markers
        """
        # Get voice indicators for country
        voice_indicators = self._get_voice_indicators(author)
        
        # Build batch prompt with distribution rules
        prompt = f"""You are enhancing {len(faq_items)} FAQ answers with your voice.

YOUR VOICE MARKERS: {', '.join(voice_indicators)}

🚫 CRITICAL DISTRIBUTION RULES:
1. **USE EACH MARKER AT MOST ONCE** across all {len(faq_items)} answers
2. **VARY MARKERS** - distribute them across different answers
3. **AIM FOR BALANCE** - if you have 7 answers and 7 markers, use each marker once
4. **AVOID CLUSTERING** - don't put multiple markers in same answer
5. **SOME ANSWERS NO MARKERS** - it's OK if 2-3 answers have zero markers

FAQ ANSWERS TO ENHANCE:
{self._format_batch_input(faq_items)}

Return the enhanced answers maintaining the same JSON structure."""
        
        # Single API call for all answers
        response = self.api_client.generate_simple(prompt, max_tokens=5000)
        
        return self._parse_batch_output(response.content)
```

**Pros**:
- ✅ Single API call (faster, cheaper)
- ✅ AI sees all answers at once
- ✅ Can distribute markers intelligently
- ✅ Natural enforcement of "use each marker once"

**Cons**:
- ❌ Requires rewrite of voice_processor.enhance()
- ❌ Larger prompt/response (but still within limits)
- ❌ All-or-nothing (if one answer fails, need to retry all)

**Estimated Effort**: 2-3 hours

---

### **Option 2: Marker Tracking with Sequential Enhancement**

**Concept**: Keep per-answer enhancement but track used markers.

**Architecture**:
```python
class VoicePostProcessor:
    def enhance_with_tracking(
        self,
        faq_items: List[Dict],
        author: Dict
    ) -> List[Dict]:
        """Track used markers across answers."""
        used_markers = set()
        available_markers = self._get_voice_indicators(author)
        
        for item in faq_items:
            # Get unused markers only
            unused = [m for m in available_markers if m not in used_markers]
            
            if len(unused) < 2:
                # Skip enhancement if too few markers left
                continue
            
            # Enhance with unused markers only
            enhanced = self.enhance(
                item['answer'],
                author,
                allowed_markers=unused,  # NEW PARAMETER
                max_markers=2
            )
            
            # Track what was actually used
            used_in_answer = self._detect_markers_in_text(enhanced, available_markers)
            used_markers.update(used_in_answer)
            
            item['answer'] = enhanced
        
        return faq_items
```

**Pros**:
- ✅ Minimal changes to existing code
- ✅ Gradual improvement (can still retry individual answers)
- ✅ Clear marker tracking logic

**Cons**:
- ❌ Still 7 separate API calls (slower, more expensive)
- ❌ Order-dependent (first answers get best markers)
- ❌ Complex tracking logic
- ❌ Hard to enforce "use each marker once" in prompt

**Estimated Effort**: 3-4 hours

---

### **Option 3: Post-Generation Marker Redistribution**

**Concept**: Generate with voice, then redistribute markers if repetition detected.

**Architecture**:
```python
class VoicePostProcessor:
    def enhance_with_redistribution(
        self,
        faq_items: List[Dict],
        author: Dict
    ) -> List[Dict]:
        """Enhance then fix repetition through redistribution."""
        
        # Step 1: Normal per-answer enhancement
        for item in faq_items:
            item['answer'] = self.enhance(item['answer'], author)
        
        # Step 2: Detect repetition
        repetition = self._analyze_marker_distribution(faq_items, author)
        
        # Step 3: If marker appears in >60% of answers, remove from some
        for marker, percentage in repetition.items():
            if percentage > 60:
                # Remove marker from random answers until <60%
                affected_items = [
                    item for item in faq_items 
                    if marker in item['answer'].lower()
                ]
                
                # Keep in first 40%, remove from rest
                keep_count = int(len(faq_items) * 0.4)
                to_fix = affected_items[keep_count:]
                
                for item in to_fix:
                    # Remove marker via API call
                    item['answer'] = self._remove_marker(
                        item['answer'],
                        marker,
                        author
                    )
        
        return faq_items
```

**Pros**:
- ✅ Non-invasive (works with current code)
- ✅ Can run as post-processing step
- ✅ Clear separation of concerns

**Cons**:
- ❌ More API calls (7 enhance + N fixes)
- ❌ Slower and more expensive
- ❌ Removing markers may damage text quality
- ❌ Doesn't prevent problem, just fixes it

**Estimated Effort**: 4-5 hours

---

## 🏆 Recommendation: Option 1 (Batch Enhancement)

### Why Option 1 is Best:

1. **Root Cause Fix**: Addresses the fundamental issue (lack of context)
2. **Performance**: Single API call vs 7+ calls
3. **Cost**: ~85% cheaper (1 call vs 7 calls)
4. **Quality**: AI can optimize marker distribution naturally
5. **Simplicity**: Cleaner architecture, less tracking logic

### Implementation Plan:

#### Phase 1: Add Batch Enhancement Method (1 hour)
```python
# voice/post_processor.py
def enhance_batch(self, faq_items, author, marker_distribution='varied'):
    # Build batch prompt with distribution rules
    # Single API call
    # Parse and return enhanced items
```

#### Phase 2: Update FAQ Generator to Use Batch (30 min)
```python
# components/faq/generators/faq_generator.py
if author and 'country' in author:
    faq_items = yaml.safe_load(faq_content)
    voice_processor = VoicePostProcessor(api_client)
    
    # BATCH ENHANCEMENT (new)
    faq_items = voice_processor.enhance_batch(
        faq_items=faq_items,
        author=author,
        marker_distribution='varied'
    )
    
    faq_content = yaml.dump(faq_items, ...)
```

#### Phase 3: Add Distribution Validation (30 min)
```python
# validation/quality_validator.py
def _check_marker_distribution(self, faq_items, author):
    """Validate markers are distributed, not clustered."""
    # Check no marker appears in >50% of answers
    # Return distribution report
```

#### Phase 4: Test & Iterate (1 hour)
- Test with Steel (Italy voice)
- Test with Aluminum (Taiwan voice)
- Verify markers distributed across answers
- Check repetition percentage drops to <50%

**Total Effort**: ~3 hours

---

## 📊 Expected Results

### Before (Current):
```
Steel FAQ (7 questions):
- "meticulous": 86% (6/7 answers)
- "precision": 57% (4/7 answers)
- "indeed": 43% (3/7 answers)

Aluminum FAQ (7 questions):
- "precise": 100% (7/7 answers) ❌
- "systematic": 86% (6/7 answers) ❌
```

### After (Batch Enhancement):
```
Steel FAQ (7 questions):
- "meticulous": 14% (1/7 answers) ✅
- "precision": 14% (1/7 answers) ✅
- "finesse": 14% (1/7 answers) ✅
- "artisan": 14% (1/7 answers) ✅
- "indeed": 14% (1/7 answers) ✅
- [2 answers with no markers] ✅

Aluminum FAQ (7 questions):
- "systematic": 14% (1/7 answers) ✅
- "precise": 14% (1/7 answers) ✅
- "detailed": 14% (1/7 answers) ✅
- "methodology": 14% (1/7 answers) ✅
- [3 answers with no markers] ✅
```

---

## 🚀 Alternative: Hybrid Approach

If batch enhancement proves too complex, combine Options 1 & 2:

1. **Try batch first** (Option 1)
2. **If fails**, fall back to tracked sequential (Option 2)
3. **Always validate** distribution at end

```python
try:
    # Try batch enhancement
    faq_items = voice_processor.enhance_batch(faq_items, author)
except Exception as e:
    logger.warning(f"Batch enhancement failed: {e}, using sequential with tracking")
    # Fall back to sequential with tracking
    faq_items = voice_processor.enhance_with_tracking(faq_items, author)

# Always validate
distribution = validator.check_marker_distribution(faq_items, author)
if not distribution['valid']:
    # Trigger retry
    return error
```

---

## 📝 Notes

- **Backward Compatibility**: Keep old `enhance()` method for non-FAQ use cases
- **Testing**: Need comprehensive tests for batch enhancement
- **Documentation**: Update voice system docs with new architecture
- **Monitoring**: Track repetition metrics before/after in validation logs

---

## ✅ Decision Required

**Approve Option 1 (Batch Enhancement)?**
- [ ] Yes - Implement batch enhancement (3 hours)
- [ ] No - Prefer Option 2 (Sequential Tracking)
- [ ] No - Prefer Option 3 (Post-Redistribution)
- [ ] Discuss - Need more information

---

**Next Steps After Approval**:
1. Implement `enhance_batch()` method
2. Update FAQ generator to use batch
3. Add distribution validation
4. Test with Steel/Aluminum
5. Regenerate all 3 test FAQs
6. Export to frontmatter
7. Verify <50% repetition rate
