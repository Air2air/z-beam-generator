# Voice System Integration Status

## Current State Analysis

### ✅ What's Working
1. **Voice System Core** (`/voice` folder)
   - `orchestrator.py` - VoiceOrchestrator class providing unified API (420 lines)
   - `base/voice_base.yaml` - Universal voice principles
   - `profiles/*.yaml` - 4 country-specific profiles
   - Taiwan profile updated with new requirements (less technical, stronger nationality markers)

2. **Author System** (`components/author/`)
   - `authors.json` - 4 authors with complete metadata (name, country, expertise, ID, image)
   - `generator.py` - Extracts author from frontmatter, generates author component
   - Author assignment works via ID-based hash in frontmatter

3. **Caption Generation** (`components/caption/generators/`)
   - Multiple generators: `enhanced_generator.py`, `generator.py`, `frontmatter_generator.py`
   - Extracts author name from frontmatter
   - Generates before/after captions with technical content

4. **Frontmatter Integration** (`scripts/generate_caption_to_frontmatter.py`)
   - Overwrites ONLY caption section in frontmatter
   - Preserves all other data (materialProperties, applications, tags, etc.)
   - Works with micro-image-only caption structure

### ❌ What's Missing - Voice NOT Integrated

1. **Caption Generators Don't Use VoiceOrchestrator**
   - Caption generators extract author name but don't get country
   - No integration with `/voice` system at all
   - Voice instructions from profiles NOT included in prompts
   - Current: Generic prompts with HumanWritingPatterns (hardcoded patterns)
   - Needed: Country-specific voice instructions from VoiceOrchestrator

2. **Personas Config Duplicated in run.py**
   - Lines 356-395 have old persona config dict with signature phrases
   - Duplicates information already in `/voice/profiles/*.yaml`
   - Not using centralized voice system
   - Should be moved/consolidated into voice system

3. **No Country Resolution from Author**
   - Caption generators get author name but not country
   - Need to map: author name → country → voice profile
   - Missing link: `AuthorComponentGenerator.authors_lookup` has country data

4. **Voice Profiles Incomplete**
   - Taiwan: ✅ Updated with new requirements
   - Italy: ⏳ Original profile, needs updates
   - Indonesia: ⏳ Original profile, needs updates
   - USA: ⏳ Original profile, needs updates

## Integration Architecture

### Current Flow (WITHOUT Voice)
```
Material → Frontmatter (has author.id) 
         → Caption Generator
         → Extracts author.name from frontmatter
         → Uses generic prompts + HumanWritingPatterns
         → Generates caption
         → Writes to frontmatter
```

### Needed Flow (WITH Voice Integration)
```
Material → Frontmatter (has author.id, author.country)
         → Caption Generator
         → Extracts author.name + author.country from frontmatter
         → Calls VoiceOrchestrator(country=author.country)
         → Gets voice instructions (~2,000 chars of country-specific guidance)
         → Integrates voice instructions into caption prompt
         → Generates caption with authentic voice
         → Writes to frontmatter
```

## Detailed Gap Analysis

### Gap 1: Caption Generator Needs Country Extraction
**Current Code** (`components/caption/generators/enhanced_generator.py` line 337):
```python
author_obj = frontmatter_data.get('author', {})
author = author_obj.get('name', 'Unknown Author')
```

**Needed Code**:
```python
author_obj = frontmatter_data.get('author', {})
author = author_obj.get('name', 'Unknown Author')
author_country = author_obj.get('country', None)

if not author_country:
    raise ValueError(f"Author country required for voice integration - fail-fast architecture")
```

### Gap 2: Caption Generator Needs VoiceOrchestrator Integration
**Current Code** (no voice integration):
```python
prompt = self._build_prompt(material_name, material_data, author, frontmatter_data, schema_fields)
```

**Needed Code**:
```python
# Initialize voice orchestrator with author's country
from voice.orchestrator import VoiceOrchestrator

voice = VoiceOrchestrator(country=author_country)
voice_instructions = voice.get_voice_instructions(context="caption_generation")

# Integrate voice instructions into prompt
prompt = self._build_prompt_with_voice(
    material_name, material_data, author, 
    voice_instructions, frontmatter_data, schema_fields
)
```

### Gap 3: Prompt Template Needs Voice Section
**Current Prompt Structure**:
- Material context
- Technical requirements
- Before/after structure
- Generic style guidelines (from HumanWritingPatterns)

**Needed Prompt Structure**:
- Material context
- Technical requirements
- Before/after structure
- **VOICE INSTRUCTIONS** (from VoiceOrchestrator - country-specific linguistic patterns)
- Generic style guidelines

### Gap 4: Voice Profiles Need Updates
**Taiwan** (`voice/profiles/taiwan.yaml`):
- ✅ Updated: Less technical, stronger nationality markers, lower AI detection
- ✅ YAML valid and tested

**Italy** (`voice/profiles/italy.yaml`):
- ⏳ Original sophisticated profile
- Needs: Slight reduction in technical sophistication
- Needs: Amplified Italian linguistic patterns (word order, aesthetic descriptions)
- Needs: More human variability for lower AI detection

**Indonesia** (`voice/profiles/indonesia.yaml`):
- ⏳ Original accessible profile
- Needs: Stronger Indonesian English patterns (repetition, simplified structures)
- Needs: More environmental/sustainability focus naturally integrated
- Needs: Conversational accessibility without losing authority

**USA** (`voice/profiles/united_states.yaml`):
- ⏳ Original conversational profile
- Needs: More American confidence and optimism
- Needs: Business context integration (ROI, performance metrics)
- Needs: Innovation focus without sounding like marketing

## Implementation Plan

### Phase 1: Update Voice Profiles (High Priority)
- [x] Taiwan profile updated
- [ ] Update Italy profile with improvements
- [ ] Update Indonesia profile with improvements  
- [ ] Update USA profile with improvements

### Phase 2: Integrate VoiceOrchestrator into Caption Generation (Critical)
- [ ] Update `enhanced_generator.py` to extract author country
- [ ] Add VoiceOrchestrator initialization in caption generator
- [ ] Modify `_build_prompt()` to accept and integrate voice instructions
- [ ] Update prompt template to include voice instructions section
- [ ] Apply same changes to `generator.py` and `frontmatter_generator.py`

### Phase 3: Clean Up Duplicate Persona Config (Cleanup)
- [ ] Move persona config from `run.py` (lines 356-395) to voice system
- [ ] Update `get_persona_config()` to use VoiceOrchestrator
- [ ] Remove redundant persona dict from run.py
- [ ] Document migration in voice system docs

### Phase 4: Testing and Validation (Verification)
- [ ] Test caption generation for all 4 authors
- [ ] Verify voice instructions appear in prompts
- [ ] Compare before/after captions for voice differences
- [ ] Validate captions written correctly to frontmatter
- [ ] Check YAML validity of generated frontmatter files

## Technical Specifications

### VoiceOrchestrator API Usage

```python
from voice.orchestrator import VoiceOrchestrator

# Initialize for specific country
voice = VoiceOrchestrator(country="Taiwan")  # or "Italy", "Indonesia", "United States"

# Get voice instructions for caption generation
instructions = voice.get_voice_instructions(
    context="caption_generation",
    word_limit=380,
    additional_guidance="Focus on observable technical findings"
)

# Instructions format (example):
# {
#   "instructions": "2000+ character string with comprehensive voice guidance",
#   "word_limit": 380,
#   "signature_phrases": ["we can see clearly", "measurement shows", ...],
#   "quality_thresholds": {"formality_minimum": 60, ...}
# }

# Get profile summary
summary = voice.get_profile_summary()
# Returns: author, country, native_language, word_limit, key characteristics
```

### Caption Prompt Integration Pattern

```python
CAPTION_PROMPT_WITH_VOICE = """
You are {author}, a technical expert writing accessible microscopy captions.

=== VOICE INSTRUCTIONS ===
{voice_instructions}

=== MATERIAL CONTEXT ===
Material: {material_name}
Category: {category}
[... existing material context ...]

=== CAPTION REQUIREMENTS ===
[... existing technical requirements ...]

IMPORTANT: Follow the voice instructions above for linguistic patterns, sentence structure,
vocabulary choices, and cultural communication style. These instructions reflect your 
authentic communication style as {author}.
"""
```

## Success Criteria

### Minimal Success
1. VoiceOrchestrator integrated into at least one caption generator
2. Generated captions show distinct voice differences between authors
3. Voice instructions visibly affect caption style and tone

### Full Success  
1. All 4 voice profiles updated with new requirements
2. All 3 caption generators using VoiceOrchestrator
3. Voice instructions integrated into all caption prompts
4. Generated captions for all 4 authors show authentic voice distinction
5. Captions properly written to frontmatter files
6. Duplicate persona config removed from run.py

### Excellence
1. Voice system fully documented with integration examples
2. Before/after comparison showing voice improvement
3. AI detection scores reduced across all authors
4. Human reviewers confirm authentic voice differences
5. Voice system becomes single source of truth for all linguistic guidance

## Next Actions

1. **Immediate**: Update remaining 3 voice profiles (Italy, Indonesia, USA)
2. **Critical**: Integrate VoiceOrchestrator into `enhanced_generator.py`
3. **Testing**: Generate test captions with all 4 authors
4. **Validation**: Verify voice instructions flow through to generated content
5. **Cleanup**: Remove duplicate persona config from run.py

## Files to Modify

### Voice Profiles (Update)
- `voice/profiles/italy.yaml` - Update with new requirements
- `voice/profiles/indonesia.yaml` - Update with new requirements
- `voice/profiles/united_states.yaml` - Update with new requirements

### Caption Generators (Modify)
- `components/caption/generators/enhanced_generator.py` - Add VoiceOrchestrator integration
- `components/caption/generators/generator.py` - Add VoiceOrchestrator integration  
- `components/caption/generators/frontmatter_generator.py` - Add VoiceOrchestrator integration

### Configuration (Clean Up)
- `run.py` - Remove/migrate persona config dict (lines 356-395)

### Testing (Validate)
- Generate test captions: Bamboo (Taiwan), Alumina (Italy), Bronze (Indonesia), Aluminum (USA)
- Compare generated content before/after voice integration

## Dependencies

### Python Imports Needed
```python
from voice.orchestrator import VoiceOrchestrator
```

### No Additional Packages Required
- VoiceOrchestrator uses only Python stdlib + PyYAML (already installed)
- No new API clients or external dependencies

## Risk Assessment

### Low Risk
- Voice system is isolated, changes won't break existing functionality
- VoiceOrchestrator already tested and working
- Caption generation already works, we're adding enhancement

### Medium Risk
- Prompt changes might affect content quality initially
- Need to tune voice instruction integration for optimal results
- Multiple caption generators need consistent updates

### Mitigation
- Test with single generator first (enhanced_generator.py)
- Compare before/after captions to ensure quality maintained
- Keep original generators as backup during migration
- Use version control to rollback if needed

## Timeline Estimate

- **Voice Profile Updates**: 2-3 hours (Italy, Indonesia, USA)
- **VoiceOrchestrator Integration**: 3-4 hours (all 3 generators)
- **Testing and Validation**: 1-2 hours (generate test captions)
- **Configuration Cleanup**: 1 hour (remove duplicate config)
- **Documentation**: 1 hour (update voice system docs)

**Total**: 8-11 hours for complete integration

## Documentation References

- Voice System Architecture: `voice/VOICE_ARCHITECTURE.md`
- Voice Integration Plan: `voice/INTEGRATION_PLAN.md`
- VoiceOrchestrator API: `voice/orchestrator.py` (comprehensive docstrings)
- Quick Reference: `voice/QUICK_REFERENCE.md`

---

**Status**: Taiwan profile updated, ready for remaining voice updates and caption integration
**Last Updated**: 2025-10-04
**Next Milestone**: Complete voice profile updates for Italy, Indonesia, USA
