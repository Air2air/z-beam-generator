# Component Prompts

**Task specifications defining WHAT to generate for each content type.**

---

## 📋 Purpose

Component prompts are **the single source of truth** for content generation instructions. They define:
- Task objectives (what the content should accomplish)
- Content requirements (what to include)
- Structural guidelines (how to organize)
- Style expectations (how to communicate)

**Key Principle**: All content instructions live HERE, not in code or config files.

---

## 📁 Available Components

| Component | Target Length | Purpose | Key Characteristics |
|-----------|---------------|---------|---------------------|
| **subtitle.txt** | 15 words | Brief material introduction | No period at end, focus on unique traits |
| **caption.txt** | 25 words | Microscopy image description | Include 1-2 measurements, technical precision |
| **description.txt** | 150 words | Comprehensive overview | Multiple paragraphs, balanced detail |
| **faq.txt** | 100 words | Answer common questions | Conversational tone, use "you" |
| **troubleshooter.txt** | 120 words | Problem-solving guide | Numbered steps, methodical approach |

**Note**: Word counts defined in `processing/config.yaml`, content instructions defined here.

---

## 📝 File Format

Each component prompt follows this structure:

```
[TASK OBJECTIVE]
Brief description of what this component should achieve.

[CONTENT REQUIREMENTS]
- Specific elements that must be included
- Data points to emphasize
- Technical details to incorporate

[STRUCTURAL GUIDELINES]
- How to organize the content
- Paragraph/sentence structure
- Formatting requirements

[STYLE EXPECTATIONS]
- Writing tone (technical, conversational, etc.)
- Vocabulary level
- Communication approach

TEMPLATE VARIABLES:
{length} - Target word count (injected from config)
{topic} - Material name (e.g., "Aluminum")
{facts} - Material properties and data (from Materials.yaml)
{voice_instructions} - Author voice patterns (from personas/)
{anti_ai_rules} - AI avoidance rules (from rules/)
```

---

## 🔍 Example: subtitle.txt

```
Generate a {length}-word subtitle for {topic} that serves as a brief, 
engaging introduction to the material.

CONTENT REQUIREMENTS:
- Focus on 1-2 unique characteristics that define this material
- Include a key application or benefit
- Use specific, concrete details (not generic descriptions)

STRUCTURAL GUIDELINES:
- Single sentence, no period at the end
- Natural flow without formulaic patterns
- Avoid "X does Y while Z" structures

STYLE EXPECTATIONS:
- Technical but accessible
- Specific measurements or properties preferred
- Avoid marketing language or superlatives

FACTS: {facts}

{voice_instructions}

{anti_ai_rules}
```

---

## ➕ Adding New Components

To create a new component type:

1. **Create .txt file** in `prompts/components/`:
   ```bash
   touch prompts/components/new_component.txt
   ```

2. **Define task specification** using the format above:
   - Task objective (what it should accomplish)
   - Content requirements (what to include)
   - Structural guidelines (how to organize)
   - Style expectations (how to write)

3. **Add word count** to `processing/config.yaml`:
   ```yaml
   component_lengths:
     new_component: 50  # target word count
   ```

4. **System automatically discovers** the new component:
   - ComponentRegistry scans `prompts/components/*.txt`
   - No code changes needed
   - Available immediately via `--component new_component`

---

## 🔧 Template Variables

Variables automatically injected by `processing/generation/prompt_builder.py`:

| Variable | Source | Description |
|----------|--------|-------------|
| `{length}` | `processing/config.yaml` | Target word count (e.g., "15") |
| `{topic}` | Runtime parameter | Material name (e.g., "Aluminum") |
| `{facts}` | `data/materials/Materials.yaml` | Material properties and data |
| `{voice_instructions}` | `prompts/personas/*.yaml` | Author voice patterns and traits |
| `{anti_ai_rules}` | `prompts/rules/anti_ai_rules.txt` | AI detection avoidance rules |

**Note**: Variables are injected at generation time, not stored in prompt files.

---

## 🚫 What NOT to Include

**NEVER put these in component prompts**:
- ❌ Word count numbers (use `{length}` variable)
- ❌ API parameters (temperature, penalties, etc.)
- ❌ Code logic or conditional statements
- ❌ Technical implementation details
- ❌ Hardcoded material properties

**WHY**: These belong in code/config, not content instructions. Component prompts define WHAT to write, not HOW the system works.

---

## 🎯 Best Practices

1. **Be Specific**: Provide concrete examples of what you want
   - ❌ "Include relevant details"
   - ✅ "Include 1-2 specific measurements (e.g., density, melting point)"

2. **Focus on Content**: Describe the content, not the writing process
   - ❌ "Make sure to vary sentence structure"
   - ✅ "Mix short, direct statements with longer explanatory sentences"

3. **Avoid Redundancy**: Don't repeat rules from `prompts/rules/`
   - Anti-AI rules already injected
   - Grammar rules already applied
   - Voice patterns already added

4. **Use Natural Language**: Write prompts as instructions, not templates
   - ❌ "{{material}} is a {{property}} that {{application}}"
   - ✅ "Describe the material's defining property and primary application"

5. **Test Changes**: Generate content after editing to verify results
   ```bash
   python3 run.py --material "Aluminum" --component subtitle
   ```

---

## 🔗 Related Documentation

- **Parent**: `prompts/README.md` - Overview of entire prompt system
- **Rules**: `prompts/rules/README.md` - Universal constraints (what to avoid)
- **Personas**: `prompts/personas/README.md` - Author voices (how to write)
- **Config**: `processing/config.yaml` - Component lengths and system settings
- **Code**: `processing/generation/prompt_builder.py` - Prompt assembly logic

---

## 📊 Quality Validation

Generated content is validated against:
1. **Word Count**: Within ±10% of target length
2. **AI Detection**: Score < 0.10 (ensemble method)
3. **Grammar**: Passes linguistic validation
4. **Voice**: Matches assigned author's patterns

See `processing/validation/` for validation logic.

---

## 🚀 Quick Commands

**Test a component prompt**:
```bash
python3 run.py --material "Aluminum" --component subtitle
```

**View available components**:
```bash
ls prompts/components/*.txt
```

**Check component discovery**:
```bash
python3 -c "from processing.generation.component_specs import ComponentRegistry; print(ComponentRegistry.list_types())"
```

**Regenerate all content for a component**:
```bash
python3 scripts/processing/regenerate_subtitles_with_processing.py
```
