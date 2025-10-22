# Z-Beam Generator: 3-Mode Pipeline Proposal

## 🎯 Overview

Consolidate all generation capabilities into three distinct, focused modes that follow the data storage policy and eliminate redundancy.

## 📊 Mode Definitions

### **Mode 1: TEXT GENERATION**
**Purpose**: Generate AI-powered text content and write directly to Materials.yaml
**Target**: Text fields only (descriptions, captions, explanations)
**Data Flow**: AI → Materials.yaml
**Command**: `python3 run.py --mode text --material "MaterialName"`

**Capabilities**:
- Caption generation (before_text, after_text)
- Technical descriptions 
- Process explanations
- Educational content
- SEO descriptions
- Author-voice generated text

**Key Features**:
- Writes directly to Materials.yaml (no intermediate files)
- Uses VoiceOrchestrator for author authenticity
- Follows GROK fail-fast principles
- Preserves existing property data

### **Mode 2: DATA RESEARCH**
**Purpose**: Research and populate missing property values in Materials.yaml
**Target**: Technical properties, measurements, specifications
**Data Flow**: AI Research → Materials.yaml
**Command**: `python3 run.py --mode research --material "MaterialName"`

**Capabilities**:
- Property value research (density, melting point, thermal conductivity, etc.)
- Range calculations (min/max values)
- Unit standardization
- Confidence scoring
- Source attribution

**Integration of Existing Tools**:
- PropertyValueResearcher
- CategoryRangeResearcher
- AI Materials Researcher
- Validation systems

### **Mode 3: FRONTMATTER OUTPUT**
**Purpose**: Generate component frontmatter from Materials.yaml + Categories.yaml
**Target**: All component types (frontmatter, caption, text, etc.)
**Data Flow**: Materials.yaml + Categories.yaml → content/components/
**Command**: `python3 run.py --mode frontmatter --material "MaterialName" --component "ComponentType"`

**Capabilities**:
- Frontmatter YAML generation
- Caption YAML output
- Text component output
- All component types supported
- Schema validation
- Dependency resolution

## 🔧 Technical Architecture

### **Core Pipeline Class**
```python
class GenerationPipeline:
    def __init__(self):
        self.mode = None
        self.materials_data = None
        self.categories_data = None
    
    def execute(self, mode: str, material: str, component: str = None):
        if mode == "text":
            return self.generate_text(material)
        elif mode == "research":
            return self.research_data(material)
        elif mode == "frontmatter":
            return self.generate_frontmatter(material, component)
```

### **Mode 1: Text Generation Flow**
```
1. Load Materials.yaml
2. Identify text fields (captions, descriptions)
3. Initialize VoiceOrchestrator with author data
4. Generate AI content using author voice
5. Validate content quality
6. Write directly to Materials.yaml
7. Save backup
```

### **Mode 2: Data Research Flow**
```
1. Load Materials.yaml
2. Scan for missing/empty properties
3. Initialize research services (AI, Web API, Database)
4. Research missing values with confidence scoring
5. Validate and standardize units
6. Write to Materials.yaml with metadata
7. Generate research report
```

### **Mode 3: Frontmatter Output Flow**
```
1. Load Materials.yaml + Categories.yaml
2. Validate data completeness
3. Apply component-specific transformations
4. Generate component YAML/content
5. Write to content/components/[type]/
6. Validate output schema
```

## 📁 File Organization

### **New Pipeline Structure**
```
pipeline/
├── __init__.py
├── core/
│   ├── pipeline_manager.py      # Main orchestrator
│   ├── mode_router.py           # Route to appropriate mode
│   └── validation.py            # Cross-mode validation
├── modes/
│   ├── text_generator.py        # Mode 1: Text generation
│   ├── data_researcher.py       # Mode 2: Property research
│   └── frontmatter_output.py    # Mode 3: Component output
└── integrations/
    ├── voice_integration.py     # VoiceOrchestrator wrapper
    ├── research_integration.py  # Existing research tools
    └── component_integration.py # Component generators
```

### **Integration with Existing Code**
- **Keep**: All existing research tools (PropertyValueResearcher, etc.)
- **Keep**: VoiceOrchestrator system
- **Keep**: Component generators
- **Consolidate**: Multiple entry points into 3 clear modes
- **Eliminate**: Redundant generation paths

## 🚦 Command Interface

### **Mode 1: Text Generation**
```bash
# Generate all text fields for a material
python3 run.py --mode text --material "Steel"

# Generate specific text field
python3 run.py --mode text --material "Steel" --field "caption"

# Batch text generation
python3 run.py --mode text --batch --materials "Steel,Aluminum,Copper"
```

### **Mode 2: Data Research**
```bash
# Research missing properties for a material
python3 run.py --mode research --material "Steel"

# Research specific properties
python3 run.py --mode research --material "Steel" --properties "density,melting_point"

# Research with confidence threshold
python3 run.py --mode research --material "Steel" --confidence-threshold 85
```

### **Mode 3: Frontmatter Output**
```bash
# Generate frontmatter for a material
python3 run.py --mode frontmatter --material "Steel"

# Generate specific component
python3 run.py --mode frontmatter --material "Steel" --component "caption"

# Generate all components
python3 run.py --mode frontmatter --material "Steel" --all-components
```

## 📊 Data Flow Validation

### **Mode 1 → Mode 2 → Mode 3 Pipeline**
```
1. Mode 1: Generate text descriptions → Materials.yaml
2. Mode 2: Research missing properties → Materials.yaml  
3. Mode 3: Generate frontmatter → content/components/
```

### **Data Integrity Checks**
- Materials.yaml is single source of truth
- No frontmatter → Materials.yaml flow (one-way only)
- Automatic backup before modifications
- Validation at each mode transition

## 🔍 Benefits

### **Clarity & Organization**
- **3 clear purposes** instead of multiple overlapping commands
- **Predictable data flow** (always through Materials.yaml)
- **Consolidates existing tools** without losing functionality

### **Developer Experience**
- **Single entry point** with clear mode selection
- **Consistent command structure** across all modes
- **Integrated validation** and error handling

### **Data Architecture Compliance**
- **Enforces Materials.yaml** as single source of truth
- **Prevents frontmatter pollution** of data storage
- **Maintains backup and versioning** systems

### **Fail-Fast Architecture**
- **Mode isolation** prevents cross-contamination
- **Clear validation points** at each stage
- **Explicit error handling** per mode

## 🚀 Migration Path

### **Phase 1: Pipeline Structure**
1. Create pipeline/ directory structure
2. Implement PipelineManager class
3. Create mode routing system

### **Phase 2: Mode Integration**
1. Integrate existing text generation (captions, etc.)
2. Consolidate research tools under Mode 2
3. Wrap component generators for Mode 3

### **Phase 3: Command Interface**
1. Update run.py with --mode parameter
2. Maintain backward compatibility temporarily
3. Add comprehensive help and examples

### **Phase 4: Testing & Validation**
1. Test each mode independently
2. Validate end-to-end pipeline
3. Performance optimization

### **Phase 5: Documentation & Cleanup**
1. Update all documentation
2. Remove redundant commands
3. Create usage examples

## 📋 Implementation Checklist

- [ ] Create pipeline/ directory structure
- [ ] Implement PipelineManager class
- [ ] Create TextGenerator (Mode 1)
- [ ] Create DataResearcher (Mode 2) 
- [ ] Create FrontmatterOutput (Mode 3)
- [ ] Update run.py with --mode parameter
- [ ] Add comprehensive validation
- [ ] Create migration documentation
- [ ] Test end-to-end pipeline
- [ ] Update user documentation

## 🎯 Success Criteria

1. **Single Command Interface**: `python3 run.py --mode [text|research|frontmatter]`
2. **Clear Data Flow**: Materials.yaml → Components (one-way)
3. **Consolidated Tools**: All existing functionality preserved
4. **Fail-Fast Compliance**: Robust error handling and validation
5. **Developer Clarity**: Obvious which mode to use for any task

---

**Status**: Proposal Ready for Review and Implementation
**Estimated Implementation**: 1-2 weeks
**Risk Level**: Low (builds on existing, working systems)