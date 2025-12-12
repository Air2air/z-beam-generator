# Documentation Archive

This directory contains archived documentation that is no longer actively maintained but preserved for historical reference.

## Archive Organization

Archives are organized by date and reason for archival:
- `YYYY-MM-reason/` - Contains documentation archived on a specific date for a specific reason

## Current Archives

### 2025-12-pre-consolidation/

**Archived**: December 11, 2025  
**Reason**: Text generation pipeline consolidation

Documentation archived during the December 2025 text generation pipeline consolidation. These files describe architecture and systems that have been replaced by newer, unified implementations.

#### optimizer/ (3 files)

**Date**: Originally created September 15, 2025  
**Archived**: December 11, 2025  
**Reason**: Superseded by unified QualityAnalyzer system

Files archived:
1. `OPTIMIZER_CONSOLIDATED_GUIDE.md` (467 lines) - Described Winston.ai composite scoring with manual aggregation
2. `SMART_OPTIMIZER_COMPREHENSIVE_GUIDE.md` (275 lines) - Documented 95% code reduction (17,794→200 lines) in old optimizer architecture
3. `SMART_OPTIMIZER_ARCHITECTURE.md` (178 lines) - Described 67-file to 3-file consolidation approach

**What replaced them**: 
- `docs/02-architecture/TEXT_GENERATION_GUIDE.md` - Unified guide with QualityAnalyzer system
- `shared/voice/quality_analyzer.py` - Single interface replacing dual AIDetector + VoicePostProcessor systems
- Consolidation reduced quality analysis from 2,172 lines to 479 lines (-78%)

**Why archived**: Architecture described in these documents no longer matches current implementation. The Winston.ai composite scoring approach was replaced by a unified QualityAnalyzer that automatically handles AI patterns, voice authenticity, and structural quality through a single interface.

## Archive Policy

### When to Archive Documentation

Documentation should be archived when:
1. **Architecture changed** - The system/approach described no longer exists
2. **Superseded** - Newer documentation covers the same topic more accurately
3. **Outdated** - Information is more than 6 months old and describes deprecated systems
4. **Consolidation** - Multiple docs merged into a single comprehensive guide

### When NOT to Archive

Do NOT archive documentation that:
1. **Active reference** - Still being used by developers or users
2. **Historical context** - Provides valuable context for current architecture decisions
3. **Transition period** - Marked as deprecated but still guiding users to new docs (keep 30 days)
4. **Unique information** - Contains information not captured elsewhere

### Retention Policy

Archived documentation:
- **Retained indefinitely** for historical reference
- **Organized by date** for easy navigation
- **Documented with context** explaining what replaced it
- **Git tracked** to maintain full history

### Accessing Archived Documentation

If you need information from archived documentation:
1. Check the archive README for what replaced it
2. Review the current documentation first (likely more accurate)
3. Use archived docs for historical context only
4. Consider that archived implementation details may not match current code

## Archive History

| Date | Type | Files | Reason | Total Lines |
|------|------|-------|--------|-------------|
| 2025-12-11 | Optimizer | 3 | QualityAnalyzer consolidation | ~920 lines |

**Total archived documentation**: 3 files, ~920 lines
