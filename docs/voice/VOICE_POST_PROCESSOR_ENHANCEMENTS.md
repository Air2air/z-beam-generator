# VoicePostProcessor Enhancement Proposal

**Purpose**: Add comprehensive validation to prevent over-adjustment and detect translation issues  
**Date**: November 1, 2025  
**Context**: Found Indonesian translations and "very-very" artifacts in materials frontmatter

---

## 🚨 Current Gaps in VoicePostProcessor

### 1. **Insufficient Re-Enhancement Check** (Line 73-78)
```python
# Current logic - TOO SIMPLE
found_markers = [ind for ind in voice_indicators if ind in text_lower]

if len(found_markers) >= min_markers:
    logger.info(f"✅ Text already has {len(found_markers)} voice markers - skipping enhancement")
    return text
```

**Problems**:
- ❌ Only counts markers, doesn't validate authenticity
- ❌ Can't detect translation artifacts ("very-very", "clean-clean")
- ❌ Doesn't check if markers are genuine or coincidental
- ❌ No language detection - might skip Indonesian text with English words

### 2. **No Language Detection**
- ❌ Doesn't check if text is in Indonesian, Italian, Chinese
- ❌ Can't detect if voice processing already translated to wrong language
- ❌ Risk: Might enhance non-English text, making it worse

### 3. **No Authenticity Scoring**
- ❌ `get_voice_score()` exists but only counts markers (lines 163-219)
- ❌ Doesn't distinguish genuine markers from translation artifacts
- ❌ No quality assessment of voice application

### 4. **No Translation Artifact Detection**
- ❌ Can't detect reduplication patterns ("very-very", "high-high")
- ❌ Can't detect broken grammar from literal translations
- ❌ Can't detect excessive conjunction usage ("then...then...then")

---

## ✅ Required Enhancements

### Enhancement 1: Add Language Detection

**Purpose**: Prevent voice enhancement on non-English text

**Implementation**:
```python
def detect_language(self, text: str) -> Dict[str, Any]:
    """
    Detect if text is in English or another language.
    
    Args:
        text: Text content to analyze
        
    Returns:
        {
            'language': str,  # 'english', 'indonesian', 'italian', 'chinese', 'unknown'
            'confidence': float,  # 0-1
            'indicators': List[str]  # Words that triggered detection
        }
    """
    # Common Indonesian words (high-frequency function words)
    indonesian_indicators = {
        'yang', 'dengan', 'untuk', 'dari', 'ini', 'dapat', 'sangat',
        'pada', 'adalah', 'atau', 'akan', 'juga', 'dalam', 'tidak',
        'memiliki', 'memerlukan', 'menggunakan', 'sebagai', 'karena',
        'ya', 'sekitar', 'proses', 'aplikasi', 'lapisan'
    }
    
    # Common Italian words
    italian_indicators = {
        'che', 'con', 'per', 'della', 'questo', 'molto', 'alla',
        'essere', 'anche', 'più', 'quando', 'come', 'quindi',
        'infatti', 'pertanto', 'mediante', 'verso'
    }
    
    text_lower = text.lower()
    words = set(text_lower.split())
    
    # Count language-specific words
    indonesian_count = len(words & indonesian_indicators)
    italian_count = len(words & italian_indicators)
    
    # Determine language
    if indonesian_count >= 3:
        return {
            'language': 'indonesian',
            'confidence': min(indonesian_count / 10.0, 1.0),
            'indicators': list(words & indonesian_indicators)
        }
    elif italian_count >= 3:
        return {
            'language': 'italian',
            'confidence': min(italian_count / 10.0, 1.0),
            'indicators': list(words & italian_indicators)
        }
    elif any(ord(c) > 127 and ord(c) < 256 for c in text):
        # Non-ASCII Latin characters (accented chars)
        return {
            'language': 'unknown',
            'confidence': 0.5,
            'indicators': ['non-ascii-chars']
        }
    
    # Default to English
    return {
        'language': 'english',
        'confidence': 0.8,
        'indicators': []
    }
```

### Enhancement 2: Detect Translation Artifacts

**Purpose**: Identify problematic patterns from literal translations

**Implementation**:
```python
def detect_translation_artifacts(self, text: str) -> Dict[str, Any]:
    """
    Detect translation artifacts that indicate poor voice application.
    
    Problematic patterns:
    - Reduplication: "very-very", "clean-clean", "high-high"
    - Excessive conjunctions: "then...then...then", "so...so...so"
    - Broken grammar: "Surface is cleaned by laser method, so quality is high"
    
    Args:
        text: Text to analyze
        
    Returns:
        {
            'has_artifacts': bool,
            'artifact_count': int,
            'patterns_found': List[Dict],  # [{type, example, count}]
            'severity': str  # 'none', 'minor', 'moderate', 'severe'
        }
    """
    import re
    
    artifacts = []
    
    # 1. Detect reduplication patterns (Indonesian-style)
    reduplication = re.findall(r'\b(\w+)-\1\b', text.lower())
    if reduplication:
        artifacts.append({
            'type': 'reduplication',
            'examples': list(set(reduplication)),
            'count': len(reduplication)
        })
    
    # 2. Detect excessive "then" usage
    then_count = len(re.findall(r'\bthen\b', text.lower()))
    sentence_count = len(re.findall(r'[.!?]', text)) or 1
    if then_count / sentence_count > 0.5:  # More than 50% of sentences
        artifacts.append({
            'type': 'excessive_then',
            'examples': [f"{then_count} uses in {sentence_count} sentences"],
            'count': then_count
        })
    
    # 3. Detect excessive "so" usage
    so_count = len(re.findall(r'\bso\b', text.lower()))
    if so_count / sentence_count > 0.5:
        artifacts.append({
            'type': 'excessive_so',
            'examples': [f"{so_count} uses in {sentence_count} sentences"],
            'count': so_count
        })
    
    # 4. Detect repetitive sentence starters
    sentences = re.split(r'[.!?]+', text)
    starters = [s.strip().split()[0].lower() for s in sentences if s.strip()]
    starter_counts = {}
    for starter in starters:
        starter_counts[starter] = starter_counts.get(starter, 0) + 1
    
    repetitive_starters = [
        starter for starter, count in starter_counts.items()
        if count >= 3 and len(starters) > 3
    ]
    
    if repetitive_starters:
        artifacts.append({
            'type': 'repetitive_starters',
            'examples': repetitive_starters,
            'count': len(repetitive_starters)
        })
    
    # Calculate severity
    total_artifacts = sum(a['count'] for a in artifacts)
    if total_artifacts == 0:
        severity = 'none'
    elif total_artifacts <= 2:
        severity = 'minor'
    elif total_artifacts <= 5:
        severity = 'moderate'
    else:
        severity = 'severe'
    
    return {
        'has_artifacts': len(artifacts) > 0,
        'artifact_count': total_artifacts,
        'patterns_found': artifacts,
        'severity': severity
    }
```

### Enhancement 3: Score Voice Authenticity

**Purpose**: Distinguish genuine voice markers from coincidental or artificial patterns

**Implementation**:
```python
def score_voice_authenticity(
    self,
    text: str,
    author: Dict[str, str],
    voice_indicators: List[str]
) -> Dict[str, Any]:
    """
    Score how authentic the voice markers are (0-100).
    
    Factors:
    - Genuine markers present (positive)
    - Translation artifacts (heavy negative)
    - Marker repetition (negative)
    - Natural distribution (positive)
    - Wrong language (critical negative)
    
    Args:
        text: Text to analyze
        author: Author dict with 'country' key
        voice_indicators: List of expected voice markers for this country
        
    Returns:
        {
            'authenticity_score': float (0-100),
            'is_authentic': bool,  # True if score >= 70
            'found_markers': List[str],
            'marker_quality': str,  # 'excellent', 'good', 'fair', 'poor'
            'issues': List[str],
            'recommendation': str  # 'keep', 'reprocess', 'translate'
        }
    """
    text_lower = text.lower()
    
    # Start at 100 and deduct for issues
    score = 100.0
    issues = []
    
    # 1. Check language (CRITICAL)
    language = self.detect_language(text)
    if language['language'] != 'english':
        score = 0.0
        issues.append(f"Text is in {language['language']}, not English")
        return {
            'authenticity_score': 0.0,
            'is_authentic': False,
            'found_markers': [],
            'marker_quality': 'poor',
            'issues': issues,
            'recommendation': 'translate'
        }
    
    # 2. Check for translation artifacts (HEAVY PENALTY)
    artifacts = self.detect_translation_artifacts(text)
    if artifacts['has_artifacts']:
        penalty = artifacts['artifact_count'] * 15
        score -= penalty
        issues.append(
            f"Translation artifacts detected ({artifacts['severity']}): "
            f"{', '.join([a['type'] for a in artifacts['patterns_found']])}"
        )
    
    # 3. Count genuine voice markers
    found_markers = [m for m in voice_indicators if m in text_lower]
    
    if len(found_markers) == 0:
        score -= 30
        issues.append("No voice markers found")
    elif len(found_markers) == 1:
        score -= 15
        issues.append("Only 1 voice marker (need 2+)")
    elif len(found_markers) >= 2 and len(found_markers) <= 4:
        # Good range - add bonus
        score += 10
    elif len(found_markers) > 6:
        # Too many markers - seems forced
        score -= 10
        issues.append(f"Excessive markers ({len(found_markers)})")
    
    # 4. Check for marker repetition
    marker_counts = {m: text_lower.count(m) for m in found_markers}
    repeated = [m for m, count in marker_counts.items() if count > 2]
    if repeated:
        score -= len(repeated) * 10
        issues.append(f"Repeated markers: {', '.join(repeated)}")
    
    # 5. Check marker distribution (are they clustered or spread?)
    if found_markers and len(text) > 200:
        # Check if markers are evenly distributed
        positions = []
        for marker in found_markers:
            pos = text_lower.find(marker)
            if pos != -1:
                positions.append(pos / len(text))  # Normalize to 0-1
        
        if positions:
            # Check variance - low variance = clustered (bad)
            import statistics
            if len(positions) > 1:
                variance = statistics.variance(positions)
                if variance < 0.1:  # Markers clustered in one area
                    score -= 10
                    issues.append("Markers clustered (not naturally distributed)")
    
    # Ensure score stays in range
    score = max(0.0, min(100.0, score))
    
    # Determine quality
    if score >= 85:
        quality = 'excellent'
    elif score >= 70:
        quality = 'good'
    elif score >= 50:
        quality = 'fair'
    else:
        quality = 'poor'
    
    # Determine recommendation
    if score >= 70:
        recommendation = 'keep'
    elif score >= 40:
        recommendation = 'reprocess'
    else:
        recommendation = 'translate'
    
    return {
        'authenticity_score': score,
        'is_authentic': score >= 70,
        'found_markers': found_markers,
        'marker_quality': quality,
        'issues': issues,
        'recommendation': recommendation
    }
```

### Enhancement 4: Comprehensive Pre-Enhancement Validation

**Purpose**: Decide whether to enhance text based on quality assessment

**Implementation**:
```python
def validate_before_enhancement(
    self,
    text: str,
    author: Dict[str, str]
) -> Dict[str, Any]:
    """
    Comprehensive validation before attempting enhancement.
    
    This is the main decision point for whether to enhance text.
    
    Args:
        text: Text to validate
        author: Author dict with 'name' and 'country'
        
    Returns:
        {
            'should_enhance': bool,
            'reason': str,
            'action_required': str,  # 'none', 'enhance', 'reprocess', 'translate'
            'details': Dict  # Full analysis results
        }
    """
    # Validate inputs
    if not text or not text.strip():
        return {
            'should_enhance': False,
            'reason': 'Empty text',
            'action_required': 'none',
            'details': {}
        }
    
    if not author or 'country' not in author:
        return {
            'should_enhance': False,
            'reason': 'Invalid author data',
            'action_required': 'none',
            'details': {}
        }
    
    # Get voice indicators
    try:
        voice = VoiceOrchestrator(country=author['country'])
        all_indicators = voice.get_voice_indicators_all_countries()
        country_key = voice.country.upper()
        voice_indicators = all_indicators.get(country_key, [])
    except Exception as e:
        logger.error(f"Failed to load voice indicators: {e}")
        return {
            'should_enhance': False,
            'reason': f'Voice system error: {e}',
            'action_required': 'none',
            'details': {}
        }
    
    # Run comprehensive analysis
    language = self.detect_language(text)
    artifacts = self.detect_translation_artifacts(text)
    authenticity = self.score_voice_authenticity(text, author, voice_indicators)
    
    details = {
        'language': language,
        'artifacts': artifacts,
        'authenticity': authenticity
    }
    
    # Decision logic
    
    # CRITICAL: Wrong language
    if language['language'] != 'english':
        return {
            'should_enhance': False,
            'reason': f"Text is in {language['language']}, needs translation to English",
            'action_required': 'translate',
            'details': details
        }
    
    # HIGH: Severe translation artifacts
    if artifacts['severity'] in ['severe', 'moderate']:
        return {
            'should_enhance': True,
            'reason': f"Translation artifacts detected ({artifacts['severity']}), reprocessing needed",
            'action_required': 'reprocess',
            'details': details
        }
    
    # GOOD: Already authentic
    if authenticity['is_authentic']:
        return {
            'should_enhance': False,
            'reason': f"Voice already authentic (score: {authenticity['authenticity_score']:.1f}/100)",
            'action_required': 'none',
            'details': details
        }
    
    # MEDIUM: Low authenticity score
    if authenticity['authenticity_score'] < 40:
        return {
            'should_enhance': True,
            'reason': f"Low authenticity score ({authenticity['authenticity_score']:.1f}/100)",
            'action_required': 'reprocess',
            'details': details
        }
    
    # DEFAULT: Enhancement needed
    return {
        'should_enhance': True,
        'reason': f"Moderate authenticity ({authenticity['authenticity_score']:.1f}/100), enhancement recommended",
        'action_required': 'enhance',
        'details': details
    }
```

### Enhancement 5: Update `enhance()` Method

**Purpose**: Integrate validation into existing enhancement workflow

**Changes to Existing Code**:
```python
def enhance(
    self,
    text: str,
    author: Dict[str, str],
    min_markers: int = 2,
    max_markers: int = 3,
    preserve_length: bool = True,
    length_tolerance: int = 5,
    voice_intensity: int = 3
) -> str:
    """
    Enhance text with author's voice markers.
    
    NOW INCLUDES: Pre-enhancement validation
    """
    # Validate inputs
    if not text or not text.strip():
        logger.warning("Empty text provided - returning unchanged")
        return text
        
    if not author or 'country' not in author:
        logger.warning("Invalid author object - returning text unchanged")
        return text
    
    # 🆕 NEW: Comprehensive pre-enhancement validation
    validation = self.validate_before_enhancement(text, author)
    
    if not validation['should_enhance']:
        logger.info(f"✅ Skipping enhancement: {validation['reason']}")
        return text
    
    if validation['action_required'] == 'translate':
        logger.error(
            f"❌ CRITICAL: Text is in {validation['details']['language']['language']}, "
            f"not English. Translation required before voice enhancement."
        )
        return text
    
    if validation['action_required'] == 'reprocess':
        logger.warning(
            f"⚠️  Text has quality issues: {validation['reason']}. "
            f"Full reprocessing recommended."
        )
        # Continue with enhancement but log the issues
    
    # Log validation details
    if 'details' in validation and 'authenticity' in validation['details']:
        auth = validation['details']['authenticity']
        logger.info(
            f"Voice authenticity: {auth['authenticity_score']:.1f}/100 "
            f"({auth['marker_quality']})"
        )
        if auth['issues']:
            logger.info(f"Issues: {'; '.join(auth['issues'])}")
    
    # ... rest of existing enhancement logic ...
    # (Initialize voice orchestrator, build prompt, make API call, etc.)
```

---

## 📊 Enhanced get_voice_score() Method

**Purpose**: Make existing method more comprehensive

**Current Implementation** (lines 163-219):
- Only counts markers
- Simple 0-100 scoring based on count
- No quality assessment

**Enhanced Implementation**:
```python
def get_voice_score(self, text: str, author: Dict[str, str]) -> Dict:
    """
    Analyze text for voice marker presence AND authenticity.
    
    Returns:
        Dictionary with comprehensive analysis:
        {
            'marker_count': int,
            'markers_found': [str],
            'country': str,
            'score': float (0-100),  # Simple marker count score
            'authenticity_score': float (0-100),  # NEW: Quality-adjusted score
            'authenticity': str,  # NEW: 'excellent', 'good', 'fair', 'poor'
            'language': str,  # NEW: Detected language
            'artifacts': Dict,  # NEW: Translation artifacts
            'recommendation': str  # NEW: 'keep', 'enhance', 'reprocess', 'translate'
        }
    """
    if not text or not author or 'country' not in author:
        return {
            'marker_count': 0,
            'markers_found': [],
            'country': 'Unknown',
            'score': 0.0,
            'authenticity_score': 0.0,
            'authenticity': 'poor',
            'language': 'unknown',
            'artifacts': {},
            'recommendation': 'none'
        }
    
    author_country = author.get('country', 'Unknown')
    
    try:
        voice = VoiceOrchestrator(country=author_country)
        all_indicators = voice.get_voice_indicators_all_countries()
        country_key = voice.country.upper()
        voice_indicators = all_indicators.get(country_key, [])
        
        text_lower = text.lower()
        found_markers = [ind for ind in voice_indicators if ind in text_lower]
        
        # Calculate simple marker count score (existing logic)
        marker_count = len(found_markers)
        if marker_count == 0:
            score = 0.0
        elif marker_count == 1:
            score = 50.0
        elif marker_count == 2:
            score = 75.0
        elif marker_count == 3:
            score = 85.0
        elif marker_count == 4:
            score = 95.0
        else:
            score = 100.0
        
        # 🆕 NEW: Run comprehensive authenticity analysis
        language = self.detect_language(text)
        artifacts = self.detect_translation_artifacts(text)
        authenticity_analysis = self.score_voice_authenticity(
            text, author, voice_indicators
        )
        
        return {
            # Existing fields
            'marker_count': marker_count,
            'markers_found': found_markers,
            'country': author_country,
            'score': score,
            # New fields
            'authenticity_score': authenticity_analysis['authenticity_score'],
            'authenticity': authenticity_analysis['marker_quality'],
            'language': language['language'],
            'artifacts': artifacts,
            'recommendation': authenticity_analysis['recommendation']
        }
        
    except Exception as e:
        logger.warning(f"Voice score analysis error: {e}")
        return {
            'marker_count': 0,
            'markers_found': [],
            'country': author_country,
            'score': 0.0,
            'authenticity_score': 0.0,
            'authenticity': 'poor',
            'language': 'unknown',
            'artifacts': {},
            'recommendation': 'none'
        }
```

---

## 🧪 Testing Strategy

### Test Case 1: Indonesian Translation
```python
def test_indonesian_detection():
    processor = VoicePostProcessor(api_client)
    
    # Actual text from gold-laser-cleaning.yaml
    indonesian_text = (
        "Ya, ablasi laser dapat secara selektif menghilangkan "
        "lapisan emas tanpa merusak substrat."
    )
    
    validation = processor.validate_before_enhancement(
        indonesian_text,
        {'name': 'Ikmanda Roswati', 'country': 'Indonesia'}
    )
    
    assert validation['action_required'] == 'translate'
    assert validation['details']['language']['language'] == 'indonesian'
    assert not validation['should_enhance']
```

### Test Case 2: Translation Artifacts
```python
def test_reduplication_detection():
    processor = VoicePostProcessor(api_client)
    
    # Text with reduplication artifacts
    artifact_text = (
        "Surface appears very-very smooth and clean-clean. "
        "Quality is high-high and restoration is good-good."
    )
    
    artifacts = processor.detect_translation_artifacts(artifact_text)
    
    assert artifacts['has_artifacts'] == True
    assert artifacts['severity'] in ['moderate', 'severe']
    assert any(a['type'] == 'reduplication' for a in artifacts['patterns_found'])
```

### Test Case 3: Authentic Voice
```python
def test_authentic_voice_skip():
    processor = VoicePostProcessor(api_client)
    
    # Text with authentic Taiwan voice markers
    authentic_text = (
        "Subsequently, the laser cleaning process demonstrates "
        "systematic removal of contaminants. It is noteworthy that "
        "the ablation threshold remains below 2.5 J/cm²."
    )
    
    validation = processor.validate_before_enhancement(
        authentic_text,
        {'name': 'Yi-Chun Lin', 'country': 'Taiwan'}
    )
    
    assert not validation['should_enhance']
    assert validation['action_required'] == 'none'
    assert validation['details']['authenticity']['is_authentic']
```

---

## 📋 Implementation Checklist

### Code Changes
- [ ] Add `detect_language()` method to VoicePostProcessor
- [ ] Add `detect_translation_artifacts()` method
- [ ] Add `score_voice_authenticity()` method
- [ ] Add `validate_before_enhancement()` method
- [ ] Update `enhance()` to use validation
- [ ] Enhance `get_voice_score()` with authenticity analysis
- [ ] Update `enhance_batch()` to use validation

### Testing
- [ ] Create `tests/test_voice_validation.py`
- [ ] Test Indonesian detection
- [ ] Test Italian detection
- [ ] Test artifact detection (reduplication)
- [ ] Test authenticity scoring
- [ ] Test validation decision logic
- [ ] Test integration with enhance()

### Documentation
- [ ] Update `shared/voice/README.md` with validation methods
- [ ] Document new parameters in API reference
- [ ] Add usage examples for validation
- [ ] Update voice integration guide

### Validation Scripts
- [ ] Create `scripts/validation/detect_translation_issues.py`
- [ ] Create `scripts/validation/score_voice_authenticity.py`
- [ ] Create `scripts/validation/generate_voice_reprocessing_plan.py`

---

## 🎯 Expected Impact

### Before Enhancement
- ❌ 5 materials with Indonesian FAQ answers
- ❌ 23+ materials with "very-very" artifacts
- ⚠️ 129 materials without voice_applied metadata
- ❌ No validation before voice processing

### After Enhancement
- ✅ Zero non-English content
- ✅ Zero translation artifacts
- ✅ Selective enhancement (only materials that need it)
- ✅ Authenticity scores tracked in metadata
- ✅ Clear recommendation for each material (keep/enhance/reprocess/translate)

---

**Status**: 📝 PROPOSAL - READY FOR IMPLEMENTATION  
**Estimated Effort**: 4-6 hours development + 2 hours testing  
**Next Step**: Implement methods in VoicePostProcessor, then create validation scripts
