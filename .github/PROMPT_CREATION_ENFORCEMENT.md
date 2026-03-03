# Prompt Creation Enforcement - AI Assistant Guide
**Date**: January 7, 2026  
**Purpose**: Prevent unauthorized prompt creation and modification  
**Status**: Active Policy

## 🚨 **THE FUNDAMENTAL RULE**

**AI Assistants MUST NOT create, modify, or suggest prompts without explicit user permission.**

## 📋 **Current Policies**

### **1. Prompt Purity Policy** (Nov 18, 2025)
**Location**: `.github/copilot-instructions.md` line 1667

❌ **FORBIDDEN**: Prompt text in code
```python
# ❌ WRONG: Hardcoded prompt in generator
system_prompt = "You are a professional writer..."
prompt = f"Write about {material}..."
```

✅ **REQUIRED**: Load from template files
```python
# ✅ CORRECT: Load from template
template = self._load_prompt_template('description.txt')
```

### **2. Embedded Prompts Policy** (Dec 29, 2025)
**Location**: `.github/copilot-instructions.md` line 1049

**Key Distinction**:
- **CONTENT generation** (user-facing) → Template files ONLY
- **DATA research** (technical properties) → Inline prompts OK

### **3. High-Impact Files Guidance** (Updated Mar 2026)
**Location**: `.github/PROTECTED_FILES.md`

**High-impact paths** (validate carefully after changes):
- `prompts/materials/*.txt`
- `prompts/contaminants/*.txt`
- `prompts/compounds/*.txt`
- `prompts/settings/*.txt`
- `shared/voice/profiles/*.yaml`

## 🛡️ **ENFORCEMENT MECHANISMS**

### **Level 1: Policy Documentation** ✅ ACTIVE
- High-impact file guidance maintained
- Policies clearly documented
- AI instructions include rules

### **Level 2: Code Verification** ✅ IMPLEMENTED
**Automated Checks**:
```bash
# Check for embedded prompts in generators (should be 0 matches)
grep -r "prompt.*=.*You are" generation/core/ domains/*/coordinator.py

# Check for hardcoded system prompts
grep -r "system_prompt\s*=" generation/ --include="*.py"
```

### **Level 3: Pre-Commit Hook** 🔥 **NEW - RECOMMENDED**
**File**: `.git/hooks/pre-commit`

```bash
#!/bin/bash

echo "🔍 Checking for policy violations..."

# Check 1: High-impact prompt file modifications
if git diff --cached --name-only | grep -E 'prompts/(materials|contaminants|compounds|settings)/.*\.txt|shared/voice/profiles/.*\.yaml'; then
    echo ""
    echo "⚠️  WARNING: Modifying high-impact prompt files!"
    echo "📋 Policy: Run focused validation before merge"
    echo "📖 See: .github/PROTECTED_FILES.md"
    echo ""
fi

# Check 2: Embedded prompts in generators
if git diff --cached | grep -E "prompt\s*=\s*['\"]You are|system_prompt\s*="; then
    echo ""
    echo "⚠️  WARNING: Potential embedded prompt detected!"
    echo "📋 Policy: Prompt Purity Policy - NO prompts in code"
    echo "📖 See: .github/copilot-instructions.md line 1667"
    echo ""
    read -p "Is this a research script (not content generator)? (yes/no): " -r
    if [[ ! $REPLY =~ ^(yes|YES|y|Y)$ ]]; then
        echo "❌ Commit blocked - Use prompt template files instead"
        exit 1
    fi
fi

# Check 3: New prompt files without approval
if git diff --cached --name-only --diff-filter=A | grep -E '\.txt$|\.yaml$'; then
    NEW_FILES=$(git diff --cached --name-only --diff-filter=A | grep -E '\.txt$|\.yaml$')
    if echo "$NEW_FILES" | grep -qE 'prompts/|voice/profiles/'; then
        echo ""
        echo "⚠️  WARNING: Creating new prompt/voice files!"
        echo "📋 Policy: All prompt changes require user approval"
        echo "🆕 New files: $NEW_FILES"
        echo ""
        read -p "Did user explicitly request these new files? (yes/no): " -r
        if [[ ! $REPLY =~ ^(yes|YES|y|Y)$ ]]; then
            echo "❌ Commit blocked - Get user approval first"
            exit 1
        fi
    fi
fi

echo "✅ Policy checks passed"
exit 0
```

### **Level 4: File Permissions** 🔥 **NEW - OPTIONAL**
**Optional local guardrails for high-impact files**:
```bash
# Lock all prompt files (user can still edit with explicit chmod)
find prompts/{materials,contaminants,compounds,settings} -name "*.txt" -exec chmod 444 {} \;
find shared/voice/profiles -name "*.yaml" -exec chmod 444 {} \;

# To edit (unlock when needed)
chmod 644 prompts/materials/micro.txt  # edit
chmod 444 prompts/materials/micro.txt  # lock again
```

### **Level 5: Code Review Checklist** 🔥 **NEW**
**For AI-generated PRs, verify**:
- [ ] No new .txt files in prompts/{materials,contaminants,compounds,settings}/
- [ ] No new .yaml files in shared/voice/profiles/
- [ ] No "prompt =" patterns in generation/core/
- [ ] No "system_prompt =" in generators
- [ ] All prompt loading uses _load_prompt_template()

## 🚫 **COMMON VIOLATION SCENARIOS**

### **Scenario 1: "The prompt isn't working right"**
```
❌ DON'T: Rewrite prompt file
✅ DO: Ask which specific part isn't working, suggest minimal targeted change
✅ DO: Show diff of proposed change, wait for approval
```

### **Scenario 2: "Need a new component type"**
```
❌ DON'T: Create prompts/materials/new_component.txt
✅ DO: Ask "Should I create a new prompt file for [component]?"
✅ DO: Wait for explicit "yes" before creating
```

### **Scenario 3: "Generation needs better instructions"**
```
❌ DON'T: Add inline prompt text to generator.py
✅ DO: Ask "Should I update the prompt template file?"
✅ DO: Show what you would add to the template
✅ DO: Wait for approval
```

### **Scenario 4: "Need to research material properties"**
```
✅ ALLOWED: Use inline prompts in scripts/research/*.py
✅ ALLOWED: This is DATA research, not CONTENT generation
✅ EXAMPLE: prompt = f"What is the density of {material}?"
```

## ✅ **VERIFICATION COMMANDS**

### **Check for Policy Violations**
```bash
# 1. Check for embedded prompts in generators (should be 0)
grep -r "prompt.*=.*You are" generation/core/ domains/*/coordinator.py

# 2. Check for system prompts in code (should be 0 in generators)
grep -r "system_prompt\s*=" generation/core/ --include="*.py"

# 3. List all prompt files (should match expected 34 files)
find prompts/{materials,contaminants,compounds,settings} -name "*.txt" -type f | wc -l

# 4. Check high-impact guidance in PROTECTED_FILES.md
grep -A 20 "High-Impact Areas" .github/PROTECTED_FILES.md
```

### **Verify Template Loading (All should use this pattern)**
```bash
grep -r "_load_prompt_template" generation/core/
# Should show all generators using template loading
```

## 📊 **SUCCESS METRICS**

✅ **Zero embedded prompts in generation/core/**
✅ **All 34 prompt files maintained without unauthorized changes**
✅ **All new prompts created with user approval**
✅ **100% use of _load_prompt_template() for content generation**

## 🔥 **EMERGENCY RESPONSE**

**If unintended prompt changes were created/modified**:

1. **STOP** all related work immediately
2. **INFORM** user: "I modified a high-impact prompt file unexpectedly"
3. **SHOW** what was changed: `git diff [file]`
4. **REVERT** if user disapproves: `git checkout HEAD -- [file]`
5. **DOCUMENT** what you were trying to accomplish
6. **ASK** for proper guidance

## 📚 **Related Documentation**

- **High-Impact File Guidance**: `.github/PROTECTED_FILES.md`
- **Prompt Purity Policy**: `.github/copilot-instructions.md` line 1667
- **Embedded Prompts Policy**: `.github/copilot-instructions.md` line 1049
- **Prompt File Locations**: 
    - Materials: `prompts/materials/` (domain templates)
    - Contaminants: `prompts/contaminants/` (domain templates)
    - Compounds: `prompts/compounds/` (domain templates)
    - Settings: `prompts/settings/` (domain templates)
  - Voice: `shared/voice/profiles/` (4 files)

## 🏆 **GRADE IMPACTS**

- **Creating prompts without explicit user request**: Grade F
- **Editing high-impact prompt files without validation evidence**: Grade F
- **Embedding prompts in generators**: Grade F
- **Asking permission first**: Grade A
- **Using template loading correctly**: Grade A
