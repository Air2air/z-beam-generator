# Database Usage Guide
**Date**: December 15, 2025  
**Status**: Consolidated Architecture  
**Version**: 1.0.0

---

## Overview

The Z-Beam system uses **SQLite databases** for learning, analytics, and quality feedback. After consolidation (Dec 15, 2025), the system maintains **2 primary databases** with clear purposes.

---

## Current Database Architecture

### 1. Winston Feedback Database (PRIMARY)

**Location**: `data/winston_feedback.db`  
**Size**: ~5.0 MB  
**Status**: ✅ **ACTIVE** (Primary learning database)  
**Last Modified**: November 22, 2025

**Purpose**: Comprehensive learning and feedback storage for text generation quality improvement.

**Tables** (15 total, 10,460 rows):

| Table | Rows | Purpose |
|-------|------|---------|
| `detection_results` | 1,633 | Winston AI detection scores per generation |
| `sentence_analysis` | 5,339 | Per-sentence AI tendency analysis |
| `ai_patterns` | 103 | Learned AI-like phrase patterns |
| `generation_parameters` | 1,603 | Parameters used (temp, penalties, etc.) |
| `subjective_evaluations` | 111 | Quality scores (realism, authenticity) |
| `fix_attempts` | 735 | Attempted parameter adjustments |
| `fix_outcomes` | 856 | Results of adjustment attempts |
| `fix_statistics` | 77 | Statistical summaries |
| `structural_patterns` | 327 | Opening patterns, rhythm analysis |
| `claude_evaluations` | 10 | Manual quality assessments |
| `sweet_spot_recommendations` | 3 | Optimal parameter sets |
| `corrections` | 0 | (Reserved for future use) |
| `learning_insights` | 0 | (Reserved for future use) |
| `realism_learning` | 0 | (Reserved for future use) |
| `sqlite_sequence` | 11 | Internal SQLite management |

**Usage**:
```python
import sqlite3

conn = sqlite3.connect('data/winston_feedback.db')
cursor = conn.cursor()

# Query detection results
cursor.execute("SELECT * FROM detection_results WHERE human_score > 0.9;")
results = cursor.fetchall()

conn.close()
```

**Active Components**:
- `generation/core/evaluated_generator.py` - Logs quality metrics
- `postprocessing/evaluation/` - Stores evaluation results
- `learning/` - Analyzes patterns for improvement
- `shared/text/validation/` - Queries patterns for validation

---

### 2. Image Generation Learning Database

**Location**: `shared/image/learning/generation_history.db`  
**Size**: ~224 KB  
**Status**: ✅ ACTIVE (Image-specific learning)  
**Purpose**: Track image generation attempts, parameters, and outcomes

**Tables** (5 total, 244 rows):

| Table | Rows | Purpose |
|-------|------|---------|
| `generation_attempts` | 146 | Image generation attempts with parameters |
| `learned_defaults` | 27 | Optimal default parameters by material |
| `pattern_effectiveness` | 71 | Contamination pattern success rates |
| `prompt_templates` | 0 | (Reserved for template versioning) |
| `sqlite_sequence` | 2 | Internal SQLite management |

**Usage**:
```python
import sqlite3

conn = sqlite3.connect('shared/image/learning/generation_history.db')
cursor = conn.cursor()

# Query successful attempts
cursor.execute("SELECT * FROM generation_attempts WHERE validation_passed = 1;")
successes = cursor.fetchall()

conn.close()
```

**Active Components**:
- `shared/image/learning/` - Logs image generation history
- `shared/image/orchestrator.py` - Queries learned defaults

---

### 3. Deprecated Databases (REMOVED)

**z-beam.db** (3.5 MB) - Deprecated December 15, 2025  
- **Status**: ⚠️ **DUPLICATE** of winston_feedback.db
- **Schema**: 83% identical (10/12 tables)
- **Data**: Older/less complete than winston_feedback.db
- **Action**: **Keep for historical reference, but DO NOT write to**
- **Recommendation**: Archive and remove from active codebase

**learning/generation_history.db** - ✅ **DELETED** (Dec 15, 2025)  
- **Status**: Empty (0 bytes)
- **Reason**: Never used, no data

**postprocessing/detection/winston_feedback.db** - ✅ **DELETED** (Dec 15, 2025)  
- **Status**: Empty (0 bytes)
- **Reason**: Never populated

**nonexistent.db** (180 KB)  
- **Status**: ⚠️ **SHOULD NOT EXIST** (name indicates testing artifact)
- **Tables**: 10 tables with minimal data
- **Action**: Review and delete if not needed

---

## Database Access Patterns

### Read Operations (Query Learning Data)

**When**: Before generation, to load learned patterns or optimal parameters

**Example**:
```python
from shared.text.validation.structural_variation_checker import StructuralVariationChecker

checker = StructuralVariationChecker(db_path="data/winston_feedback.db")
diversity_score = checker.check_structural_diversity(text)
```

**Pattern**:
1. Connect to database
2. Query specific table (e.g., `structural_patterns`, `learned_defaults`)
3. Process results
4. Close connection
5. **DO NOT** hold connection open across generations

---

### Write Operations (Log New Data)

**When**: After generation, to log quality metrics for learning

**Example**:
```python
from learning.feedback_logger import FeedbackLogger

logger = FeedbackLogger(db_path="data/winston_feedback.db")
logger.log_detection_result(
    detection_id=123,
    human_score=0.95,
    ai_score=0.05,
    content="Generated text...",
    metadata={'temperature': 0.7}
)
```

**Pattern**:
1. Import logging utility
2. Create logger instance with db_path
3. Call logging method
4. Logger handles connection management

---

## Schema Documentation

### winston_feedback.db Schema

**detection_results** table:
```sql
CREATE TABLE detection_results (
    detection_id INTEGER PRIMARY KEY,
    human_score REAL,
    ai_score REAL,
    fake_score REAL,
    content TEXT,
    parameters TEXT,  -- JSON
    timestamp DATETIME,
    material_name TEXT,
    component_type TEXT,
    author_id INTEGER,
    exclusion_reason TEXT  -- Why this attempt was excluded
);
```

**sentence_analysis** table:
```sql
CREATE TABLE sentence_analysis (
    sentence_id INTEGER PRIMARY KEY,
    detection_id INTEGER,
    sentence_text TEXT,
    ai_tendency_score REAL,
    pattern_matched TEXT,
    FOREIGN KEY (detection_id) REFERENCES detection_results(detection_id)
);
```

**generation_parameters** table:
```sql
CREATE TABLE generation_parameters (
    param_id INTEGER PRIMARY KEY,
    detection_id INTEGER,
    temperature REAL,
    frequency_penalty REAL,
    presence_penalty REAL,
    max_tokens INTEGER,
    humanness_level INTEGER,
    component_type TEXT,
    -- ... (32 total columns)
    FOREIGN KEY (detection_id) REFERENCES detection_results(detection_id)
);
```

**Full schema**: See `scripts/schema/export_schema.py` for complete DDL

---

### Image Generation Schema

**generation_attempts** table:
```sql
CREATE TABLE generation_attempts (
    attempt_id INTEGER PRIMARY KEY,
    material_name TEXT,
    timestamp DATETIME,
    prompt_used TEXT,
    validation_score REAL,
    validation_passed INTEGER,  -- Boolean
    parameters TEXT,  -- JSON
    result_path TEXT
);
```

**learned_defaults** table:
```sql
CREATE TABLE learned_defaults (
    material_category TEXT PRIMARY KEY,
    optimal_temperature REAL,
    optimal_frequency_penalty REAL,
    optimal_presence_penalty REAL,
    learned_from_attempts INTEGER,
    last_updated DATETIME
);
```

---

## Maintenance Operations

### Backup Databases

```bash
# Backup before major operations
cp data/winston_feedback.db data/winston_feedback.db.backup
cp shared/image/learning/generation_history.db shared/image/learning/generation_history.db.backup

# Add timestamp
DATE=$(date +%Y%m%d)
cp data/winston_feedback.db backups/winston_feedback_${DATE}.db
```

### Vacuum (Reclaim Space)

```bash
# Reclaim space from deleted rows
sqlite3 data/winston_feedback.db "VACUUM;"

# Check size reduction
ls -lh data/winston_feedback.db
```

### Export Schema

```bash
# Export schema for documentation
sqlite3 data/winston_feedback.db ".schema" > docs/schema/winston_feedback_schema.sql
```

### Query Statistics

```python
import sqlite3

conn = sqlite3.connect('data/winston_feedback.db')
cursor = conn.cursor()

# Get table row counts
cursor.execute("""
    SELECT name, 
           (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=tables.name) as row_count
    FROM sqlite_master tables
    WHERE type='table' AND name NOT LIKE 'sqlite_%'
""")

for table, count in cursor.fetchall():
    print(f"{table}: {count} rows")

conn.close()
```

---

## Best Practices

### ✅ DO

1. **Use connection context managers**:
```python
with sqlite3.connect('data/winston_feedback.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detection_results;")
    results = cursor.fetchall()
# Connection auto-closes
```

2. **Use parameterized queries** (prevent SQL injection):
```python
cursor.execute(
    "SELECT * FROM detection_results WHERE material_name = ?",
    (material_name,)
)
```

3. **Close connections** when done:
```python
conn = sqlite3.connect('data/winston_feedback.db')
# ... operations
conn.close()
```

4. **Index frequently queried columns**:
```sql
CREATE INDEX idx_detection_material ON detection_results(material_name);
CREATE INDEX idx_detection_author ON detection_results(author_id);
```

---

### ❌ DON'T

1. **Don't hold connections open across requests**:
```python
# ❌ WRONG
conn = sqlite3.connect('data/winston_feedback.db')  # Opened once
for material in materials:
    generate(material)  # Long-running operation
conn.close()  # Connection held open too long
```

2. **Don't write to multiple databases for same purpose**:
```python
# ❌ WRONG - Use winston_feedback.db only
log_to_database('data/winston_feedback.db', data)
log_to_database('z-beam.db', data)  # Duplicate!
```

3. **Don't use string concatenation for queries**:
```python
# ❌ WRONG - SQL injection risk
query = f"SELECT * FROM detection_results WHERE material_name = '{material}'"
```

4. **Don't forget to commit writes**:
```python
conn = sqlite3.connect('data/winston_feedback.db')
cursor.execute("INSERT INTO detection_results ...")
# ❌ Missing: conn.commit()
conn.close()  # Data NOT saved!
```

---

## Troubleshooting

### Database Locked Error

**Symptom**: `sqlite3.OperationalError: database is locked`

**Cause**: Another process has database open with uncommitted transaction

**Solution**:
```bash
# Check for processes using database
lsof | grep winston_feedback.db

# If stuck, kill process or close connection
# Then retry operation
```

---

### Database Corrupted

**Symptom**: `sqlite3.DatabaseError: database disk image is malformed`

**Cause**: Incomplete writes, system crash, disk errors

**Solution**:
```bash
# Try to recover with .dump and reimport
sqlite3 data/winston_feedback.db ".dump" > winston_backup.sql
sqlite3 data/winston_feedback_new.db < winston_backup.sql

# If successful, replace
mv data/winston_feedback.db data/winston_feedback.db.corrupt
mv data/winston_feedback_new.db data/winston_feedback.db
```

---

### Slow Queries

**Symptom**: Queries taking >1 second

**Solution**:
```sql
-- Analyze query plan
EXPLAIN QUERY PLAN SELECT * FROM detection_results WHERE material_name = 'Aluminum';

-- Add index if needed
CREATE INDEX idx_detection_material ON detection_results(material_name);

-- Update statistics
ANALYZE;
```

---

## Migration Guide

### Consolidating z-beam.db → winston_feedback.db

**IF you need to preserve z-beam.db data** (only if it has newer data than winston_feedback.db):

```python
import sqlite3

# Connect to both databases
src = sqlite3.connect('z-beam.db')
dst = sqlite3.connect('data/winston_feedback.db')

# Attach source database
dst.execute("ATTACH DATABASE 'z-beam.db' AS source;")

# Copy tables (example: detection_results)
dst.execute("""
    INSERT INTO detection_results
    SELECT * FROM source.detection_results
    WHERE detection_id NOT IN (SELECT detection_id FROM detection_results);
""")

dst.commit()
dst.close()
src.close()

print("✅ Migration complete")
```

**Recommended**: Archive z-beam.db and move forward with winston_feedback.db only.

---

## Code References

### Database Connections in Codebase

**Winston Feedback Database**:
- `generation/core/evaluated_generator.py` - Logs quality metrics
- `shared/text/validation/structural_variation_checker.py` - Queries patterns
- `shared/text/validation/forbidden_phrase_validator.py` - Queries AI patterns
- `learning/feedback_logger.py` - Logging utility
- `postprocessing/evaluation/subjective_evaluator.py` - Logs evaluations

**Image Learning Database**:
- `shared/image/learning/image_logger.py` - Logs attempts
- `shared/image/orchestrator.py` - Queries learned defaults

**Deprecated References** (should be updated to winston_feedback.db):
```bash
# Find any remaining z-beam.db references
grep -r "z-beam\.db" generation/ shared/ postprocessing/ --include="*.py"

# Update to winston_feedback.db
sed -i '' 's/z-beam\.db/data\/winston_feedback.db/g' {file}
```

---

## Performance Benchmarks

**Query Performance** (on 5.0 MB database):
- Simple SELECT by ID: <1ms
- SELECT with WHERE on indexed column: 1-5ms
- SELECT with JOIN: 5-20ms
- INSERT single row: <1ms
- VACUUM: 100-500ms

**Recommended Max Size**: ~50 MB before archiving/partitioning older data

---

## Future Enhancements

### Potential: Time-Series Partitioning

For databases >100 MB, partition by time period:

```
data/
├── winston_feedback_2025_Q4.db
├── winston_feedback_2025_Q3.db
└── winston_feedback_current.db  # Active writing
```

### Potential: Read Replicas

For high-volume querying, create read-only replicas:

```bash
# Create read replica
cp data/winston_feedback.db data/winston_feedback_readonly.db
chmod 444 data/winston_feedback_readonly.db  # Read-only
```

Query read replica to avoid locking primary database.

---

## References

- **Database Comparison Tool**: `scripts/analysis/compare_databases.py`
- **Schema Export**: `scripts/schema/export_schema.py`
- **Backup Script**: `scripts/maintenance/backup_databases.sh`
- **Learning Logger**: `learning/feedback_logger.py`
- **Image Logger**: `shared/image/learning/image_logger.py`

---

**Last Updated**: December 15, 2025  
**Maintainer**: GitHub Copilot (Claude Sonnet 4.5)  
**Status**: ✅ Consolidated Architecture
