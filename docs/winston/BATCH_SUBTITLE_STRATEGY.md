# Winston Batch Subtitle Detection Strategy

**Problem:** Winston API requires minimum 300 characters, but subtitles are typically 100-400 chars (20-80 words). Many individual subtitles are too short.

**Solution:** Batch multiple subtitles together for Winston analysis, then apply the composite score to all items in the batch.

---

## 📊 Batch Strategy Options

### **Option A: Concatenate with Delimiters** (RECOMMENDED)
Combine multiple subtitles into a single text block separated by clear delimiters.

```python
# Example batch
batch = [
    "Aluminum: Lightweight metal for aerospace",
    "Steel: High-strength alloy for construction", 
    "Copper: Excellent conductor for electronics"
]

# Concatenate with delimiters
combined = "\n\n===\n\n".join(batch)
# Total: ~180 chars → need 2 batches minimum

# Send to Winston API
result = winston_api.detect(combined)

# Apply composite score to all items
for subtitle in batch:
    subtitle.ai_score = result['ai_score']
```

**Advantages:**
- ✅ Simple implementation
- ✅ Winston sees full context
- ✅ One API call = 3-5 subtitles analyzed
- ✅ Cost-effective (1 API call vs 5)

**Disadvantages:**
- ❌ Can't identify which specific subtitle has AI patterns
- ❌ One bad subtitle affects whole batch score

---

### **Option B: Dynamic Batching with Size Optimization**
Intelligently group subtitles to maximize batch size while staying under token limits.

```python
def create_optimal_batches(subtitles: List[str], min_chars: int = 300, max_chars: int = 5000):
    """
    Create batches that meet Winston's minimum and stay under max.
    
    Args:
        subtitles: List of subtitle texts
        min_chars: Minimum chars per batch (300 for Winston)
        max_chars: Maximum chars per batch (avoid token limits)
    
    Returns:
        List of batches, each containing multiple subtitles
    """
    batches = []
    current_batch = []
    current_length = 0
    
    for subtitle in subtitles:
        subtitle_length = len(subtitle)
        delimiter_length = 7  # "\n\n===\n\n"
        
        # Would this exceed max?
        if current_length + subtitle_length + delimiter_length > max_chars:
            if current_batch:  # Save current batch
                batches.append(current_batch)
            current_batch = [subtitle]
            current_length = subtitle_length
        else:
            current_batch.append(subtitle)
            current_length += subtitle_length + delimiter_length
    
    # Save final batch
    if current_batch:
        batches.append(current_batch)
    
    return batches

# Usage
batches = create_optimal_batches(all_subtitles)
# Result: [[sub1, sub2, sub3], [sub4, sub5, sub6], ...]
# Each batch: 300-5000 chars
```

**Advantages:**
- ✅ Maximizes efficiency (5-10 subtitles per batch)
- ✅ Respects Winston limits
- ✅ Handles variable lengths gracefully

**Disadvantages:**
- ❌ More complex implementation
- ❌ Still can't identify individual problematic subtitles

---

### **Option C: Hybrid Approach with Fallback**
Use batching by default, but re-test individually if batch fails.

```python
def analyze_subtitle_batch_with_fallback(
    subtitles: List[str],
    winston_api,
    threshold: float = 0.3
):
    """
    Batch analyze subtitles, re-test individually if batch fails.
    
    Flow:
    1. Combine subtitles into batch
    2. Run Winston on batch
    3. If batch passes → mark all as passed
    4. If batch fails → re-test each subtitle individually (if length allows)
    """
    # Step 1: Create batch
    combined = "\n\n===\n\n".join(subtitles)
    
    # Step 2: Batch analysis
    batch_result = winston_api.detect(combined)
    
    # Step 3: If batch passes, all pass
    if batch_result['ai_score'] <= threshold:
        return [{'subtitle': s, 'ai_score': batch_result['ai_score'], 'method': 'batch_passed'} 
                for s in subtitles]
    
    # Step 4: Batch failed - re-test individually (if long enough)
    results = []
    for subtitle in subtitles:
        if len(subtitle) >= 300:
            # Individual analysis
            individual_result = winston_api.detect(subtitle)
            results.append({
                'subtitle': subtitle,
                'ai_score': individual_result['ai_score'],
                'method': 'individual'
            })
        else:
            # Too short - use pattern-based detection
            pattern_score = pattern_detector.detect(subtitle)['ai_score']
            results.append({
                'subtitle': subtitle,
                'ai_score': pattern_score,
                'method': 'pattern_fallback'
            })
    
    return results
```

**Advantages:**
- ✅ Best of both worlds: efficient + granular
- ✅ Identifies specific problematic subtitles
- ✅ Graceful fallback for short text

**Disadvantages:**
- ❌ Most complex implementation
- ❌ Could use more credits (batch + individuals)

---

## 🎯 Recommended Implementation

**Use Option B: Dynamic Batching with Size Optimization**

### Implementation Plan

1. **Add to orchestrator.py:**
```python
def analyze_subtitle_batch(
    self,
    subtitles: List[Dict],  # [{'material': 'Aluminum', 'text': '...'}, ...]
    component_type: str = 'subtitle'
) -> List[Dict]:
    """
    Analyze multiple subtitles in optimized batches.
    
    Returns:
        List of results with ai_score for each subtitle
    """
    # Create optimal batches
    batches = self._create_optimal_batches([s['text'] for s in subtitles])
    
    results = []
    for batch in batches:
        # Combine with delimiters
        combined = "\n\n===\n\n".join(batch)
        
        # Winston detection
        detection = self.detector.detect(combined)
        
        # Log to database (batch)
        if self.feedback_db:
            self.feedback_db.log_detection(
                material=f"BATCH_{len(batch)}_subtitles",
                component_type=component_type,
                generated_text=combined,
                winston_result=detection,
                success=(detection['ai_score'] <= self.ai_threshold)
            )
        
        # Apply score to all subtitles in batch
        for subtitle_text in batch:
            results.append({
                'text': subtitle_text,
                'ai_score': detection['ai_score'],
                'method': 'batch_winston',
                'batch_size': len(batch)
            })
    
    return results
```

2. **Add CLI command:**
```bash
# Analyze all subtitles in batch mode
python3 run.py --validate-ai-detection --winston-component subtitle --batch-mode

# Analyze specific materials in batch
python3 run.py --validate-ai-detection --winston-component subtitle --batch-mode --materials "Aluminum,Steel,Copper"
```

3. **Update winston_audit.py script:**
```python
# Add batch mode support
if args.batch_mode:
    # Group by component type
    subtitle_texts = [item['text'] for item in subtitle_items]
    
    # Use orchestrator batch method
    results = orchestrator.analyze_subtitle_batch(subtitle_items)
else:
    # Individual analysis (existing code)
    ...
```

---

## 📊 Cost Analysis

### Individual Analysis (Current)
- 132 materials × 1 subtitle each = 132 API calls
- Average subtitle: 40 words = ~200 chars
- ~50 subtitles too short → skipped
- ~82 subtitles analyzed individually
- **Total credits: ~1,640** (82 subtitles × 20 words avg)

### Batch Analysis (Proposed)
- 132 subtitles grouped into batches
- Batch size: 5 subtitles per batch (avg 1000 chars total)
- Number of batches: 132 ÷ 5 = ~27 batches
- **Total credits: ~5,400** (27 batches × 200 words avg)

**⚠️ IMPORTANT:** Batching uses MORE credits but provides more comprehensive analysis of short content.

### Hybrid Approach
- Batch analysis first: 27 batches = ~5,400 credits
- If batch passes: done
- If batch fails: re-test individually (only failures)
- Estimated additional: ~1,000 credits
- **Total credits: ~6,400 maximum**

---

## 🎛️ Configuration

Add to `processing/config.yaml`:

```yaml
# Winston Batch Analysis
winston_batch_mode: true              # Enable batch analysis for subtitles
winston_batch_min_chars: 300          # Minimum chars per batch
winston_batch_max_chars: 5000         # Maximum chars per batch
winston_batch_delimiter: "\n\n===\n\n"  # Delimiter between items
winston_batch_fallback: true          # Re-test individually if batch fails
```

---

## 🧪 Testing Strategy

1. **Test batch creation:**
   - Verify batches meet 300 char minimum
   - Verify batches stay under 5000 char maximum
   - Test with varying subtitle lengths

2. **Test Winston API:**
   - Send sample batch to Winston
   - Verify response format unchanged
   - Check credit usage matches expectations

3. **Test database logging:**
   - Verify batch results logged correctly
   - Check material names use "BATCH_N_subtitles" format
   - Ensure individual subtitle mapping preserved

4. **Test fallback logic:**
   - Force batch failure (inject AI phrases)
   - Verify individual re-testing triggers
   - Check pattern fallback for short text

---

## ✅ Recommendation

**Implement Option B (Dynamic Batching)** as the default for subtitles, with these characteristics:

- ✅ **Efficient:** 5-10 subtitles per batch
- ✅ **Cost-effective:** Fewer API calls than individual
- ✅ **Comprehensive:** Analyzes all content (nothing skipped)
- ✅ **Simple:** Single composite score per batch
- ✅ **Database-friendly:** Logs batch results with material mapping

**Add Option C (Hybrid Fallback)** as an optional flag (`--batch-with-fallback`) for maximum granularity when needed.
