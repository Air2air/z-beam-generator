# Shared Dynamic Prompt Architecture Proposal
**Date**: November 25, 2025  
**Purpose**: Unified prompting system for material image generation AND validation  
**Status**: 🎯 PROPOSED - Ready for Implementation

---

## 🎯 Objectives

1. **Single Source of Truth**: All prompting guidance in one shared location
2. **Dynamic Feedback Loop**: Update prompts based on validation results
3. **Zero Code Duplication**: Remove hardcoded prompts from generator/validator code
4. **Easy Iteration**: Review output → update prompts → regenerate (no code changes)
5. **Consistent Standards**: Generation and validation use identical quality criteria

---

## 🏗️ Proposed Architecture

### Directory Structure
```
domains/materials/image/prompts/
├── __init__.py
├── shared/                              # NEW - Shared prompt chain
│   ├── __init__.py
│   ├── generation/
│   │   ├── base_structure.txt          # Core image structure rules
│   │   ├── realism_physics.txt         # Physics constraints (NEW)
│   │   ├── contamination_rules.txt     # Contamination behavior (NEW)
│   │   ├── micro_scale_details.txt     # Grain following, stress points (NEW)
│   │   └── forbidden_patterns.txt      # Anti-patterns to avoid (NEW)
│   ├── validation/
│   │   ├── realism_criteria.txt        # Validation scoring rubric
│   │   ├── physics_checklist.txt       # Physics compliance tests
│   │   └── red_flags.txt               # AI mistake detection
│   └── feedback/                        # NEW - Human feedback integration
│       ├── iteration_log.yaml          # Track prompt improvements
│       ├── quality_adjustments.txt     # Latest quality guidance
│       └── user_corrections.txt        # Your manual corrections
├── material_researcher.py
├── category_contamination_researcher.py
└── prompt_builder.py                    # NEW - Replaces material_prompts.py

DEPRECATED (to be removed):
├── base_prompt.txt                      # Move to shared/generation/base_structure.txt
└── material_prompts.py                  # Replace with prompt_builder.py
```

### Key Changes

**1. Generation Prompt Chain** (4-layer system)
```
LAYER 1: Base Structure (shared/generation/base_structure.txt)
  → Core format: side-by-side, 16:9, same object, 5-10% shift
  
LAYER 2: Realism Physics (shared/generation/realism_physics.txt)
  → Gravity effects, accumulation zones, thickness variation
  → Environmental exposure (UV, moisture, stress points)
  → Natural layering and temporal sequence
  
LAYER 3: Contamination Rules (shared/generation/contamination_rules.txt)
  → Uneven distribution imperatives
  → Grain following, edge concentration
  → Material-specific interaction patterns
  
LAYER 4: Micro-Scale Details (shared/generation/micro_scale_details.txt)
  → Surface topology following
  → Porosity effects, stress point concentration
  → Feathering, undercutting, boundary transitions

ANTI-LAYER: Forbidden Patterns (shared/generation/forbidden_patterns.txt)
  → Painted-on appearance (AVOID)
  → Uniform coating (AVOID)
  → Symmetric patterns (AVOID)
  → Floating particles (AVOID)
```

**2. Validation Criteria** (mirrors generation)
```
shared/validation/realism_criteria.txt
  → 90-100: Photorealistic (maps to generation realism_physics.txt)
  → 75-89: Good realism (maps to contamination_rules.txt)
  → 60-74: Acceptable (maps to micro_scale_details.txt)
  → 0-59: Fails (violates forbidden_patterns.txt)

shared/validation/physics_checklist.txt
  → Exact same physics rules as generation/realism_physics.txt
  → Ensures validator checks what generator was told to create

shared/validation/red_flags.txt
  → Exact inverse of generation/forbidden_patterns.txt
  → Detects violations of what generator was told to avoid
```

**3. Feedback Integration Loop**
```
USER WORKFLOW:
1. Generate image with current prompts
2. Review output quality
3. Edit shared/feedback/user_corrections.txt:
   "Image #123: Contamination too uniform on edges.
    CORRECTION: Emphasize edge concentration with 50%+ thickness."
4. Regenerate → prompt_builder.py automatically includes feedback
5. Validate → validator uses same updated criteria

FEEDBACK FILE FORMAT:
shared/feedback/user_corrections.txt
---
# Quality Adjustments (Applied to ALL future generations)

## Edge Contamination (Updated: 2025-11-25)
ISSUE: Edges showing uniform coating
FIX: "Edge areas must show 50-80% heavier contamination due to 
     capillary action. Concentration gradient from edge (thick) 
     to center (thin)."
PRIORITY: HIGH

## Gravity Effects (Updated: 2025-11-25)  
ISSUE: Vertical surfaces not showing drips
FIX: "Vertical surfaces MUST show 3-5 visible drip patterns.
     Drips follow gravity: wider at top, narrower at bottom."
PRIORITY: CRITICAL

## Material Appearance (Updated: 2025-11-24)
ISSUE: Clean side looks too pristine
FIX: "Clean side should retain 5-10% base oxidation/aging.
     NOT brand new - shows material age under contamination."
PRIORITY: MEDIUM
---
```

---

## 📝 Implementation Plan

### Phase 1: Extract Prompts from Code (2 hours)

**Step 1.1**: Create shared prompt directory structure
```bash
mkdir -p domains/materials/image/prompts/shared/{generation,validation,feedback}
```

**Step 1.2**: Extract generation prompts
- Move `base_prompt.txt` → `shared/generation/base_structure.txt`
- Extract physics rules from `material_prompts.py` → `shared/generation/realism_physics.txt` (NEW)
- Extract contamination imperatives → `shared/generation/contamination_rules.txt` (NEW)
- Extract micro-scale guidance → `shared/generation/micro_scale_details.txt` (NEW)
- Create `shared/generation/forbidden_patterns.txt` (NEW)

**Step 1.3**: Extract validation prompts
- Extract from `validator.py` line 243-338 → `shared/validation/realism_criteria.txt`
- Extract physics checks → `shared/validation/physics_checklist.txt`
- Extract red flags → `shared/validation/red_flags.txt`

**Step 1.4**: Create feedback templates
```bash
touch shared/feedback/iteration_log.yaml
touch shared/feedback/quality_adjustments.txt
touch shared/feedback/user_corrections.txt
```

### Phase 2: Build Prompt Loader (1 hour)

**Create `prompt_builder.py`**:
```python
#!/usr/bin/env python3
"""
Shared Dynamic Prompt Builder

Loads prompts from shared/ directory for BOTH generation and validation.
Automatically integrates user feedback from feedback/ files.

Author: AI Assistant
Date: November 25, 2025
"""

from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SharedPromptBuilder:
    """
    Loads and assembles prompts from shared directory.
    
    Used by BOTH MaterialImageGenerator and MaterialImageValidator
    to ensure consistent standards.
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """Initialize with shared prompts directory."""
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent / "shared"
        
        self.prompts_dir = prompts_dir
        self.generation_dir = prompts_dir / "generation"
        self.validation_dir = prompts_dir / "validation"
        self.feedback_dir = prompts_dir / "feedback"
        
        # Validate directory structure
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Shared prompts directory not found: {self.prompts_dir}")
        
        logger.info(f"✅ Shared prompt builder initialized: {self.prompts_dir}")
    
    def build_generation_prompt(
        self,
        material_name: str,
        research_data: Dict,
        contamination_level: int = 3,
        contamination_uniformity: int = 3,
        view_mode: str = "Contextual",
        environment_wear: int = 3
    ) -> str:
        """
        Build complete generation prompt from shared templates + user feedback.
        
        Loads:
        - base_structure.txt (core format)
        - realism_physics.txt (physics constraints)
        - contamination_rules.txt (distribution rules)
        - micro_scale_details.txt (micro-scale guidance)
        - forbidden_patterns.txt (anti-patterns)
        - feedback/user_corrections.txt (your latest adjustments)
        
        Returns:
            Complete prompt string for Imagen 4
        """
        prompt_parts = []
        
        # Layer 1: Base Structure
        base = self._load_template(self.generation_dir / "base_structure.txt")
        base = self._replace_variables(base, material_name, research_data, 
                                       contamination_level, contamination_uniformity,
                                       view_mode, environment_wear)
        prompt_parts.append(base)
        
        # Layer 2: Realism Physics
        physics = self._load_template(self.generation_dir / "realism_physics.txt")
        prompt_parts.append(physics)
        
        # Layer 3: Contamination Rules
        contamination = self._load_template(self.generation_dir / "contamination_rules.txt")
        prompt_parts.append(contamination)
        
        # Layer 4: Micro-Scale Details
        micro_scale = self._load_template(self.generation_dir / "micro_scale_details.txt")
        prompt_parts.append(micro_scale)
        
        # Anti-Layer: Forbidden Patterns
        forbidden = self._load_template(self.generation_dir / "forbidden_patterns.txt")
        prompt_parts.append(f"AVOID: {forbidden}")
        
        # User Feedback Integration
        feedback = self._load_feedback()
        if feedback:
            prompt_parts.append(f"CRITICAL CORRECTIONS (from review):\n{feedback}")
        
        return "\n\n".join(prompt_parts)
    
    def build_validation_prompt(
        self,
        material_name: str,
        research_data: Dict,
        config: Optional[Dict] = None
    ) -> str:
        """
        Build validation prompt using SAME standards as generation.
        
        Loads:
        - validation/realism_criteria.txt (scoring rubric)
        - validation/physics_checklist.txt (mirrors generation physics)
        - validation/red_flags.txt (mirrors generation forbidden patterns)
        - feedback/user_corrections.txt (ensures validator checks new rules)
        
        Returns:
            Complete validation prompt for Gemini Vision
        """
        prompt_parts = []
        
        # Header with material context
        patterns = research_data.get('selected_patterns', [])
        pattern_names = [p.get('pattern_name', p.get('name', 'Unknown')) for p in patterns[:3]]
        
        contamination_level = config.get('contamination_level', 3) if config else 3
        uniformity = config.get('contamination_uniformity', 3) if config else 3
        view_mode = config.get('view_mode', 'Contextual') if config else 'Contextual'
        
        prompt_parts.append(f"""Analyze this material before/after laser cleaning image of {material_name}.

EXPECTED CHARACTERISTICS:
- Material: {material_name}
- Contamination patterns: {', '.join(pattern_names)}
- Contamination intensity: {contamination_level}/5
- Contamination variety: {uniformity}/5
- View mode: {view_mode}
""")
        
        # Realism Criteria (maps to generation standards)
        criteria = self._load_template(self.validation_dir / "realism_criteria.txt")
        prompt_parts.append(criteria)
        
        # Physics Checklist (exact same as generation physics)
        physics = self._load_template(self.validation_dir / "physics_checklist.txt")
        prompt_parts.append(physics)
        
        # Red Flags (exact inverse of generation forbidden patterns)
        red_flags = self._load_template(self.validation_dir / "red_flags.txt")
        prompt_parts.append(red_flags)
        
        # User Feedback (validator checks updated criteria)
        feedback = self._load_feedback()
        if feedback:
            prompt_parts.append(f"UPDATED VALIDATION CRITERIA (from review):\n{feedback}")
        
        # JSON response format
        prompt_parts.append(self._get_validation_json_format())
        
        return "\n\n".join(prompt_parts)
    
    def _load_template(self, template_path: Path) -> str:
        """Load prompt template from file."""
        if not template_path.exists():
            logger.warning(f"⚠️  Template not found: {template_path}")
            return ""
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def _load_feedback(self) -> str:
        """Load latest user feedback corrections."""
        feedback_path = self.feedback_dir / "user_corrections.txt"
        
        if not feedback_path.exists():
            return ""
        
        feedback = self._load_template(feedback_path)
        if feedback:
            logger.info(f"📝 Applied user feedback from {feedback_path.name}")
        
        return feedback
    
    def _replace_variables(self, template: str, material_name: str, 
                          research_data: Dict, contamination_level: int,
                          contamination_uniformity: int, view_mode: str,
                          environment_wear: int) -> str:
        """Replace template variables with actual values."""
        common_object = research_data.get('common_object', f'{material_name} object')
        environment = research_data.get('typical_environment', 'typical environment')
        
        patterns = research_data.get('selected_patterns', research_data.get('contaminants', []))
        contamination_section = self._build_contamination_section(patterns)
        
        replacements = {
            '{MATERIAL}': material_name,
            '{COMMON_OBJECT}': common_object,
            '{ENVIRONMENT}': environment,
            '{CONTAMINATION_LEVEL}': str(contamination_level),
            '{UNIFORMITY}': str(contamination_uniformity),
            '{VIEW_MODE}': view_mode,
            '{ENVIRONMENT_WEAR}': str(environment_wear),
            '{CONTAMINANTS_SECTION}': contamination_section
        }
        
        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)
        
        return result
    
    def _build_contamination_section(self, patterns: list) -> str:
        """Build contamination list from research patterns."""
        if not patterns:
            raise ValueError("No contamination patterns provided")
        
        lines = []
        for pattern in patterns[:4]:
            if 'pattern_name' in pattern:
                name = pattern['pattern_name']
                visual = pattern.get('visual_characteristics', {})
                color = visual.get('color_range', 'varied tones')
                texture = visual.get('texture_detail', 'varied texture')
                lines.append(f"{name}: {color}, {texture}")
            else:
                name = pattern.get('name', 'contamination')
                appearance = pattern.get('appearance', {})
                color = appearance.get('color', 'dark')
                texture = appearance.get('texture', 'uneven')
                lines.append(f"{name}: {color}, {texture}")
        
        return ". ".join(lines) + "."
    
    def _get_validation_json_format(self) -> str:
        """Return JSON response format for validation."""
        return """RESPOND IN JSON FORMAT:
{
  "realism_score": <0-100>,
  "same_object": <true/false>,
  "position_shift_appropriate": <true/false>,
  "damage_consistent": <true/false>,
  "physics_compliant": <true/false>,
  "physics_issues": ["<issue1>", ...] or [],
  "distribution_realistic": <true/false>,
  "distribution_issues": ["<issue1>", ...] or [],
  "layering_natural": <true/false>,
  "layering_issues": ["<issue1>", ...] or [],
  "clean_side_accurate": <true/false>,
  "material_appearance_issues": ["<issue1>", ...] or [],
  "contamination_matches_research": <true/false>,
  "research_deviations": ["<deviation1>", ...] or [],
  "micro_scale_accurate": <true/false>,
  "micro_scale_issues": ["<issue1>", ...] or [],
  "confidence": <0.0-1.0>,
  "overall_assessment": "<2-3 sentence summary>",
  "recommendations": ["<improvement1>", ...] or []
}

SCORING GUIDANCE:
- 90-100: Photorealistic, all physics correct, excellent micro-details
- 75-89: Good realism, minor issues, mostly authentic
- 60-74: Acceptable, noticeable artificial elements
- 40-59: Poor realism, significant issues
- 0-39: Fails validation, looks AI-generated"""


def create_prompt_builder() -> SharedPromptBuilder:
    """Factory function to create shared prompt builder."""
    return SharedPromptBuilder()
```

### Phase 3: Update Generator (30 minutes)

**Modify `material_generator.py`**:
```python
# Replace:
from domains.materials.image.prompts.material_prompts import build_material_cleaning_prompt

# With:
from domains.materials.image.prompts.prompt_builder import SharedPromptBuilder

# In __init__:
self.prompt_builder = SharedPromptBuilder()

# In generate_prompt():
return self.prompt_builder.build_generation_prompt(
    material_name=material_name,
    research_data=research_data,
    contamination_level=config.contamination_level,
    contamination_uniformity=config.contamination_uniformity,
    view_mode=config.view_mode,
    environment_wear=config.environment_wear
)
```

### Phase 4: Update Validator (30 minutes)

**Modify `validator.py`**:
```python
# Add to __init__:
from domains.materials.image.prompts.prompt_builder import SharedPromptBuilder

self.prompt_builder = SharedPromptBuilder()

# Replace _build_material_validation_prompt():
def _build_material_validation_prompt(
    self,
    material_name: str,
    research_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> str:
    """Build validation prompt using shared templates."""
    return self.prompt_builder.build_validation_prompt(
        material_name=material_name,
        research_data=research_data,
        config=config
    )
```

### Phase 5: Create Initial Templates (1 hour)

**Example: `shared/generation/realism_physics.txt`**:
```
REALISM PHYSICS (CRITICAL - Non-negotiable physical laws):

1. GRAVITY EFFECTS:
   - Drips flow DOWNWARD on vertical surfaces (3-5 visible drip patterns)
   - Pooling in LOW areas (bottom edges, horizontal surfaces)
   - Runs follow VERTICAL orientation (not horizontal)
   - Heavier contamination accumulates at BOTTOM due to settling

2. ACCUMULATION ZONES:
   - Crevices and JOINTS: 50-80% heavier contamination
   - EDGES and seams: Capillary action causes concentration
   - CORNERS: Multiple-surface convergence increases buildup
   - Horizontal SURFACES: Dust settling creates even layer

3. ENVIRONMENTAL EXPOSURE:
   - UV-facing surfaces: MORE oxidation, chalking, fading
   - SHADED areas: Moisture retention causes different patterns
   - Weather-facing: Wind/rain creates directional patterns
   - Stress points: Cracks, bends show concentrated aging

4. THICKNESS VARIATION:
   - Transparent thin layers (light contamination)
   - Translucent medium layers (moderate contamination)
   - OPAQUE thick buildup (heavy contamination zones)
   - Gradual TRANSITIONS (not sharp boundaries)

5. NATURAL LAYERING:
   - Temporal SEQUENCE: Base corrosion → Dirt → Weathering
   - Older layers UNDER newer layers (stratigraphy)
   - Different contamination TYPES interact naturally
   - No "painted on" appearance (organic accumulation)
```

**Example: `shared/validation/physics_checklist.txt`**:
```
PHYSICS COMPLIANCE CHECKLIST:

Check EACH of these physical requirements:

□ Gravity Effects:
  - Drips flow downward (not horizontal/upward)
  - Pooling in low areas (not on vertical surfaces)
  - Vertical runs (not horizontal streaks)
  - Bottom-heavy distribution (not top-heavy)

□ Accumulation Zones:
  - Crevices 50-80% heavier (not uniform)
  - Edge concentration visible (not evenly distributed)
  - Corner buildup present (not absent)
  - Horizontal surface dust layer (if present)

□ Environmental Exposure:
  - UV side more oxidized (if applicable)
  - Shaded areas show moisture effects (if applicable)
  - Weather patterns directional (if applicable)
  - Stress points concentrated aging (visible damage)

□ Thickness Variation:
  - Thin transparent → thick opaque gradient
  - NOT uniform coating thickness
  - Gradual transitions (not sharp boundaries)
  - Natural thickness distribution

□ Layering:
  - Base corrosion under dirt (temporal sequence)
  - Multiple contaminant types stacked
  - NOT "painted on" appearance
  - Organic accumulation visible

PHYSICS_COMPLIANT = ALL checkboxes ✓
```

**Example: `shared/feedback/user_corrections.txt`** (Template):
```
# Material Image Quality Corrections
# Updated: 2025-11-25
# 
# Add your feedback here after reviewing generated images.
# Format: Issue description → Fix instruction
# Priority: CRITICAL (must fix) | HIGH (should fix) | MEDIUM (nice to have)

---

## [TEMPLATE - Delete this section when you add real feedback]

ISSUE: [Describe what's wrong with the output]
FIX: "[Exact instruction to add to prompts]"
PRIORITY: [CRITICAL | HIGH | MEDIUM]
EXAMPLES: [Image IDs or filenames showing the issue]

---

# Your Corrections Below This Line:

```

---

## 🎯 Benefits

### For You (User)
1. **Easy Iteration**: Edit text files → regenerate → see improvements (no code changes)
2. **Feedback Workflow**: Document issues in `user_corrections.txt` → automatically applied
3. **Quality Control**: Validator uses same standards as generator (consistency)
4. **Debugging**: See exact prompts used for generation/validation (transparency)

### For System
1. **DRY Principle**: Zero duplication of physics rules, criteria, patterns
2. **Consistency**: Generator and validator always in sync
3. **Maintainability**: Change one file → affects both generation and validation
4. **Auditability**: Git tracks all prompt iterations (`feedback/iteration_log.yaml`)

### For Quality
1. **Faster Improvement**: Iterate on prompts without code changes
2. **Cumulative Learning**: Each correction builds on previous ones
3. **Traceable Evolution**: See what changed and why in feedback logs
4. **Systematic Refinement**: Structured approach to quality enhancement

---

## 📊 Compliance Check

### ✅ Follows All Policies

**1. Fail-Fast Architecture**: 
- `SharedPromptBuilder.__init__()` raises FileNotFoundError if directory missing
- No fallback to hardcoded prompts

**2. Zero Hardcoded Values**:
- All prompt text externalized to .txt files
- No hardcoded criteria in code

**3. Configuration-Driven**:
- Material properties from research_data (not hardcoded)
- Contamination levels from MaterialImageConfig
- Feedback from user_corrections.txt (dynamic)

**4. Template-Only Policy**:
- Zero prompt text in generator/validator code
- All prompts loaded from shared/ templates

**5. Prompt Purity Policy**:
- No inline prompt construction in code
- prompt_builder.py ONLY loads and assembles templates

**6. Documentation First**:
- This proposal IS the documentation
- Implementation follows documented architecture

---

## 🚀 Quick Start After Implementation

### Workflow: Generate → Review → Improve

**1. Generate image**:
```bash
python3 domains/materials/image/generate.py \
  --material "Aluminum" \
  --contamination-level 3 \
  --output aluminum_test_001.png
```

**2. Review output**:
- Check: Is contamination realistic?
- Check: Are physics correct (gravity, accumulation)?
- Check: Does validation agree with your assessment?

**3. Document feedback**:
Edit `domains/materials/image/prompts/shared/feedback/user_corrections.txt`:
```
ISSUE: Aluminum showing uniform edge coating (not realistic)
FIX: "Aluminum edge areas MUST show 60-75% heavier contamination
     due to oxide formation at edges. Create clear gradient from
     edge (thick oxide) to center (thinner contamination)."
PRIORITY: HIGH
EXAMPLES: aluminum_test_001.png, aluminum_test_002.png
```

**4. Regenerate**:
```bash
python3 domains/materials/image/generate.py \
  --material "Aluminum" \
  --contamination-level 3 \
  --output aluminum_test_003.png
```
→ New image automatically includes your edge gradient instruction

**5. Validate improvement**:
```bash
python3 domains/materials/image/validate.py \
  --image aluminum_test_003.png \
  --material "Aluminum"
```
→ Validator checks for edge gradient (same standard)

---

## 📋 Implementation Checklist

- [ ] Phase 1: Create shared/ directory structure (15 min)
- [ ] Phase 1: Extract generation prompts to 5 template files (45 min)
- [ ] Phase 1: Extract validation prompts to 3 template files (30 min)
- [ ] Phase 1: Create feedback template files (15 min)
- [ ] Phase 2: Implement SharedPromptBuilder class (1 hour)
- [ ] Phase 3: Update MaterialImageGenerator to use SharedPromptBuilder (30 min)
- [ ] Phase 4: Update MaterialImageValidator to use SharedPromptBuilder (30 min)
- [ ] Phase 5: Create initial template content (1 hour)
- [ ] Phase 6: Test generation with new system (15 min)
- [ ] Phase 7: Test validation with new system (15 min)
- [ ] Phase 8: Document feedback workflow in README (15 min)
- [ ] Phase 9: Delete deprecated files (base_prompt.txt, material_prompts.py) (5 min)

**Total Estimated Time**: 5 hours 35 minutes

---

## 🎓 Next Steps

1. **Review this proposal** - Does this architecture meet your needs?
2. **Approve implementation** - Ready to proceed with Phase 1?
3. **Provide initial feedback** - Any specific quality issues to address in templates?

**Question**: Would you like me to proceed with implementation, or would you like to adjust the architecture first?

