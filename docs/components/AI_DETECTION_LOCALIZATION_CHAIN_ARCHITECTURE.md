# AI Detection + Localization Prompt Chain Architecture

## Overview

The Z-Beam Generator uses a **two-stage prompt chain architecture** that separates AI detection optimization from cultural localization:

```
AI Detection Prompts → Localization Prompts → Base Content Prompts
```

This architecture ensures:
- **AI detection logic** can evolve dynamically without affecting localization
- **Localization prompts** remain culturally authentic and unchanged
- **Clear separation of concerns** between AI optimization and cultural authenticity

## Architecture Components

### 1. AI Detection Prompt Chain (`components/text/ai_detection/`)

**Purpose**: Provides dynamic AI detection optimization prompts that adapt based on Winston AI analysis.

**Key Features**:
- Dynamic enhancement flags (natural_language_patterns, sentence_variability, etc.)
- Evolutionary prompts that improve based on AI detection scores
- Independent from localization logic
- Can be updated by optimization system without affecting culture

**Location**: `components/text/ai_detection/prompt_chain.py`

### 2. Localization Prompt Chain (`components/text/localization/`)

**Purpose**: Provides mandatory cultural and linguistic authenticity based on author country.

**Key Features**:
- Country-specific persona and formatting requirements
- Cultural language patterns and writing styles
- **Never modified by AI detection optimization**
- Preserves authentic cultural characteristics

**Location**: `components/text/localization/prompt_chain.py`

## Prompt Chain Flow

### Stage 1: AI Detection Prompts (FIRST)
```yaml
=== AI DETECTION OPTIMIZATION (DYNAMIC) ===
ENABLED ENHANCEMENTS: natural_language_patterns, sentence_variability
[Dynamic AI detection guidance based on current enhancement flags]
=== END AI DETECTION OPTIMIZATION ===
```

### Stage 2: Localization Prompts (SECOND)
```yaml
=== LOCALIZATION REQUIREMENTS (MANDATORY) ===
PERSONA: Alessandro Moretti
BACKGROUND: Laser-Based Additive Manufacturing
[Cultural and linguistic requirements for Italian author]
=== END LOCALIZATION REQUIREMENTS ===
```

### Stage 3: Base Content Prompts (THIRD)
```yaml
MATERIAL: Aluminum
TASK: Write comprehensive technical article...
[Specific content generation instructions]
```

## Integration Points

### Text Generator (`components/text/generators/fail_fast_generator.py`)

Updated `_construct_prompt` method follows the new architecture:

```python
def _construct_prompt(self, ...):
    # STEP 1: Add AI detection prompts FIRST
    ai_detection_prompt = get_ai_detection_prompt(enhancement_flags)
    
    # STEP 2: Add mandatory localization chain SECOND  
    localization_prompt = get_required_localization_prompt(author_info)
    
    # STEP 3: Build sections in order
    sections = [
        ai_detection_prompt,  # AI detection guidance FIRST
        localization_prompt   # Localization requirements SECOND
    ]
    # ... add base content prompts THIRD
```

### AI Detection Enhancement Flags

The AI detection system can dynamically enable/disable enhancement flags:

```python
from components.text.ai_detection import get_ai_detection_prompt, update_ai_detection_flags

# Update enhancement flags based on Winston AI analysis
enhancement_flags = {
    'natural_language_patterns': True,
    'sentence_variability': True,
    'cultural_adaptation': True,
    'conversational_boost': True
}

# Get AI detection prompt with current flags
ai_prompt = get_ai_detection_prompt(enhancement_flags)
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
- AI detection logic is isolated from localization logic
- Each system has a single, clear responsibility
- Changes to one system don't affect the other

### 2. **Independent Evolution**
- AI detection prompts can evolve based on Winston AI feedback
- Localization prompts remain stable and culturally authentic
- Optimization system only touches AI detection, never localization

### 3. **Clear Chain Order**
- AI detection prompts establish general human-like writing guidelines
- Localization prompts add specific cultural and linguistic requirements
- Base content prompts provide material-specific instructions

### 4. **Maintainability**
- Each prompt chain has clear ownership and responsibility
- Testing can validate each chain independently
- Debugging is simplified with clear separation

## Usage Examples

### Basic Usage
```python
from components.text.ai_detection import get_ai_detection_prompt
from components.text.localization import get_required_localization_prompt

# Get AI detection prompt (basic)
ai_prompt = get_ai_detection_prompt()

# Get localization prompt for Italian author
author_info = {'name': 'Alessandro Moretti', 'country': 'Italy'}
localization_prompt = get_required_localization_prompt(author_info)

# Combine in order: AI Detection → Localization → Content
full_prompt = f"{ai_prompt}\n\n{localization_prompt}\n\n{base_content_prompt}"
```

### Dynamic AI Detection
```python
# Update enhancement flags based on optimization analysis
enhancement_flags = {
    'natural_language_patterns': True,
    'cognitive_variability': True,
    'mid_thought_interruptions': True
}

# Get enhanced AI detection prompt
enhanced_ai_prompt = get_ai_detection_prompt(enhancement_flags)
```

## Testing

The architecture is validated through comprehensive tests:

```bash
# Test the complete prompt chain architecture
python3 tests/test_ai_detection_localization_chain.py
```

**Test Coverage**:
- ✅ AI detection prompt generation (basic and enhanced)
- ✅ Localization prompt generation for all supported countries
- ✅ Combined prompt chain order validation
- ✅ Architecture separation verification

## Files Modified

### New Files Created
- `components/text/ai_detection/prompt_chain.py` - AI detection prompt system
- `components/text/ai_detection/__init__.py` - AI detection module interface
- `tests/test_ai_detection_localization_chain.py` - Architecture validation tests

### Existing Files Updated
- `components/text/generators/fail_fast_generator.py` - Updated prompt construction to use new chain order

### Existing Files Preserved
- `components/text/localization/` - **Unchanged** - localization system remains intact
- `components/text/prompts/ai_detection_core.yaml` - **Unchanged** - existing AI detection prompts preserved

## Future Enhancements

1. **Advanced AI Detection**: More sophisticated enhancement flag combinations
2. **Winston Integration**: Direct integration with Winston AI analysis for real-time flag updates
3. **A/B Testing**: Compare different AI detection prompt strategies
4. **Performance Monitoring**: Track effectiveness of different enhancement flag combinations

This architecture provides a clean, maintainable foundation for both AI detection optimization and cultural localization while keeping these concerns properly separated.
