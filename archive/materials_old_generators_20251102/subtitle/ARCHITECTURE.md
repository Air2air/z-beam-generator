# Subtitle Component Architecture

**Pattern**: Discrete Component with Single Voice Generation  
**Follows**: Caption reference pattern  
**Updated**: October 26, 2025

---

## 🏗️ Structure

```
components/subtitle/
├── __init__.py                    # Package exports
├── core/
│   └── subtitle_generator.py     # Main generator logic
├── prompts/
│   └── (future prompt templates)
└── config/
    └── config.yaml                # Subtitle-specific settings
```

---

## 🎯 Component Pattern

### Single Voice Call Architecture

Subtitle generates **8-12 word engaging subtitles** using VoiceOrchestrator.

```python
from voice.orchestrator import VoiceOrchestrator

class SubtitleComponentGenerator(APIComponentGenerator):
    """Generate engaging 8-12 word subtitles"""
    
    def generate(self, material_name: str, material_data: Dict, 
                 api_client, **kwargs) -> ComponentResult:
        """
        Single voice call with word count constraints.
        
        Flow:
        1. Load frontmatter data (author country required)
        2. Build subtitle-specific prompt
        3. Call VoiceOrchestrator.get_voice_for_component()
        4. Generate with API
        5. Validate word count (8-12 words)
        6. Return ComponentResult
        """
        pass
```

---

## 🔑 Key Features

### 1. Voice Integration
- **VoiceOrchestrator**: Country-specific author voice
- **Author Required**: Frontmatter must have author.country
- **Reusable Service**: Voice service shared across components

### 2. Word Count Enforcement
- **Minimum**: 8 words
- **Maximum**: 12 words
- **Target**: 10 words
- **Validation**: Strict enforcement in generate() method

### 3. Separation from Caption
- **Caption**: Dual voice calls (before/after, 20-100 words each)
- **Subtitle**: Single voice call (8-12 words)
- **Shared**: Both use VoiceOrchestrator but different constraints

---

## 📊 Comparison to Caption

| Aspect | Caption | Subtitle |
|--------|---------|----------|
| Voice Calls | 2 (before/after) | 1 (single) |
| Word Count | 20-100 per section | 8-12 total |
| Structure | Dual sections | Single phrase |
| Purpose | Microscopy descriptions | Engaging tagline |
| Prompts | Section-specific (contaminated/cleaned) | Single engaging prompt |

---

## ✅ Discrete Component Benefits

1. **Self-Contained**: All subtitle logic in one component
2. **Reusable Services**: VoiceOrchestrator shared, not duplicated
3. **Clear Boundaries**: Subtitle-specific prompts/config separate
4. **Easy Testing**: Component can be tested independently
5. **Follows Pattern**: Matches caption's proven discrete architecture

---

## 🔮 Future Enhancements

- Add `prompts/templates/` for subtitle-specific prompt variations
- Add quality scoring for subtitle engagement
- Add A/B testing support for different subtitle styles
- Add analytics tracking for subtitle effectiveness

---

**Reference**: See `components/caption/ARCHITECTURE.md` for full discrete component pattern.
