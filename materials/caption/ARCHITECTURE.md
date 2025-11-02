# Caption Component Architecture

**Last Updated**: October 24, 2025  
**Refactoring**: Dual Voice Call Architecture

---

## 🏗️ Architecture Overview

The Caption component generates dual-section microscopy descriptions (BEFORE contamination + AFTER cleaning) while keeping the **Voice service completely separate and reusable**.

### Key Principle: Separation of Concerns

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPTION COMPONENT                         │
│  (Caption-specific dual-generation logic)                   │
│                                                              │
│  • Determines target word counts for before/after           │
│  • Calculates style guidance (brief/moderate/comprehensive) │
│  • Calls Voice service TWICE independently                  │
│  • Combines results into dual-section structure             │
│  • Handles caption-specific validation                      │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ calls twice
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                     VOICE SERVICE                            │
│  (Generic, reusable content generation)                     │
│                                                              │
│  • Country-specific voice authenticity                      │
│  • Single-section prompt construction                       │
│  • Linguistic pattern enforcement                           │
│  • Completely agnostic to caption structure                 │
│  • Reusable for ANY component                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📞 Dual Voice Call Flow

### Step 1: Caption Component Initializes
```python
# Caption determines its own dual-section requirements
min_section_words = 20
max_section_words = 100

before_words = random.randint(min_section_words, max_section_words)
after_words = random.randint(min_section_words, max_section_words)
```

### Step 2: First Voice Call (BEFORE section)
```python
before_prompt = self._build_single_section_prompt(
    material_name=material_name,
    frontmatter_data=frontmatter_data,
    section_type="before",  # Caption-specific: contaminated surface
    target_words=before_words,
    style_guidance="brief and focused",
    paragraph_count="1 concise paragraph"
)

before_response = api_client.generate_simple(prompt=before_prompt, ...)
before_text = self._extract_single_section_content(before_response.content, "before")
```

### Step 3: Second Voice Call (AFTER section)
```python
after_prompt = self._build_single_section_prompt(
    material_name=material_name,
    frontmatter_data=frontmatter_data,
    section_type="after",  # Caption-specific: cleaned surface
    target_words=after_words,
    style_guidance="comprehensive and detailed",
    paragraph_count="2-3 paragraphs"
)

after_response = api_client.generate_simple(prompt=after_prompt, ...)
after_text = self._extract_single_section_content(after_response.content, "after")
```

### Step 4: Caption Combines Results
```python
ai_content = {
    'before': before_text,
    'after': after_text,
    # Caption-specific metadata
    'technicalFocus': 'surface_analysis',
    'contaminationProfile': f'{material_name} contamination'
}
```

---

## 🎯 Why This Architecture?

### ✅ Benefits

1. **Voice Service Reusability**
   - Voice can now be used by Text component, Tags component, etc.
   - Each component calls Voice with their own requirements
   - No caption-specific logic leaks into Voice

2. **Caption Component Ownership**
   - Caption owns its dual before/after structure
   - Caption determines word count ranges (20-100 per section)
   - Caption handles section-specific validation

3. **Clean Separation**
   - Voice knows NOTHING about captions
   - Caption knows NOTHING about linguistic patterns
   - Each component has single responsibility

4. **Independent Variation**
   - Each section gets fully independent generation
   - Different word counts, styles, and cache seeds
   - Maximum randomization without patterns

### ❌ Previous Architecture Problems

**Old Way**: Single API call with dual-section template
```yaml
# ❌ Voice template had caption-specific structure baked in
caption_generation:
  base_template: |
    Write BEFORE_TEXT: {before_words} words
    Write AFTER_TEXT: {after_words} words
    
    OUTPUT FORMAT:
    **BEFORE_TEXT:**
    [content]
    
    **AFTER_TEXT:**
    [content]
```

**Problems:**
- Voice service was caption-specific (not reusable)
- Single API call meant both sections influenced each other
- API response caching affected both sections together
- Template structure leaked caption logic into Voice

---

## 🔧 Implementation Details

### Caption Component Methods

#### `_build_single_section_prompt()`
Builds prompt for ONE section using Voice service:
```python
def _build_single_section_prompt(
    self,
    material_name: str,
    frontmatter_data: Dict,
    section_type: str,  # "before" or "after"
    target_words: int,
    style_guidance: str,
    paragraph_count: str
) -> str
```

- **Input**: Caption-specific section requirements
- **Output**: Complete Voice prompt for single section
- **Calls**: `VoiceOrchestrator.get_unified_prompt()` with `microscopy_description` template

#### `_extract_single_section_content()`
Extracts and validates single section text:
```python
def _extract_single_section_content(
    self,
    ai_response: str,
    material_name: str,
    section_type: str
) -> str
```

- **Input**: Raw AI response for one section
- **Output**: Cleaned, validated section text
- **Validation**: Minimum 100 chars, fail-fast on empty

#### `generate()`
Main generation orchestrator:
```python
def generate(self, material_name: str, material_data: Dict, api_client) -> ComponentResult:
    # 1. Determine before/after word counts (caption-specific logic)
    before_words = random.randint(20, 100)
    after_words = random.randint(20, 100)
    
    # 2. Call Voice for BEFORE section
    before_text = self._generate_section("before", before_words, ...)
    
    # 3. Call Voice for AFTER section  
    after_text = self._generate_section("after", after_words, ...)
    
    # 4. Combine into caption structure
    return self._create_caption_result(before_text, after_text)
```

### Voice Service Integration

#### New Generic Template: `microscopy_description`

```yaml
microscopy_description:
  base_template: |
    You are {author_name}, a {author_expertise} expert from {author_country}.
    
    MATERIAL: {material_name}
    FOCUS: {section_focus}
    TASK: {section_instruction}
    
    REQUIREMENTS:
    - Target: {target_words} words
    - Style: {style_guidance}
    - Paragraphs: {paragraph_count}
    
    Generate your analysis now.
```

**Key Parameters:**
- `section_focus`: "contaminated surface microscopy" or "cleaned surface restoration"
- `section_instruction`: Caption provides section-specific guidance
- `target_words`: Independent for each call
- `style_guidance`: "brief and focused" | "moderate detail" | "comprehensive"

---

## 📊 Performance Characteristics

### API Call Pattern
```
Old Architecture:
  1 API call → Both sections generated together
  
New Architecture:
  2 API calls → Each section independent
```

### Timing Example (Basalt)
```
Call 1 (BEFORE):  7.45s  →  91 words generated
Call 2 (AFTER):   6.26s  →  74 words generated
Total:           13.71s  → 165 total words (40% variation!)
```

### Cache Behavior
```
Old: Single cache key → Both sections stuck together
New: Two cache keys → Each section can vary independently
```

---

## 🔮 Future Components

This architecture enables easy addition of new components:

### Text Component (Future)
```python
# Text component can call Voice multiple times for different sections
intro = voice.generate_content("introduction", target_words=50)
technical = voice.generate_content("technical_detail", target_words=150)
conclusion = voice.generate_content("conclusion", target_words=30)
```

### Tags Component (Future)
```python
# Tags can call Voice once for tag generation
tags = voice.generate_content("metadata_tags", target_words=10)
```

### Any Component Pattern
```python
# Generic pattern: Component owns structure, Voice provides content
content = voice.generate_content(
    component_type="custom_type",
    section_focus="your focus",
    target_words=your_count
)
```

---

## 🛠️ Configuration

### Caption Word Ranges
```python
# Defined in Caption component only
MIN_SECTION_WORDS = 20
MAX_SECTION_WORDS = 100

# Total caption range: 40-200 words
```

### Style Tiers
```python
# Caption-specific style calculation
if words < 40:
    style = "brief and focused"
    paragraphs = "1 concise paragraph"
elif words < 70:
    style = "moderate detail"
    paragraphs = "1-2 paragraphs"
else:
    style = "comprehensive and detailed"
    paragraphs = "2-3 paragraphs"
```

### Voice Settings
```python
# Voice orchestrator settings (country-specific)
temperature = 0.7  # Natural variation
max_tokens = dynamic  # Based on author word limits
```

---

## 🎭 Voice Authenticity

Voice service maintains country-specific patterns **independent of caption structure**:

### Taiwan (Yi-Chun Lin)
- Technical measurements with µm precision
- Systematic methodology language
- Comparative analysis with peer materials

### Italy (Alessandro Moretti)
- Engineering sophistication
- Refined technical vocabulary
- UNI EN ISO standards references

### USA (Todd Dunning)
- Efficiency-focused language
- Bottom-line pragmatism
- ASTM/ASME standard references

### Indonesia (Ikmanda Roswati)
- Collective language patterns
- Environmental responsibility focus
- SNI standard compliance

**Each voice is applied consistently to BOTH before and after sections**

---

## 📝 Summary

### What Caption Component Does
✅ Determines dual-section structure (before + after)  
✅ Calculates independent word counts (20-100 each)  
✅ Determines style guidance per section  
✅ Calls Voice service twice  
✅ Combines results into caption format  
✅ Validates caption-specific requirements  

### What Voice Service Does
✅ Provides country-specific voice authenticity  
✅ Generates single-section content  
✅ Enforces linguistic patterns  
✅ Maintains author credibility  
✅ **Completely reusable for any component**  

### What This Enables
✅ Other components can use Voice independently  
✅ Caption maintains full control over its structure  
✅ Maximum variation between sections (no convergence)  
✅ Clean, testable, maintainable architecture  
✅ Future-proof for new component types  

---

**Architecture Status**: ✅ Implemented and Tested  
**Voice Reusability**: ✅ Ready for other components  
**Separation of Concerns**: ✅ Complete

---

## 🔄 Manual Override Behavior

### Always Overwrite Policy

**Critical Principle**: Manual caption generation requests **ALWAYS overwrite** existing captions without checking for existence.

```python
# ✅ CORRECT: Manual requests always overwrite
def generate(self, material_name: str, material_data: Dict, **kwargs):
    # No existence check - always generate and save
    before_text = self._generate_section("before", ...)
    after_text = self._generate_section("after", ...)
    
    # Always write to Materials.yaml
    self._write_caption_to_materials(material_name, before_text, after_text)
```

```python
# ❌ WRONG: Never skip generation based on existence
def generate(self, material_name: str, material_data: Dict, **kwargs):
    # ❌ NEVER DO THIS
    if material_data.get('caption'):
        return existing_caption  # WRONG - violates manual override
```

### Use Cases

1. **Quality Improvement**: User wants to regenerate with updated voice profiles (e.g., Indonesian emotional marker prohibition)

2. **Testing Variations**: User wants to test different authors or see alternative generations

3. **Image Path Updates**: User wants to ensure all materials have updated frontmatter with micro images

4. **Consistency**: User wants to regenerate all captions after system improvements

### Verification

Manual override behavior verified through testing:
- Material: Copper
- Original: 69 words (generated 2025-10-24)
- Regenerated: 84 words (generated 2025-10-25)
- Timestamp: Updated automatically
- Conclusion: ✅ Manual override working correctly

### Implementation Details

The `_write_caption_to_materials()` method:
- **Never checks** if caption exists
- **Always overwrites** caption data
- **Always updates** timestamp
- **Always recalculates** word/character counts

This ensures users have full control over content regeneration.

````
