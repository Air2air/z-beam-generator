# Quick Reference

## Workflow Orchestration (Read First)
The workflow orchestration guide is the first step for every AI task.

- Primary guide: docs/08-development/AI_ASSISTANT_GUIDE.md#workflow-orchestration
- Copilot instructions: .github/copilot-instructions.md

## Common Tasks
- Generate content: .github/COPILOT_GENERATION_GUIDE.md
- Troubleshoot errors: TROUBLESHOOTING.md
- System interactions: docs/SYSTEM_INTERACTIONS.md
- Architecture overview: docs/02-architecture/
- Policies: docs/08-development/

## Keyword → Full Page (Centralized)
- Create a new page from one topic keyword (seed source item, run multi-field generation, sync frontmatter):
  - `python3 run.py --seed-from-keyword "Aerospace Coatings" --domain applications`
- Reuse for other domains (override taxonomy when needed):
  - `python3 run.py --seed-from-keyword "Nickel Slag" --domain contaminants --category inorganic-coating --subcategory residue`
- Use a specific donor template item:
  - `python3 run.py --seed-from-keyword "Marine Hull" --domain applications --template-item aerospace-laser-cleaning-applications`
- Preview only (no writes):
  - `python3 run.py --seed-from-keyword "Composite Bondline" --domain applications --dry-run`

## Terminal Usage Rules

### File Creation
- **NEVER** create files via heredoc or multi-line echo in the terminal — the VS Code integrated terminal truncates or drops multi-line content, producing empty/partial files and spawning retry terminals.
- **ALWAYS** use the `create_file` tool to write any file (including `/tmp/*.py` probe scripts), then run it with a single terminal line: `python3 /tmp/script.py`

### Hanging Commands
- **DETECT**: Exit code 130 = Ctrl+C = the command hung or was too slow. **Never re-run the identical command.**
- **DETECT**: Terminal context showing the same command repeated 2+ times = hang loop. Stop immediately.
- **FIX — long pytest runs**: Narrow to one file: `python3 -m pytest tests/path/test_file.py --tb=short -q`  
  OR run background: `isBackground: true` + `timeout: 120000` + `get_terminal_output` to check
- **FIX — hanging build**: Use `isBackground: true` and poll with `get_terminal_output`
- **FIX — if scope is unavoidably large**: Add `timeout` parameter to the terminal call; never run blocking with no timeout on a full test suite
- **RULE**: After any exit-130, change strategy before retrying — same command = Grade F violation

## Field Naming Reference (Single Source of Truth)
- All field names, every domain, camelCase ↔ snake_case mapping: **docs/08-development/FIELD_NAMING_REFERENCE.md**
- Field order canonical spec: data/schemas/FrontmatterFieldOrder.yaml
- Content-generation field policy (all domains): data/schemas/content_generation_policy.yaml
- Single-line component prompts + variable contracts: data/schemas/component_single_line_prompts.yaml

## Frontmatter Parity Gates (CI + Local)
- CI workflow: `.github/workflows/data-validation.yml` job `validate-frontmatter-parity`
- Export before validating parity: `python3 run.py --export-all --no-parallel`
- Field-order parity check: `python3 scripts/check_field_order.py`
- Strict schema parity check: `python3 scripts/validation/validate_frontmatter_schema.py --strict`
- Data completeness gate: `python3 scripts/validation/validate_data_completeness.py --max-critical 0 --max-high 0`
- Contract split: field-order validator checks ordering; strict schema validator checks shape/completeness.

## Materials Section Contract Keys
- properties.materialCharacteristics
- properties.laserMaterialInteraction
- faq
- relationships.interactions.contaminatedBy
- relationships.operational.industryApplications
- relationships.safety.regulatoryStandards
- laserMaterialInteraction (root-level alias of properties.laserMaterialInteraction)
