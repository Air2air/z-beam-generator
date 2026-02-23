# Lessons Learned

- 2026-02-23: When the user specifies a workflow doc as the first step each turn, surface it at the top of primary AI guides and remove legacy instruction files to avoid conflicting guidance.
- 2026-02-23: When the workflow is updated, replace prior workflow text and rebase plans to follow the new session ritual and plan verification steps.
- 2026-02-23: Never trust a conversation summary's claim that source data is "already normalized." Always run a direct check (grep or python) on the actual file before planning. The summary said Applications.yaml was correct; it was not.
- 2026-02-23: Do not patch the export pipeline to compensate for incorrect source data. Fix the source data first, then re-export. Patching exporters mid-investigation before understanding the full picture caused an incorrect fix that had to be reverted.
- 2026-02-23: After modifying source data and re-exporting, always check for stale frontmatter files from the old naming convention. The re-export created new files but left the old ones in place — both sets existed until explicitly deleted.
