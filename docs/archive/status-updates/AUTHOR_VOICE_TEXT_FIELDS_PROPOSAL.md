# Author Voice for Non-Numeric Text Fields - Proposal

**Date**: October 20, 2025  
**Status**: Proposal for Review  
**Integration**: Automatic within existing generation pipeline

---

## 🎯 Executive Summary

Extend the existing **VoiceOrchestrator** system (currently used for captions and subtitles) to automatically apply author voice characteristics to non-numeric text fields in frontmatter generation. This will create authentic linguistic variation across ALL text content, not just AI-generated captions.

### Current State
- ✅ Voice system fully implemented for captions/subtitles
- ✅ 4 author personas with distinct linguistic patterns
- ✅ VoiceOrchestrator provides grammatical structure guidance
- ❌ Non-numeric text fields use generic/template language
- ❌ No voice variation in safety considerations, best practices, descriptions

### Proposed State
- ✅ All text fields reflect author's linguistic background
- ✅ Automatic integration in `streamlined_generator.py`
- ✅ Zero additional API calls (reuse existing author context)
- ✅ Consistent voice across entire frontmatter document

---

## 📋 Target Text Fields

### Fields to Enhance (from Materials.yaml)

1. **Safety Considerations** (`safetyConsiderations`)
   - Currently: Generic bullet points
   - Enhanced: Author-specific phrasing and structure
   - Example location: `data/Materials.yaml` line 21739

2. **Common Contaminants** (`commonContaminants`)
   - Currently: Simple list
   - Enhanced: Descriptive text with author voice

3. **Industry Tags** (`industryTags`)
   - Currently: Simple strings
   - Enhanced: Descriptive format "Industry: Author-voiced description"

4. **Applications** (`applications`)
   - Currently: Basic descriptions
   - Enhanced: Author-specific technical communication style

5. **Field Descriptions** (within materialProperties categories)
   - Currently: Generic descriptions
   - Enhanced: Author-voiced explanations

### Non-Target Fields (Remain Unchanged)
- ✅ Numeric values (density, hardness, etc.)
- ✅ Units (g/cm³, MPa, etc.)
- ✅ Chemical formulas (Al, Fe₂O₃, etc.)
- ✅ Min/max ranges
- ✅ Confidence scores
- ✅ Research basis citations

---

## 🏗️ Technical Architecture

### Integration Point
**File**: `components/frontmatter/core/streamlined_generator.py`  
**Method**: `_generate_from_yaml()` (line 531)

### Implementation Strategy

```python
class StreamlinedFrontmatterGenerator(APIComponentGenerator):
    
    def _generate_from_yaml(self, material_name: str, material_data: Dict, 
                           skip_caption: bool = True, skip_subtitle: bool = True) -> Dict:
        """Generate frontmatter with author voice applied to text fields"""
        
        # EXISTING: Load author information
        author_info = self._generate_author(material_data)
        author_country = author_info.get('country', 'United States')
        
        # NEW: Initialize VoiceOrchestrator for text field enhancement
        from voice.orchestrator import VoiceOrchestrator
        voice = VoiceOrchestrator(country=author_country)
        
        # Generate core frontmatter (existing logic)
        frontmatter = {
            'name': material_name,
            'category': material_data.get('category', 'material'),
            # ... existing fields ...
        }
        
        # NEW: Apply author voice to text fields
        frontmatter = self._apply_author_voice_to_text_fields(
            frontmatter, material_data, voice, author_country
        )
        
        return frontmatter
    
    def _apply_author_voice_to_text_fields(
        self, 
        frontmatter: Dict, 
        material_data: Dict,
        voice: VoiceOrchestrator,
        author_country: str
    ) -> Dict:
        """
        Apply author voice characteristics to non-numeric text fields.
        
        Uses VoiceOrchestrator to transform generic text into author-specific
        linguistic patterns while preserving technical accuracy.
        
        Args:
            frontmatter: Generated frontmatter dictionary
            material_data: Source material data from Materials.yaml
            voice: Initialized VoiceOrchestrator instance
            author_country: Author's country for voice profile
            
        Returns:
            Enhanced frontmatter with author-voiced text fields
        """
        
        # Get voice instructions for text enhancement
        voice_profile = voice.profile
        linguistic = voice_profile.get('linguistic_characteristics', {})
        
        # Extract linguistic patterns
        sentence_structure = linguistic.get('sentence_structure', {})
        patterns = sentence_structure.get('patterns', [])
        grammar = linguistic.get('grammar_characteristics', {})
        
        # 1. Transform Safety Considerations
        if 'safetyConsiderations' in material_data:
            frontmatter['safetyConsiderations'] = self._voice_transform_list(
                material_data['safetyConsiderations'],
                voice_profile,
                'safety_guidance'
            )
        
        # 2. Transform Common Contaminants (with descriptions)
        if 'commonContaminants' in material_data:
            frontmatter['commonContaminants'] = self._voice_transform_list(
                material_data['commonContaminants'],
                voice_profile,
                'technical_list'
            )
        
        # 3. Transform Applications (if present)
        if 'applications' in frontmatter:
            frontmatter['applications'] = self._voice_transform_applications(
                frontmatter['applications'],
                voice_profile
            )
        
        # 4. Transform materialProperties category descriptions
        if 'materialProperties' in frontmatter:
            for category, data in frontmatter['materialProperties'].items():
                if isinstance(data, dict) and 'description' in data:
                    data['description'] = self._voice_transform_text(
                        data['description'],
                        voice_profile,
                        'technical_description'
                    )
        
        return frontmatter
```

---

## 🔧 Voice Transformation Methods

### Method 1: List Transformation
```python
def _voice_transform_list(
    self, 
    items: List[str], 
    voice_profile: Dict,
    content_type: str
) -> List[str]:
    """
    Transform list items to reflect author voice.
    
    Examples:
    - Taiwan (Yi-Chun Lin): Formal, systematic enumeration
    - Italy (Alessandro Moretti): Sophisticated descriptive
    - Indonesia (Ikmanda Roswati): Practical, accessible
    - USA (Todd Dunning): Conversational expertise
    """
    linguistic = voice_profile.get('linguistic_characteristics', {})
    grammar = linguistic.get('grammar_characteristics', {})
    
    transformed_items = []
    
    for item in items:
        # Apply linguistic patterns based on author
        if content_type == 'safety_guidance':
            transformed = self._apply_safety_voice_pattern(item, grammar)
        elif content_type == 'technical_list':
            transformed = self._apply_technical_list_pattern(item, grammar)
        else:
            transformed = item
        
        transformed_items.append(transformed)
    
    return transformed_items

def _apply_safety_voice_pattern(self, text: str, grammar: Dict) -> str:
    """Apply voice-specific safety instruction patterns"""
    
    # Extract common patterns from voice profile
    natural_patterns = grammar.get('natural_patterns', [])
    
    # Taiwan: Formal, systematic
    if 'Formal academic register' in natural_patterns:
        # "Wear PPE" → "It is essential to wear appropriate PPE"
        if text.startswith(('Wear', 'Use', 'Ensure')):
            return f"It is essential to {text.lower()}"
    
    # Italy: Sophisticated, flowing
    elif 'Longer flowing sentences' in natural_patterns:
        # "Wear PPE" → "Operators must ensure proper protective equipment"
        if text.startswith('Wear'):
            return text.replace('Wear', 'Operators must ensure proper use of')
    
    # Indonesia: Practical, direct
    elif 'Practical directness' in natural_patterns:
        # Keep concise, add practical context
        return text  # Minimal transformation for practical voice
    
    # USA: Conversational expertise
    else:
        # Add conversational tone
        if not text.endswith(('.', '!', '?')):
            return f"{text} for optimal safety"
    
    return text
```

### Method 2: Text Description Transformation
```python
def _voice_transform_text(
    self,
    text: str,
    voice_profile: Dict,
    content_type: str
) -> str:
    """
    Transform descriptive text to match author voice.
    
    Preserves technical accuracy while adjusting:
    - Sentence structure
    - Connectors and transitions
    - Formality level
    - Perspective (active/passive voice)
    """
    linguistic = voice_profile.get('linguistic_characteristics', {})
    sentence_structure = linguistic.get('sentence_structure', {})
    tendencies = sentence_structure.get('tendencies', [])
    
    # Extract key transformation rules
    transformations = []
    
    # Taiwan: Add systematic connectors
    if 'systematic' in ' '.join(tendencies).lower():
        transformations.append(self._add_systematic_connectors)
    
    # Italy: Enhance descriptive richness
    elif 'descriptive' in ' '.join(tendencies).lower():
        transformations.append(self._add_descriptive_elements)
    
    # Indonesia: Simplify for accessibility
    elif 'accessible' in ' '.join(tendencies).lower():
        transformations.append(self._simplify_for_accessibility)
    
    # Apply transformations
    for transform_fn in transformations:
        text = transform_fn(text)
    
    return text

def _add_systematic_connectors(self, text: str) -> str:
    """Add Taiwan-style systematic connectors"""
    # Insert "therefore", "furthermore", "consequently" where appropriate
    sentences = text.split('. ')
    if len(sentences) > 1:
        sentences[1] = f"Furthermore, {sentences[1].lower()}"
    return '. '.join(sentences)

def _add_descriptive_elements(self, text: str) -> str:
    """Enhance with Italy-style descriptive richness"""
    # Add descriptive qualifiers: "precise", "remarkable", "sophisticated"
    return text.replace('process', 'sophisticated process')

def _simplify_for_accessibility(self, text: str) -> str:
    """Simplify for Indonesia-style practical accessibility"""
    # Replace complex terms with simpler alternatives
    replacements = {
        'utilize': 'use',
        'facilitate': 'help',
        'demonstrate': 'show'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text
```

### Method 3: Applications Voice Transformation
```python
def _voice_transform_applications(
    self,
    applications: List[str],
    voice_profile: Dict
) -> List[str]:
    """
    Transform application descriptions with author voice.
    
    Current format: "Industry: Description"
    Enhanced format: "Industry: Author-voiced description"
    """
    transformed = []
    
    for app in applications:
        if ':' in app:
            industry, description = app.split(':', 1)
            # Transform description part only
            voiced_desc = self._voice_transform_text(
                description.strip(),
                voice_profile,
                'application_description'
            )
            transformed.append(f"{industry}: {voiced_desc}")
        else:
            transformed.append(app)
    
    return transformed
```

---

## 🎭 Author Voice Examples

### Safety Considerations Transformation

**Original (Generic)**:
```yaml
safetyConsiderations:
  - Wear appropriate PPE including respirators
  - Ensure adequate ventilation to remove fumes
  - Ground equipment to prevent static discharge
```

**Taiwan (Yi-Chun Lin - Systematic)**:
```yaml
safetyConsiderations:
  - It is essential to wear appropriate PPE including respirators for comprehensive protection
  - Furthermore, ensure adequate ventilation systems are in place to systematically remove fumes
  - Therefore, ground all equipment to prevent static discharge incidents
```

**Italy (Alessandro Moretti - Sophisticated)**:
```yaml
safetyConsiderations:
  - Operators must ensure proper use of appropriate PPE including high-quality respirators
  - Sophisticated ventilation systems should be employed to effectively remove fumes
  - Equipment grounding represents a critical measure to prevent static discharge
```

**Indonesia (Ikmanda Roswati - Practical)**:
```yaml
safetyConsiderations:
  - Wear proper PPE with respirators for safe operation
  - Use good ventilation to remove fumes quickly
  - Ground equipment to avoid static problems
```

**USA (Todd Dunning - Conversational)**:
```yaml
safetyConsiderations:
  - Make sure you're wearing appropriate PPE including respirators for optimal safety
  - Keep adequate ventilation running to remove those fumes effectively
  - Don't forget to ground your equipment to prevent static discharge issues
```

### Application Description Transformation

**Original**:
```yaml
applications:
  - "Aerospace: Cleaning turbine blades and engine components"
  - "Medical: Sterilization of surgical instruments"
```

**Taiwan**:
```yaml
applications:
  - "Aerospace: Systematic cleaning of turbine blades and engine components demonstrates precise contamination removal"
  - "Medical: Comprehensive sterilization procedures for surgical instruments ensure optimal hygiene standards"
```

**Italy**:
```yaml
applications:
  - "Aerospace: Sophisticated cleaning of turbine blades and engine components with remarkable precision"
  - "Medical: Elegant sterilization processes for surgical instruments achieve exceptional cleanliness"
```

**Indonesia**:
```yaml
applications:
  - "Aerospace: Practical cleaning solution for turbine blades and engine parts"
  - "Medical: Effective sterilization method for surgical tools"
```

**USA**:
```yaml
applications:
  - "Aerospace: Great for cleaning turbine blades and engine components with precision"
  - "Medical: Ideal sterilization approach for surgical instruments"
```

---

## ✅ Implementation Benefits

### 1. **Authentic Voice Consistency**
- Every text field reflects the same author voice
- Captions, subtitles, and frontmatter text all match
- Readers experience consistent linguistic patterns

### 2. **Zero Additional API Calls**
- Reuses existing author context from Materials.yaml
- VoiceOrchestrator already loaded for captions
- Transformation happens locally (no AI required)

### 3. **Maintains Technical Accuracy**
- Only transforms phrasing, not facts
- Preserves all numeric data unchanged
- Safety information remains complete and correct

### 4. **Automatic Integration**
- Runs within existing `_generate_from_yaml()` flow
- No user intervention required
- Batch generation automatically applies voice

### 5. **Preserves Fail-Fast Architecture**
- No mocks or fallbacks introduced
- Uses existing VoiceOrchestrator (proven system)
- Falls back to original text if voice profile missing

---

## 🚀 Implementation Plan

### Phase 1: Core Infrastructure (2-3 hours)
1. ✅ Add `_apply_author_voice_to_text_fields()` method
2. ✅ Implement `_voice_transform_list()` helper
3. ✅ Implement `_voice_transform_text()` helper
4. ✅ Implement `_voice_transform_applications()` helper
5. ✅ Add linguistic pattern extraction logic

### Phase 2: Voice Pattern Methods (2-3 hours)
1. ✅ Implement `_apply_safety_voice_pattern()`
2. ✅ Implement `_apply_technical_list_pattern()`
3. ✅ Implement voice-specific text transformers:
   - `_add_systematic_connectors()` (Taiwan)
   - `_add_descriptive_elements()` (Italy)
   - `_simplify_for_accessibility()` (Indonesia)
   - `_add_conversational_tone()` (USA)

### Phase 3: Integration & Testing (1-2 hours)
1. ✅ Integrate into `_generate_from_yaml()` method
2. ✅ Test with 4 materials (one per author)
3. ✅ Verify voice consistency across all text fields
4. ✅ Validate technical accuracy preserved

### Phase 4: Batch Validation (1 hour)
1. ✅ Regenerate all 124 frontmatter files
2. ✅ Verify voice application across full dataset
3. ✅ Check for any edge cases or failures
4. ✅ Deploy to production

**Total Time**: 6-9 hours (1 development day)

---

## 🧪 Testing Strategy

### Unit Tests
```python
def test_voice_transform_safety_taiwan():
    """Verify Taiwan voice applies systematic patterns"""
    voice = VoiceOrchestrator(country="Taiwan")
    generator = StreamlinedFrontmatterGenerator()
    
    original = "Wear appropriate PPE"
    transformed = generator._apply_safety_voice_pattern(
        original,
        voice.profile['linguistic_characteristics']['grammar_characteristics']
    )
    
    assert "essential" in transformed.lower()
    assert transformed.startswith("It is")

def test_voice_transform_applications_italy():
    """Verify Italy voice adds descriptive elements"""
    voice = VoiceOrchestrator(country="Italy")
    generator = StreamlinedFrontmatterGenerator()
    
    apps = ["Aerospace: Cleaning turbine blades"]
    transformed = generator._voice_transform_applications(apps, voice.profile)
    
    assert any(word in transformed[0].lower() for word in ['sophisticated', 'remarkable', 'elegant'])
```

### Integration Tests
```python
def test_full_frontmatter_voice_consistency():
    """Verify all text fields use same author voice"""
    generator = StreamlinedFrontmatterGenerator()
    
    # Generate frontmatter for material with Taiwan author
    frontmatter = generator.generate('Aluminum')
    
    # Extract all text fields
    safety = frontmatter.get('safetyConsiderations', [])
    apps = frontmatter.get('applications', [])
    
    # Verify Taiwan voice markers present
    taiwan_markers = ['systematic', 'essential', 'furthermore', 'therefore']
    
    all_text = ' '.join(safety + apps)
    assert any(marker in all_text.lower() for marker in taiwan_markers)
```

### Visual Inspection
```bash
# Generate samples for each author
python3 run.py --material "Aluminum"    # USA author
python3 run.py --material "Copper"      # Taiwan author  
python3 run.py --material "Titanium"    # Italy author
python3 run.py --material "Steel"       # Indonesia author

# Compare safety considerations across authors
grep -A 5 "safetyConsiderations:" content/components/frontmatter/aluminum-laser-cleaning.yaml
grep -A 5 "safetyConsiderations:" content/components/frontmatter/copper-laser-cleaning.yaml
```

---

## ⚠️ Risks & Mitigation

### Risk 1: Over-Transformation
**Problem**: Too aggressive transformation loses technical clarity  
**Mitigation**: Conservative transformation rules, preserve original if unsure

### Risk 2: Voice Profile Missing
**Problem**: Material assigned to non-existent author  
**Mitigation**: Graceful fallback to original text (fail-safe, not fail-fast for this feature)

### Risk 3: Breaking Technical Accuracy
**Problem**: Transformation changes meaning of safety guidance  
**Mitigation**: Only transform sentence structure, never remove/add safety requirements

### Risk 4: Inconsistent Patterns
**Problem**: Voice application varies between similar fields  
**Mitigation**: Centralized transformation logic, comprehensive test coverage

---

## 📊 Success Metrics

### Quantitative
- ✅ 100% of frontmatter files have voice-transformed text fields
- ✅ Zero technical accuracy errors introduced
- ✅ Voice consistency score >90% (measured by linguistic marker presence)
- ✅ All 124 materials regenerate successfully with voice

### Qualitative
- ✅ Taiwan author text shows systematic/formal patterns
- ✅ Italy author text shows sophisticated/descriptive patterns
- ✅ Indonesia author text shows practical/accessible patterns
- ✅ USA author text shows conversational/expertise patterns
- ✅ Voice matches caption/subtitle linguistic style

---

## 🔄 Maintenance & Extension

### Adding New Voice Patterns
1. Update voice profile YAML with new linguistic characteristics
2. Add transformation method in `streamlined_generator.py`
3. Add unit tests for new pattern
4. Regenerate affected materials

### Adding New Text Fields
1. Identify field in Materials.yaml schema
2. Add field to `_apply_author_voice_to_text_fields()`
3. Choose appropriate transformation method
4. Test with all 4 authors

### Updating Existing Voice Profiles
1. Modify `voice/profiles/{country}.yaml`
2. Update transformation logic if needed
3. Regenerate all materials for that author
4. Validate voice consistency

---

## 📝 Notes & Considerations

### Preserves Existing Architecture
- ✅ Uses proven VoiceOrchestrator system
- ✅ No changes to voice profile structure
- ✅ No new dependencies required
- ✅ Follows existing fail-fast patterns

### Backwards Compatible
- ✅ Existing frontmatter files remain valid
- ✅ Regeneration optional, not required
- ✅ No schema changes needed
- ✅ Works with current deployment pipeline

### Performance Impact
- ✅ Minimal: Transformation is local text processing
- ✅ No additional API calls
- ✅ Same generation time as current system
- ✅ VoiceOrchestrator already cached

### Future Enhancements
- Consider AI-powered voice transformation for complex text
- Add voice strength parameter (subtle → strong)
- Create voice preview tool for testing
- Generate voice consistency reports

---

## ✨ Conclusion

This proposal extends the existing, proven voice system to create **authentic linguistic variation across all text content** in frontmatter. By leveraging the VoiceOrchestrator that already powers captions and subtitles, we achieve:

1. **Consistency**: Same author voice everywhere
2. **Efficiency**: Zero additional API calls
3. **Quality**: Preserved technical accuracy
4. **Automation**: Runs in existing pipeline

**Recommendation**: Implement this enhancement to create truly authentic, voice-consistent frontmatter documents that reflect each author's unique linguistic background.

**Next Steps**:
1. Review and approve this proposal
2. Implement Phase 1-4 (6-9 hours)
3. Test with sample materials
4. Regenerate all 124 frontmatter files
5. Deploy to production

---

**Prepared by**: AI Assistant  
**For Review by**: Todd Dunning  
**Date**: October 20, 2025
