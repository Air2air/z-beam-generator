# User Feedback Guidelines

**Date**: November 25, 2025  
**Status**: ✅ MANDATORY POLICY

---

## 🚨 **Critical Rule: General/Category-Level Feedback Only**

All user feedback **MUST** be general or category-level. **NEVER** material-specific.

### ❌ **Prohibited: Material-Specific Feedback**

```plaintext
# WRONG - Singles out specific materials
❌ "Birch wood: Must show horizontal lenticels"
❌ "Steel oxidation needs darker patches"
❌ "Fix Aluminum reflections"
❌ "Copper should have green patina"
```

**Why this is wrong**: Only affects one material, creating inconsistency.

### ✅ **Required: General/Category-Level Feedback**

```plaintext
# CORRECT - Applies to entire category
✅ "Wood surfaces: Grain patterns must follow material structure"
✅ "Rust patterns: Must show gravity effects with vertical drips"
✅ "All materials: Edge contamination 60-75% heavier than center"
✅ "Metal oxidation: Color progression from base metal outward"
```

**Why this is right**: Applies to ALL materials in category automatically.

---

## 📋 **Feedback Template**

```plaintext
## [Category/Pattern Name] (Updated: YYYY-MM-DD)
ISSUE: [Describe what's wrong - must apply to multiple materials]
FIX: "[Exact instruction that works for entire category]"
PRIORITY: [CRITICAL | HIGH | MEDIUM]
APPLIES TO: [Category name or "All materials"]
EXAMPLES: [Material names that showed this issue]
```

---

## 🎯 **Examples by Category**

### **Wood Materials** (Oak, Birch, Maple, etc.)
```plaintext
## Wood Grain Patterns (Updated: 2025-11-25)
ISSUE: Grain patterns appear uniform and artificial across all wood types
FIX: "Wood surfaces: Grain must show natural variation with 30-40% density changes, following growth ring curvature. Avoid perfectly parallel lines."
PRIORITY: HIGH
APPLIES TO: wood_hardwood, wood_softwood
EXAMPLES: Birch, Oak, Maple images all showed uniform grain
```

### **Metal Oxidation** (Rust, Patina, Corrosion)
```plaintext
## Rust Gravity Effects (Updated: 2025-11-25)
ISSUE: Rust accumulation defies physics - horizontal runs on vertical surfaces
FIX: "Rust patterns: MUST follow gravity with vertical drips from moisture points. Heavier accumulation at bottom edges (60-75%). NO horizontal streaks on vertical surfaces."
PRIORITY: CRITICAL
APPLIES TO: metals_ferrous, metals_reactive
EXAMPLES: Steel, Iron images showed horizontal rust lines
```

### **All Materials** (Universal Rules)
```plaintext
## Edge Contamination Distribution (Updated: 2025-11-25)
ISSUE: Contamination evenly distributed across surface
FIX: "All materials: Edge areas MUST show 60-75% heavier contamination than center. Corners show 80-90% concentration. This applies to dirt, rust, oxidation, and all contamination types."
PRIORITY: HIGH
APPLIES TO: All categories
EXAMPLES: Multiple materials (Steel, Aluminum, Concrete) showed even distribution
```

---

## 🔄 **How Feedback Propagates**

### **Single Feedback → Multiple Materials**

When you write:
```plaintext
FIX: "Wood surfaces: Avoid perfectly parallel grain lines"
```

This automatically improves:
- ✅ Oak (next generation)
- ✅ Birch (next generation)
- ✅ Maple (next generation)
- ✅ Cherry (next generation)
- ✅ Walnut (next generation)
- ✅ ALL future wood materials

### **Why This Matters**

**Bad Approach** (Material-Specific):
```
Fix Birch grain → Only Birch improves
Fix Oak grain → Only Oak improves
Fix Maple grain → Only Maple improves
Result: 3 separate fixes for same issue
```

**Good Approach** (Category-Level):
```
Fix "Wood grain patterns" → ALL wood materials improve
Result: 1 fix affects entire category
```

---

## 📊 **Priority Levels**

### 🔴 **CRITICAL**
- Physics violations (gravity, light, material properties)
- Safety issues (incorrect material representations)
- Blocking quality failures
- **Action**: Fix immediately, affects all generations

### 🟡 **HIGH**
- Quality impact visible to users
- Reduces realism scores
- Category-wide appearance issues
- **Action**: Fix within current batch

### 🟢 **MEDIUM**
- Minor improvements
- Edge case handling
- Aesthetic preferences
- **Action**: Nice to have, accumulate with other feedback

---

## ✅ **Validation Checklist**

Before adding feedback, verify:

- [ ] **Not material-specific**: Can apply to multiple materials?
- [ ] **Category identified**: Which category does this affect?
- [ ] **Universal principle**: Based on physics/reality, not preference?
- [ ] **Clear instruction**: Can Imagen understand and apply it?
- [ ] **Measurable**: Can validator check if it's fixed?

---

## 🚫 **Common Mistakes**

### **Mistake 1: Overly Specific**
```
❌ "Birch bark must show white with black horizontal marks"
✅ "Wood bark textures: Show characteristic species features with natural color variation"
```

### **Mistake 2: Single Material Focus**
```
❌ "Steel needs more rust in corners"
✅ "Metal corners: Oxidation concentration 80-90% (applies to all ferrous metals)"
```

### **Mistake 3: Aesthetic Preference**
```
❌ "Make Aluminum shinier"
✅ "Metal surfaces: Clean side must show appropriate reflectivity for material type (matte vs polished)"
```

---

## 📚 **Categories Reference**

Use these category names in "APPLIES TO":

**Metals**:
- `metals_ferrous` (Steel, Iron)
- `metals_non_ferrous` (Aluminum, Copper, Brass)
- `metals_reactive` (Titanium, Magnesium)
- `metals_corrosion_resistant` (Stainless Steel, Chrome)

**Ceramics**:
- `ceramics_traditional` (Porcelain, Terracotta)
- `ceramics_construction` (Brick, Concrete)
- `ceramics_glass` (Glass)

**Polymers**:
- `polymers_thermoplastic` (ABS, Polycarbonate)
- `polymers_engineering` (Nylon)
- `polymers_elastomer` (Rubber)

**Wood**:
- `wood_hardwood` (Oak, Maple, Birch, Cherry)
- `wood_softwood` (Pine, Cedar, Spruce)
- `wood_engineered` (Plywood, MDF)

**Composites**:
- `composites_polymer_matrix` (Fiberglass, Carbon Fiber)

**Universal**:
- `All materials` (Applies to everything)

---

## 🎯 **Real-World Example**

**Scenario**: Birch image shows horizontal grain lines instead of realistic variation.

### ❌ **Wrong Feedback**:
```
## Birch Wood Grain (Updated: 2025-11-25)
ISSUE: Birch shows unrealistic grain
FIX: "Birch must have varied grain with lenticels"
PRIORITY: HIGH
EXAMPLES: birch-laser-cleaning.png
```
**Problem**: Only fixes Birch. Oak, Maple still broken.

### ✅ **Correct Feedback**:
```
## Wood Grain Realism (Updated: 2025-11-25)
ISSUE: Wood grain appears uniform with parallel lines across multiple species
FIX: "Wood surfaces: Grain patterns must show 30-40% density variation following growth ring curvature. Include knots, ray flecks, and natural irregularities specific to wood type. Avoid perfectly parallel lines."
PRIORITY: HIGH
APPLIES TO: wood_hardwood, wood_softwood
EXAMPLES: Birch, Oak, Maple all showed uniform grain
```
**Result**: Fixes Birch, Oak, Maple, and all future wood materials.

---

## 🔄 **Feedback Lifecycle**

1. **Generate Material** → Spot issue
2. **Write General Feedback** → Add to `user_corrections.txt`
3. **Automatic Integration** → System loads feedback
4. **All Future Generations** → Use improved prompts
5. **Regenerate if Needed** → Previous materials can be regenerated with feedback

---

## 📖 **Related Documentation**

- **Feedback Prompt Catalog Entry**: `prompts/shared/feedback/user_corrections.txt` (in `prompts/registry/prompt_catalog.yaml`)
- **Prompt Builder**: `shared/image/utils/prompt_builder.py` (automatic integration)
- **Category Map**: `domains/materials/image/research/contamination_pattern_selector.py`
- **Testing**: `tests/test_shared_prompt_builder.py::TestFeedbackIntegration`

---

**Remember**: One good general fix is worth a dozen material-specific patches. Think category-wide, not material-specific.
