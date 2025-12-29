# Generator Prompts Directory

This directory contains **external prompt files** for generators that use AI/LLM generation.

## 📋 Policy: All Prompts Must Be External

**MANDATORY**: All prompt text MUST exist in .txt files, NEVER inline in generator code.

### Why External Prompts?

1. **Version Control**: Track prompt changes in git
2. **Collaboration**: Non-developers can edit prompts
3. **Testing**: Easy A/B testing of different prompts
4. **Consistency**: Ensures all generators follow same pattern
5. **Maintainability**: Update prompts without touching code

### Prompt Format

All prompts should follow the **ultra-short, content-only design**:

```plaintext
Write [what to generate] for {variable}.

CONTEXT: [Brief context statement]

EMPHASIS: [What to focus on]

TECHNICAL DATA:
{facts}

WORD LENGTH: [range]

{voice_instruction}

Generate [field_name]:
```

### Example Prompt Files

Currently, most generators don't use prompts (they compute fields deterministically).

Future generators that may need prompts:
- `author_resolution.txt` - Resolve author references (if using AI)
- `relationship_intensity.txt` - Compute intensity scores (if using AI)
- `section_metadata.txt` - Generate section descriptions (if using AI)

### Non-Prompt Generators

Most generators in Phase 1-3 **don't need prompts** because they compute fields:
- SlugGenerator - Derives from ID
- URLGenerator - Builds from slug + category
- BreadcrumbGenerator - Constructs from URL
- AuthorReferenceGenerator - Looks up from registry

Only generators that use LLM/AI generation need prompt files.

### Adding New Prompts

When creating a new prompt file:

1. **Use ultra-short format** (see examples in `domains/*/prompts/`)
2. **Content-only** (no "You are..." system messages)
3. **Name matches generator**: `{generator_name}.txt`
4. **Load in generator**: `self._load_prompt('generator_name')`

Example:
```python
# In generator code
class MyGenerator(BaseGenerator):
    def generate(self, data):
        # Load external prompt
        prompt = self._load_prompt('my_generator')
        # ... use prompt
```

### Current Status

**Phase 1 Complete**: Infrastructure generators (no prompts needed)
- SlugGenerator ✅
- URLGenerator ✅
- BreadcrumbGenerator ✅

**Future Phases**: May add prompt files for:
- Relationship description generation
- Section metadata generation
- Any AI-assisted field population
