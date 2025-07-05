# Section Prompts

This directory contains the centralized JSON file for all section prompts used in the Z-Beam content generation system.

## File Structure

- `sections.json`: Contains all section prompts and their metadata

## Section Structure

Each section in the JSON file has the following structure:
```json
{
  "name": "section_name",
  "title": "Section Title",
  "ai_detect": true,
  "order": 1,
  "section_type": "TEXT",
  "prompt": "The actual prompt content..."
}
```

- **name**: Unique identifier for the section
- **title**: Display title for the section
- **ai_detect**: Whether AI detection should be run on this section
- **order**: The display order of the section
- **section_type**: Type of section (TEXT, CHART, TABLE, METADATA, SYSTEM)
- **prompt**: The actual prompt content used for generation

## Usage

These files are loaded by the `EnhancedJsonPromptRepository` class in the application. See the implementation in:
`/generator/infrastructure/storage/enhanced_json_prompt_repository.py`

## Management

Use the utility script to view section prompts:
```bash
./section_json_util.py
```

For the comprehensive documentation of the prompt system, see:
`/docs/PROMPT_JSON_ARCHITECTURE.md`
