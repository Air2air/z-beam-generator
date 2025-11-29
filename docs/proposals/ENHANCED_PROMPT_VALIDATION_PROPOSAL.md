# Enhanced Prompt Validation Proposal

**Date**: November 28, 2025  
**Status**: PROPOSAL  
**Author**: AI Assistant  

## Problem Statement

Current validation system has several limitations:

1. **Fragmented Architecture**: Validation spread across multiple files (`validator.py`, `prompt_validator.py`, `validate_feedback.py`, `orchestrator.py`) with inconsistent interfaces
2. **Late Detection**: Many issues caught only after image generation (expensive)
3. **Limited AI Assistant Support**: Validation errors not actionable - assistants don't know HOW to fix issues
4. **No Staged Validation**: Can't validate intermediate stages of the prompt chain
5. **Missing Auto-Fix**: Issues identified but never auto-corrected
6. **Inconsistent Reporting**: Different validation tools use different output formats

## Proposed Architecture: Unified Validation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED VALIDATION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │ Stage 1: EARLY  │    │ Stage 2: PROMPT │    │ Stage 3: POST   │     │
│  │ (Pre-Research)  │────│ (Pre-Generation)│────│ (Post-Image)    │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│          │                       │                      │               │
│          ▼                       ▼                      ▼               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │ • Config check  │    │ • Length check  │    │ • Realism score │     │
│  │ • Material valid│    │ • Logic check   │    │ • Prompt comply │     │
│  │ • Template load │    │ • Quality check │    │ • Physics check │     │
│  │ • Feedback sync │    │ • Auto-optimize │    │ • Text detection│     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│          │                       │                      │               │
│          └───────────────────────┼──────────────────────┘               │
│                                  ▼                                      │
│                    ┌─────────────────────────┐                          │
│                    │   UNIFIED RESULT API    │                          │
│                    │   ValidationReport      │                          │
│                    └─────────────────────────┘                          │
│                                  │                                      │
│                    ┌─────────────┼─────────────┐                        │
│                    ▼             ▼             ▼                        │
│              ┌─────────┐   ┌─────────┐   ┌─────────┐                   │
│              │  JSON   │   │ Report  │   │  Fix    │                   │
│              │ Export  │   │ Format  │   │ Actions │                   │
│              └─────────┘   └─────────┘   └─────────┘                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. ValidationReport (Unified Result Object)

```python
@dataclass
class ValidationReport:
    """Universal validation result usable by humans AND AI assistants."""
    
    # Overall status
    status: Literal['PASS', 'WARN', 'FAIL', 'CRITICAL']
    stage: Literal['early', 'prompt', 'post']
    
    # Scores
    scores: Dict[str, float]  # {'realism': 85.0, 'compliance': 92.0, ...}
    
    # Issues with actionable fixes
    issues: List[ValidationIssue]
    
    # AI Assistant Support
    fix_actions: List[FixAction]  # Programmatic fixes
    fix_instructions: str         # Natural language for AI
    
    # Context for learning
    attempt_number: int
    material: str
    component_type: str
    
    def get_ai_prompt(self) -> str:
        """Get prompt snippet for AI assistant to fix issues."""
        
    def apply_auto_fixes(self, prompt: str) -> str:
        """Apply all safe auto-fixes and return corrected prompt."""
        
    def to_json(self) -> str:
        """Export for logging/learning."""
        
    def to_report(self) -> str:
        """Human-readable report."""
```

### 2. FixAction (Programmatic Auto-Fix)

```python
@dataclass
class FixAction:
    """Single actionable fix that can be auto-applied."""
    
    action_type: Literal['replace', 'remove', 'append', 'prepend', 'optimize']
    severity: Literal['critical', 'high', 'medium', 'low']
    description: str
    
    # For auto-application
    target: str           # What to find
    replacement: str      # What to replace with (if applicable)
    location: str         # Where in prompt
    
    # For AI assistants
    ai_instruction: str   # Natural language: "Replace 'thick buildup' with 'thin film'"
    
    # Safety
    safe_to_auto_apply: bool  # True = can apply automatically
    requires_review: bool     # True = AI should verify
    
    def apply(self, text: str) -> str:
        """Apply this fix to text."""
```

### 3. ValidationStage (Stage-Specific Validators)

```python
class EarlyStageValidator:
    """Validates BEFORE any prompt building."""
    
    def validate(self, material: str, config: Dict) -> ValidationReport:
        """
        Check:
        - Material exists in Materials.yaml
        - Config values valid
        - Required templates exist
        - Feedback consistency
        - API keys configured
        """

class PromptStageValidator:
    """Validates BEFORE API call."""
    
    def validate(self, prompt: str, negative: str, config: Dict) -> ValidationReport:
        """
        Check:
        - Length within limits (4096 chars)
        - No contradictions
        - No duplications
        - Physics rules present
        - Anti-text terms present
        - Auto-optimize if needed
        """

class PostStageValidator:
    """Validates AFTER image generation."""
    
    def validate(self, image_path: Path, prompt: str, research: Dict) -> ValidationReport:
        """
        Check:
        - Realism score (via Gemini Vision)
        - Prompt compliance
        - Physics adherence
        - Text/label detection
        - Before/after consistency
        """
```

### 4. UnifiedValidator (Orchestrating All Stages)

```python
class UnifiedValidator:
    """
    Single entry point for all validation.
    
    AI Assistant Usage:
        validator = UnifiedValidator()
        
        # Early check (before building prompt)
        report = validator.validate_early(material="Aluminum", config={...})
        if report.status == 'FAIL':
            print(report.fix_instructions)  # AI gets natural language fix guide
            return
        
        # Prompt check (before API call)
        report = validator.validate_prompt(prompt, negative_prompt)
        if report.status == 'FAIL':
            prompt = report.apply_auto_fixes(prompt)  # Auto-fix what's possible
        
        # Post check (after image)
        report = validator.validate_image(image_path, prompt, research)
        if report.status == 'FAIL':
            print(report.get_ai_prompt())  # Get correction prompt for retry
    """
    
    def __init__(self):
        self.early = EarlyStageValidator()
        self.prompt = PromptStageValidator()
        self.post = PostStageValidator()
    
    def validate_early(self, material: str, config: Dict) -> ValidationReport:
        """Stage 1: Pre-research validation."""
        
    def validate_prompt(self, prompt: str, negative: str = None, **context) -> ValidationReport:
        """Stage 2: Pre-generation validation with auto-fix."""
        
    def validate_image(self, image_path: Path, prompt: str, research: Dict) -> ValidationReport:
        """Stage 3: Post-generation validation."""
        
    def full_pipeline(self, material: str, config: Dict, prompt: str, 
                      negative: str, image_path: Path, research: Dict) -> Dict[str, ValidationReport]:
        """Run all stages and return combined report."""
```

## AI Assistant Integration

### Natural Language Fix Instructions

```python
# Instead of cryptic error messages:
"❌ CRITICAL (LENGTH): Prompt exceeds IMAGEN API hard limit: 4500/4096 chars"

# Provide actionable AI instructions:
report.fix_instructions = """
FIX REQUIRED: Prompt is 404 characters over the 4096 limit.

RECOMMENDED ACTIONS (in order):
1. Remove duplicate phrases (found 3 duplicates, saves ~200 chars)
   - "contamination settles at bottom" appears 2x
   - "thin surface films" appears 3x

2. Condense verbose sections (saves ~150 chars)
   - Replace "photographed from TWO DIFFERENT HORIZONTAL ANGLES" with "split view"
   - Remove redundant "CRITICAL:" labels

3. Truncate low-priority content (saves ~100 chars)
   - Can remove 2 micro-scale detail items
   - Can shorten contamination descriptions

APPLY AUTO-FIX: Call report.apply_auto_fixes(prompt) to apply safe fixes automatically.
"""
```

### Programmatic Fix Actions

```python
report.fix_actions = [
    FixAction(
        action_type='replace',
        severity='high',
        description='Remove duplicate phrase',
        target='contamination settles at bottom',
        replacement='',  # Remove second occurrence
        location='lines 45-47',
        ai_instruction='Remove the duplicate "contamination settles at bottom" on line 47',
        safe_to_auto_apply=True,
        requires_review=False
    ),
    FixAction(
        action_type='optimize',
        severity='medium', 
        description='Condense verbose opening',
        target='photographed from TWO DIFFERENT HORIZONTAL ANGLES',
        replacement='split view',
        location='line 1',
        ai_instruction='Shorten "photographed from TWO DIFFERENT HORIZONTAL ANGLES" to "split view"',
        safe_to_auto_apply=True,
        requires_review=False
    ),
]
```

### Auto-Fix Application

```python
# AI assistant can apply fixes automatically:
if report.status == 'FAIL':
    # Apply all safe fixes
    fixed_prompt = report.apply_auto_fixes(prompt)
    
    # Re-validate
    new_report = validator.validate_prompt(fixed_prompt)
    
    if new_report.status == 'PASS':
        print("✅ Auto-fixes resolved all issues")
    else:
        # Manual fixes needed
        print(new_report.fix_instructions)
```

## Feedback Consistency Validation

### Enhanced Conflict Detection

```python
class FeedbackConsistencyChecker:
    """
    Validates feedback rules don't contradict each other.
    
    Runs automatically when:
    - User adds new feedback
    - Before every generation
    - When templates are modified
    """
    
    # Enhanced conflict rules
    CONFLICT_RULES = {
        'thickness': {
            'prohibited': ['thick', 'heavy', 'caked', 'buildup', 'glob'],
            'required': ['thin', 'film', 'patina', 'dusting', 'light'],
            'context_exceptions': ['prohibition_list', 'never_statements']
        },
        'cleanliness': {
            'prohibited': ['perfectly clean', '100% clean', 'spotless'],
            'required': ['residual', 'traces', '5-10%', 'subtle'],
            'context_exceptions': []
        },
        # ... more rules
    }
    
    def check_consistency(self) -> ValidationReport:
        """Check all templates for contradictions."""
        
    def suggest_resolution(self, conflict: Conflict) -> str:
        """Suggest how to resolve a conflict."""
```

## Implementation Plan

### Phase 1: Core Infrastructure (2 hours)
1. Create `shared/validation/unified_validator.py`
2. Implement `ValidationReport` and `FixAction` dataclasses
3. Migrate existing validation logic to new structure

### Phase 2: Stage Validators (3 hours)
1. Implement `EarlyStageValidator`
2. Implement `PromptStageValidator` with auto-fix
3. Implement `PostStageValidator` (migrate from existing)

### Phase 3: AI Integration (2 hours)
1. Add natural language fix instructions
2. Add programmatic fix actions
3. Add `apply_auto_fixes()` method

### Phase 4: Feedback Consistency (1 hour)
1. Migrate `validate_feedback.py` to new system
2. Add context-aware conflict detection
3. Add resolution suggestions

### Phase 5: Testing & Documentation (2 hours)
1. Unit tests for each validator
2. Integration tests for full pipeline
3. Update copilot-instructions.md with new API

## Benefits

1. **Unified API**: Single `UnifiedValidator` class for all validation
2. **AI-Friendly**: Natural language instructions + programmatic fixes
3. **Auto-Fix**: Safe fixes applied automatically
4. **Staged Validation**: Catch issues early (before expensive API calls)
5. **Consistent Output**: Same `ValidationReport` format everywhere
6. **Learning Integration**: JSON export for learning database

## Migration Path

```python
# OLD API (multiple validators, inconsistent interfaces):
from domains.materials.image.validator import MaterialImageValidator
from shared.validation.prompt_validator import validate_image_prompt
from domains.materials.image.tools.validate_feedback import FeedbackValidator

validator = MaterialImageValidator(api_key)
result1 = validator.validate_material_image(...)  # Returns MaterialValidationResult
result2 = validate_image_prompt(prompt)           # Returns PromptValidationResult
result3 = FeedbackValidator().validate_all()      # Returns Dict

# NEW API (unified):
from shared.validation import UnifiedValidator

validator = UnifiedValidator()
report = validator.validate_early(material, config)     # Returns ValidationReport
report = validator.validate_prompt(prompt, negative)    # Returns ValidationReport
report = validator.validate_image(path, prompt, data)   # Returns ValidationReport
```

## Example Usage for AI Assistants

```python
# In generate.py main():

validator = UnifiedValidator()

# Stage 1: Early validation
early_report = validator.validate_early(
    material=args.material,
    config={'category': category, 'uniformity': config.contamination_uniformity}
)

if early_report.status == 'FAIL':
    logger.error(f"❌ Early validation failed:\n{early_report.fix_instructions}")
    sys.exit(1)

# Build prompt...

# Stage 2: Prompt validation with auto-fix
prompt_report = validator.validate_prompt(
    prompt=prompt_package['prompt'],
    negative=prompt_package['negative_prompt'],
    material=args.material
)

if prompt_report.status in ('FAIL', 'WARN'):
    # Auto-fix what's possible
    prompt_package['prompt'] = prompt_report.apply_auto_fixes(prompt_package['prompt'])
    logger.info(f"🔧 Applied {len(prompt_report.fix_actions)} auto-fixes")
    
    # Check if still failing
    recheck = validator.validate_prompt(prompt_package['prompt'])
    if recheck.status == 'FAIL':
        logger.error(f"❌ Manual fixes needed:\n{recheck.fix_instructions}")
        sys.exit(1)

# Generate image...

# Stage 3: Post validation
post_report = validator.validate_image(
    image_path=output_path,
    prompt=prompt_package['prompt'],
    research=prompt_package['research_data']
)

if post_report.status == 'FAIL':
    # Get correction prompt for retry
    correction = post_report.get_ai_prompt()
    logger.info(f"🔄 Retry with corrections:\n{correction}")
```

## Next Steps

1. **Review proposal** - Get feedback on architecture
2. **Prototype** - Build minimal `UnifiedValidator` with one stage
3. **Migrate** - Move existing validation to new structure
4. **Test** - Verify all existing functionality works
5. **Document** - Update copilot-instructions.md

---

**Approval Required**: This is a significant architectural change. Please review and approve before implementation.
