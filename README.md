# Z-Beam Generator

A dynamic, schema-driven content generator for laser cleaning technical documentation with real-time status updates and iterative AI detection improvement.

## ✨ Features

- **🎮 Interactive Mode**: Step-by-step generation with user prompts
- **📊 Schema-Driven**: Fully dynamic content generation using JSON schemas
- **🤖 AI-Powered**: Integration with DeepSeek API for intelligent content creation
- **📈 Real-Time Status Updates**: Live progress tracking every 10 seconds during generation
- **🔄 Iterative AI Detection**: Winston.ai integration for content quality improvement
- **🧪 Comprehensive Testing**: 41+ tests ensuring reliability
- **🔧 Flexible Architecture**: Clean, maintainable codebase

## 🧠 AI Detection System

### Recent Improvements (v2.1)

The AI detection system has been significantly enhanced with a focus on stability, realistic targets, and technical content optimization:

#### ✅ **Fixed Issues**
- **Prompt Chain Integration**: AI detection prompt now properly included in API calls (increased from ~3000 to 4246 characters)
- **Simplified Enhancement Strategy**: Reduced from 8-9 features to 4 core features for better stability
- **Realistic Score Targets**: Adjusted target from 70.0 to 45.0 for achievable technical content goals
- **Conservative Optimization**: Implemented technical-focused, score-based optimization logic

#### 🎯 **Core Features (4 Enabled)**
- **Conversational Style**: Natural, professional technical writing
- **Natural Language Patterns**: Authentic sentence structure and flow
- **Cultural Adaptation**: Appropriate for technical audience
- **Sentence Variability**: Natural length and complexity variation

#### 📊 **Performance Metrics**
- **Target Score**: 45.0 (realistic for technical content)
- **Score Stability**: No degradation observed in testing
- **Optimization Strategy**:
  - Score < 20: Enable all 4 core features
  - Score 20-40: Maintain and refine existing features
  - Score > 40: Minimal technical adjustments only

#### 🔧 **Configuration**
```yaml
# config/ai_detection.yaml
provider: winston
enabled: true
target_score: 45.0
conversational_style: true
natural_language_patterns: true
cultural_adaptation: true
sentence_variability: true
# Advanced features disabled for stability
human_error_simulation: false
emotional_depth: false
```

#### 🧪 **Testing & Validation**
- **Comprehensive Test Suite**: New tests for prompt chain integration and optimization
- **API Connectivity Tests**: Validates Winston.ai and DeepSeek integration
- **Performance Validation**: Ensures stable scores across iterations
- **Configuration Backup/Restore**: Automatic backup system for safety

### AI Detection Integration

The system integrates Winston.ai for real-time content quality assessment:

- **Real-time Scoring**: Every generated content piece receives AI detection analysis
- **Iterative Improvement**: Automatic content optimization using DeepSeek API
- **Quality Thresholds**: Configurable scoring targets with human believability metrics
- **Performance Tracking**: Full iteration history and improvement tracking

### Three-Layer Prompt System

The text component uses a sophisticated three-layer prompt architecture:

1. **Base Layer**: Pure technical content requirements and guidelines
2. **AI Detection Layer**: Human authenticity and natural writing patterns
3. **Persona Layer**: Author characteristics (American, British, Australian, Canadian)
4. **Formatting Layer**: Cultural presentation preferences and structure

**Prompt Chain Length**: ~4246 characters (including AI detection guidelines)

## 🚀 Quick Start

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

#### Interactive Mode (Recommended)
```bash
python3 run.py --interactive
```

#### Batch Processing
```bash
python3 run.py --all --limit 10
```

## 🎮 Interactive Mode

The interactive mode provides the best user experience with fine-grained control and real-time status updates:

### Key Features
- **Step-by-step processing**: Generate one material at a time
- **Real-time status updates**: Progress tracking every 10 seconds
- **User prompts**: Choose to continue, skip, pause, or quit
- **Progress tracking**: Live completion status with AI detection scores
- **Resume capability**: Start from any specific material

### Status Update Format
```
📊 [START] Beginning iterative improvement for Aluminum - Target: 70.0 - Max iterations: 5
📊 [TIME STATUS] 20:46:12 - Elapsed: 21.9s - Progress: 40.0% - Iteration: 2/5 - Best score: 60.0
📊 [ITERATION STATUS] Iteration 1/5 (20.0%) - Elapsed: 0.0s - Best score: 0.0
🎉 [STATUS] Iterative improvement completed! Total time: 72.3s - Final best score: 96.2 - Iterations: 3
```

### Commands
- **Y/Yes**: Continue to next material (default)
- **N/No**: Pause generation
- **S/Skip**: Skip current material
- **Q/Quit**: Exit with summary
- **List**: Show next 10 materials

### Examples
```bash
# Basic interactive mode
python3 run.py --interactive

# Start from specific material
python3 run.py --interactive --start-from "Copper"

# With verbose logging
python3 run.py --interactive --verbose
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

| Component | Description | Status | AI Detection | API Provider | Dependencies |
|-----------|-------------|---------|--------------|--------------|-------------|
| `frontmatter` | YAML metadata | ✅ Working | ❌ Disabled | deepseek | None |
| `propertiestable` | Technical properties table | ✅ Working | ❌ Disabled | none | None |
| `badgesymbol` | Material symbol badge | ✅ Working | ❌ Disabled | none | **REQUIRES frontmatter** |
| `author` | Author information | ✅ Working | ❌ Disabled | none | **REQUIRES frontmatter** |
| `bullets` | Key characteristics list | ✅ Working | ✅ Enabled | deepseek | None |
| `caption` | Brief material description | ✅ Working | ✅ Enabled | gemini | None |
| `text` | Full technical article | ✅ Working | ✅ Enabled | deepseek | None |
| `tags` | SEO tags | ✅ Working | ❌ Disabled | deepseek | None |
| `metatags` | HTML meta tags | ✅ Working | ❌ Disabled | none | None |
| `jsonld` | Structured data markup | ✅ Working | ❌ Disabled | none | None |

## ⚠️ CRITICAL DEPENDENCY: Frontmatter Data

**IMPORTANT**: Component generation depends on frontmatter data for that specified material. Component failures will cascade without it. This is intentional design.

### Frontmatter Dependency Chain

```
┌─────────────────┐
│   Frontmatter   │ ←── REQUIRED for dependent components
│     Data        │
└─────────────────┘
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
   - Missing required fields (category, formula, properties)
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

### Example Failure Scenario

```bash
# Frontmatter file missing or incomplete
$ python3 run.py --material "Aluminum" --components "frontmatter,badgesymbol,author"

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

- **Static Components** (`api_provider: "none"`): `author`, `badgesymbol`, `propertiestable`, `jsonld`, `metatags`
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

### File Structure
```
z-beam-generator/
├── run.py                      # Main CLI interface
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
- ✅ **NEW**: AI detection optimization tests
- ✅ **NEW**: Prompt chain integration tests

### New Test Files

#### `test_ai_detection_optimization.py`
Comprehensive testing for the AI detection configuration optimizer:
- Configuration validation and loading
- DeepSeek client integration
- Optimization prompt generation for different score ranges
- Backup and restore functionality
- API failure handling

#### `test_prompt_chain_integration.py`
Validates complete prompt chain integration:
- All prompt layers properly included (Base + AI Detection + Persona + Formatting)
- Prompt length validation (4246+ characters with AI detection)
- Correct prompt order verification
- Performance testing for prompt building
- Error handling for missing/invalid files

### Running Specific Tests
```bash
# Run AI detection optimization tests
python3 -m pytest tests/test_ai_detection_optimization.py -v

# Run prompt chain integration tests
python3 -m pytest tests/test_prompt_chain_integration.py -v

# Run all tests with coverage
python3 -m pytest test_*.py -v --cov=components --cov=api
```

## ⚙️ Configuration

### API Settings
Configure in `.env`:
```
DEEPSEEK_API_KEY=your_deepseek_key_here
WINSTON_API_KEY=your_winston_key_here
```

### AI Detection Configuration
Configure in `config/ai_detection.yaml`:
```yaml
provider: winston
enabled: true
target_score: 45.0
max_iterations: 5
improvement_threshold: 3.0
# Core features (4 enabled)
conversational_style: true
natural_language_patterns: true
cultural_adaptation: true
sentence_variability: true
# Advanced features disabled for stability
human_error_simulation: false
emotional_depth: false
```

### Material Symbols
The system includes automatic material symbol generation with fallback to chemical symbols.

### Three-Layer Prompt System
The text component uses a sophisticated three-layer prompt system:
- **Base Layer**: Pure technical content requirements
- **Persona Layer**: Author characteristics and writing style
- **Formatting Layer**: Cultural presentation preferences

## 📊 Performance

### Current Status
- **✅ 10/11 components** generating successfully
- **✅ Real-time status updates** working for text component
- **✅ AI detection integration** with Winston.ai
- **✅ Iterative improvement** with DeepSeek optimization
- **✅ Three-layer prompt system** fully functional

### Generation Speed (Text Component)
- **API Call**: ~20-30s per iteration
- **AI Detection**: ~1s per analysis
- **Configuration Optimization**: ~10s per cycle
- **Total per iteration**: ~30-40s
- **Status updates**: Every 10 seconds

### AI Detection Scores
- **Target Score**: ≥45.0 (realistic for technical content)
- **Typical Results**: 40.0-60.0 range (stable performance)
- **Improvement Tracking**: Full iteration history in frontmatter
- **Optimization Strategy**: Conservative, technical-focused enhancements

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

The Z-Beam system includes a comprehensive test suite organized in the root directory.

### Quick Testing
```bash
# Run all tests including API response validation
python3 -m pytest test_*.py -v

# Run specific test categories
python3 test_iterative_improvement.py    # Test iterative AI detection
python3 test_content_generation.py       # Test content generation
python3 test_validation_diagnostics.py   # Test validation system
```

### Test Categories

#### Core Tests (default)
- **Iterative Improvement**: AI detection scoring and improvement
- **Content Generation**: Full content generation pipeline
- **Status Updates**: Real-time progress tracking
- **Prompt System**: Three-layer prompt construction

### Test Results
- **EXCELLENT (100%)**: All tests pass - production ready
- **GOOD (80-99%)**: Minor issues - mostly functional
- **FAIR (60-79%)**: Some issues - core functionality works
- **POOR (<60%)**: Significant issues - needs debugging

## 🐛 Known Issues

1. **Some component generators missing**: `badgesymbol`, `caption`, `jsonld`, `metatags`, `propertiestable`, `table`, `tags`
2. **Frontmatter validation**: Some materials missing required fields
3. **API timeouts**: Occasional timeout on long content generation

## 🔮 Roadmap

- [ ] Implement missing component generators
- [ ] Add frontmatter validation and auto-fix
- [ ] Implement batch resumption capability
- [ ] Improve error recovery for API timeouts
- [ ] Add progress persistence across sessions
- [ ] Implement material filtering options

## 📚 Documentation

- [Interactive Mode Guide](docs/README.md)
- [Three-Layer Architecture](docs/CLEAN_ARCHITECTURE_SUMMARY.md)
- [AI Detection Integration](docs/WINSTON_AI_INTEGRATION.md)
- [Testing Framework](tests/README.md)

## 🤝 Contributing

1. Run tests: `python3 -m pytest test_*.py -v`
2. Validate changes with interactive mode
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
- Use interactive mode for best experience

**Status Updates:** The system now provides real-time status updates every 10 seconds during text generation, showing progress, elapsed time, and AI detection scores!
