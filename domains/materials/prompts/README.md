# Materials Text Generation Prompts

This folder contains prompts and templates for materials text content generation (descriptions, micros, FAQs, etc.).

## Structure

```
domains/materials/prompts/
├── material_description.txt         # Main material description prompt (30-80 words)
├── micro.txt                        # Microscopic view caption prompt (80-120 words)
└── faq.txt                          # FAQ generation prompt (multiple Q&A pairs)
```

## Component Prompts

Each component type has its own prompt template with specific requirements:

- **material_description.txt** - Comprehensive technical description emphasizing unique properties
- **micro.txt** - Microscopic view captions (before/after laser cleaning)
- **faq.txt** - Frequently asked questions with practical customer concerns

## Shared Templates

System-level and evaluation templates are shared across all domains:

- **System Templates**: `shared/text/templates/system/` - Base prompts and humanness layer
- **Evaluation Templates**: `shared/text/templates/evaluation/` - Quality assessment criteria

## Usage

These templates are used by the universal text processing pipeline (`generation/core/evaluated_generator.py`):

1. **Component Templates** - Domain-specific content requirements (this directory)
2. **System Templates** - Shared base instructions and humanness layer
3. **Evaluation Templates** - Shared quality assessment criteria

## Author Voices

Author voice definitions are in `shared/voice/profiles/`:
- `taiwan.yaml` - Yi-Chun Lin (Mandarin EFL)
- `italy.yaml` - Alessandro Moretti (Italian EFL) 
- `indonesia.yaml` - Ikmanda Roswati (Bahasa EFL)
- `united-states.yaml` - Todd Dunning (American native)

## Image Generation

Image generation prompts are separate and located at:
- `domains/materials/image/prompts/` - Image-specific prompts (unchanged)
