# Detection and Improvement Prompts

This directory contains JSON files for detection and improvement prompts used in the Z-Beam content generation system.

## File Structure

- `detection_prompts.json`: Contains all AI and human detection prompts
- `improvement_prompts.json`: Contains all content improvement strategy prompts

## Usage

These files are loaded by the `EnhancedJsonPromptRepository` class in the application. See the implementation in:
`/generator/infrastructure/storage/enhanced_json_prompt_repository.py`

## Management

Use the utility script to view and validate the prompt files:
```bash
./detection_prompts_util.py summary
./detection_prompts_util.py view detection ai_detection_enhanced
./detection_prompts_util.py validate
```

## Migration

All legacy .txt prompt files have been migrated to these JSON structures. The migration provides:
1. Centralized management of prompts
2. Structured metadata for each prompt type
3. Consistent interface for accessing different prompt types
4. Better version control and maintenance

For the comprehensive documentation of the prompt system, see:
`/docs/PROMPT_JSON_ARCHITECTURE.md`
