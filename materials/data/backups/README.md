# Backups Directory

Automated backups created before data updates.

## Retention Policy

- **Keep**: Last 5 backups of each file
- **Delete**: Backups older than 30 days (unless last 5)
- **Automatic**: Backups created by populate_deep_research.py

## Files

- `PropertyResearch_backup_YYYYMMDD_HHMMSS.yaml` - Property research backups
- `SettingResearch_backup_YYYYMMDD_HHMMSS.yaml` - Setting research backups
- `Materials_backup_YYYYMMDD_HHMMSS.yaml` - Materials data backups

See `BACKUP_RETENTION_POLICY.md` for details.
