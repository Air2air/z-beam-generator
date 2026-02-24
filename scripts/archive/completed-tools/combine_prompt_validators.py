"""Helper: combine prompt_validator + prompt_coherence_validator into prompt_validators.py"""
import pathlib
import re

root = pathlib.Path(__file__).parent.parent.parent
content_dir = root / 'shared' / 'validation' / 'content'

pv_text = (content_dir / 'prompt_validator.py').read_text()
pcv_text = (content_dir / 'prompt_coherence_validator.py').read_text()

# ── Strip warnings from prompt_validator ──────────────────────────────────────
pv_clean = re.sub(r'^import warnings\n', '', pv_text, flags=re.MULTILINE)
pv_clean = re.sub(
    r'\n# Emit deprecation warning on module import\nwarnings\.warn\([^)]+\)\n',
    '\n',
    pv_clean,
    flags=re.DOTALL,
)

# ── Extract body (everything from 'import logging' onward) ────────────────────
def extract_body(text: str) -> str:
    """Strip module docstring, keep imports + code."""
    m = re.search(r'^import logging', text, re.MULTILINE)
    return text[m.start():].rstrip() if m else text.rstrip()

pv_body = extract_body(pv_clean)
pcv_body = extract_body(pcv_text)

# ── Deduplicate shared imports: pcv_body re-imports logging/re/dataclass/etc ──
# We rely on pv_body already having those; strip duplicate top-level import lines
# from pcv that are already declared in pv.
pv_imports = set(re.findall(r'^(?:import|from) .+', pv_body, re.MULTILINE))

def strip_duplicate_imports(body: str, already_imported: set) -> str:
    lines = body.splitlines()
    result = []
    for line in lines:
        if re.match(r'^(?:import|from) ', line) and line in already_imported:
            continue  # already in pv section
        result.append(line)
    return '\n'.join(result)

pcv_body_deduped = strip_duplicate_imports(pcv_body, pv_imports)

# ── Build combined file ───────────────────────────────────────────────────────
sep = '# ' + '=' * 77

combined_lines = [
    '"""',
    'Prompt Validators — Text/Image Quality + Coherence Checking',
    '=' * 62,
    '',
    'Canonical module for all prompt quality checks before API submission.',
    '',
    'Contains two validator families:',
    '',
    '1. Prompt Validator (text/image API limits, logic, quality, encoding):',
    '   - PromptValidator, PromptValidationResult, ValidationIssue',
    '   - validate_text_prompt, validate_image_prompt, validate_and_raise',
    '',
    '2. Coherence Validator (separation of concerns, contradictions):',
    '   - PromptCoherenceValidator, CoherenceValidationResult, CoherenceIssue',
    '   - validate_prompt_coherence',
    '',
    'Backward-compat shims at old import paths:',
    '  shared.validation.content.prompt_validator           → this module',
    '  shared.validation.content.prompt_coherence_validator → this module',
    '',
    'Created: November 27, 2025 (prompt_validator) / December 11, 2025 (coherence)',
    'Consolidated: February 23, 2026',
    'Policy: PROMPT_CHAINING_POLICY.md',
    '"""',
    '',
    '',
    sep,
    '# SECTION 1: Prompt Validator — Text and Image Generation',
    sep,
    '',
    pv_body,
    '',
    '',
    sep,
    '# SECTION 2: Coherence Validator — Separation of Concerns',
    sep,
    '',
    pcv_body_deduped,
    '',
]

combined = '\n'.join(combined_lines)
out_path = content_dir / 'prompt_validators.py'
out_path.write_text(combined)
print(f'Written {out_path} ({len(combined.splitlines())} lines)')
