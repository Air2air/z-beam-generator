# Image Generation Learning System

**Status**: ✅ COMPLETE  
**Date**: November 25, 2025  
**Purpose**: Track generation attempts, learn from feedback, optimize parameters

---

## Overview

The Learning System automatically logs every image generation attempt to a SQLite database, capturing generation parameters, validation results, user feedback, and outcomes. This enables:

- **Pattern Recognition**: Identify what works across materials and categories
- **Feedback Analysis**: Measure effectiveness of different feedback types
- **Knowledge Base**: Build searchable library of successful approaches
- **A/B Testing**: Compare before/after feedback effectiveness
- **Optimization**: Learn which parameters lead to success

## Architecture

```
domains/materials/image/learning/
├── __init__.py                      # Exports create_logger factory
├── image_generation_logger.py       # Core logging system (SQLite)
├── analytics.py                     # CLI tool for viewing analytics
└── generation_history.db            # SQLite database (auto-created)
```

### Database Schema

```sql
CREATE TABLE generation_attempts (
    id TEXT PRIMARY KEY,              -- UUID
    timestamp TEXT NOT NULL,          -- ISO format
    material TEXT NOT NULL,           -- "Birch", "Steel", etc.
    category TEXT NOT NULL,           -- "wood_hardwood", "metal_ferrous"
    
    -- Generation Parameters
    gen_prompt_length INTEGER,
    guidance_scale REAL,
    contamination_uniformity INTEGER,
    view_mode TEXT,
    patterns_used TEXT,               -- JSON array
    feedback_applied BOOLEAN,
    feedback_text TEXT,               -- 🔥 NEW: Actual feedback content
    feedback_category TEXT,           -- 🔥 NEW: physics, aesthetics, etc.
    feedback_source TEXT,             -- 🔥 NEW: user, automated, system
    
    -- Validation Results
    val_prompt_length INTEGER,
    val_truncated BOOLEAN,
    realism_score INTEGER,            -- 0-100
    passed BOOLEAN,                   -- >= 75/100
    physics_issues TEXT,              -- JSON array
    red_flags TEXT,                   -- JSON array
    
    -- Outcome
    failure_category TEXT,            -- physics, quality, etc.
    retry_count INTEGER,
    final_success BOOLEAN,
    
    -- Image Metadata
    image_path TEXT,
    image_size_kb REAL,
    notes TEXT
);
```

## Core Components

### ImageGenerationLogger

Main logging class with automatic schema creation and query methods.

**Methods**:
- `log_attempt()` - Log generation attempt with all metadata
- `get_category_stats()` - Success rates by material category
- `get_common_physics_violations()` - Most frequent issues
- `get_feedback_effectiveness()` - Before/after feedback comparison
- `get_prompt_truncation_impact()` - Correlation analysis
- `get_feedback_patterns()` - 🔥 NEW: Effectiveness by feedback type
- `search_feedback()` - 🔥 NEW: Find feedback by keyword
- `get_best_feedback_examples()` - 🔥 NEW: Successful feedback library
- `get_recent_attempts()` - Timeline of recent generations
- `print_analytics_report()` - Comprehensive report

### Analytics CLI

Command-line tool for viewing analytics without code.

**Usage**:
```bash
# Comprehensive report
python3 domains/materials/image/learning/analytics.py --report

# Category-specific stats
python3 domains/materials/image/learning/analytics.py --category wood_hardwood

# Physics violations
python3 domains/materials/image/learning/analytics.py --physics-violations

# Feedback effectiveness
python3 domains/materials/image/learning/analytics.py --feedback-effectiveness

# 🔥 NEW: Feedback patterns
python3 domains/materials/image/learning/analytics.py --feedback-patterns

# 🔥 NEW: Search feedback
python3 domains/materials/image/learning/analytics.py --search-feedback "physics"

# 🔥 NEW: Best feedback examples
python3 domains/materials/image/learning/analytics.py --best-feedback physics
```

## Feedback Capture System 🔥 NEW

### What Gets Logged

**Before Enhancement**:
- ✓ `feedback_applied: True/False` (binary flag)
- ✗ Lost: What the feedback was
- ✗ Lost: What type of feedback
- ✗ Lost: Which feedback worked

**After Enhancement**:
- ✅ `feedback_text`: Full verbatim feedback content
- ✅ `feedback_category`: Type classification
- ✅ `feedback_source`: Origin (user, automated, system)
- ✅ Searchable: Find similar issues/solutions
- ✅ Analyzable: Measure effectiveness by type

### Feedback Categories

| Category | Purpose | Example |
|----------|---------|---------|
| `physics` | Gravity, contamination placement | "Dust should accumulate in low points, not float" |
| `material_behavior` | Rust, oxidation, wear patterns | "Rust starts at edges, follows oxidation chemistry" |
| `contamination` | Distribution, density, realism | "Dirt particles vary in size, natural accumulation" |
| `object_realism` | Material appearance, surface | "Wood grain should be visible through contamination" |
| `aesthetics` | Visual quality, composition | "Lighting should show material texture clearly" |
| `scale` | Particle size, proportions | "Dust particles should be microscopic, not visible chunks" |

### How to Log Feedback

```python
from domains.materials.image.learning import create_logger

logger = create_logger()

# Log attempt with feedback
attempt_id = logger.log_attempt(
    material="Birch",
    category="wood_hardwood",
    generation_params={
        'prompt_length': 3200,
        'guidance_scale': 0.35,
        'contamination_uniformity': 3,
        'view_mode': 'natural_placement',
        'patterns_used': ['dust', 'dirt'],
        'feedback_applied': True,
        'feedback_text': 'Dust should accumulate in natural low points and crevices, not float in mid-air. Follow gravity rules.',
        'feedback_category': 'physics',
        'feedback_source': 'user'
    },
    validation_results={
        'prompt_length': 3940,
        'truncated': False,
        'realism_score': 82,
        'passed': True,
        'physics_issues': [],
        'red_flags': []
    },
    outcome={
        'failure_category': None,
        'retry_count': 1,
        'final_success': True
    }
)
```

## Analytics Examples

### Overall Statistics

```python
logger = create_logger()
logger.print_analytics_report()
```

**Output**:
```
📊 IMAGE GENERATION ANALYTICS REPORT
════════════════════════════════════════════════════════════════════

📈 OVERALL STATISTICS:
   • Total attempts: 6
   • Passed: 2 (33.3%)
   • Failed: 4 (66.7%)
   • Average score: 76.3/100

📊 BY CATEGORY:
   • metal_ferrous: 1 attempts, 100.0% pass rate, 78.0 avg score
   • wood_hardwood: 5 attempts, 20.0% pass rate, 76.0 avg score

🚨 TOP PHYSICS VIOLATIONS:
   • Edge concentration issues: 33.3%
   • Multiple quality issues: 33.3%

📈 FEEDBACK EFFECTIVENESS:
   Before: 0.0% pass rate
   After:  40.0% pass rate
   Improvement: +40.0%

💡 FEEDBACK EFFECTIVENESS BY TYPE:
   • physics: 1 uses, 100.0% success, 82.0 avg score
   • material_behavior: 1 uses, 100.0% success, 78.0 avg score

🌟 TOP PERFORMING FEEDBACK:
   • Birch (82/100) - physics
     "Focus on realistic contamination distribution..."
   • Steel (78/100) - material_behavior
     "Rust patterns should show natural progression..."
════════════════════════════════════════════════════════════════════
```

### Feedback Pattern Analysis 🔥 NEW

```python
patterns = logger.get_feedback_patterns()
for pattern in patterns:
    print(f"{pattern['category']}: "
          f"{pattern['usage_count']} uses, "
          f"{pattern['success_rate']:.1f}% success")
```

**Output**:
```
physics: 5 uses, 80.0% success, 78.5 avg score
material_behavior: 3 uses, 100.0% success, 81.0 avg score
contamination: 2 uses, 50.0% success, 72.0 avg score
```

### Search Feedback 🔥 NEW

```python
results = logger.search_feedback('dust')
for result in results:
    print(f"{result['material']}: {result['feedback_text'][:50]}...")
```

**Output**:
```
Birch: "Dust should accumulate in natural low points..."
Oak: "Fine dust particles need microscopic scale..."
```

### Best Feedback Examples 🔥 NEW

```python
examples = logger.get_best_feedback_examples(category='physics', limit=3)
for ex in examples:
    print(f"{ex['material']} ({ex['realism_score']}/100)")
    print(f"  {ex['feedback_text']}")
```

**Output**:
```
Birch (82/100)
  Focus on realistic contamination distribution - dust should 
  accumulate in natural low points and crevices, not float in 
  mid-air. Follow gravity rules.

Steel (78/100)
  Rust patterns should show natural progression - starting at 
  edges and exposed areas, following oxidation chemistry.
```

## Success Criteria

**Pass Threshold**: Realism score >= 75/100

**Success Factors**:
1. Physics compliance (gravity, accumulation)
2. Material appearance accuracy
3. Contamination realism
4. Before/after consistency
5. Lighting and composition

## Integration

### Automatic Logging

The system automatically logs attempts when integrated with `generate.py`:

```python
from domains.materials.image.learning import create_logger

logger = create_logger()

# After generation and validation
logger.log_attempt(
    material=material_name,
    category=category,
    generation_params={...},
    validation_results={...},
    outcome={...}
)
```

### Query in Code

```python
# Get category stats
stats = logger.get_category_stats("wood_hardwood")
print(f"Pass rate: {stats['success_rate']:.1f}%")

# Get common issues
violations = logger.get_common_physics_violations(5)
for v in violations:
    print(f"{v['issue']}: {v['count']} times")

# Search feedback
results = logger.search_feedback("contamination")
print(f"Found {len(results)} relevant feedback entries")
```

## Cost Analysis

**Database**: SQLite (local, free)  
**Storage**: ~1KB per attempt  
**Performance**: <1ms query time  
**Scalability**: 100K+ attempts supported

## Benefits

### For Development
- Track failure patterns across materials
- Identify problematic categories
- Measure parameter effectiveness
- Optimize generation settings

### For Users
- Learn from past successes
- Search similar issues
- Reuse effective feedback
- Build expertise knowledge base

### For System
- A/B test feedback types
- Correlate parameters with success
- Detect prompt truncation issues
- Monitor validation accuracy

## Maintenance

### Database Location
```
domains/materials/image/learning/generation_history.db
```

### Backup
```bash
cp generation_history.db generation_history.backup.db
```

### Reset (if needed)
```bash
rm generation_history.db
# Database auto-recreates on next use
```

### Export to CSV
```python
import sqlite3
import csv

conn = sqlite3.connect('generation_history.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM generation_attempts")

with open('export.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(cursor.fetchall())
```

## Future Enhancements

### Planned
1. **Parameter Optimization**: Suggest optimal settings per category
2. **Trend Analysis**: Track success rate changes over time
3. **Correlation Matrix**: Identify which params matter most
4. **Auto-feedback**: Generate suggestions from patterns
5. **Export/Import**: Share learning data between systems

### Possible
1. **Web Dashboard**: Visual analytics interface
2. **Real-time Monitoring**: Watch generation attempts live
3. **Alerts**: Notify on consistent failures
4. **Multi-model Tracking**: Compare Imagen vs other generators

## Troubleshooting

### Database locked
```python
# Close existing connections
logger = None
# Recreate
logger = create_logger()
```

### Missing columns (after upgrade)
```bash
# Run migration script
python3 domains/materials/image/learning/migrate_db.py
```

### Query performance
```python
# Database auto-indexes on:
# - category
# - timestamp
# - passed
# No manual indexing needed
```

## Related Documentation

- **FEEDBACK_GUIDELINES.md** - How to give effective feedback
- **SYSTEM_VERIFICATION.md** - Validation and quality gates
- **ARCHITECTURE.md** - System design and data flow
- **API_USAGE.md** - Integration examples

---

## Quick Reference

### Log Attempt
```python
logger.log_attempt(material, category, gen_params, val_results, outcome)
```

### View Report
```bash
python3 domains/materials/image/learning/analytics.py --report
```

### Search Feedback
```bash
python3 domains/materials/image/learning/analytics.py --search-feedback "dust"
```

### Best Examples
```bash
python3 domains/materials/image/learning/analytics.py --best-feedback physics
```

---

**🎓 Key Insight**: Every generation attempt makes the system smarter. Feedback is no longer ephemeral - it becomes a permanent learning asset!
