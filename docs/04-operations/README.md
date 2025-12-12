# Operations & Running the System

Documentation for running, operating, and maintaining the Z-Beam Generator.

## Content Generation

- **[CONTENT_GENERATION.md](CONTENT_GENERATION.md)** - Content generation overview
- **[ADVANCED_CONTENT_GENERATION_STRATEGY.md](ADVANCED_CONTENT_GENERATION_STRATEGY.md)** - Advanced generation strategies

## Batch Operations

- **[BATCH_OPERATIONS.md](BATCH_OPERATIONS.md)** - Batch processing documentation
- **[CAPTION_TAGS_PIPELINE_INTEGRATION.md](CAPTION_TAGS_PIPELINE_INTEGRATION.md)** - Pipeline integration
- **[PIPELINE_INTEGRATION_BENEFITS.md](PIPELINE_INTEGRATION_BENEFITS.md)** - Pipeline benefits

## Performance & Caching

- **[CACHING_QUICK_START.md](CACHING_QUICK_START.md)** - API caching configuration

## Deployment & Maintenance

- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist
- **[MAINTENANCE.md](MAINTENANCE.md)** - System maintenance guide (41 KB)

## Quick Commands

```bash
# Generate single material
python3 run.py --material "MaterialName"

# Batch generate all materials
python3 scripts/batch/batch_generate_micros.py

# Generate with specific component
python3 run.py --material "Steel" --component micro

# Check generation status
python3 run.py --status
```

## Time Estimates

- Single material: ~9 seconds (7s API + 2s processing)
- All 132 materials: ~25 minutes (conservative)
- Batch mode recommended for multiple materials

## See Also

- [Setup Documentation](../setup/) - Initial configuration
- [Component Documentation](../components/) - Component-specific details
- [Deployment Documentation](../deployment/) - Deployment monitoring
