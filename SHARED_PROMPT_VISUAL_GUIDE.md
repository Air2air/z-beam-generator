# Shared Dynamic Prompt System - Visual Architecture

## 🔄 Current System (Duplicated Prompts)

```
┌─────────────────────────────────────────────────────────────┐
│  MaterialImageGenerator                                     │
│  ├── Hardcoded physics rules in material_prompts.py        │
│  ├── Hardcoded contamination rules in material_prompts.py  │
│  └── Hardcoded base template in base_prompt.txt            │
└─────────────────────────────────────────────────────────────┘
                                ↓
                         [Generates Image]
                                ↓
┌─────────────────────────────────────────────────────────────┐
│  MaterialImageValidator                                     │
│  ├── Hardcoded physics checks in validator.py (line 243)   │
│  ├── Hardcoded contamination checks in validator.py        │
│  └── Hardcoded realism criteria in validator.py            │
└─────────────────────────────────────────────────────────────┘

❌ PROBLEM: Generator and validator have DIFFERENT criteria
❌ PROBLEM: Updating quality requires changing BOTH code files
❌ PROBLEM: Your feedback requires code edits (not text edits)
```

---

## ✅ Proposed System (Shared Prompts)

```
                    ┌─────────────────────────────────────────┐
                    │  shared/generation/                     │
                    │  ├── base_structure.txt                 │
                    │  ├── realism_physics.txt    ←───────────┼── You edit these
                    │  ├── contamination_rules.txt            │   to improve
                    │  ├── micro_scale_details.txt            │   quality
                    │  └── forbidden_patterns.txt             │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────────┐
                    │  SharedPromptBuilder                    │
                    │  (Loads templates + your feedback)      │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────────┐
                    │  shared/feedback/                       │
                    │  └── user_corrections.txt  ←─── You add │
                    │      (Your quality notes)       feedback│
                    └──────────────┬──────────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │                                          │
              ↓                                          ↓
┌──────────────────────────────┐      ┌──────────────────────────────┐
│  MaterialImageGenerator      │      │  MaterialImageValidator      │
│  Uses: SharedPromptBuilder   │      │  Uses: SharedPromptBuilder   │
│  ├── build_generation_prompt()│     │  ├── build_validation_prompt()│
│  └── (Zero hardcoded prompts)│      │  └── (Zero hardcoded checks) │
└──────────────┬───────────────┘      └───────────────┬──────────────┘
               │                                       │
               ↓                                       ↓
        [Generates Image]                      [Validates Image]
               │                                       │
               └───────────────┬───────────────────────┘
                               │
                               ↓
                    ┌─────────────────────────────────┐
                    │  shared/validation/             │
                    │  ├── realism_criteria.txt       │
                    │  ├── physics_checklist.txt      │
                    │  └── red_flags.txt              │
                    │  (Mirrors generation standards) │
                    └─────────────────────────────────┘

✅ BENEFIT: Generator and validator use IDENTICAL standards
✅ BENEFIT: Quality improvement = text file edits (no code changes)
✅ BENEFIT: Your feedback automatically applied to both systems
```

---

## 📝 Feedback Workflow

```
YOU                              SYSTEM                         OUTPUT
───                              ──────                         ──────

1. Generate image
   python3 generate.py
   --material Aluminum      →   Loads generation prompts    →  aluminum_001.png
                                 + your previous feedback

2. Review output
   [Image looks off:              
    edges too uniform]

3. Document feedback
   Edit:
   user_corrections.txt     →   Saved to shared/feedback/
   
   "ISSUE: Uniform edges
    FIX: Add 60-75% 
    gradient at edges"

4. Regenerate
   python3 generate.py
   --material Aluminum      →   Loads prompts               →  aluminum_002.png
                                 + NEW edge gradient rule       (Better!)

5. Validate
   python3 validate.py
   --image aluminum_002.png →   Checks edge gradient        →  ✅ PASS
                                 (same standard as gen)          Score: 87/100
```

---

## 🎯 Single Edit → Dual Impact

```
When you edit shared/generation/realism_physics.txt:

BEFORE:
┌────────────────────────────────────────────────────────────┐
│ realism_physics.txt (OLD):                                 │
│                                                             │
│ 1. GRAVITY EFFECTS:                                        │
│    - Drips flow downward                                   │
│    - Pooling in low areas                                  │
└────────────────────────────────────────────────────────────┘

AFTER:
┌────────────────────────────────────────────────────────────┐
│ realism_physics.txt (UPDATED):                             │
│                                                             │
│ 1. GRAVITY EFFECTS:                                        │
│    - Drips flow downward (3-5 visible drips REQUIRED)     │
│    - Pooling in low areas (minimum 2 pooling zones)       │
│    - Edge accumulation 60-75% heavier than center         │
└────────────────────────────────────────────────────────────┘

IMPACT:
├──> MaterialImageGenerator
│    └──> Next generation includes "3-5 visible drips"
│         and "60-75% edge accumulation"
│
└──> MaterialImageValidator  
     └──> Validation checks for "3-5 drips present?"
          and "edge 60-75% heavier?" automatically
```

---

## 🔗 Template Mirroring

```
Generation Template                 Validation Template
──────────────────                  ───────────────────

shared/generation/                  shared/validation/
realism_physics.txt                 physics_checklist.txt
┌─────────────────────┐            ┌─────────────────────┐
│ GRAVITY EFFECTS:    │  mirrors   │ □ Gravity Effects:  │
│ - Drips downward    │  ═══════>  │   - Drips downward? │
│ - Pooling in lows   │  ═══════>  │   - Pooling in lows?│
│ - 60-75% edge heavy │  ═══════>  │   - Edge 60-75%?    │
└─────────────────────┘            └─────────────────────┘

Generation tells Imagen:            Validator checks image:
"Create drips flowing down"        "Are drips flowing down? ✓"
"Make edges 60-75% heavier"        "Are edges 60-75% heavier? ✓"

ONE EDIT → BOTH UPDATED
```

---

## 📊 File Organization

```
domains/materials/image/prompts/
│
├── shared/                          ← NEW: Single source of truth
│   │
│   ├── generation/                  ← What to CREATE
│   │   ├── base_structure.txt       (16:9, side-by-side, etc.)
│   │   ├── realism_physics.txt      (Gravity, accumulation, layering)
│   │   ├── contamination_rules.txt  (Distribution, edge effects)
│   │   ├── micro_scale_details.txt  (Grain following, stress points)
│   │   └── forbidden_patterns.txt   (Uniform coating, floating particles)
│   │
│   ├── validation/                  ← What to CHECK
│   │   ├── realism_criteria.txt     (90-100 = photorealistic, etc.)
│   │   ├── physics_checklist.txt    (Mirrors realism_physics.txt)
│   │   └── red_flags.txt            (Mirrors forbidden_patterns.txt)
│   │
│   └── feedback/                    ← YOUR CORRECTIONS
│       ├── user_corrections.txt     (Edit this after reviewing images)
│       ├── quality_adjustments.txt  (Auto-generated summary)
│       └── iteration_log.yaml       (Git-tracked change history)
│
├── prompt_builder.py                ← NEW: Loads and assembles templates
├── category_contamination_researcher.py
├── material_researcher.py
│
└── [DEPRECATED - Will be removed]
    ├── base_prompt.txt              → Move to shared/generation/base_structure.txt
    └── material_prompts.py          → Replace with prompt_builder.py
```

---

## ⚡ Efficiency Comparison

### Current System (Code Changes Required)
```
1. Review bad image
2. Open material_prompts.py         (242 lines of code)
3. Find physics section              (line 150-180)
4. Edit code carefully               (Python syntax, indentation)
5. Open validator.py                 (424 lines of code)
6. Find matching physics section     (line 260-285)
7. Edit code to match                (Keep consistent with generator)
8. Test both files                   (Ensure no syntax errors)
9. Regenerate and revalidate         (Hope changes work)

Time: 30-45 minutes per iteration
Risk: HIGH (code syntax errors, inconsistency between files)
```

### Proposed System (Text Edits Only)
```
1. Review bad image
2. Open user_corrections.txt         (Plain text, your notes)
3. Add feedback:
   ISSUE: Edges uniform
   FIX: "60-75% edge accumulation"
4. Save file                         (1 minute)
5. Regenerate                        (Automatically applies feedback)

Time: 5 minutes per iteration
Risk: ZERO (no code changes, automatic consistency)
```

**10x faster iteration, zero code risk**

---

## 🎓 Example: Real Workflow

### Day 1: Initial Generation
```bash
$ python3 generate.py --material "Aluminum" --output aluminum_001.png
✅ Generated: aluminum_001.png
📊 Using prompts: realism_physics.txt v1.0
```

Image shows: Contamination too uniform, no edge concentration

### Day 1: Add Feedback
```bash
$ nano shared/feedback/user_corrections.txt
```
```
ISSUE: Aluminum edges showing uniform coating
FIX: "Aluminum oxide formation concentrates at edges.
     Edge areas MUST be 60-75% heavier than center.
     Create visible gradient from edge to center."
PRIORITY: HIGH
```

### Day 1: Regenerate
```bash
$ python3 generate.py --material "Aluminum" --output aluminum_002.png
📝 Applied user feedback: 1 correction loaded
✅ Generated: aluminum_002.png
```

Image shows: Better! Edge gradient visible, but vertical drips missing

### Day 2: Refine Feedback
```bash
$ nano shared/feedback/user_corrections.txt
```
```
[Previous feedback...]

ISSUE: Vertical surfaces lacking drip patterns
FIX: "Vertical surfaces MUST show 3-5 distinct drip patterns.
     Drips are wider at origin, narrower at terminus.
     Follow gravity (straight down, not curved)."
PRIORITY: CRITICAL
```

### Day 2: Regenerate
```bash
$ python3 generate.py --material "Aluminum" --output aluminum_003.png
📝 Applied user feedback: 2 corrections loaded
✅ Generated: aluminum_003.png
```

Image shows: Excellent! Edge gradient + drips present

### Day 2: Validate
```bash
$ python3 validate.py --image aluminum_003.png --material "Aluminum"
📝 Using validation criteria: 2 user corrections applied
✅ PASSED: 91/100
   ✓ Edge gradient: 65% heavier (target: 60-75%) ✓
   ✓ Drip patterns: 4 visible (target: 3-5) ✓
   ✓ Physics compliant ✓
```

**Result**: 2 iterations, 10 minutes total, 91/100 quality score

---

## 🚀 Ready to Implement?

This architecture provides:
- **Zero code changes** for quality improvements
- **Automatic consistency** between generation and validation
- **Fast iteration** via text file edits
- **Cumulative learning** through feedback logs
- **Full compliance** with system policies

**Next**: Review proposal and approve implementation (5.5 hours estimated)
