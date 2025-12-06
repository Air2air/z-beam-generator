# Prompt Chaining & Orchestration Policy

**Date**: November 27, 2025  
**Scope**: Text and Image Generation  
**Priority**: TIER 1 - Architecture Foundation

---

## 🎯 Core Principle

**Maximum use of prompt chaining and orchestration to preserve separation of concerns and specificity.**

Instead of one monolithic prompt trying to do everything, break generation into:
1. **Specialized prompts** - Each does ONE thing extremely well
2. **Orchestration layer** - Chains prompts together with context passing
3. **Clear boundaries** - Each prompt has explicit inputs/outputs

---

## 📋 Architecture Pattern

### ❌ **ANTI-PATTERN: Monolithic Prompt**

```
Single massive prompt trying to:
- Research material properties
- Generate visual descriptions
- Apply style guidelines
- Ensure technical accuracy
- Format output
- All at once with conflicting instructions
```

**Problems**:
- Conflicting instructions confuse the model
- Hard to debug which part failed
- Can't reuse components
- Loses specificity as prompt grows
- Quality degrades with complexity

### ✅ **CORRECT PATTERN: Chained Prompts**

```
Prompt 1 (Research): Material property extraction
   ↓ (properties data)
Prompt 2 (Visual Description): Physical appearance from properties
   ↓ (visual details)
Prompt 3 (Style Application): Apply domain-specific style
   ↓ (styled content)
Prompt 4 (Formatting): Structure and polish
   ↓ (final output)
```

**Benefits**:
- Each prompt focused on ONE task
- Clear data flow between stages
- Easy to debug specific stage
- Reusable components
- Maintains specificity and quality

---

## 🔧 Implementation Requirements

### **1. Specialized Prompt Files**

Each prompt file does ONE specific task:

```
shared/image/templates/
├── research/
│   ├── material_properties.txt      # Research: Extract properties
│   └── visual_appearance.txt        # Research: Visual characteristics
├── generation/
│   ├── hero_composition.txt         # Generate: Before/after layout
│   ├── contamination_details.txt    # Generate: Contamination specifics
│   └── lighting_setup.txt           # Generate: Lighting and atmosphere
└── refinement/
    ├── technical_accuracy.txt       # Refine: Check technical correctness
    └── image_polish.txt             # Refine: Final polish and details
```

### **2. Orchestration Layer**

**File**: `shared/image/orchestrator.py` or similar

```python
class ImagePromptOrchestrator:
    """Chains specialized prompts for image generation"""
    
    def generate_hero_image_prompt(self, material: str) -> str:
        # Stage 1: Research material properties
        properties = self._research_properties(material)
        
        # Stage 2: Generate visual appearance
        visual = self._generate_visual_description(material, properties)
        
        # Stage 3: Compose before/after layout
        composition = self._compose_hero_layout(material, visual)
        
        # Stage 4: Add lighting and atmosphere
        final = self._apply_lighting_setup(composition, properties)
        
        return final
    
    def _research_properties(self, material: str) -> Dict:
        """Specialized prompt: Extract material properties"""
        template = self._load_template('research/material_properties.txt')
        prompt = template.format(material_name=material)
        return self.api.call(prompt, temperature=0.3)  # Low temp for accuracy
    
    def _generate_visual_description(self, material: str, props: Dict) -> str:
        """Specialized prompt: Generate visual description"""
        template = self._load_template('generation/visual_appearance.txt')
        prompt = template.format(
            material_name=material,
            color=props['color'],
            texture=props['texture'],
            reflectivity=props['reflectivity']
        )
        return self.api.call(prompt, temperature=0.7)  # Higher temp for creativity
    
    # ... more specialized methods
```

### **3. Context Passing**

**Critical**: Each stage receives OUTPUT from previous stage as INPUT:

```python
# ✅ CORRECT: Pass context forward
stage1_output = research_prompt(material)
stage2_output = visual_prompt(material, stage1_output)  # Uses stage 1 results
stage3_output = compose_prompt(material, stage1_output, stage2_output)

# ❌ WRONG: Independent prompts without context
stage1 = research_prompt(material)
stage2 = visual_prompt(material)  # Doesn't use stage 1!
stage3 = compose_prompt(material)  # Duplicates work!
```

---

## 📐 Text Generation Example

### Current Architecture (Single-Pass with Learning)

**File**: `generation/core/evaluated_generator.py` (QualityEvaluatedGenerator)

```python
def generate(self, material: str, component: str) -> QualityEvaluatedResult:
    # Stage 1: Build base prompt from template
    base_prompt = self.prompt_builder.build_prompt(
        component_type=component,
        material_name=material,
        voice_params=self.voice_params
    )
    
    # Stage 2: Add humanness layer (randomized voice, structure)
    humanness_prompt = self.humanness_optimizer.generate_humanness_instructions(
        component_type=component,
        strictness_level=1  # Fixed level, no retry escalation
    )
    
    # Stage 3: Generate content (single API call)
    content = self.api.generate(humanness_prompt)
    
    # Stage 4: Save immediately to Materials.yaml (no gating)
    self._save_to_yaml(material, component, content)
    
    # Stage 5: Evaluate quality (for learning, NOT gating)
    evaluation = self.evaluator.evaluate(content)
    winston_result = self._check_winston_detection(content)
    
    # Stage 6: Log to learning database
    self._log_attempt_for_learning(evaluation, winston_result)
    
    return QualityEvaluatedResult(success=True, content=content, quality_scores=...)
```

**Why This Works**:
- ✅ Single-pass: fast generation (~5 seconds)
- ✅ Always saves: 100% completion rate
- ✅ Still evaluates: quality scores logged for learning
- ✅ Clear data flow: template → humanness → generation → save → evaluate → log

---

## 🎨 Image Generation Example (NEW)

### Proposed Architecture

**File**: `shared/image/orchestrator.py`

```python
class ImagePromptOrchestrator:
    """Orchestrates chained prompts for image generation"""
    
    def generate_hero_image(
        self,
        domain: str,
        identifier: str,
        **kwargs
    ) -> ImagePrompt:
        """
        Generate hero image through prompt chaining.
        
        Chain:
        1. Material Research (if needed)
        2. Visual Appearance Generation
        3. Composition Layout
        4. Technical Refinement
        5. Final Assembly
        """
        
        # Stage 1: Research phase (specialized prompt)
        research_data = self._research_stage(domain, identifier)
        
        # Stage 2: Visual description (specialized prompt)
        visual_desc = self._visual_stage(identifier, research_data)
        
        # Stage 3: Composition (specialized prompt)
        composition = self._composition_stage(identifier, visual_desc, research_data)
        
        # Stage 4: Technical refinement (specialized prompt)
        refined = self._refinement_stage(composition, research_data)
        
        # Stage 5: Final assembly
        final_prompt = self._assembly_stage(refined, **kwargs)
        
        return ImagePrompt(
            prompt=final_prompt,
            metadata={
                'research': research_data,
                'visual': visual_desc,
                'composition': composition,
                'stages': ['research', 'visual', 'composition', 'refinement', 'assembly']
            }
        )
    
    def _research_stage(self, domain: str, identifier: str) -> Dict:
        """Stage 1: Research material/contaminant properties"""
        template = self._load_template('research/properties.txt')
        prompt = template.format(
            domain=domain,
            identifier=identifier
        )
        
        # Use low temperature for factual accuracy
        result = self.api.generate(prompt, temperature=0.3)
        return self._parse_research_output(result)
    
    def _visual_stage(self, identifier: str, research: Dict) -> str:
        """Stage 2: Generate visual appearance description"""
        template = self._load_template('generation/visual_appearance.txt')
        prompt = template.format(
            name=identifier,
            properties=research['properties'],
            color=research.get('color', 'natural'),
            texture=research.get('texture', 'smooth')
        )
        
        # Higher temperature for creative visual descriptions
        return self.api.generate(prompt, temperature=0.7)
    
    def _composition_stage(
        self,
        identifier: str,
        visual_desc: str,
        research: Dict
    ) -> str:
        """Stage 3: Compose before/after layout"""
        template = self._load_template('generation/hero_composition.txt')
        prompt = template.format(
            name=identifier,
            visual_description=visual_desc,
            category=research.get('category', 'unknown')
        )
        
        return self.api.generate(prompt, temperature=0.6)
    
    def _refinement_stage(self, composition: str, research: Dict) -> str:
        """Stage 4: Technical refinement and accuracy check"""
        template = self._load_template('refinement/technical_accuracy.txt')
        prompt = template.format(
            composition=composition,
            technical_constraints=research.get('constraints', [])
        )
        
        return self.api.generate(prompt, temperature=0.4)
    
    def _assembly_stage(self, refined: str, **kwargs) -> str:
        """Stage 5: Final assembly with any additional requirements"""
        template = self._load_template('refinement/final_polish.txt')
        prompt = template.format(
            content=refined,
            **kwargs
        )
        
        return self.api.generate(prompt, temperature=0.5)
```

---

## 🔍 Template Specialization

### Research Templates (Low Temperature 0.3-0.4)

**File**: `shared/image/templates/research/material_properties.txt`

```
Task: Extract factual properties for {material_name}

Extract ONLY the following properties:
- Physical color (as it appears naturally)
- Surface texture (smooth, rough, porous, etc.)
- Reflectivity (matte, semi-gloss, mirror-like)
- Common contamination types
- Industrial applications

Output format: JSON with keys matching above
Be precise and factual. No creative descriptions.
```

### Generation Templates (Higher Temperature 0.6-0.8)

**File**: `shared/image/templates/generation/visual_appearance.txt`

```
Task: Create vivid visual description for {name}

Given properties:
- Color: {color}
- Texture: {texture}
- Reflectivity: {reflectivity}

Generate a detailed visual description focusing on:
- How light interacts with the surface
- Visible texture and finish
- Color nuances and variations
- Distinguishing visual characteristics

Be creative and descriptive while staying accurate to the properties.
```

### Composition Templates (Balanced Temperature 0.5-0.6)

**File**: `shared/image/templates/generation/hero_composition.txt`

```
Task: Compose before/after split-screen layout

Material: {name}
Visual characteristics: {visual_description}
Category: {category}

Create a detailed composition description:

LEFT SIDE (Before):
[Describe contaminated state based on typical contamination for this category]

RIGHT SIDE (After):
[Describe cleaned state based on visual characteristics]

TECHNICAL DETAILS:
- Lighting setup
- Camera angle
- Background
- Focus points

Be specific about composition and technical execution.
```

---

## 📊 Benefits of Prompt Chaining

### **1. Separation of Concerns**

| Concern | Specialized Prompt | Temperature |
|---------|-------------------|-------------|
| **Factual Research** | `research/properties.txt` | 0.3 (precise) |
| **Visual Creativity** | `generation/visual.txt` | 0.7 (creative) |
| **Technical Composition** | `generation/composition.txt` | 0.5 (balanced) |
| **Accuracy Check** | `refinement/accuracy.txt` | 0.4 (precise) |

### **2. Optimal Temperature per Stage**

```python
# Different temperatures for different tasks
research_stage(temp=0.3)      # Factual, low variance
visual_stage(temp=0.7)        # Creative, high variance
composition_stage(temp=0.5)   # Balanced
refinement_stage(temp=0.4)    # Precise corrections
```

### **3. Reusability**

```python
# Same research stage used for multiple image types
research = orchestrator._research_stage('materials', 'Aluminum')

# Reuse research for different compositions
hero = orchestrator._compose_hero(research)
micro = orchestrator._compose_micro(research)
industrial = orchestrator._compose_industrial(research)
```

### **4. Debuggability**

```python
# Easy to debug specific stage
result = orchestrator.generate_hero_image('materials', 'Aluminum')

print(result.metadata['research'])      # Check research stage
print(result.metadata['visual'])         # Check visual stage
print(result.metadata['composition'])    # Check composition stage
```

---

## 🚨 Policy Enforcement

### **MANDATORY for ALL Generation Systems**

✅ **Text Generation**: Already compliant (evaluated_generator.py)
✅ **Image Generation**: Must implement orchestrator pattern
✅ **Any New Domains**: Must follow chaining pattern

### **Code Review Checklist**

Before accepting any generation code:

- [ ] Is there an orchestrator/coordinator layer?
- [ ] Are prompts specialized (one task each)?
- [ ] Is context passed between stages?
- [ ] Are temperatures optimized per stage?
- [ ] Are templates in separate files (not code)?
- [ ] Can each stage be tested independently?
- [ ] Is the data flow documented?

### **Grade Penalties**

| Violation | Grade Impact |
|-----------|-------------|
| Monolithic prompt (no chaining) | -30 points (Grade C max) |
| Prompts hardcoded in code | -20 points (Tier 1 violation) |
| No context passing between stages | -15 points |
| Missing orchestration layer | -25 points |
| Cannot test stages independently | -10 points |

---

## 📚 Examples from Codebase

### ✅ **GOOD: Text Generation Chaining**

**File**: `generation/core/evaluated_generator.py` (lines 150-250)

```python
# Stage 1: Base prompt
base = self.prompt_builder.build_prompt(...)

# Stage 2: Humanness enhancement
enhanced = self.humanness_optimizer.enhance(base, ...)

# Stage 3: Generation
content = self.api.generate(enhanced)

# Stage 4: Evaluation
eval = self.evaluator.evaluate(content)

# Stage 5: Feedback loop
if eval.score < threshold:
    content = self._apply_feedback(enhanced, eval.feedback)
```

### ✅ **GOOD: Voice Orchestration**

**File**: `shared/voice/orchestrator.py`

Chains multiple voice parameters through stages.

### ❌ **BAD: Monolithic Approach** (Historical, now fixed)

```python
# OLD APPROACH - DON'T DO THIS
def generate(material):
    prompt = f"""
    Research {material} properties, generate visual description,
    create before/after composition, ensure technical accuracy,
    apply style guidelines, format output...
    [3000 words of conflicting instructions]
    """
    return api.generate(prompt)  # One massive call
```

---

## 🎯 Implementation Timeline

### **Phase 1: Image Generation** (IMMEDIATE)

1. Create `shared/image/orchestrator.py`
2. Create specialized templates in `shared/image/templates/`
3. Update `shared/image/generator.py` to use orchestrator
4. Add tests for each stage independently

### **Phase 2: Cross-Domain Validation** (WEEK 1)

1. Verify text generation maintains chaining
2. Document all prompt chains
3. Add orchestration to any new domains

### **Phase 3: Quality Metrics** (WEEK 2)

1. Measure quality improvement from chaining
2. Optimize temperatures per stage
3. Fine-tune context passing

---

## 📝 Summary

**Core Rule**: Maximum use of prompt chaining and orchestration to preserve separation of concerns and specificity.

**Apply To**:
- ✅ Text generation (already compliant)
- ✅ Image generation (implement now)
- ✅ Any future generation systems

**Benefits**:
- Clear separation of concerns
- Optimal parameters per stage
- Reusable components
- Easy debugging
- Better quality output

**Enforcement**: Code review checklist + grade penalties for violations

---

**Policy Owner**: AI Architecture Team  
**Review Date**: Monthly  
**Last Updated**: November 27, 2025
