# Data Documentation

All documentation related to data architecture, storage, validation, and completion.

## Core Policies

- **[DATA_STORAGE_POLICY.md](DATA_STORAGE_POLICY.md)** - Single source of truth policy for Materials.yaml and Categories.yaml
- **[ZERO_NULL_POLICY.md](ZERO_NULL_POLICY.md)** - Zero null policy and AI research methodology

## Architecture

- **[DATA_VALIDATION_STRATEGY.md](DATA_VALIDATION_STRATEGY.md)** - Validation architecture and quality gates
- **[DATA_SYSTEM_COMPLETE_GUIDE.md](DATA_SYSTEM_COMPLETE_GUIDE.md)** - Complete data system overview

## Completion & Research

- **[DATA_COMPLETION_ACTION_PLAN.md](DATA_COMPLETION_ACTION_PLAN.md)** - Plan to achieve 100% data coverage
- **[DATA_COMPLETENESS_COMPLETE_GUIDE.md](DATA_COMPLETENESS_COMPLETE_GUIDE.md)** - Data completeness guide
- **[RUN_PY_DATA_FLAG_GUIDE.md](RUN_PY_DATA_FLAG_GUIDE.md)** - CLI commands for data operations
- **[PROPERTY_SYSTEM_COMPLETE.md](PROPERTY_SYSTEM_COMPLETE.md)** - Property system documentation

## Quick Commands

```bash
# Data completeness report
python3 run.py --data-completeness-report

# Identify data gaps
python3 run.py --data-gaps

# Enforce completeness (strict mode)
python3 run.py --enforce-completeness
```

## See Also

- [Architecture Documentation](../architecture/) - System architecture including data flow
- [Validation Documentation](../validation/) - Validation methodology
