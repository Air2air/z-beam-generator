# Frontmatter Date Update Script

## Purpose
Automatically updates `datePublished` and `dateModified` fields in frontmatter YAML files based on Git commit history.

## How It Works

### Date Detection
- **`datePublished`**: Uses the **first commit** date when the file was created
- **`dateModified`**: Uses the **last commit** date when the file was most recently modified

### Git Commands Used
```bash
# Get file creation date (first commit)
git log --follow --format=%aI --reverse "filepath" | head -1

# Get last modification date (most recent commit)
git log --follow --format=%aI -1 "filepath"
```

## Usage

### Test on Single File (Dry Run)
```bash
node scripts/update-frontmatter-dates.js --dry-run --file=frontmatter/materials/aluminum-laser-cleaning.yaml
```

### Update Single File
```bash
node scripts/update-frontmatter-dates.js --file=frontmatter/materials/aluminum-laser-cleaning.yaml
```

### Test All Frontmatter Files (Dry Run)
```bash
node scripts/update-frontmatter-dates.js --dry-run
```

### Update All Frontmatter Files
```bash
node scripts/update-frontmatter-dates.js
```

## Example Output

```
======================================================================
📅 Frontmatter Date Updater - Using Git Commit History
======================================================================
🔍 DRY RUN MODE - No files will be modified

Processing: frontmatter/materials/aluminum-laser-cleaning.yaml
  Current datePublished: 2025-11-11T04:44:00.602Z
  Current dateModified:  2025-11-11T04:55:00.603Z
  Git created date:      2025-10-30T15:30:08-07:00
  Git modified date:     2025-11-12T16:21:27-08:00
  → New datePublished:   2025-10-30T15:30:08-07:00
  → New dateModified:    2025-11-12T16:21:27-08:00
  [DRY RUN] Would update file

======================================================================
📊 Summary
======================================================================
Total files processed: 1
✅ Updated:            1
⏭️  Unchanged:          0
❌ Errors:             0

💡 This was a dry run. Run without --dry-run to apply changes.
```

## Safety Features

1. **Dry Run Mode**: Use `--dry-run` to preview changes without modifying files
2. **Git Fallback**: If Git history is unavailable, uses current date
3. **Error Handling**: Continues processing other files if one fails
4. **Detailed Logging**: Shows before/after values for each file

## Benefits

### Accurate Timestamps
- **Real creation dates**: Based on when file was actually added to repo
- **Real modification dates**: Based on latest commit, not manual updates
- **SEO friendly**: Search engines value accurate publication dates

### Example Timeline
For a material added on Oct 30 and last updated today:
- ❌ **Before**: Both dates show Nov 11, 2025 (arbitrary/fake)
- ✅ **After**: Published Oct 30, 2025 | Updated Nov 12, 2025 (accurate)

### Display Impact
On the author component, this would show:
```
📅 Published: Oct 30, 2025
🕐 Updated: Today
```

Instead of the current fake dates.

## Considerations

### When to Run
- **After bulk content generation**: When placeholder dates were used
- **Before deployment**: To ensure accurate timestamps for SEO
- **After restructuring**: When files were moved/renamed

### What Gets Updated
- ✅ All `.yaml` files in `/frontmatter/` directory
- ✅ Preserves all other YAML fields
- ✅ Maintains YAML structure and comments

### What Doesn't Change
- ❌ Files not tracked in Git (uses fallback date)
- ❌ Other metadata fields
- ❌ File timestamps (modification dates)

## Technical Details

### Dependencies
- `js-yaml`: YAML parsing/dumping
- `child_process`: Git command execution
- Node.js built-ins: `fs`, `path`

### Date Format
- Uses ISO 8601 format from Git (`%aI`)
- Example: `2025-11-12T16:21:27-08:00`
- Includes timezone offset

### Performance
- Processes ~286 files in under 1 minute
- Single Git command per file (efficient)
- Sequential processing (safe for large repos)

## Common Use Cases

### 1. Fix Placeholder Dates
```bash
# Review what would change
node scripts/update-frontmatter-dates.js --dry-run

# Apply changes
node scripts/update-frontmatter-dates.js
```

### 2. Update After Content Edits
```bash
# Single file you just edited
node scripts/update-frontmatter-dates.js --file=frontmatter/materials/copper-laser-cleaning.yaml
```

### 3. Verify Specific File
```bash
# Check without modifying
node scripts/update-frontmatter-dates.js --dry-run --file=frontmatter/materials/aluminum-laser-cleaning.yaml
```

## Integration with Existing Workflow

### Git Hooks
Add to `.git/hooks/pre-commit` to auto-update dates:
```bash
#!/bin/bash
node scripts/update-frontmatter-dates.js --file="$staged_file"
```

### CI/CD Pipeline
```yaml
- name: Update Frontmatter Dates
  run: node scripts/update-frontmatter-dates.js
```

## Notes

- Script is idempotent (safe to run multiple times)
- Changes are reversible via Git
- Dry run recommended before first full run
- Works with `git log --follow` to track file renames
