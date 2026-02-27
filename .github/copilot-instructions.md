# AI Assistant Instructions for Z-Beam Generator

**Archived pre-refactor version**: `docs/archive/2026-02/copilot-instructions-pre-refactor-feb2026.md`
**Full policy library**: `docs/08-development/`
**Quick answers**: `docs/QUICK_REFERENCE.md`

---

## ⚡ STEP 0 — MANDATORY EVERY TURN

**State your classification as the first line of every response, no exceptions:**

> `SIMPLE` — single file, obvious fix, no pipeline impact
> `COMPLEX` — generator/exporter/data pipeline, 3+ files, protected file, new pattern

| Triggers COMPLEX |
|-----------------|
| Generator, exporter, data pipeline, or 3+ files |
| Protected file (see `.github/PROTECTED_FILES.md`) |
| New architectural pattern, domain, or component |

**SIMPLE tasks:** Apply Core 5 Rules only, proceed.
**COMPLEX tasks:** Write plan to `tasks/todo.md` first, verify plan, then execute.

---

## ⚡ CORE 5 RULES — Always apply, no exceptions

1. Don't rewrite working code
2. No hardcoded values in production code
3. No mocks/fallbacks in production code
4. Fix at source, not at output (never patch frontmatter directly — fix generators or source data)
5. Verify it works before claiming done

---

## 🚫 GRADE F VIOLATIONS — Immediate failure

- Mock/fallback responses in production code (ANY `.get('key', default)` on required fields)
- Hardcoded thresholds, temperatures, penalties in code (use `dynamic_config`)
- Rewriting working code without explicit permission
- Patching frontmatter files directly (fix Layer 1 source data or Layer 2 export config)
- Generating text outside `QualityEvaluatedGenerator` pipeline
- Reporting success when a quality gate has failed
- Documenting a feature as COMPLETE without a passing verification test
- Auto-regenerating images without explicit user instruction
- Using `max_tokens` to enforce word count (causes truncation)
- Bypassing dual-write: every save to data YAML must also sync frontmatter
- Using heredoc or multi-line echo in the terminal to create files (always use `create_file` tool, then run with one terminal call)
- Re-running a terminal command that previously exited with code 130 (Ctrl+C / hang) without changing strategy (see decision tree below)

---

## ✅ PRE-CHANGE CHECKLIST — COMPLEX tasks

Before writing any code:

- [ ] Classify: SIMPLE or COMPLEX (stated at top of response)
- [ ] Check `.github/PROTECTED_FILES.md` — is this file protected? If Tier 1: STOP, ask user
- [ ] Read the actual source files — never trust a summary or recent context
- [ ] Search `docs/QUICK_REFERENCE.md` for existing guidance
- [ ] Check `docs/08-development/` for a policy doc on this area
- [ ] Identify the exact minimal change (one sentence)
- [ ] Confirm scope: fix X means fix ONLY X
- [ ] Plan written to `tasks/todo.md` (COMPLEX only)
- [ ] Fix at source: is this a data issue, export config issue, or code issue?
- [ ] After change: run verification (test, audit, grep) before claiming done

---

## 🚦 DECISION TREES

**Should I use a default value?**
Config/setup issue → FAIL FAST (raise ConfigurationError)
Runtime/transient issue → RETRY with backoff
Otherwise → FAIL FAST

**Should I rewrite this code?**
Works correctly → NO (integrate around it)
Broken, small fix → FIX the broken part only
Broken, needs rewrite → ASK PERMISSION first

**Should I fix frontmatter directly?**
Never → Fix Layer 1 (source YAML) or Layer 2 (export config), re-export
**How do I create a file?**
Always → `create_file` tool to write the file, then one terminal call to run it
NEVER → heredoc, multi-line echo, or any terminal-based file creation

**A terminal command exited with code 130 or never returned — what now?**
1. STOP — do not re-run the same command
2. Diagnose: is it a long-running process (pytest full suite, npm run build)?
3. If yes → switch to `isBackground: true` with a `timeout`, OR narrow scope (single test file, `--co` collect-only, specific `--keyword`), OR use `head -n` to limit output
4. For pytest specifically: `python3 -m pytest tests/specific_test.py --tb=short -q` — never run the full suite blocking without a timeout
5. If it hangs again → run it as background (`isBackground: true`) and use `get_terminal_output` to check progress
---

## 🔒 PROTECTED FILES — Ask before touching

**Tier 1 (NEVER without explicit permission):**
- `shared/voice/profiles/*.yaml`
- `prompts/{domain}/*.txt`
- `generation/core/evaluated_generator.py`
- `generation/core/generator.py`
- `shared/text/utils/prompt_builder.py`

**Tier 2 (Explain impact, wait for approval):**
- `generation/config.yaml`, `domains/*/config.yaml`
- `data/materials/Materials.yaml`, `data/settings/Settings.yaml`
- `learning/*.py`

Full list: `.github/PROTECTED_FILES.md`

---

## 📖 QUICK NAVIGATION

| Task | Resource |
|------|----------|
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
| Frontmatter export path | `frontmatter/materials/`, `frontmatter/contaminants/`, etc. → `/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/` |

---

## 🔒 Author Assignment Immutability

Once `author.id` is written to a data YAML, it **NEVER changes**.

- Author assignment happens **once** at content creation time
- All regenerations for that item use the same author's voice
- Voice is controlled by `shared/voice/profiles/*.yaml` — do not override in prompts
- See `docs/08-development/AUTHOR_ASSIGNMENT_POLICY.md` for full policy

---

## 📋 AFTER EVERY CORRECTION

Update `tasks/lessons.md` with the pattern that caused the mistake and the rule that prevents it.

Format: `- YYYY-MM-DD: [what went wrong] → [rule to prevent recurrence]`
