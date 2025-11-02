# Voice Validation Strategy for Materials Frontmatter

**Purpose**: Validate existing frontmatter text fields for voice accuracy and determine whether re-processing is needed, avoiding over-adjustment.

**Date**: November 1, 2025  
**Context**: 132 materials, 3 with `voice_applied: true`, evidence of Indonesian translation issues

---

## 🔍 Current State Assessment

### Voice Application Status
- **Total Materials**: 132
- **Voice Applied**: 3 (aluminum, bronze, steel)
- **No Voice Metadata**: 129 materials
- **Critical Issue**: Indonesian FAQ answers translated to Indonesian instead of English

### Evidence of Translation Issues

**Found in frontmatter/materials/**:
- `gold-laser-cleaning.yaml`: Indonesian FAQ answer
- `platinum-laser-cleaning.yaml`: Indonesian FAQ answer  
- `copper-laser-cleaning.yaml`: Indonesian FAQ answer
- `cast-iron-laser-cleaning.yaml`: Indonesian FAQ answer
- `quartz-glass-laser-cleaning.yaml`: Indonesian FAQ answer

**Translation Artifacts**:
- Reduplication patterns: "very-very", "clean-clean", "high-high", "ready-ready", "cling-cling"
- These appear to be Indonesian reduplication patterns translated literally to English
- Not authentic voice markers - translation errors

---

## 🎯 Validation Requirements

### 1. Language Detection (CRITICAL)
**Requirement**: Detect if text is in wrong language before attempting voice processing

**Implementation**:
```python
def detect_language(text: str) -> str:
    """
    Detect language of text content.
    
    Returns:
        'english', 'indonesian', 'italian', 'chinese', 'unknown'
    """
    # Common Indonesian words
    indonesian_markers = [
        'yang', 'dengan', 'untuk', 'dari', 'ini', 'dapat', 'sangat', 
        'pada', 'adalah', 'atau', 'akan', 'juga', 'dalam', 'tidak',
        'memiliki', 'memerlukan', 'menggunakan', 'sebagai', 'karena'
    ]
    
    # Common Italian words
    italian_markers = [
        'che', 'con', 'per', 'della', 'questo', 'molto', 'alla',
        'essere', 'anche', 'più', 'quando', 'come', 'quindi'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    
    # Count markers
    indonesian_count = sum(1 for marker in indonesian_markers if marker in words)
    italian_count = sum(1 for marker in italian_markers if marker in words)
    
    # Decision logic
    if indonesian_count >= 3:
        return 'indonesian'
    elif italian_count >= 3:
        return 'italian'
    elif any(ord(c) > 127 for c in text):  # Non-ASCII chars
        return 'unknown'
    
    return 'english'
```

### 2. Voice Authenticity Scoring (HIGH PRIORITY)
**Requirement**: Distinguish genuine voice markers from translation artifacts

**Problematic Patterns** (Translation Artifacts):
- Reduplication: "very-very", "clean-clean", "high-high", "ready-ready"
- Literal translations: "cling-cling", "etched-etched"
- Broken grammar: "Surface is cleaned by laser method, so quality is high"
- Repetitive conjunctions: overuse of "then", "so"

**Authentic Voice Markers**:
- Taiwan: "Subsequently", "It is noteworthy that", systematic analysis
- Italy: "elegantly", "sophisticated", "refined", technical elegance
- Indonesia: "straightforward", "practical", "accessible" (in English!)
- USA: "pretty", "fairly", "typically", conversational expertise

**Scoring Algorithm**:
```python
def score_voice_authenticity(
    text: str, 
    author_country: str,
    voice_indicators: List[str]
) -> Dict[str, Any]:
    """
    Score voice authenticity - distinguish real markers from artifacts.
    
    Returns:
        {
            'authenticity_score': float (0-100),
            'is_authentic': bool,
            'found_markers': List[str],
            'translation_artifacts': List[str],
            'recommendation': str  # 'keep', 'reprocess', 'translate'
        }
    """
    text_lower = text.lower()
    
    # Check for translation artifacts
    artifacts = []
    artifact_patterns = [
        r'\b(\w+)-\1\b',  # Reduplication: very-very, clean-clean
        r'\bthen\b.*\bthen\b',  # Repeated "then"
        r'\bso\b.*\bso\b.*\bso\b',  # Excessive "so"
    ]
    
    for pattern in artifact_patterns:
        if re.search(pattern, text_lower):
            artifacts.append(pattern)
    
    # Check for genuine voice markers
    found_markers = [m for m in voice_indicators if m in text_lower]
    
    # Calculate authenticity score
    authenticity_score = 100.0
    
    # Penalize translation artifacts heavily
    authenticity_score -= len(artifacts) * 25
    
    # Penalize excessive marker repetition
    marker_counts = {m: text_lower.count(m) for m in found_markers}
    excessive = [m for m, count in marker_counts.items() if count > 2]
    authenticity_score -= len(excessive) * 15
    
    # Reward natural marker distribution
    if len(found_markers) >= 2 and len(found_markers) <= 4:
        authenticity_score += 10
    
    # Ensure score stays in range
    authenticity_score = max(0.0, min(100.0, authenticity_score))
    
    # Determine recommendation
    if authenticity_score >= 70:
        recommendation = 'keep'
    elif authenticity_score >= 40:
        recommendation = 'reprocess'
    else:
        recommendation = 'translate'  # Likely wrong language
    
    return {
        'authenticity_score': authenticity_score,
        'is_authentic': authenticity_score >= 70,
        'found_markers': found_markers,
        'translation_artifacts': artifacts,
        'recommendation': recommendation
    }
```

### 3. Pre-Enhancement Validation (MANDATORY)
**Requirement**: Check text quality BEFORE deciding to enhance

**Validation Checklist**:
```python
def should_enhance_voice(
    text: str,
    author: Dict[str, str],
    voice_indicators: List[str]
) -> Dict[str, Any]:
    """
    Determine if text should be voice-enhanced.
    
    Returns decision with rationale.
    """
    # Step 1: Language detection
    language = detect_language(text)
    if language != 'english':
        return {
            'should_enhance': False,
            'reason': f'Text is in {language}, needs translation first',
            'action_required': 'translate_to_english'
        }
    
    # Step 2: Voice authenticity scoring
    authenticity = score_voice_authenticity(text, author['country'], voice_indicators)
    
    if authenticity['is_authentic']:
        return {
            'should_enhance': False,
            'reason': f"Voice already authentic (score: {authenticity['authenticity_score']:.1f})",
            'action_required': 'none'
        }
    
    if authenticity['authenticity_score'] < 40:
        return {
            'should_enhance': True,
            'reason': f"Low authenticity (score: {authenticity['authenticity_score']:.1f}), likely translation artifacts",
            'action_required': 'full_reprocess'
        }
    
    # Step 3: Marker count check (existing logic)
    text_lower = text.lower()
    found_markers = [m for m in voice_indicators if m in text_lower]
    
    if len(found_markers) >= 2:
        return {
            'should_enhance': False,
            'reason': f"Already has {len(found_markers)} voice markers",
            'action_required': 'none'
        }
    
    # Default: enhance needed
    return {
        'should_enhance': True,
        'reason': 'Insufficient voice markers',
        'action_required': 'enhance'
    }
```

---

## 📋 Validation Workflow for Materials Frontmatter

### Phase 1: Audit Current State
```bash
# Step 1: Detect non-English content
python3 scripts/validation/detect_translation_issues.py --all-materials

# Expected output:
# ❌ gold-laser-cleaning.yaml: FAQ answer in Indonesian
# ❌ platinum-laser-cleaning.yaml: FAQ answer in Indonesian
# ⚠️  calcite-laser-cleaning.yaml: Translation artifacts (very-very)
# ✅ aluminum-laser-cleaning.yaml: Authentic voice markers
```

### Phase 2: Score Voice Authenticity
```bash
# Step 2: Score all text fields
python3 scripts/validation/score_voice_authenticity.py --material Calcite

# Expected output:
# Caption beforeText: 45/100 (translation artifacts: reduplication)
# Caption afterText: 50/100 (translation artifacts: reduplication)
# FAQ Q1: 75/100 (authentic voice markers detected)
# Subtitle: 85/100 (authentic, no reprocessing needed)
```

### Phase 3: Generate Reprocessing Plan
```bash
# Step 3: Identify materials needing reprocessing
python3 scripts/validation/generate_voice_reprocessing_plan.py

# Expected output:
# CRITICAL (translate): 5 materials (Indonesian FAQ answers)
# HIGH (reprocess): 23 materials (translation artifacts)
# MEDIUM (enhance): 87 materials (no voice markers)
# GOOD (keep): 17 materials (authentic voice)
```

### Phase 4: Selective Reprocessing
```bash
# Step 4: Reprocess only materials that need it
python3 run.py --voice-reprocess --priority critical  # Translate 5 materials
python3 run.py --voice-reprocess --priority high      # Reprocess 23 materials
python3 run.py --voice-reprocess --priority medium    # Enhance 87 materials
```

---

## 🔧 Implementation Plan

### 1. Enhance `VoicePostProcessor` (shared/voice/post_processor.py)

**Add Methods**:
```python
class VoicePostProcessor:
    
    def validate_before_enhancement(
        self,
        text: str,
        author: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Validate text before attempting enhancement.
        
        Returns decision dict with should_enhance, reason, action_required
        """
        # Implementation from above
    
    def detect_translation_artifacts(self, text: str) -> List[str]:
        """Detect problematic translation patterns"""
        # Implementation from above
    
    def score_authenticity(
        self,
        text: str,
        author: Dict[str, str]
    ) -> Dict[str, Any]:
        """Score voice marker authenticity (0-100)"""
        # Implementation from above
```

**Update `enhance()` Method**:
```python
def enhance(self, text: str, author: Dict[str, str], **kwargs) -> str:
    """Enhanced with pre-validation"""
    
    # NEW: Pre-enhancement validation
    validation = self.validate_before_enhancement(text, author)
    
    if not validation['should_enhance']:
        logger.info(f"✅ Skipping enhancement: {validation['reason']}")
        return text
    
    if validation['action_required'] == 'translate_to_english':
        logger.error(f"❌ Text is in wrong language - translation required")
        return text  # Don't enhance wrong language
    
    # Existing enhancement logic...
```

### 2. Create Validation Scripts

**Script 1**: `scripts/validation/detect_translation_issues.py`
- Scan all materials frontmatter
- Detect non-English text
- Report Indonesian/Italian/Chinese content
- Generate critical reprocessing list

**Script 2**: `scripts/validation/score_voice_authenticity.py`
- Score all text fields (0-100)
- Detect translation artifacts
- Compare against voice indicators
- Generate authenticity report

**Script 3**: `scripts/validation/generate_voice_reprocessing_plan.py`
- Analyze all 132 materials
- Prioritize by severity:
  - CRITICAL: Wrong language
  - HIGH: Translation artifacts
  - MEDIUM: No voice markers
  - GOOD: Authentic voice
- Generate selective reprocessing plan

### 3. Update BaseFrontmatterGenerator

**Add Validation Step**:
```python
def _apply_author_voice(
    self,
    frontmatter_data: Dict[str, Any],
    author_data: Dict[str, str],
    context: GenerationContext
) -> Dict[str, Any]:
    """Apply voice with pre-validation"""
    
    # Initialize processor
    processor = VoicePostProcessor(self.api_client)
    
    # Recursive field processing with validation
    def process_field(value):
        if isinstance(value, str) and len(value) > 50:
            # NEW: Validate before enhancement
            validation = processor.validate_before_enhancement(value, author_data)
            
            if validation['action_required'] == 'translate_to_english':
                logger.error(f"❌ Field in wrong language, skipping")
                return value
            
            if not validation['should_enhance']:
                logger.info(f"✅ {validation['reason']}")
                return value
            
            # Enhance only if needed
            return processor.enhance(value, author_data, **voice_params)
        # ... rest of recursion logic
```

---

## 📊 Expected Outcomes

### Validation Report Format
```
Voice Validation Report - Materials Frontmatter
================================================

Total Materials: 132
Voice Applied Metadata: 3

Language Issues:
  ❌ Indonesian Text: 5 materials (gold, platinum, copper, cast-iron, quartz-glass)
  ✅ English Text: 127 materials

Voice Authenticity:
  ✅ Authentic (70-100): 17 materials (keep as-is)
  ⚠️  Moderate (40-69): 23 materials (reprocess recommended)
  ❌ Poor (0-39): 87 materials (enhancement needed)
  ❌ Translation Artifacts: 5 materials (critical reprocessing)

Translation Artifacts Detected:
  - Reduplication patterns: 23 occurrences (very-very, clean-clean)
  - Excessive conjunctions: 12 occurrences (then...then...then)
  - Broken grammar: 8 occurrences

Recommendation:
  1. CRITICAL (5 materials): Translate Indonesian FAQ answers to English
  2. HIGH (23 materials): Reprocess to remove translation artifacts
  3. MEDIUM (87 materials): Enhance with authentic voice markers
  4. GOOD (17 materials): No action needed

Estimated Cost:
  - Translation: ~$0.50 (5 materials × ~$0.10)
  - Reprocessing: ~$2.30 (23 materials × ~$0.10)
  - Enhancement: ~$8.70 (87 materials × ~$0.10)
  - Total: ~$11.50
```

---

## ✅ Success Criteria

1. **No Non-English Content**: All text fields in English only
2. **No Translation Artifacts**: Zero reduplication patterns, broken grammar
3. **Authentic Voice Markers**: 2-4 genuine markers per text field
4. **Selective Enhancement**: Only enhance materials that need it (avoid over-adjustment)
5. **Validation Metadata**: Track authenticity scores in frontmatter

---

## 🚦 Implementation Priority

### Phase 1 (CRITICAL - This Week)
- ✅ Create `detect_translation_issues.py` script
- ✅ Scan all 132 materials for Indonesian/Italian text
- ✅ Generate critical reprocessing list (5 materials)
- ✅ Translate FAQ answers to English

### Phase 2 (HIGH - Next Week)
- ✅ Implement `score_voice_authenticity.py` script
- ✅ Score all text fields for authenticity
- ✅ Detect translation artifacts (reduplication patterns)
- ✅ Generate reprocessing plan

### Phase 3 (MEDIUM - Week 3)
- ✅ Enhance `VoicePostProcessor` with validation
- ✅ Add `validate_before_enhancement()` method
- ✅ Update `BaseFrontmatterGenerator._apply_author_voice()`
- ✅ Add authenticity scoring to voice metadata

### Phase 4 (LOW - Week 4)
- ✅ Selective reprocessing of 110 materials
- ✅ Validation report generation
- ✅ Final quality audit

---

## 📝 Documentation Updates Required

1. **VoicePostProcessor Documentation** - Add validation methods
2. **Voice System README** - Document authenticity scoring
3. **Materials Validation Guide** - Add voice validation section
4. **API Reference** - Document new validation methods

---

**Status**: ⏳ PENDING IMPLEMENTATION  
**Next Action**: Create validation scripts and enhance VoicePostProcessor
