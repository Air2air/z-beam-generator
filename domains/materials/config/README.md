# Materials Domain Configuration

This directory contains configuration files for the materials domain text generation.

## Files

### `prompts.yaml`
Defines metadata for each text component in the materials domain:
- **micro**: Two-paragraph before/after description at 1000x magnification
- **description**: Single-sentence subtitle highlighting primary advantage
- **faq**: Practical Q&A about laser cleaning this material

### Component Structure
Each component defines:
- `title`: Display name
- `description`: What this component generates
- `prompt_file`: Template file in `../prompts/`
- `word_count`: min/max/target word counts
- `structure`: Output structure (raw, before_after, qa_pairs)
- `output_field`: Field name in frontmatter YAML

## Prompts Directory
Actual prompt templates are in `../prompts/`:
- `micro.txt` - Caption generation prompt
- `description.txt` - Material description prompt
- `faq.txt` - FAQ generation prompt

## Usage
The generation pipeline reads these configs to:
1. Load the correct prompt template
2. Apply word count constraints
3. Parse output according to structure type
4. Save to the correct frontmatter field
