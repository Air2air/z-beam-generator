# Detection and Improvement Prompt System Architecture

This document outlines the structure and usage of the unified detection and improvement prompt system in the Z-Beam content generation pipeline.

## Architecture Overview

The prompt system has been refactored to use a centralized JSON-based configuration for all prompt types:

1. **Section prompts**: Located in `/sections/sections.json` - Contains all section-specific prompts
2. **Detection prompts**: Located in `/detection/detection_prompts.json` - Contains all AI/human detection prompts
3. **Improvement prompts**: Located in `/detection/improvement_prompts.json` - Contains all content improvement strategy prompts

This unified approach provides several advantages:
- Centralized management of all prompts
- Easier version control and diffing
- Structured metadata for each prompt
- Enhanced modularity and configurability
- Simplified prompt variation selection

## JSON Structure

### Detection Prompts

Each detection prompt has the following fields:
```json
{
  "name": "ai_detection_enhanced",
  "type": "ai",
  "description": "Enhanced AI detection prompt with detailed patterns",
  "is_default": true,
  "prompt": "Analyze this text for AI-generated patterns..."
}
```

- **name**: Unique identifier for the prompt
- **type**: Either "ai" or "human" for detection prompts
- **description**: Brief description of the prompt's purpose or characteristics
- **is_default**: Whether this is the default prompt for its type
- **prompt**: The actual prompt content

### Improvement Prompts

Each improvement prompt has the following fields:
```json
{
  "name": "reduce_ai_patterns",
  "description": "Focused on significantly reducing AI patterns",
  "is_default": false,
  "strategy_type": "ai_reduction",
  "prompt": "Rewrite this content to significantly reduce AI-detection patterns..."
}
```

- **name**: Unique identifier for the prompt
- **description**: Brief description of the prompt's purpose
- **is_default**: Whether this is the default improvement prompt
- **strategy_type**: The improvement strategy category (e.g., "default", "ai_reduction", "human_enhancement", "balanced", "light")
- **prompt**: The actual prompt content

## Prompt Repository

The `EnhancedJsonPromptRepository` class provides a unified interface to access all prompt types from their respective JSON files. It extends the existing `IPromptRepository` interface with additional methods specific to detection and improvement prompts:

```python
# Get a prompt by name and type
prompt = repository.get_prompt("ai_detection_enhanced", "detection")

# Get a detection prompt by detection type
prompt = repository.get_detection_prompt_by_type("ai")

# Get an improvement prompt by strategy type
prompt = repository.get_improvement_prompt_by_strategy("ai_reduction")

# List all prompts of a specific type
prompts = repository.list_prompts("detection")

# Get metadata for all prompts
metadata = repository.get_all_prompt_metadata()
```

## Adaptive Improvement Strategy

The content generation service uses an adaptive strategy for content improvement based on detection scores:

1. **High AI, Low Human**: Use "reduce_ai_patterns" strategy
2. **Low AI, High Human**: Use "increase_human_qualities" strategy
3. **High AI, High Human**: Use "balanced_improvement" strategy
4. **Low AI, Low Human**: Use "light_refinement" strategy

The system tracks strategy performance and can learn from successful improvements over time.

## Utility Tools

Two utility scripts are provided for working with the prompt system:

1. **section_json_util.py**: For viewing and managing section prompts
2. **detection_prompts_util.py**: For viewing and managing detection/improvement prompts

Usage examples:
```bash
# View summary of all detection and improvement prompts
./detection_prompts_util.py summary

# View a specific prompt in detail
./detection_prompts_util.py view detection ai_detection_enhanced --full

# Validate JSON structure
./detection_prompts_util.py validate
```

## Implementation in Detection Service

The Detection Service has been updated to use the new JSON-based prompts. Key changes include:

1. Using `EnhancedJsonPromptRepository` instead of the file-based prompt loading
2. Selecting detection prompts by type and variation
3. Enhanced error handling for missing prompts
4. Improved logging with minimal output

## Implementation in Content Service

The Content Service now uses adaptive improvement strategies based on detection scores:

1. Analyzing detection results to select the appropriate strategy
2. Creating targeted feedback based on specific issues identified
3. Tracking strategy performance for learning
4. Providing strategy-specific guidance in improvement prompts

## Migration Guide

If you still have prompt files in the legacy .txt format, they will be automatically loaded as a fallback when:

1. The prompt is not found in the corresponding JSON file
2. The JSON file itself is missing

To migrate remaining .txt files to the JSON structure:
1. Use `detection_prompts_util.py` to verify the current JSON structure
2. Add the prompt content and metadata to the appropriate JSON file
3. Test with the utility scripts to ensure proper loading

## Future Extensions

Potential future enhancements to the prompt system include:

1. Adding versioning support for prompts
2. Implementing A/B testing for prompt variations
3. Adding machine learning for automatic prompt optimization
4. Creating a web interface for prompt management
5. Supporting remote prompt storage (e.g., in a database)
