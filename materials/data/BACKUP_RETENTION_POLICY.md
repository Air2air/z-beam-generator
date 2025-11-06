# Backup Retention Policy

**Effective Date**: November 5, 2025

## Policy

**Keep only the last 3 semantically meaningful backups** in `materials/data/`.

### Current Retained Backups

1. **Materials_backup_before_author_migration.yaml** (2.0M)
   - Created: November 5, 2025
   - Purpose: Backup before migrating from full author objects to author IDs
   
2. **materials_backup_before_lmi_research.yaml** (1.9M)
   - Created: November 4, 2025
   - Purpose: Backup before LMI property research phase
   
3. **materials_backup_before_normalization.yaml** (1.9M)
   - Created: November 4, 2025
   - Purpose: Backup before data structure normalization

### Rationale

- **Disk space**: 53 backup files were consuming 74M+ of space
- **Git performance**: Large binary files slow down git operations
- **Clarity**: Semantic backups are more useful than timestamped ones
- **Archive**: Older backups already preserved in `.archive/` (7.1M)

## Guidelines

### When to Create a Backup

Create backups ONLY before:
- **Major data migrations** (e.g., schema changes)
- **Automated transformations** (e.g., bulk property updates)
- **Structural changes** (e.g., field renames/removals)

### Naming Convention

Use descriptive names that explain WHY:
```
materials_backup_before_<operation_name>.yaml
```

**Good examples**:
- `materials_backup_before_author_migration.yaml`
- `materials_backup_before_lmi_research.yaml`
- `materials_backup_before_normalization.yaml`

**Bad examples**:
- `Materials.backup_20251103_214958.yaml` (no context)
- `materials_backup.yaml` (not specific)
- `backup.yaml` (useless)

### When to Rotate Backups

After creating a new meaningful backup:
1. Review existing backups (should have 3-4 max)
2. Delete oldest backup if more than 3 exist
3. Keep the 3 most recent meaningful backups

### DO NOT Create Backups For

- ❌ Small edits to individual materials
- ❌ Adding new materials
- ❌ Fixing typos or formatting
- ❌ Updating single property values
- ✅ Git history is sufficient for these cases

## Recovery Process

If you need to restore from backup:

```bash
# 1. Verify current state is problematic
git status

# 2. Copy backup to restore
cp materials_backup_before_<operation>.yaml Materials.yaml

# 3. Clear cache to force reload
python3 -c "from materials.data.materials import clear_materials_cache; clear_materials_cache()"

# 4. Verify restoration worked
python3 run.py --material "Steel" --components frontmatter
```

## Cleanup Summary (November 5, 2025)

- **Before**: 56 backup files, 74M in materials/data/
- **After**: 3 backup files, 5.8M in materials/data/
- **Space saved**: ~68M (91% reduction)
- **Archived**: Historical backups preserved in `.archive/` directory
