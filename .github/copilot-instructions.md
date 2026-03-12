# AI Assistant Instructions for Z-Beam Generator

**Archived pre-refactor version**: `docs/archive/2026-02/copilot-instructions-pre-refactor-feb2026.md`
**Full policy library**: `docs/08-development/`
**Quick answers**: `docs/QUICK_REFERENCE.md`
**Grok-first mirror**: `governance/copilot-instructions.md`

**Pipeline 2 note**: Grok-first direct generation should read `governance/`, `aggregates/`, `voices/`, `frontmatter-templates/`, and `schemas/pipeline_2_policy.yaml` first; legacy runtime paths remain available for compatibility but are deprecated in favor of Grok's hybrid tools (e.g., browse_page for fetches, code_execution for YAML parses).

---

## STEP 0 — MANDATORY EVERY TURN

**State your classification as the first line of every response, no exceptions:**

> `SIMPLE` — single file, obvious fix, no pipeline impact
> `COMPLEX` — generator/exporter/data pipeline, 3+ files, high-impact file, new pattern

| Triggers COMPLEX |
|-----------------|
| Generator, exporter, data pipeline, or 3+ files |
| High-impact file (see `.github/PROTECTED_FILES.md`) |
| New architectural pattern, domain, or component |

**SIMPLE tasks:** Apply Core 5 Rules only, proceed.
**COMPLEX tasks:** Write plan to `tasks/todo.md` first, verify plan, then execute. For Grok-led tasks, use multi-agent mode (Captain orchestrate, Harper research, Benjamin fact-check, Eliza prose).

---

## CORE 5 RULES — Always apply, no exceptions

1. Don't rewrite working code
2. No hardcoded values in production code
3. No mocks/fallbacks in production code
4. Fix at source, not at output (never patch frontmatter directly — fix generators or aggregate source YAMLs)
5. Verify it works before claiming done

---

## GRADE F VIOLATIONS — Immediate failure

- Mock/fallback responses in production code (ANY `.get('key', default)` on required fields)
- Hardcoded thresholds, temperatures, penalties in code (use `dynamic_config`)
- Rewriting working code without explicit permission
- Patching frontmatter files directly (fix Layer 1 aggregate source YAMLs or Layer 2 export config)
- Generating text outside `QualityEvaluatedGenerator` pipeline (or Grok's Pipeline 2 direct gens)
- Reporting success when a quality gate has failed
- Documenting a feature as COMPLETE without a passing verification test
- Auto-regenerating images without explicit user instruction
- Using `max_tokens` to enforce word count (causes truncation)
- Bypassing dual-write: every save to aggregate source YAML must also sync frontmatter
- Using heredoc or multi-line echo in the terminal to create files (always use `create_file` tool, then run with one terminal call)
- Re-running a terminal command that previously exited with code 130 (Ctrl+C / hang) without changing strategy (see decision tree below)
- Ignoring Grok tools in Pipeline 2 (e.g., web_search/browse_page for hybrid research)

---

## PRE-CHANGE CHECKLIST — COMPLEX tasks

Before writing any code:

- [ ] Classify: SIMPLE or COMPLEX (stated at top of response)
- [ ] Check `.github/PROTECTED_FILES.md` — is this file high-impact? Plan focused validation
- [ ] Read the actual source files — never trust a summary or recent context
- [ ] Search `docs/QUICK_REFERENCE.md` for existing guidance
- [ ] Check `docs/08-development/` for a policy doc on this area
- [ ] Identify the exact minimal change (one sentence)
- [ ] Confirm scope: fix X means fix ONLY X
- [ ] Plan written to `tasks/todo.md` (COMPLEX only)
- [ ] Fix at source: is this a data issue, export config issue, or code issue?
- [ ] For Grok tasks: Incorporate multi-agent breakdown and hybrid tools
- [ ] After change: run verification (test, audit, grep) before claiming done

---

## DECISION TREES

**Should I use a default value?**
Config/setup issue → FAIL FAST (raise ConfigurationError)
Runtime/transient issue → RETRY with backoff
Otherwise → FAIL FAST

**Should I rewrite this code?**
Works correctly → NO (integrate around it)
Broken, small fix → FIX the broken part only
Broken, needs rewrite → ASK PERMISSION first

**Should I fix frontmatter directly?**
Never → Fix Layer 1 (aggregate source YAMLs) or Layer 2 (export config), re-export; use Grok Pipeline 2 for direct gens

**How do I create a file?**
Always → `create_file` tool to write the file, then one terminal call to run it
NEVER → heredoc, multi-line echo, or any terminal-based file creation

**A terminal command exited with code 130 or never returned — what now?**
1. STOP — do not re-run the same command
2. Diagnose: is it a long-running process (pytest full suite, npm run build)?
3. If yes → switch to `isBackground: true` with a `timeout`, OR narrow scope (single test file, `--co` collect-only, specific `--keyword`), OR use `head -n` to limit output
4. For pytest specifically: `python3 -m pytest tests/specific_test.py --tb=short -q` — never run the full suite blocking without a timeout
5. If it hangs again → run it as background (`isBackground: true`) and use `get_terminal_output` to check progress
6. For Grok: Prefer in-chat simulations over legacy runtime

**Should I use legacy Python or Grok Pipeline 2?**
Grok-capable (e.g., direct YAML gens) → Use Pipeline 2 with multi-agents/tools
Fallback needed → Use legacy runtime minimally (e.g., verify scripts)

---

## HIGH-IMPACT FILES — Validate after touching

**High-impact examples:**
- `voices/*.yaml` (canonical Grok-first)
- `prompts/{domain}/*.txt`
- `generation/core/evaluated_generator.py`
- `generation/core/generator.py`
- `shared/text/utils/prompt_builder.py`

**Additional high-impact examples:**
- `generation/config.yaml`, `domains/*/config.yaml`
- `aggregates/Materials.yaml`, `aggregates/Settings.yaml`
- `learning/*.py`
- `schemas/pipeline_2_policy.yaml`

Full list: `.github/PROTECTED_FILES.md`

---

## QUICK NAVIGATION

| Task | Resource |
|------|----------|
| Grok-first governance | `governance/` |
| Pipeline 2 policy | `schemas/pipeline_2_policy.yaml` |
| Aggregate source YAMLs | `aggregates/` |
| Generate content | `.github/COPILOT_GENERATION_GUIDE.md` |
| Understand data flow | `docs/02-architecture/processing-pipeline.md` |
| Policy lookup (hardcoded values, prompts, naming, etc.) | `docs/08-development/` |
| Fix bugs / understand side effects | `docs/SYSTEM_INTERACTIONS.md` |
| Quick answers | `docs/QUICK_REFERENCE.md` |
| **All field names (camelCase ↔ snake_case, all domains)** | `docs/08-development/FIELD_NAMING_REFERENCE.md` |
| Frontmatter source-of-truth policy | `docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md` |
| Material name conventions | `docs/08-development/MATERIAL_NAME_CONSISTENCY_POLICY.md` |
| Terminal logging | `docs/08-development/TERMINAL_LOGGING_POLICY.md` |
| Voice centralization | `docs/08-development/AUTHOR_ASSIGNMENT_POLICY.md` |
| Frontmatter export path | Production website repo: `https://github.com/Air2air/z-beam/tree/main/frontmatter` (`frontmatter/materials/`, `frontmatter/contaminants/`, etc.) |
| Grok Tools & Thresholds | `governance/grok-tools.md` (browse_page, code_execution; >85% confidence) |

---

## Author Assignment Immutability

Once `author.id` is written to an aggregate source YAML, it **NEVER changes**.

- Author assignment happens **once** at content creation time
- All regenerations for that item use the same author's voice
- Canonical Grok-first voice profiles live in `voices/*.yaml`; `shared/voice/profiles/*.yaml` remains the compatibility path used by legacy runtime code.
- See `docs/08-development/AUTHOR_ASSIGNMENT_POLICY.md` for full policy

---

## GROK HANDOFF & PIPELINE 2 INTEGRATION

- **Multi-Agent Mode**: For COMPLEX tasks, orchestrate with Captain (plan), Harper (research/cite), Benjamin (fact-check/calculate), Eliza (prose). Show contributions before outputs.
- **Hybrid Research**: Pull from local aggregates/ via code_execution; supplement with web_search/browse_page for citations (inline [web:X], tested non-404 links).
- **YAML Rules**: Preserve structure (breadcrumbs, _section, icons); update text only (20-70 words, unusual effects); neutral US base with subtle nationality; quote semicolons.
- **Thresholds**: >85% confidence, 98.1% property accuracy, Grok 60% quality weight.
- **Cleanup**: Quarterly prune /legacy/; run integrity post-changes.
- **Fallbacks**: Minimize legacy Python; fail-fast on errors, no mocks.

---

## AFTER EVERY CORRECTION

Update `tasks/lessons.md` with the pattern that caused the mistake and the rule that prevents it.

Format: `- YYYY-MM-DD: [what went wrong] → [rule to prevent recurrence]`
