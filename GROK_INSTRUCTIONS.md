# Grok Instructions for Z-Beam Generator

## 🚨 **THIS FILE IS DEPRECATED - USE CONSOLIDATED DOCUMENTATION**

**➡️ PRIMARY DOCUMENTATION: [.github/copilot-instructions.md](/.github/copilot-instructions.md)**  
**➡️ QUICK REFERENCE: [GROK_QUICK_REF.md](./GROK_QUICK_REF.md)**

---

## 📖 **Why Consolidate?**

Originally, this system had three separate instruction files:
- `GROK_INSTRUCTIONS.md` (587 lines) - Grok-specific rules
- `GROK_QUICK_REF.md` (168 lines) - Quick decision trees
- `.github/copilot-instructions.md` (924 lines) - All AI assistants

**Problem**: 70% duplication, conflicting updates, outdated information

**Solution**: Single source of truth with quick reference

---

## 📘 **New Documentation Structure**

### **For Quick Decisions** → [GROK_QUICK_REF.md](./GROK_QUICK_REF.md)
- Tier priorities (TIER 1/2/3)
- Decision trees ("Should I use a default?")
- Terminal output policy
- **Read time: 30 seconds**

### **For Complete Rules** → [.github/copilot-instructions.md](/.github/copilot-instructions.md)
- All core rules and guardrails
- Verification protocols
- Recent updates and policies
- Pre-change checklists
- **Comprehensive reference**

---

## ⚡ **Migration Guide for AI Assistants**

If you were using `GROK_INSTRUCTIONS.md`, here's what moved:

| Old Location | New Location |
|-------------|-------------|
| Core Rules | `.github/copilot-instructions.md` → Core Principles |
| Lessons from Past Failures | `.github/copilot-instructions.md` → Lessons section |
| Pre-Change Checklist | `.github/copilot-instructions.md` → Checklist |
| Tier Priorities | `GROK_QUICK_REF.md` + `.github/copilot-instructions.md` |
| Decision Trees | `GROK_QUICK_REF.md` + `.github/copilot-instructions.md` |

---

## 🔒 **Preserved Guardrails**

All critical guardrails from this file have been preserved in the consolidated documentation:

✅ **No mocks/fallbacks in production** (Core Principle #2)  
✅ **No hardcoded values** (Core Principle #3)  
✅ **Verification before claiming success** (Mandatory Verification Protocol)  
✅ **Search for existing solutions first** (Anti-pattern warnings)  
✅ **Honest reporting** (Step 7: Honest Reporting)  
✅ **Fail-fast architecture** (Core Principle #3)  
✅ **Preserve working code** (Core Principle #1)  

---

## 📌 **Start Here**

1. **Quick decision?** → Read [GROK_QUICK_REF.md](./GROK_QUICK_REF.md) (30 seconds)
2. **Making changes?** → Read [.github/copilot-instructions.md](/.github/copilot-instructions.md) (comprehensive)
3. **Need documentation?** → See `docs/QUICK_REFERENCE.md` for fastest path

---

## 🎯 **Quick Actions**

- **Found this file by accident?** → Go to [GROK_QUICK_REF.md](./GROK_QUICK_REF.md)
- **Need comprehensive guide?** → Go to [.github/copilot-instructions.md](/.github/copilot-instructions.md)
- **Looking for old content?** → It's been moved and improved in the files above

---

**Last Updated**: November 20, 2025  
**Status**: DEPRECATED - All content consolidated into copilot-instructions.md  
