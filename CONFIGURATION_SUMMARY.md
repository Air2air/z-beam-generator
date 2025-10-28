# Generator Configuration Summary

**Date**: October 28, 2025  
**Status**: ✅ All configurations at top of files

---

## Configuration Locations

### FAQ Generator (`components/faq/generators/faq_generator.py`)
**Lines 27-55** - Configuration Section

```python
# Answer length constraints (words)
MIN_WORDS_PER_ANSWER = 15
MAX_WORDS_PER_ANSWER = 50

# Question generation settings
MIN_QUESTIONS = 5
MAX_QUESTIONS = 10
QUESTION_RESEARCH_MAX_TOKENS = 2000
QUESTION_RESEARCH_TEMPERATURE = 0.7

# Answer generation settings
ANSWER_GENERATION_TEMPERATURE = 0.6
TOKEN_ESTIMATION_PER_WORD = 1.3  # Conservative estimate
TOKEN_SAFETY_MARGIN = 1.5  # Prevent truncation

# API call delays
API_CALL_DELAY_SECONDS = 0.5

# Data file paths
MATERIALS_DATA_PATH = "data/Materials.yaml"
CATEGORIES_DATA_PATH = "data/Categories.yaml"
```

---

### Subtitle Generator (`components/subtitle/core/subtitle_generator.py`)
**Lines 23-38** - Configuration Section

```python
# Word count range for subtitles (random selection within bounds)
MIN_WORDS_PER_SUBTITLE = 7  # Allow 7 for flexibility
MAX_WORDS_PER_SUBTITLE = 12

# Generation settings
SUBTITLE_GENERATION_TEMPERATURE = 0.6
SUBTITLE_MAX_TOKENS = 100

# Data file paths
MATERIALS_DATA_PATH = "data/Materials.yaml"
```

---

### Caption Generator (`components/caption/generators/generator.py`)
**Lines 23-49** - Configuration Section

```python
# Word count ranges for caption sections
MIN_WORDS_BEFORE = 30
MAX_WORDS_BEFORE = 70
MIN_WORDS_AFTER = 30
MAX_WORDS_AFTER = 70

# Total caption constraints
MIN_TOTAL_WORDS = 60
MAX_TOTAL_WORDS = 140

# Generation settings
CAPTION_GENERATION_TEMPERATURE = 0.6
CAPTION_MAX_TOKENS = 300  # Enough for both sections

# Word count tolerance
WORD_COUNT_TOLERANCE = 10

# Data file paths
MATERIALS_DATA_PATH = "data/Materials.yaml"
```

---

## Consistent Pattern

All generators follow this structure:

1. **Shebang** (`#!/usr/bin/env python3`)
2. **Module Docstring** (5-10 lines explaining discrete architecture)
3. **Imports** (standard library → third-party → local)
4. **Logger Setup** (`logger = logging.getLogger(__name__)`)
5. **CONFIGURATION SECTION** (clearly marked with `# ===` lines)
   - Word count constraints
   - Generation settings (temperature, max tokens)
   - API delays (FAQ only)
   - Data file paths
6. **Class Definition**

---

## Benefits of Top Configuration

✅ **Easy Tuning**: All magic numbers in one place  
✅ **No Code Diving**: Change settings without reading methods  
✅ **Clear Defaults**: Explicit values, no hidden constants  
✅ **Quick Reference**: See all settings at a glance  
✅ **Safe Changes**: Modify settings without touching logic  

---

## Quick Reference

| Setting | FAQ | Subtitle | Caption |
|---------|-----|----------|---------|
| **Min Words** | 15 | 7 | 30 (each) |
| **Max Words** | 50 | 12 | 70 (each) |
| **Temperature** | 0.6 | 0.6 | 0.6 |
| **Max Tokens** | 2000 (research) | 100 | 300 |
| **Data Source** | Materials.yaml | Materials.yaml | Materials.yaml |

---

**Status**: ✅ **All generators normalized with configurations at top**
