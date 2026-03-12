# Component Documentation

Documentation for individual system components.

## Available Components

### Micro Component
- Generates before/after micros for laser cleaning materials
- Multi-author voice system (Taiwan, Italy, Indonesia, USA)
- Quality scoring and AI detection evasion

### Frontmatter Component
- **[FRONTMATTER_GENERATOR.md](../frontmatter/FRONTMATTER_GENERATOR.md)** - Frontmatter generation
- **[FRONTMATTER_PIPELINE_GUARANTEE.md](../frontmatter/FRONTMATTER_PIPELINE_GUARANTEE.md)** - Pipeline guarantees

### Text Component
- **[text/README.md](text/README.md)** - Complete text generation documentation (14 KB)
- Multi-layered prompt architecture
- Author personas with linguistic nuances

### Voice System
See [voice/README.md](../../voice/README.md) for complete voice system documentation

### Quality Analysis System
- **[../02-architecture/TEXT_GENERATION_GUIDE.md](../02-architecture/TEXT_GENERATION_GUIDE.md)** - Unified quality analysis with QualityAnalyzer
- **[../08-development/ENRICHMENT_ARCHITECTURE_SUMMARY.md](../08-development/ENRICHMENT_ARCHITECTURE_SUMMARY.md)** - Current enrichment and optimizer architecture notes

## Component Guides

- **[AI_DETECTION_LOCALIZATION_CHAIN_ARCHITECTURE.md](AI_DETECTION_LOCALIZATION_CHAIN_ARCHITECTURE.md)** - AI detection chain

## Creating New Components

See: [../08-development/new_component_guide.md](../08-development/new_component_guide.md)

## Component Architecture

```
components/
├── micro/          # Before/after micros
├── frontmatter/      # YAML frontmatter
├── text/             # Text content generation
└── [future]/         # FAQ, tags, etc.
```

## Quick Commands

```bash
# Generate with specific component
python3 run.py --material "Steel" --component micro

# List available components
python3 run.py --list-components
```

## See Also

- [Architecture Documentation](../02-architecture/) - Component system architecture
- [Operations Documentation](../04-operations/) - Running components
