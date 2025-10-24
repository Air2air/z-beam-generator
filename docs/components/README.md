# Component Documentation

Documentation for individual system components.

## Available Components

### Caption Component
- Generates before/after captions for laser cleaning materials
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

## Component Guides

- **[OPTIMIZER_CONSOLIDATED_GUIDE.md](OPTIMIZER_CONSOLIDATED_GUIDE.md)** - Optimizer component guide
- **[SMART_OPTIMIZER_COMPREHENSIVE_GUIDE.md](SMART_OPTIMIZER_COMPREHENSIVE_GUIDE.md)** - Smart optimizer details
- **[SMART_OPTIMIZER_ARCHITECTURE.md](SMART_OPTIMIZER_ARCHITECTURE.md)** - Optimizer architecture
- **[AI_DETECTION_LOCALIZATION_CHAIN_ARCHITECTURE.md](AI_DETECTION_LOCALIZATION_CHAIN_ARCHITECTURE.md)** - AI detection chain

## Creating New Components

See: [development/new_component_guide.md](../development/new_component_guide.md)

## Component Architecture

```
components/
├── caption/          # Before/after captions
├── frontmatter/      # YAML frontmatter
├── text/             # Text content generation
└── [future]/         # FAQ, tags, etc.
```

## Quick Commands

```bash
# Generate with specific component
python3 run.py --material "Steel" --component caption

# List available components
python3 run.py --list-components
```

## See Also

- [Architecture Documentation](../architecture/COMPONENT_SYSTEM.md) - Component system architecture
- [Operations Documentation](../operations/) - Running components
