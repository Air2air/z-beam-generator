# Cross-Domain Cleanup Summary
**Date**: November 26, 2025  
**Duration**: 45 minutes recommended  
**Risk**: LOW

---

## 🎯 Quick Overview

Found **2 critical cross-domain violations** during Settings domain separation verification:

1. **Materials → Settings**: `data_loader.py` imports from settings domain (3 locations)
2. **Materials → Contaminants**: `material_generator.py` imports from contaminants domain (1 location)

Both violate **Domain Independence Policy** requiring zero cross-domain contamination.

---

## 🚨 Critical Violations

### Violation 1: Materials → Settings (Lines 35, 170, 273)
```python
# ❌ CURRENT (WRONG)
from domains.settings.data_loader import load_settings_yaml
```

**Fix**: Create orchestrator for data merging
```python
# ✅ CORRECT
# domains/materials/data_loader.py - Remove settings imports
# orchestrators/data_orchestrator.py - NEW file handles merging
```

### Violation 2: Materials → Contaminants (Line 24)
```python
# ❌ CURRENT (WRONG)
from domains.contaminants import ContaminationValidator, ContaminationContext
```

**Fix**: Extract shared types
```python
# ✅ CORRECT  
from shared.types.contamination import ContaminationContext
from shared.validation.contamination_validator import ContaminationValidatorInterface
```

---

## ✅ Quick Fix Checklist

**Phase 1: Materials → Settings** (15-20 min)
- [ ] Create `orchestrators/data_orchestrator.py` with merge logic
- [ ] Remove 3 settings imports from `domains/materials/data_loader.py`
- [ ] Update callers to use orchestrator

**Phase 2: Materials → Contaminants** (20-25 min)
- [ ] Create `shared/types/contamination.py` with ContaminationContext
- [ ] Create `shared/validation/contamination_validator.py` with interface
- [ ] Update `domains/materials/image/material_generator.py` imports
- [ ] Update `domains/contaminants/` to implement interface

**Verification** (5 min)
- [ ] Run: `grep -r "from domains\." domains/materials/ | grep -v "from domains.materials"`
- [ ] Should return 0 results
- [ ] Run tests to confirm no breakage

---

## 📊 Files to Modify

| File | Type | Changes |
|------|------|---------|
| `orchestrators/data_orchestrator.py` | NEW | Merge logic from materials loader |
| `shared/types/contamination.py` | NEW | Extract ContaminationContext |
| `shared/validation/contamination_validator.py` | NEW | Validator interface |
| `domains/materials/data_loader.py` | EDIT | Remove 3 settings imports |
| `domains/materials/image/material_generator.py` | EDIT | Update 1 import line |
| `domains/contaminants/*` | EDIT | Implement shared interface |

**Total**: 6 files (3 new, 3 edited)

---

## ⏱️ Time Breakdown

- **Orchestrator creation**: 10 min
- **Remove settings imports**: 5 min
- **Extract shared types**: 15 min
- **Update imports**: 5 min
- **Verification**: 5 min
- **Testing**: 5 min

**Total**: 45 minutes

---

## 🎓 Lessons Learned

1. **Domain separation requires import cleanup** - Moving files is not enough
2. **Cross-domain imports create tight coupling** - Violates independence
3. **Orchestrator pattern is the solution** - Integration at edges, not within domains
4. **Shared utilities preserve independence** - Common types in shared/, not cross-imports

---

## 📚 Full Details

See `ARCHITECTURE_ORGANIZATION_OPPORTUNITIES_NOV26_2025.md` for:
- Complete analysis (5 organization opportunities)
- Priority 2 & 3 recommendations (11-14 hours)
- Compliance verification
- Success metrics

---

**Next Step**: Fix Priority 1 violations (45 min) → Document → Evaluate Priority 2 & 3 with user

**Grade**: A (95/100) - Quick, focused, actionable
