# Z-Beam Generator

A modular Python application for generating high-quality laser cleaning articles with AI-powered content generation and style optimization.

## Overview

The Z-Beam Generator creates technical articles about laser cleaning for various materials, with structured metadata and optimized writing style. It uses a three-phase pipeline: Generation, Optimization, and Orchestration.

## Architecture

### Modular Design
- **ContentGenerator**: Creates text sections using configured prompts
- **MetadataGenerator**: Generates structured metadata without AI prompts
- **Optimizer**: Applies writing style improvements (iterative or writing samples)
- **ArticleOrchestrator**: Assembles final markdown output
- **APIClient**: Handles multiple AI providers (OpenAI, XAI, Gemini, DeepSeek)

### Three-Phase Pipeline

1. **GENERATION PHASE**
   - Loads section prompts from `sections.json`
   - Generates text sections with word limit enforcement
   - Creates structured metadata using material properties and author data
   - No AI prompts for metadata - ensures consistency

2. **OPTIMIZATION PHASE** 
   - Applies selected optimization method to improve writing style
   - **Writing Samples**: Matches author's writing style using provided samples
   - **Iterative**: Refines content through multiple AI iterations

3. **ORCHESTRATION PHASE**
   - Assembles final markdown article with YAML frontmatter
   - Combines optimized sections with metadata
   - Formats according to article template

## Configuration

### User Settings (run.py)
```python
context = {
    "material": "titanium",     # Material to generate article about
    "author_id": 2,            # Author ID from authors.json
    "article_type": "material"  # Type of article
}
```

### API Configuration
```python
config = {
    "provider": "OPENAI",      # OPENAI, XAI, GEMINI, DEEPSEEK
    "model": "gpt-4o",         # Model for selected provider
    "temperature": 0.3,        # Lower = more consistent output
    "optimization_method": "writing_samples",  # or "iterative"
    
    # Word limits
    "max_section_words": 75,
    "target_section_words": 75,
    "max_total_words": 800,
}
```

## File Structure

```
z-beam-generator/
├── generator.py              # Main orchestrator
├── run.py                   # Configuration and context
├── content_generator.py     # Text section generation
├── metadata/
│   └── metadata_generator.py # Structured metadata generation
├── optimizers/
│   ├── iterative_optimizer.py
│   └── writing_samples_optimizer.py
├── orchestrator.py          # Final assembly
├── api_client.py           # Multi-provider API client
├── prompts/
│   ├── text/
│   │   └── sections.json    # Section prompts and configuration
│   ├── authors/
│   │   └── authors.json     # Author data and writing samples
│   └── optimizations/
│       └── writing_samples/
│           └── rewrite_prompt.md
└── output/                  # Generated articles
```

## Key Features

### Structured Metadata Generation
- Material properties generated via AI prompting
- Author data loaded from `authors.json`
- High-quality tag generation using material properties
- No hardcoded values - everything from configuration

### Writing Style Optimization
- **Writing Samples Method**: Matches author's natural writing style
- **Iterative Method**: Refines content through multiple passes
- Configurable optimization parameters
- AI detection score monitoring

### Multi-Provider Support
- OpenAI (GPT-4, GPT-4 Turbo, GPT-3.5)
- XAI (Grok models)
- Google Gemini (1.5 Pro, Flash)
- DeepSeek (Chat, Coder, Reasoner)

### Word Limit Enforcement
- Configurable word limits per section
- Critical instruction injection for AI models
- Validation and truncation if needed

## Usage

### Basic Usage
```bash
python generator.py
```

### Custom Configuration
1. Edit `run.py` to set material, author, and API settings
2. Update prompts in `prompts/text/sections.json`
3. Add author data to `prompts/authors/authors.json`
4. Run the generator

### Output
Generated articles are saved as:
- Format: `{material}_laser_cleaning.md`
- Location: `output/` directory
- Example: `titanium_laser_cleaning.md`

## Article Structure

### YAML Frontmatter
```yaml
---
title: "Laser Cleaning titanium"
articleType: "material"
nameShort: "titanium"
description: "Explore how laser cleaning removes contaminants..."
authorId: "2"
authorName: "Mario Jordan"
authorSlug: "mario-jordan"
atomicNumber: "22"
chemicalSymbol: "Ti"
materialClass: "Transition Metal"
applications: ["Aerospace components", "Medical implants"]
laserCleaningParameters: {...}
performanceMetrics: {...}
tags: ["Laser Cleaning", "Aerospace", "Construction"]
---
```

### Content Sections
- Introduction
- Comparison with Traditional Methods
- Contaminants Removed
- Substrate Applications
- Additional configured sections

## Configuration Files

### sections.json
Defines article sections and their prompts:
```json
{
  "sections": [
    {
      "name": "introduction",
      "title": "Introduction", 
      "prompt": "Write an introduction about laser cleaning {material}..."
    }
  ]
}
```

### authors.json
Author data and writing samples:
```json
[
  {
    "id": 2,
    "name": "Mario Jordan",
    "slug": "mario-jordan",
    "title": "Senior Laser Applications Engineer",
    "bio": "Mario Jordan is a senior laser applications engineer...",
    "country": "Italy",
    "writing_sample": "Sample text in author's natural style..."
  }
]
```

## Environment Variables

Set your API keys:
```bash
export OPENAI_API_KEY="your-openai-key"
export XAI_API_KEY="your-xai-key"
export GEMINI_API_KEY="your-gemini-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

## Requirements

- Python 3.8+
- openai
- requests
- pathlib
- json
- logging

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables for API keys
4. Configure `run.py` with your settings
5. Run: `python generator.py`

## Optimization Methods

### Writing Samples
- Uses author's writing samples to match style
- Applies rewrite prompt to make content sound like the author
- Best for maintaining consistent author voice

### Iterative
- Refines content through multiple AI passes
- Improves clarity, technical accuracy, and flow
- Best for general content improvement

## Logging

Comprehensive logging shows:
- Configuration loading
- API calls and responses
- Section generation progress
- Optimization steps
- Final assembly process

Logs are saved to `logs/` directory with timestamps.

## Error Handling

- **Fail Fast**: Invalid configuration stops execution immediately
- **Graceful Degradation**: Missing data uses reasonable defaults
- **Detailed Logging**: All errors logged with context
- **Validation**: Input validation throughout pipeline

## Customization

### Adding New Materials
1. Update material properties in `MetadataGenerator`
2. Add material-specific prompts if needed
3. Test generation with new material

### Adding New Sections
1. Add section configuration to `sections.json`
2. Create appropriate prompts
3. Update orchestrator if needed

### Adding New Authors
1. Add author data to `authors.json`
2. Include writing samples for style matching
3. Test optimization with new author

## Contributing

1. Follow modular architecture principles
2. Maintain separation of concerns
3. Add comprehensive logging
4. Include error handling
5. Update documentation

## License

[Your License Here]