# Naming Conventions Policy

**Date**: November 27, 2025  
**Scope**: All Python code, classes, methods, and modules  
**Priority**: TIER 2 - Code Quality

---

## 🎯 Core Principle

**Simplify and standardize code and method naming. Remove redundant prefixes that don't add clarity.**

---

## 📋 Class Naming Rules

### ❌ **AVOID: Redundant Prefixes**

**Don't use these prefixes** unless they genuinely disambiguate:

```python
# ❌ WRONG: Redundant "Simple" prefix
class SimpleGenerator:
    pass

# ❌ WRONG: Redundant "Basic" prefix
class BasicValidator:
    pass

# ❌ WRONG: Redundant "Universal" prefix (when obvious from context)
class UniversalImageGenerator:  # In shared/image/ - already universal
    pass

# ❌ WRONG: Redundant "Unified" prefix
class UnifiedProcessor:
    pass
```

### ✅ **CORRECT: Clear, Direct Names**

```python
# ✅ RIGHT: Direct, clear name
class Generator:
    """Text content generator for materials"""
    pass

# ✅ RIGHT: Specific purpose in name
class QualityGatedGenerator:
    """Generator with quality gates and retry logic"""
    pass

# ✅ RIGHT: Context makes scope clear
class ImageGenerator:  # In shared/image/ - context shows it's shared
    """Image prompt generator for all domains"""
    pass

# ✅ RIGHT: Descriptor adds meaningful information
class PromptValidator:
    """Validates prompts before API submission"""
    pass
```

---

## 📐 Method Naming Rules

### ❌ **AVOID: Redundant Prefixes**

```python
# ❌ WRONG: Redundant "simple_" prefix
def simple_generate(self, material: str) -> str:
    pass

# ❌ WRONG: Redundant "basic_" prefix
def basic_validate(self, data: dict) -> bool:
    pass

# ❌ WRONG: Redundant "do_" prefix (verb already clear)
def do_process(self, item: str) -> str:
    pass
```

### ✅ **CORRECT: Clear, Action-Oriented Names**

```python
# ✅ RIGHT: Clear action verb
def generate(self, material: str) -> str:
    """Generate content for material"""
    pass

# ✅ RIGHT: Specific action
def validate(self, data: dict) -> bool:
    """Validate data structure"""
    pass

# ✅ RIGHT: Clear verb describes action
def process(self, item: str) -> str:
    """Process item through pipeline"""
    pass

# ✅ RIGHT: Descriptor adds context when needed
def generate_with_quality_gates(self, material: str) -> str:
    """Generate with quality validation and retry logic"""
    pass
```

---

## 🗂️ File/Module Naming Rules

### ❌ **AVOID: Redundant Prefixes in Filenames**

```python
# ❌ WRONG: File in generation/core/
simple_generator.py          # "simple" redundant - context is clear

# ❌ WRONG: File in shared/validation/
universal_validator.py       # "universal" redundant - shared/ implies universal

# ❌ WRONG: File in shared/image/
universal_image_generator.py # Both prefixes redundant
```

### ✅ **CORRECT: Context-Aware Filenames**

```python
# ✅ RIGHT: File in generation/core/
generator.py                 # Simple and clear
evaluated_generator.py       # Descriptor adds meaning

# ✅ RIGHT: File in shared/validation/
prompt_validator.py          # Clear purpose, context from directory

# ✅ RIGHT: File in shared/image/
generator.py                 # Context from directory path
orchestrator.py              # Specific role in system
```

---

## 🔄 Migration Strategy

### **Phase 1: New Code** (IMMEDIATE)

All new code MUST follow these conventions:
- ✅ No `Simple`, `Basic`, `Universal`, `Unified` prefixes
- ✅ Use clear, direct names
- ✅ Let directory structure provide context

### **Phase 2: Critical Path** (PRIORITY)

Rename these high-visibility classes:
1. `SimpleGenerator` → `Generator`
2. `UniversalImageGenerator` → `ImageGenerator`
3. `UniversalPromptValidator` → `PromptValidator`

### **Phase 3: Comprehensive Refactor** (LOW PRIORITY)

Update all remaining instances:
- Search codebase for redundant prefixes
- Update imports across all files
- Update documentation references
- Update test names

---

## 📊 Before/After Examples

### **Example 1: Text Generation**

**❌ Before:**
```python
# File: generation/core/simple_generator.py
class SimpleGenerator:
    def simple_generate(self, material: str) -> str:
        return self._do_basic_generation(material)
    
    def _do_basic_generation(self, material: str) -> str:
        pass
```

**✅ After:**
```python
# File: generation/core/generator.py
class Generator:
    def generate(self, material: str) -> str:
        return self._build_content(material)
    
    def _build_content(self, material: str) -> str:
        pass
```

### **Example 2: Image Generation**

**❌ Before:**
```python
# File: shared/image/generator.py
class UniversalImageGenerator:
    def simple_generate_prompt(self, material: str) -> str:
        pass
```

**✅ After:**
```python
# File: shared/image/generator.py
class ImageGenerator:
    def generate_prompt(self, material: str) -> str:
        pass
```

### **Example 3: Validation**

**❌ Before:**
```python
# File: shared/validation/prompt_validator.py
class UniversalPromptValidator:
    def basic_validate(self, prompt: str) -> bool:
        pass
```

**✅ After:**
```python
# File: shared/validation/prompt_validator.py
class PromptValidator:
    def validate(self, prompt: str) -> bool:
        pass
```

---

## 🚫 When Prefixes ARE Appropriate

### **Use prefixes when they disambiguate:**

```python
# ✅ CORRECT: "Quality" distinguishes from base Generator
class QualityGatedGenerator:
    """Generator with quality gates and retry logic"""
    pass

# ✅ CORRECT: "Batch" indicates different behavior
class BatchGenerator:
    """Generates multiple items in batch"""
    pass

# ✅ CORRECT: "Streaming" indicates mode
class StreamingProcessor:
    """Processes data in streaming mode"""
    pass

# ✅ CORRECT: "Async" is meaningful descriptor
class AsyncImageGenerator:
    """Asynchronous image generation"""
    pass
```

### **Don't use prefixes when context is clear:**

```python
# ❌ WRONG: In generation/core/ directory
class SimpleGenerator:  # "Simple" redundant - it's the base generator

# ✅ RIGHT: Context from directory
class Generator:  # Clearly the base generator
```

---

## 📝 Naming Checklist

Before naming any class, method, or file:

- [ ] Does the prefix add meaningful information?
- [ ] Would the name be clear without the prefix?
- [ ] Does directory context already provide this information?
- [ ] Would a developer instantly understand the purpose without the prefix?
- [ ] Am I using "Simple", "Basic", "Universal", or "Unified"? (RED FLAG)

**If you answered "yes" to 2+ questions above, remove the prefix.**

---

## 🎯 Rationale

### **Why Remove Redundant Prefixes?**

1. **Clarity**: `Generator` is clearer than `SimpleGenerator`
2. **Brevity**: Shorter names are easier to read and type
3. **Context**: Directory structure provides scope information
4. **Consistency**: Reduces cognitive load across codebase
5. **Evolution**: Classes naturally grow complex - "Simple" becomes misleading

### **What "Simple" Actually Means**

```python
# What we think "Simple" means:
class SimpleGenerator:  # "Basic, easy to understand"
    pass

# What "Simple" actually signals:
class SimpleGenerator:  # "This is incomplete, needs a 'Complex' version later"
    pass
```

**Reality**: There's usually only ONE generator. Call it `Generator`.

---

## 🔧 Migration Commands

### **Step 1: Rename Files**
```bash
# Rename simple_generator.py → generator.py
mv generation/core/simple_generator.py generation/core/generator.py
```

### **Step 2: Update Class Names**
```python
# In generator.py
class SimpleGenerator:  # Old
class Generator:        # New
```

### **Step 3: Update Imports**
```bash
# Find all imports
grep -r "from.*simple_generator import SimpleGenerator" .

# Update each one
sed -i '' 's/from generation.core.simple_generator import SimpleGenerator/from generation.core.generator import Generator/g' **/*.py
```

### **Step 4: Update References**
```bash
# Find all usages
grep -r "SimpleGenerator" .

# Update documentation
grep -r "SimpleGenerator" docs/
```

---

## 📚 Examples from Codebase

### **Current State (Need Refactoring)**

| Current Name | Issues | Suggested Name |
|--------------|--------|----------------|
| `SimpleGenerator` | "Simple" redundant | `Generator` |
| `UniversalImageGenerator` | "Universal" redundant (in shared/) | `ImageGenerator` |
| `UniversalPromptValidator` | "Universal" redundant (in shared/) | `PromptValidator` |
| `simple_generate()` | "simple_" redundant | `generate()` |
| `basic_validate()` | "basic_" redundant | `validate()` |
| `do_process()` | "do_" redundant | `process()` |

### **Good Examples (Keep As-Is)**

| Current Name | Why It's Good | Keep? |
|--------------|---------------|-------|
| `QualityGatedGenerator` | "QualityGated" adds meaning | ✅ Yes |
| `BatchGenerator` | "Batch" distinguishes behavior | ✅ Yes |
| `ImagePromptOrchestrator` | "Orchestrator" describes role | ✅ Yes |
| `WinstonFeedbackDatabase` | "Grok" is specific service | ✅ Yes |

---

## 🚨 Enforcement

### **Code Review Checklist**

- [ ] No `Simple*` class names
- [ ] No `Basic*` class names
- [ ] No `Universal*` class names (in shared/ directories)
- [ ] No `Unified*` class names (unless truly unifying different systems)
- [ ] No `simple_*` method names
- [ ] No `basic_*` method names
- [ ] No `do_*` method names (unless "do" adds meaning)

### **Grade Penalties**

| Violation | Grade Impact |
|-----------|-------------|
| Using `Simple` prefix in new code | -5 points |
| Using `Basic` prefix in new code | -5 points |
| Using `Universal` in shared/ directories | -5 points |
| Not considering context before naming | -10 points |

### **Exceptions**

Prefixes allowed when they genuinely disambiguate:
- ✅ `QualityGatedGenerator` vs `Generator` (different behavior)
- ✅ `BatchProcessor` vs `StreamingProcessor` (different modes)
- ✅ `AsyncClient` vs `SyncClient` (different paradigms)

---

## 📖 Summary

**Golden Rule**: Remove prefixes that don't add information. Let directory structure and context do the work.

**Quick Test**: If you need to explain why the prefix is needed, it's probably redundant.

**Examples**:
- ❌ `SimpleGenerator` → ✅ `Generator`
- ❌ `UniversalImageGenerator` → ✅ `ImageGenerator`
- ❌ `simple_validate()` → ✅ `validate()`
- ❌ `basic_process()` → ✅ `process()`

**When to use prefixes**: Only when they disambiguate multiple similar classes/methods in the same context.

---

**Policy Owner**: AI Architecture Team  
**Review Date**: Monthly  
**Last Updated**: November 27, 2025
