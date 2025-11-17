# Archive - Deprecated Files

**Historical files that are no longer used in the current system.**

---

## ⚠️ WARNING

**DO NOT USE FILES IN THIS DIRECTORY**

These files are preserved for historical reference and understanding system evolution, but are **NOT ACTIVE** in the current generation pipeline.

Using archived files may:
- Violate current architectural policies
- Introduce deprecated patterns
- Bypass active validation systems
- Create inconsistent content

---

## 📁 Archived Files

### voice_rules.txt
**Deprecated**: November 16, 2025  
**Reason**: Redundant with persona system

**Original Purpose**: Template for injecting author voice instructions into prompts

**Why Deprecated**:
- Functionality fully replaced by `prompts/personas/*.yaml`
- Persona files provide richer, more detailed voice definitions
- YAML format allows structured linguistic patterns
- Abstract pattern notation more flexible than text templates
- Grep search found **ZERO active references** in codebase

**Migration Path**: Voice instructions now come from `voice_instructions` field in persona YAML files, automatically injected by `processing/generation/prompt_builder.py`

**Reference**: See `prompts/personas/README.md` for current persona system

---

### component_specs.yaml
**Deprecated**: November 16, 2025  
**Reason**: Violates "Content Instruction Policy"

**Original Purpose**: Define component specifications including format rules, focus areas, and style notes

**Why Deprecated**:
- **Policy Violation**: Content instructions belong ONLY in `prompts/components/*.txt`, not config files
- Mixed content (WHAT to write) with configuration (word counts, technical settings)
- Created ambiguity about single source of truth for content instructions
- Hardcoded component types, preventing dynamic component discovery

**What Moved Where**:
- **Word Counts** → `processing/config.yaml` (component_lengths section)
- **Content Instructions** → `prompts/components/*.txt` (individual component prompt files)
- **Format Rules** → Removed (embedded in component prompts)
- **Focus Areas** → Removed (embedded in component prompts)
- **Style Notes** → Removed (embedded in component prompts)

**Migration Path**: 
- Configuration (word counts, end punctuation) → `processing/config.yaml`
- Content instructions (what to write, how to format) → `prompts/components/*.txt`
- Component discovery → Dynamic scanning of `prompts/components/` directory

**Reference**: 
- `docs/prompts/CONTENT_INSTRUCTION_POLICY.md` - Policy explanation
- `prompts/components/README.md` - Current component system
- `processing/config.yaml` - Configuration location

---

### unified_template.txt
**Deprecated**: Multiple iterations (2024-2025)  
**Reason**: Replaced by modular prompt system

**Original Purpose**: Single monolithic template for all content generation

**Why Deprecated**:
- Inflexible - all components used same template
- Hard to maintain - changes affected everything
- Poor separation - content, voice, and rules mixed together
- Difficult testing - couldn't isolate component specifications

**What Replaced It**:
- **Component Prompts** → `prompts/components/*.txt` (one file per component type)
- **Universal Rules** → `prompts/rules/*.txt` (constraints applied to all)
- **Author Voices** → `prompts/personas/*.yaml` (structured voice definitions)
- **Prompt Assembly** → `processing/generation/prompt_builder.py` (dynamic combination)

**Migration Path**: Modular system allows:
- Independent component editing
- Shared rule updates
- Per-author voice customization
- Dynamic prompt construction

**Reference**: 
- `prompts/README.md` - Current prompt system overview
- `docs/architecture/PROMPT_SEPARATION_ANALYSIS.md` - Migration rationale

---

## 🔍 Why Archive Instead of Delete?

Files are archived (not deleted) for:

1. **Historical Context**: Understand why current architecture exists
2. **Migration Reference**: Compare old vs new approaches
3. **Learning Resource**: See evolution of system design
4. **Rollback Safety**: Theoretical recovery if needed (though not recommended)
5. **Documentation**: Evidence of architectural decisions

**However**: Archived files should NEVER be used in active generation.

---

## 📜 Deprecation Timeline

| Date | File | Action | Reason |
|------|------|--------|--------|
| Nov 16, 2025 | `voice_rules.txt` | Archived | Zero references, replaced by personas |
| Nov 16, 2025 | `component_specs.yaml` | Archived | Violates content instruction policy |
| 2024-2025 | `unified_template.txt` | Archived | Replaced by modular system |

---

## 🚫 Common Mistakes to Avoid

### ❌ DON'T: Reference archived files in code
```python
# WRONG - references deprecated file
template = load_file('prompts/archive/voice_rules.txt')
```

### ✅ DO: Use current system
```python
# CORRECT - uses active persona system
persona = load_persona(author_id)
voice_instructions = persona['voice_instructions']
```

---

### ❌ DON'T: Copy content from archived specs
```yaml
# WRONG - copying from component_specs.yaml
focus_areas:
  - "unique characteristics"
  - "key benefits"
```

### ✅ DO: Write content instructions in component prompts
```
# CORRECT - in prompts/components/subtitle.txt
Focus on 1-2 unique characteristics that define this material.
Include a key application or benefit.
```

---

### ❌ DON'T: Use archived template structure
```
# WRONG - monolithic template approach
[unified template with all components]
```

### ✅ DO: Use modular prompt system
```
# CORRECT - separate files for each component
prompts/components/subtitle.txt
prompts/components/caption.txt
prompts/components/description.txt
```

---

## 📊 Verification: Confirm No Active Usage

To verify archived files are not referenced in active code:

```bash
# Check for voice_rules.txt references
grep -r "voice_rules" --include="*.py" processing/
# Expected: No results (or only comments/documentation)

# Check for component_specs.yaml references  
grep -r "component_specs.yaml" --include="*.py" processing/
# Expected: No results (or only comments/documentation)

# Check for unified_template.txt references
grep -r "unified_template" --include="*.py" processing/
# Expected: No results (or only comments/documentation)
```

**If you find active references**: File the issue - archived files should not be in production code paths.

---

## 🔗 Current System Documentation

Instead of using archived files, refer to:

### For Voice/Author Patterns:
- **Active System**: `prompts/personas/*.yaml`
- **Documentation**: `prompts/personas/README.md`
- **Code**: `processing/voice/store.py`

### For Component Specifications:
- **Active System**: `prompts/components/*.txt` (content) + `processing/config.yaml` (lengths)
- **Documentation**: `prompts/components/README.md`
- **Code**: `processing/generation/component_specs.py`, `processing/generation/prompt_builder.py`

### For Universal Rules:
- **Active System**: `prompts/rules/*.txt`
- **Documentation**: `prompts/rules/README.md`
- **Code**: `processing/generation/prompt_builder.py`

---

## 📝 Notes for Future Developers

**If considering un-archiving a file**:
1. Review why it was archived (see above)
2. Check if root issue was fixed
3. Verify it doesn't violate current policies
4. Get approval before reintegrating
5. Update all documentation

**If adding new files to archive**:
1. Verify no active code references (grep search)
2. Document deprecation reason above
3. Add migration path for users
4. Link to replacement system
5. Update this README

**If cleaning up archive**:
- Files older than 2 years with no references can be deleted
- Maintain git history for true archival
- Document deletion in git commit message

---

## 🚀 Quick Commands

**Verify archived files have no active references**:
```bash
# Search for voice_rules.txt
grep -r "voice_rules" --include="*.py" processing/

# Search for component_specs.yaml
grep -r "component_specs" --include="*.py" processing/

# Search for unified_template.txt
grep -r "unified_template" --include="*.py" processing/
```

**View deprecation timeline**:
```bash
# Check git history for when files were moved here
git log --follow -- prompts/archive/voice_rules.txt
git log --follow -- prompts/archive/component_specs.yaml
```

**Compare old vs new**:
```bash
# Compare archived spec to current component prompt
diff prompts/archive/component_specs.yaml prompts/components/subtitle.txt
```

---

## 📖 Related Documentation

- **Parent**: `prompts/README.md` - Current prompt system overview
- **Policy**: `docs/prompts/CONTENT_INSTRUCTION_POLICY.md` - Why component_specs.yaml was deprecated
- **Architecture**: `docs/architecture/PROMPT_SEPARATION_ANALYSIS.md` - System reorganization rationale
- **Migration**: `docs/architecture/PROMPT_OVERRIDE_ANALYSIS.md` - Original problem analysis

---

**Remember**: Archived files are **historical artifacts**, not production code. Always use the current system documented in `prompts/README.md`.
