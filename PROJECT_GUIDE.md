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

## 📁 CODEBASE STRUCTURE (Target: 10 files)
```
run.py                    # User config entry
main.py                   # Application entry  
config/global_config.py   # Config + exceptions
modules/content_generator.py # Content logic
modules/api_client.py     # API calls
modules/ai_detector.py    # Detection
compliance/               # Discrete compliance folder
├── audit_violations.py   # Development tool
├── show_config.py        # Utility
└── validation_rules.py   # Compliance rules
tests/simple_test.py      # Tests
tests/comprehensive_test.py # Tests
```

**FILE COUNT PHILOSOPHY:**
- **Target**: 10 files (optimal for this project)
- **Priority**: Functionality over arbitrary file reduction
- **Approach**: Maintain reasonable file organization while avoiding unnecessary fragmentation
- **NOT REQUIRED**: Continual shrinking of file count below functional needs

## 🛠️ DEVELOPMENT RULES

**RESEARCH MODIFICATION RULE:**
Before creating ANY new file, MUST thoroughly research modifying existing files:

1. **ANALYZE EXISTING FILES** - Review current file contents and structure
2. **IDENTIFY MODIFICATION POINTS** - Find where new functionality can be added
3. **ASSESS MERGE FEASIBILITY** - Can new code be integrated into existing files?
4. **DOCUMENT MODIFICATION PLAN** - Explain how existing files will be changed
5. **JUSTIFY NEW FILE** - Only if modification is genuinely impossible

**MODIFICATION RESEARCH CHECKLIST:**
- [ ] Reviewed all existing files for integration points
- [ ] Identified specific functions/classes to modify  
- [ ] Confirmed new functionality fits existing file purpose
- [ ] Attempted inline implementation first
- [ ] Documented why existing files cannot accommodate changes

**FILE COUNT CONSIDERATIONS:**
- **Functional clarity** over artificial file reduction
- **Logical separation** when it serves clear purposes
- **Avoid fragmentation** without forcing artificial merging
- **Maintain target structure** while allowing reasonable variations

**BEFORE ANY CHANGE:**
1. Can existing code be modified instead?
2. Uses GlobalConfigManager for user/runtime config?
3. Is this the simplest working solution?
4. Does file organization serve functional needs?

## 🔒 CLAUDE RULES

**FORBIDDEN ACTIONS:**
- ❌ Adding files without completing research modification process
- ❌ Using forbidden phrases: "extensible", "scalable", "better architecture"
- ❌ Hardcoding user settings (use GlobalConfigManager for runtime config)
- ❌ Suggesting abstractions, interfaces, design patterns
- ❌ Creating new files without documenting modification research
- ❌ Artificially forcing file merging that reduces functionality

**COMPLIANCE**: Follow the simplest working approach without adding complexity or forcing artificial constraints.

## 📊 VALIDATION

**VALIDATION TOOLS:**
- **Quick Check**: `python compliance/audit_violations.py` 
- **Config Display**: `python compliance/show_config.py`
- **Runtime**: `main.py` validates before operations

**COMPLIANCE FOLDER STRUCTURE:**
```
compliance/
├── audit_violations.py   # PROJECT_GUIDE violation checker
├── show_config.py        # Configuration display utility
└── validation_rules.py   # Centralized compliance rules
```

---
**🔥 FINAL RULE**: If Claude violates ANY rule, stop and start over with compliant approach. File count should serve functionality, not arbitrary metrics.
