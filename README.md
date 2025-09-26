# Z-Beam Generator

A dynamic, schema-driven content generator for laser cleaning technical documentation with enhanced frontmatter management, real-time status updates, and robust fail-fast architecture.

## ✨ Features

- **🏗️ Consolidated Architecture**: Streamlined to 6 active components from original 11
- **📊 Schema-Driven**: Fully dynamic content generation using JSON schemas
- **🗂️ Unified Frontmatter**: Single component generating both materialProperties and machineSettings
- **🤖 AI-Powered**: DeepSeek API integration for frontmatter generation
- **� PropertyResearcher**: Two-stage property discovery with 85% confidence threshold
- **🏭 Component Factory**: ComponentGeneratorFactory pattern for clean component management  
- **🧪 Comprehensive Testing**: Integration test suite covering all 6 components
- **🔧 Fail-Fast Architecture**: Explicit dependency validation with no fallbacks
- **💾 122 Materials Ready**: Complete material database with YAML frontmatter
- **📋 Dependency Validation**: Frontmatter-dependent components with cascading failure prevention

## 🏗️ Architecture Overview

The Z-Beam Generator uses a consolidated 6-component architecture for streamlined content generation:

### Component Structure
```
z-beam-generator/
├── components/                     # 6 active components
│   ├── frontmatter/               # Unified metadata with materialProperties + machineSettings  
│   ├── author/                    # Author information (depends on frontmatter)
│   ├── badgesymbol/              # Material symbol badges (depends on frontmatter)
│   ├── metatags/                 # HTML meta tags
│   ├── jsonld/                   # JSON-LD structured data
│   └── propertiestable/          # Technical properties table
├── research/                      # PropertyResearcher two-stage system
├── schemas/                       # frontmatter.json + json-ld.json validation
├── tests/                         # Comprehensive integration test suite
└── docs/                          # Architecture and usage documentation
```

### Key Architectural Benefits
- **Simplified Dependencies**: Clear frontmatter → component relationships
- **Reduced Maintenance**: 6 components vs. original 11 
- **Improved Performance**: Streamlined generation pipeline
- **Better Testing**: Comprehensive integration test coverage
- **Enhanced Reliability**: Consolidated frontmatter with dual functionality
├── content/
│   └── components/                 # Generated component outputs
├── components/                     # Component generators
├── data/                          # Base material data and schemas
└── ...
```

### Frontmatter-First Architecture
The system now uses a **frontmatter-first approach** where validated material data drives all component generation:

1. **Root-Level Frontmatter**: Material data elevated to project root for better visibility
2. **Schema Validation**: JSON Schema enforces data integrity across 109+ materials
3. **Fail-Fast Components**: Components validate frontmatter before generation
4. **Enhanced Error Handling**: Specific, actionable error messages with field-level validation

## 🚀 Recent Updates (September 2025)

### � Unit/Value Separation Implementation (v6.1.0) - **LATEST**

**Major Enhancement**: Complete implementation of numeric-only value format with clean unit separation.

**Key Achievements:**
- ✅ **Pure Numeric Values**: All property and machine setting values are now numeric (int/float)
- ✅ **Clean Unit Separation**: Units stored in dedicated `*Unit` fields (e.g., `densityUnit: "g/cm³"`)
- ✅ **Min/Max Field Processing**: Fixed UnifiedPropertyEnhancementService to process all Min/Max fields
- ✅ **Schema Validation**: Updated JSON schema to enforce numeric types for all value fields
- ✅ **Comprehensive Testing**: Enhanced test suite validates numeric-only format
- ✅ **Mathematical Processing Ready**: Clean numeric values enable direct calculations

**Before vs After:**
```yaml
# Before: Mixed string/numeric with units embedded
density: "8.9 g/cm³"
powerRange: "50 W"
meltingMax: "2800°C"

# After: Clean numeric separation
density: 8.9
densityUnit: "g/cm³"
powerRange: 50.0
powerRangeUnit: "W" 
meltingMax: 2800
meltingPointUnit: "°C"
```

**Technical Implementation:**
- **`_extract_numeric_only()` method**: Regex-based numeric extraction from unit strings
- **Enhanced `_preserve_min_max_properties()`**: Processes Min/Max fields that contain units
- **Schema Updates**: All Min/Max fields now require `"type": "number"`
- **Comprehensive Validation**: 30+ numeric values per material file verified

**Verification Results:**
- **Copper**: 30 numeric values (12 properties + 18 machine settings)
- **Bronze**: 33 numeric values (15 properties + 18 machine settings)
- **Schema Validation**: All generated files pass strict numeric validation
- **Zero String Values**: Complete elimination of units from numeric fields

### 🔬 Pure AI Research Implementation (v6.0.0)

**BREAKING CHANGE**: Complete transformation to pure AI research system with zero fallback defaults.

**Key Achievements:**
- ✅ **100% Fallback Removal**: Eliminated all hardcoded defaults from frontmatter generator and PropertyEnhancementService
- ✅ **AI Research Requirements**: Template forces AI to research all machine settings (scanningSpeed, beamProfile, safetyClass)
- ✅ **Materials.yaml Priority**: Structured data prioritized over AI generation where available
- ✅ **Calculated Enhancements**: Programmatic property breakdown calculations instead of AI generation
- ✅ **Legacy Format Compliance**: Exact match with breccia and brick examples
- ✅ **Fail-Fast Validation**: System fails immediately if values cannot be researched or calculated

**Technical Implementation:**
```yaml
# Before: Hardcoded fallbacks
beamProfile: "Gaussian"  # Default fallback
safetyClass: "Class 4"   # Default fallback

# After: Pure AI research
beamProfile: "Top-hat (flat-top) for uniform energy distribution"  # AI-researched
safetyClass: "Class 4 laser safety requirements with fume extraction"  # AI-researched
```

**Verification Results:**
- **Zirconia Test**: Accurate ZrO2 properties (density 5.68-6.10 g/cm³, melting point 2715°C)
- **Machine Settings**: Material-specific values ("100-1000 mm/s depending on contamination level")
- **Applications**: Research-based uses (aerospace turbine blades, medical dental implants)
- **Zero Fallbacks**: Complete audit confirmed no remaining hardcoded defaults

### Enhanced Frontmatter Management System (v3.0.0)

Major architectural enhancement moving frontmatter to root level with comprehensive validation:

#### ✅ **New Frontmatter Architecture**
- **Root-Level Elevation**: Frontmatter moved from `content/components/frontmatter/` to `frontmatter/materials/`
- **Schema-Driven Validation**: JSON Schema validation for all 109 material frontmatter files
- **Enhanced Management Tools**: `FrontmatterManager` class with caching, validation, and integrity checking
- **Migration System**: Automated migration tools with backup and path updating capabilities
- **Fail-Fast Integration**: Enhanced component generators with strict validation requirements

#### 🔧 **Key Components**
- **`FrontmatterManager`**: Centralized loading, validation, and caching system
- **Migration Tools**: Comprehensive migration script with dry-run capability
- **Enhanced Generators**: Base classes for robust component generation with validation
- **Field Management**: Automated field updating and maintenance tools
- **Integrity Reporting**: Comprehensive validation and completeness reporting

#### 📊 **Benefits Achieved**
- **Data Quality**: Schema validation ensures consistent, valid frontmatter across all materials
- **System Reliability**: Fail-fast validation catches issues before component generation
- **Developer Productivity**: Automated tools reduce manual frontmatter management
- **Architecture Clarity**: Clear separation between data (`frontmatter/`) and outputs (`content/`)
- **Future Flexibility**: Extensible system supports evolving requirements

For detailed implementation guide, see [Frontmatter Architecture Proposal](docs/FRONTMATTER_ARCHITECTURE_PROPOSAL.md)

### Material Data Structure Improvements (v2.2.1)

Major improvement in material data handling ensuring consistent access patterns:

#### ✅ **Fixed Critical Issues**
- **Material Not Found Error**: Fixed "Material 'Steel' not found" error in tests despite material existing in data
- **Batch Generation**: Fixed batch generation mode (`--all` flag) to properly find and process materials
- **Data Structure Consistency**: Ensured consistent access to the "materials" key in data structure
- **Test Environment**: Updated tests to use real materials.yaml file instead of mocks for consistency

#### 🔧 **Key Improvements**
- **Consistent Data Structure**: Modified `load_materials()` to return complete structure with "materials" key
- **Unified Data Source**: Removed mock materials in tests to ensure all code uses real data from materials.yaml
- **Batch Generation Fix**: Updated run.py to properly navigate the materials data structure
- **Comprehensive Testing**: Added new test file specifically for testing material loading functionality

For more details, see [Material Data Structure Improvements](docs/MATERIAL_DATA_STRUCTURE_IMPROVEMENTS.md)

### API Configuration Centralization (v2.1.0)

Major architecture improvement with comprehensive API configuration centralization:

#### ✅ **Fixed Critical Issues**
- **API Timeout Resolution**: Fixed connection timeouts caused by aggressive parameters (max_tokens=2000, temperature=0.9)
- **Configuration Centralization**: Eliminated duplicate API_PROVIDERS definitions across 12+ files
- **Single Source of Truth**: All API configurations now centralized in `run.py`
- **Import Consistency**: Standardized access pattern using `get_api_providers()` function

#### 🔧 **Optimized Parameters**
- **DeepSeek**: max_tokens=800, temperature=0.7 (conservative for large prompts)
- **Grok**: max_tokens=800, temperature=0.7 (reliable for content generation)
- **Winston**: max_tokens=1000, temperature=0.1 (optimized for detection tasks)
- **Timeout Settings**: connect=10s, read=45s (sufficient for 39s response times)

#### 📁 **Files Updated**
- `api/config.py`, `api/client_factory.py`, `api/client_manager.py`
- `api/enhanced_client.py`, `api/key_manager.py`
- `cli/api_config.py`, `cli/component_config.py`, `cli/__init__.py`
- `config/unified_config.py`, `utils/config/environment_checker.py`

#### ✅ **Verified Functionality**
- **API Connectivity**: All 3 providers connect successfully
- **Content Generation**: Frontmatter generation working for Steel material
- **Data Integration**: Materials loaded from `data/materials.yaml` (109 materials, 8 categories)
- **Large Prompt Support**: Successfully handles 4116+ character prompts

## �🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file with your API keys:
```
DEEPSEEK_API_KEY=your_deepseek_key_here
WINSTON_API_KEY=your_winston_key_here
```

### Basic Usage

#### Test API Connection
```bash
python3 run.py --test-api
```

#### Generate for Single Material with Status Updates
```bash
python3 run.py --material "Aluminum"
```

#### Batch Processing
```bash
python3 run.py --all --limit 10
```

## 📋 Available Materials

View all available materials:
```bash
python3 run.py --list-materials
```

**Material Categories:**
- Ceramic (3 materials)
- Composite (9 materials)
- Glass (7 materials)
- Masonry (14 materials)
- Metal (37 materials)
- Plastic (30 materials)
- Semiconductor (6 materials)
- Stone (7 materials)
- Wood (9 materials)

**Total: 122 materials**

## 🧩 Component Types

Each material generates these component types:

| Component | Description | Status | API Provider | Dependencies |
|-----------|-------------|---------|--------------|-------------|
| `frontmatter` | YAML metadata with materialProperties & machineSettings | ✅ Working | deepseek | None |
| `author` | Author information | ✅ Working | none | **REQUIRES frontmatter** |
| `badgesymbol` | Material symbol badge | ✅ Working | none | **REQUIRES frontmatter** |
| `metatags` | HTML meta tags | ✅ Working | none | None |
| `jsonld` | Structured data markup | ✅ Working | none | None |
| `propertiestable` | Technical properties table | ✅ Working | none | None |

**Total: 6 active components** (consolidated from 11 original components)

## ⚠️ CRITICAL DEPENDENCY: Frontmatter Data

**IMPORTANT**: The frontmatter component generates comprehensive metadata including both `materialProperties` and `machineSettings` sections. Component generation depends on this frontmatter data for that specified material. Component failures will cascade without it. This is intentional design.

### Frontmatter Dependency Chain

```
┌─────────────────────────────────────┐
│          Frontmatter               │ ←── REQUIRED for dependent components
│  (materialProperties +             │
│   machineSettings)                 │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   badgesymbol   │    │     author      │
│   Component     │    │   Component     │
│                 │    │                 │
│  DEPENDS ON     │    │  DEPENDS ON     │
│  frontmatter    │    │  frontmatter    │
└─────────────────┘    └─────────────────┘
```

### Consolidated Frontmatter Structure

The frontmatter component now generates a unified structure containing:

#### materialProperties Section
- Physical and chemical properties
- Performance characteristics  
- Technical specifications

#### machineSettings Section
- Laser parameters and power settings
- Processing speeds and configurations
- Equipment recommendations

### Required Frontmatter Fields

#### For badgesymbol Component
- `name` - Material name
- `category` - Material category
- `symbol` - Chemical symbol (e.g., "Al", "Cu")

#### For author Component
- `name` - Material name
- `category` - Material category
- `author` - Author name from frontmatter

#### For All Components
- Complete frontmatter file at: `content/components/frontmatter/{material}-laser-cleaning.md`

### Cascading Failure Behavior

When frontmatter data is missing or incomplete:

1. **Frontmatter Generation Fails**
   - Missing required fields (category, formula, materialProperties)
   - Invalid data structure  
   - File not found

2. **Dependent Components Fail**
   - `badgesymbol` cannot generate without material symbol
   - `author` cannot personalize without author data
   - Other components may fail if they depend on frontmatter data

3. **Complete Material Failure**
   - No content generated for the material
   - User must fix frontmatter data before proceeding
   - System maintains data integrity

### Example Usage

```bash
# Generate all components for a material
$ python3 run.py --material "Aluminum" --components "frontmatter,badgesymbol,author,metatags,jsonld,propertiestable"

# Generate only frontmatter (base dependency)
$ python3 run.py --material "Aluminum" --components "frontmatter"

# Generate dependent components (requires frontmatter to exist)
$ python3 run.py --material "Aluminum" --components "badgesymbol,author"
```

## 🏗️ Consolidated Architecture

The system has been consolidated from 11 original components to **6 active components** for improved maintainability and reduced complexity:

### Architecture Benefits
- **Simplified Dependencies**: Clear frontmatter → dependent component relationships
- **Reduced Maintenance**: Fewer components to maintain and test
- **Improved Reliability**: Consolidated frontmatter includes both materialProperties and machineSettings
- **Better Performance**: Streamlined generation pipeline with fewer API calls

### Component Integration
- **PropertyResearcher**: Two-stage property discovery and value research
- **Schema Validation**: Unified frontmatter.json and json-ld.json schemas  
- **Template System**: Single frontmatter template in MaterialAwarePromptGenerator
- **Factory Pattern**: ComponentGeneratorFactory supports all 6 components

For detailed architecture information, see `docs/CONSOLIDATED_ARCHITECTURE_GUIDE.md`.

# Result:
❌ frontmatter: Missing required fields (category, formula, properties)
❌ badgesymbol: No frontmatter data available
❌ author: No frontmatter data available

# Complete material generation fails
```

### Frontmatter Validation

The system validates frontmatter data before component generation:

```python
def validate_frontmatter_for_generation(frontmatter_data: Dict) -> bool:
    """Validate frontmatter contains sufficient data for generation"""
    required_fields = ['name', 'category', 'properties', 'applications']

    for field in required_fields:
        if field not in frontmatter_data:
            return False

        value = frontmatter_data[field]
        if not value:
            return False

        if field in ['properties', 'applications'] and len(value) == 0:
            return False

    return True
```

### Best Practices

#### For Users
1. **Ensure Frontmatter Exists**
   - Create frontmatter files before generation
   - Validate all required fields are present

2. **Check Frontmatter Completeness**
   - Run validation tests before generation
   - Fix missing fields before proceeding

3. **Understand Failure Causes**
   - Frontmatter issues cause component failures
   - Fix root cause (frontmatter) before retrying

#### For Developers
1. **Always Validate Frontmatter First**
   ```python
   if not validate_frontmatter_for_generation(frontmatter_data):
       raise ValueError("Insufficient frontmatter data for generation")
   ```

2. **Fail Fast on Missing Dependencies**
   ```python
   if not frontmatter_data:
       return ComponentResult(component_type, "", False, "No frontmatter data available")
   ```

3. **Provide Clear Error Messages**
   ```python
   error_msg = f"Missing required frontmatter fields: {missing_fields}"
   ```

### Testing Frontmatter Dependencies

Run comprehensive dependency tests:

```bash
# Test frontmatter dependency chain
python3 tests/test_frontmatter_dependency_chain.py

# Test cascading failures
python3 tests/test_cascading_failure.py

# Validate frontmatter data
python3 tests/test_frontmatter_validation.py
```

### Troubleshooting Frontmatter Issues

#### Common Issues
1. **"No frontmatter data available"**
   - Check if frontmatter file exists
   - Verify file path and naming convention

2. **"Missing required frontmatter fields"**
   - Add missing fields to frontmatter file
   - Validate YAML structure

3. **"Component generation failed"**
   - Check frontmatter data completeness
   - Run validation tests

#### Debugging Steps
1. Check frontmatter file:
   ```bash
   cat content/components/frontmatter/aluminum-laser-cleaning.md
   ```

2. Run dependency tests:
   ```bash
   python3 tests/test_frontmatter_dependency_chain.py
   ```

3. Validate frontmatter structure:
   ```bash
   python3 -c "import yaml; print(yaml.safe_load(open('content/components/frontmatter/aluminum-laser-cleaning.md')))"
   ```

### Component Configuration Notes

- **Static Components** (`api_provider: "none"`): `author`, `badgesymbol`, `propertiestable`, `jsonld`, `metatags`, `table`
  - No API calls required
  - AI detection flags removed (default to `False`)
  - Faster generation, lower cost

- **API-Driven Components**: `frontmatter`, `bullets`, `caption`, `text`, `tags`
  - Use external AI services
  - AI detection enabled for content components
  - Iterative improvement for quality enhancement

- **Critical Dependencies**:
  - **`badgesymbol` REQUIRES `frontmatter`**: Must be generated first, no fallback available
  - **`author` REQUIRES `frontmatter`**: Uses material data for content personalization
  - **Generation Order**: Always generate `frontmatter` → `badgesymbol` → `author` → other components

- **Text Component Special Features**:
  - **Real-time status updates** every 10 seconds
  - **Iterative AI detection** with Winston.ai scoring
  - **Configuration optimization** using DeepSeek
  - **Three-layer prompt system**: Base + Persona + Formatting

## 🏗️ Architecture

### Core Components
- **MaterialLoader**: Loads materials from `data/materials.yaml`
- **ComponentGenerator**: Uses prompts + DeepSeek API
- **SchemaValidator**: Validates against JSON schemas
- **ContentWriter**: Saves to `content/` folder
- **AIDetectionService**: Winston.ai integration for content quality
- **StatusTracker**: Real-time progress monitoring
- **LayerValidator**: Three-layer architecture integrity protection
- **FrontmatterDependencyValidator**: Cascading failure prevention
- **AIDetectionCircuitBreaker**: Service resilience and fallback management
- **ComponentHealthMonitor**: Performance tracking and health assessment
- **PersonaDriftDetector**: Cultural authenticity protection

### File Structure
```
z-beam-generator/
├── run.py                      # Main CLI interface
├── utils/                      # Robustness framework modules
│   ├── layer_validator.py      # Three-layer architecture validation
│   ├── frontmatter_validator.py # Dependency validation & health monitoring
│   └── quality_validator.py    # AI detection circuit breaker & quality assurance
├── generators/
│   ├── dynamic_generator.py    # Schema-driven generator
│   └── component_generators.py # Individual component generators
├── components/                 # Component templates and generators
│   ├── text/
│   │   ├── generator.py        # Text component with status updates
│   │   ├── generators/
│   │   │   └── fail_fast_generator.py # Core generation logic
│   │   └── prompts/            # Three-layer prompt system
│   │       ├── base_content_prompt.yaml
│   │       ├── personas/
│   │       └── formatting/
│   └── [other components]/
├── ai_detection/               # Winston.ai integration
├── api/                        # API client management
├── data/materials.yaml         # Materials database
├── schemas/                    # JSON validation schemas
├── test_robustness_improvements.py # Comprehensive robustness tests
└── content/                    # Generated output
    └── components/             # Component-organized output
```

## 🧪 Testing

### Unified Test Runner

Run comprehensive tests across all architectures with a single command:

```bash
# Run all tests (components + services)
python3 run_unified_tests.py

# Run component tests only (with frontmatter validation)
python3 run_unified_tests.py --components

# Run service tests only (AI detection, iterative workflow, etc.)
python3 run_unified_tests.py --services

# Quick component tests (skip slow tests)
python3 run_unified_tests.py --components --quick

# Verbose output with detailed results
python3 run_unified_tests.py --verbose
```

**Features:**
- ✅ **Unified Architecture**: Combines component-based and service-based testing
- ✅ **Frontmatter Validation**: Only tests materials with complete frontmatter files
- ✅ **Dependency Testing**: Validates frontmatter dependency chain and cascading failures
- ✅ **Comprehensive Coverage**: 20+ tests covering all system components and services
- ✅ **Real-time Status**: Live progress tracking during test execution
- ✅ **Clear Reporting**: Detailed pass/fail summary with timing information
- ✅ **Fail-Fast Validation**: Confirms no fallbacks or mocks in production code

**Test Categories:**
- **Component Tests**: Frontmatter dependency validation, core component generation
- **Service Tests**: AI detection optimization, iterative workflow, dynamic evolution
- **Integration Tests**: Cross-system compatibility and performance validation

### Individual Test Files

Run comprehensive test suite:
```bash
python3 -m pytest test_*.py -v
```

**Test Coverage:**
- ✅ 13 core functionality tests
- ✅ AI detection integration tests
- ✅ Iterative improvement tests
- ✅ Status update functionality tests
- ✅ Prompt system validation tests
- ✅ **NEW**: Robustness framework tests (29 tests)
- ✅ **NEW**: Layer validation and circuit breaker tests
- ✅ **NEW**: Frontmatter dependency validation tests
- ✅ **NEW**: AI detection circuit breaker tests
- ✅ **NEW**: Cultural authenticity protection tests

### Robustness Test Files

#### `test_robustness_improvements.py`
Comprehensive testing for the robustness framework:
- Three-layer architecture validation with caching and recovery
- Frontmatter dependency validation and cascading failure prevention
- AI detection circuit breaker with service fallback testing
- Component health monitoring and performance metrics
- Cultural authenticity protection and persona drift detection
- Quality score validation with persona-specific thresholds

**Key Test Categories:**
- **Layer Validation Tests**: Base, persona, and formatting layer integrity
- **Dependency Tests**: Frontmatter requirement validation and risk assessment
- **Circuit Breaker Tests**: Service failure handling and recovery mechanisms
- **Health Monitoring Tests**: Component performance and status tracking
- **Authenticity Tests**: Persona drift detection and cultural validation

### Running Specific Tests
```bash
# Run robustness framework tests
python3 -m pytest test_robustness_improvements.py -v

# Run AI detection optimization tests
python3 -m pytest tests/test_ai_detection_optimization.py -v

# Run prompt chain integration tests
python3 -m pytest tests/test_prompt_chain_integration.py -v

# Run all tests with coverage
python3 -m pytest test_*.py -v --cov=components --cov=api --cov=utils
```

### Test Results Summary
- **EXCELLENT (100%)**: All 29 robustness tests pass - production ready
- **GOOD (80-99%)**: Minor issues - mostly functional
- **FAIR (60-79%)**: Some issues - core functionality works
- **POOR (<60%)**: Significant issues - needs debugging

**Recent Testing Improvements:**
- ✅ **Fixed hanging tests** by implementing proper mock client usage
- ✅ **Resolved API parameter issues** in TextComponentGenerator
- ✅ **Corrected frontmatter file structure** for aluminum test case
- ✅ **Validated fail-fast behavior** with mock client exceptions
- ✅ **Added comprehensive robustness test coverage** (29 new tests)

## ⚙️ Configuration

### API Settings
Configure in `.env`:
```
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### Component Configuration
The system uses configuration files for component generation:

#### PropertyResearcher Settings
Configure property discovery in `research/material_property_researcher.py`:
- **Confidence Threshold**: 85% for property values
- **Two-Stage Process**: Property discovery + value research
- **API Integration**: Uses DeepSeek for property analysis

#### Schema Validation
- **frontmatter.json**: 41KB comprehensive schema for frontmatter generation
- **json-ld.json**: 10KB schema for structured data validation
- **Material Symbols**: Automatic generation with chemical symbol fallbacks

### Component Dependencies
```yaml
# Dependency chain for component generation
frontmatter:
  dependencies: []
  generates: [materialProperties, machineSettings]
  
author:
  dependencies: [frontmatter]
  requires: [name, category, author]
  
badgesymbol: 
  dependencies: [frontmatter]
  requires: [name, category, symbol]

# Independent components (no dependencies)
metatags: []
jsonld: []
propertiestable: []
```

## 📊 Performance

### Current Status
- **✅ 6/6 components** generating successfully (consolidated architecture)
- **✅ Frontmatter consolidation** with materialProperties + machineSettings
- **✅ PropertyResearcher integration** with two-stage discovery system
- **✅ Schema validation** with frontmatter.json and json-ld.json
- **✅ Component factory** supporting all active components
- **✅ Dependency validation** preventing cascading failures

### Generation Performance
- **Frontmatter Generation**: ~20-30s per material (API-dependent)
- **Local Components**: <1s per component (author, badgesymbol, metatags, jsonld, propertiestable)
- **PropertyResearcher**: ~5-10s for property discovery and value research
- **Schema Validation**: <0.1s per component
- **Total Generation Time**: ~25-40s per complete material

### Architecture Performance Metrics
- **Component Discovery**: <0.01s via ComponentGeneratorFactory
- **Dependency Validation**: <0.05s per component analysis
- **Schema Loading**: <0.1s (cached after first load)
- **Template Processing**: <0.01s per template
- **Memory Usage**: Reduced by ~40% due to consolidation

### Quality Metrics
- **Schema Compliance**: 100% for all generated components
- **Frontmatter Completeness**: Both materialProperties and machineSettings sections
- **PropertyResearcher Accuracy**: 85% confidence threshold
- **Component Integration**: 6/6 components working with factory pattern
- **Test Coverage**: Comprehensive integration tests for all workflows

## 🛠️ Development

### Adding New Materials
Edit `data/materials.yaml`:
```yaml
materials:
  metal:
    items:
      - name: "New Material"
        category: "metal"
        article_type: "material"
```

### Adding New Components
1. Create component directory: `components/newcomponent/`
2. Add `generator.py` with component logic
3. Update `generators/component_generators.py`
4. Add validation schema if needed

### Schema Updates
Update schemas in `schemas/` directory to modify validation rules.

## 🧪 Testing

The Z-Beam system includes comprehensive testing for the consolidated 6-component architecture:

### Integration Testing
```bash
# Run comprehensive integration tests
python3 -m pytest tests/test_consolidated_architecture.py -v

# Run all tests  
python3 -m pytest test_*.py -v
```

### Test Coverage

#### Consolidated Architecture Tests (`tests/test_consolidated_architecture.py`)
- **Component Integration**: All 6 components working with ComponentGeneratorFactory
- **Frontmatter Consolidation**: Validates both materialProperties and machineSettings sections  
- **Dependency Testing**: Tests frontmatter-dependent components (author, badgesymbol)
- **DataMetrics Compliance**: Ensures generated content matches expected schema structure
- **PropertyResearcher Integration**: Tests two-stage property discovery system
- **Architecture Stability**: Validates core architectural patterns and reliability

#### Legacy Tests
- **Exception Handling**: API error scenarios and recovery
- **NA Normalization**: Data cleaning and standardization
- **Component Generation**: Individual component functionality

### Test Results Status
All integration tests passing for consolidated 6-component architecture:
- ✅ **Frontmatter generation** with unified materialProperties + machineSettings
- ✅ **Component factory** creating all 6 component types
- ✅ **Dependency validation** for author and badgesymbol components
- ✅ **Schema compliance** for all generated content
- ✅ **PropertyResearcher** integration and confidence thresholds

## ✅ System Status

### Architecture Consolidation Complete
All component consolidation work has been completed successfully:

- ✅ **6 Active Components**: frontmatter, author, badgesymbol, metatags, jsonld, propertiestable
- ✅ **Text Component Removed**: All references and dependencies cleaned up
- ✅ **Schema System Restored**: frontmatter.json and json-ld.json from backup archives
- ✅ **PropertyResearcher Updated**: Now uses consolidated frontmatter schema
- ✅ **Template System Cleaned**: MaterialAwarePromptGenerator only has frontmatter template
- ✅ **Factory Pattern Working**: ComponentGeneratorFactory supports all 6 components
- ✅ **Testing Complete**: Integration test suite covers all workflows
- ✅ **Documentation Updated**: Architecture guide and main README refreshed

### Recent Achievements
- **210 files removed** during consolidation (metricsproperties, metricsmachinesettings, text components)
- **Unified frontmatter** generating both materialProperties and machineSettings sections
- **Comprehensive test suite** validating all 6 components and architectural patterns
- **Complete documentation** including consolidated architecture guide

## 🔮 Future Enhancements

### Potential Improvements
- [ ] **Performance Optimization**: Further reduce generation times through caching
- [ ] **Additional Materials**: Expand from 122 to more specialized materials
- [ ] **Enhanced Validation**: More sophisticated schema validation patterns
- [ ] **Monitoring Dashboard**: Real-time system health and performance metrics
- [ ] **Batch Processing**: Improved bulk generation capabilities

### Maintenance Goals  
- [ ] **Regular Schema Updates**: Keep schemas current with evolving requirements
- [ ] **Component Documentation**: Individual component usage guides
- [ ] **API Integration**: Additional AI service providers for redundancy

## 📚 Documentation

- [Three-Layer Architecture](docs/CLEAN_ARCHITECTURE_SUMMARY.md)
- [AI Detection Integration](docs/WINSTON_AI_INTEGRATION.md)
- [Robustness Framework](docs/z-beam_ROBUSTNESS_IMPROVEMENTS.md)
- [Testing Framework](tests/README.md)
- [Frontmatter Dependencies](docs/FRONTMATTER_DEPENDENCY_ARCHITECTURE.md)
- [Component Standards](docs/COMPONENT_STANDARDS.md)
- [Component Architecture Standards](docs/COMPONENT_ARCHITECTURE_STANDARDS.md) ⚠️ **Required Reading**

## 🤝 Contributing

1. Run tests: `python3 -m pytest test_*.py -v`
2. Validate changes with batch mode
3. Update documentation as needed
4. Ensure all tests pass before submitting

## 📄 License

[Add your license information here]

---

**Need Help?**
- Use `--help` for command options
- Check test results: `python3 -m pytest test_*.py -v`
- Check logs in console output
- Test API with `--test-api`
- Use batch mode for best experience

**Status Updates:** The system now provides real-time status updates every 10 seconds during text generation, showing progress, elapsed time, and AI detection scores!
