# 🔥 Z-BEAM PROJECT GUIDE - SINGLE SOURCE OF TRUTH

> **🚨 CRITICAL**: This is the ONLY documentation. Follow ALL rules strictly.

## 🎯 SYSTEM OVERVIEW
**Purpose**: Generate MDX content for Next.js using single-pass, template-driven generation.  
**Flow**: Load template → Apply variables → API call → Process → Output MDX

## 🔥 CORE PRINCIPLES (MANDATORY)

**SIMPLICITY COMMANDMENTS:**
1. **DELETE BEFORE CREATE** - Modify existing, don't add files
2. **MERGE BEFORE SEPARATE** - Combine files, don't split  
3. **INLINE BEFORE ABSTRACT** - Direct code over abstractions
4. **SIMPLEST WINS** - Never choose complex solutions

**FORBIDDEN CONCEPTS:** ❌ "extensible", "scalable", "future-proof", "just in case", "better architecture", base classes, interfaces, design patterns

## 📊 CURRENT STATUS
**FOCUS**: Working code over arbitrary metrics

## 🚨 CONFIG RULES
**Use GlobalConfigManager for user settings, API keys, and runtime config.**

```python
# ❌ NEVER: User settings as constants
TEMPERATURE = 0.3

# ✅ ALWAYS: Runtime config via manager  
config = GlobalConfigManager.get_instance()
temperature = config.get_content_temperature()

# ✅ OK: True constants that never change
FILE_EXTENSION = ".mdx"
DEFAULT_ENCODING = "utf-8"
```

## 📁 CODEBASE STRUCTURE (10 files)
```
run.py                    # User config entry
main.py                   # Application entry  
config/global_config.py   # Config + exceptions
modules/content_generator.py # Content logic
modules/api_client.py     # API calls
modules/ai_detector.py    # Detection
show_config.py            # Utility
audit_violations.py       # Development tool
tests/simple_test.py      # Tests
tests/comprehensive_test.py # Tests
```

## 🛠️ DEVELOPMENT RULES

**BEFORE ANY CHANGE:**
1. Can existing code be modified instead?
2. Uses GlobalConfigManager for user/runtime config?
3. Is this the simplest working solution?

## 🔒 CLAUDE RULES

**FORBIDDEN ACTIONS:**
- ❌ Adding files without justification (prefer modifying existing)
- ❌ Using forbidden phrases: "extensible", "scalable", "better architecture"
- ❌ Hardcoding user settings (use GlobalConfigManager for runtime config)
- ❌ Suggesting abstractions, interfaces, design patterns

**COMPLIANCE**: Follow the simplest working approach without adding complexity.

## 📊 VALIDATION

**VALIDATION TOOLS:**
- **Quick Check**: `python audit_violations.py` 
- **Pre-commit**: `.git/hooks/pre-commit` (auto-runs on commit)
- **Runtime**: `main.py` validates before operations

---
**🔥 FINAL RULE**: If Claude violates ANY rule, stop and start over with compliant approach.
