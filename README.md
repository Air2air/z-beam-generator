# Z-Beam Generator

A dynamic, schema-driven content generator for laser cleaning technical documentation.

## ✨ Features

- **🎮 Interactive Mode**: Step-by-step generation with user prompts
- **📊 Schema-Driven**: Fully dynamic content generation using JSON schemas
- **🤖 AI-Powered**: Integration with DeepSeek API for intelligent content creation
- **🧪 Comprehensive Testing**: 41+ tests ensuring reliability
- **🔧 Flexible Architecture**: Clean, maintainable codebase

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file with your DeepSeek API key:
```
DEEPSEEK_API_KEY=your_api_key_here
```

### Basic Usage

#### Test API Connection
```bash
python3 z_beam_generator.py --test-api
```

#### Generate for Single Material
```bash
python3 z_beam_generator.py --material "Aluminum"
```

#### Interactive Mode (Recommended)
```bash
python3 z_beam_generator.py --interactive
```

#### Batch Processing
```bash
python3 z_beam_generator.py --all --limit 10
```

## 🎮 Interactive Mode

The interactive mode provides the best user experience with fine-grained control:

### Key Features
- **Step-by-step processing**: Generate one material at a time
- **User prompts**: Choose to continue, skip, pause, or quit
- **Progress tracking**: Real-time completion status
- **Resume capability**: Start from any specific material

### Commands
- **Y/Yes**: Continue to next material (default)
- **N/No**: Pause generation
- **S/Skip**: Skip current material
- **Q/Quit**: Exit with summary
- **List**: Show next 10 materials

### Examples
```bash
# Basic interactive mode
python3 z_beam_generator.py --interactive

# Start from specific material
python3 z_beam_generator.py --interactive --start-from "Copper"

# With verbose logging
python3 z_beam_generator.py --interactive --verbose
```

See [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md) for detailed documentation.

## 📋 Available Materials

View all available materials:
```bash
python3 z_beam_generator.py --list-materials
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

| Component | Description | Status |
|-----------|-------------|---------|
| `caption` | Brief material description | ✅ Working |
| `propertiestable` | Technical properties table | ✅ Working |
| `bullets` | Key characteristics list | ✅ Working |
| `content` | Full technical article | ✅ Working |
| `frontmatter` | YAML metadata | ⚠️ YAML formatting issues |
| `metatags` | HTML meta tags | ✅ Working |
| `jsonld` | Structured data markup | ✅ Working |

## 🏗️ Architecture

### Core Components
- **MaterialLoader**: Loads materials from `data/materials.yaml`
- **ComponentGenerator**: Uses prompts + DeepSeek API
- **SchemaValidator**: Validates against JSON schemas
- **ContentWriter**: Saves to `content/` folder

### File Structure
```
z-beam-generator/
├── z_beam_generator.py      # Main CLI interface
├── simple_generator.py      # Core generation logic
├── fully_dynamic_generator.py # Schema-driven generator
├── api_client.py           # DeepSeek API integration
├── data/materials.yaml      # Materials database
├── components/             # Component templates
│   ├── bullets/
│   ├── caption/
│   ├── content/
│   ├── frontmatter/
│   ├── jsonld/
│   ├── metatags/
│   └── propertiestable/
├── schemas/               # JSON validation schemas
└── content/              # Generated output
```

## 🧪 Testing

Run comprehensive test suite:
```bash
python3 -m pytest test_*.py -v
```

**Test Coverage:**
- ✅ 29 core functionality tests
- ✅ 12 schema validation tests  
- ✅ API integration tests
- ✅ Material loading tests
- ✅ Component generation tests

## ⚙️ Configuration

### API Settings
Configure in `.env`:
```
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=3000
```

### Material Symbols
The system includes automatic material symbol generation with fallback to chemical symbols.

### Schema Validation
All content is validated against JSON schemas in `schemas/`:
- `application.json`
- `author.json` 
- `base.json`
- `material.json`
- `region.json`
- `thesaurus.json`

## 📊 Performance

### Current Status
- **✅ 6/7 components** generating successfully
- **✅ 80% schema compliance** across examples
- **✅ 100% test pass rate** (41 tests)
- **⚠️ YAML formatting** needs fixes in 11 files

### Generation Speed
- **Caption**: ~6s per material
- **Properties Table**: ~30s per material
- **Bullets**: ~27s per material
- **Content**: ~60s per material (longest)
- **Frontmatter**: ~52s per material
- **Metatags**: ~16s per material
- **JSON-LD**: ~21s per material

**Total per material**: ~3.5 minutes average

## 🛠️ Development

### Adding New Materials
Edit `data/materials.yaml`:
```yaml
materials:
  metal:
    items:
      - Your New Material
```

### Adding New Components
1. Create component directory: `components/newcomponent/`
2. Add `prompt.yaml` template
3. Update generator logic
4. Add validation schema

### Schema Updates
Update schemas in `schemas/` directory to modify validation rules.

## 🧪 Testing

The Z-Beam system includes a comprehensive test suite organized in the `tests/` directory.

### Quick Testing
```bash
# Run all tests including API response validation (default)
python3 -m tests

# Alternative: Use the wrapper script  
python3 test.py
```

### Test Categories

#### All Tests (default)
- **Dynamic System Tests**: Core functionality and schema loading
- **API Response Tests**: Basic API response validation for DeepSeek and Grok
- **Component Configuration**: Component routing and provider assignment
- **Integration Tests**: End-to-end workflows with API response validation

### Test Results
- **EXCELLENT (100%)**: All tests pass - production ready
- **GOOD (80-99%)**: Minor issues - mostly functional
- **FAIR (60-79%)**: Some issues - core functionality works
- **POOR (<60%)**: Significant issues - needs debugging

For detailed testing documentation, see [`tests/README.md`](tests/README.md).

## 🐛 Known Issues

1. **YAML Formatting**: 11 frontmatter files need YAML fixes
2. **Missing Template Variables**: Some prompts reference undefined variables
3. **API Timeouts**: Occasional timeout on long content generation

## 🔮 Roadmap

- [ ] Fix YAML formatting issues
- [ ] Implement schema consolidation 
- [ ] Add batch resumption capability
- [ ] Improve error recovery
- [ ] Add progress persistence
- [ ] Implement material filtering

## 📚 Documentation

- [Interactive Mode Guide](INTERACTIVE_MODE.md)
- [Schema Analysis Report](SCHEMA_EVALUATION_REPORT.md) 
- [System Summary](FINAL_SYSTEM_SUMMARY.md)
- [Test Suite Documentation](tests/README.md)

## 🤝 Contributing

1. Run tests: `python3 -m tests`
2. Validate changes with interactive mode
3. Update documentation as needed
4. Ensure all tests pass before submitting

## 📄 License

[Add your license information here]

---

**Need Help?** 
- Use `--help` for command options
- Check test results: `python3 -m tests --all`
- Check logs in `logs/` directory
- Test API with `--test-api`
- Use interactive mode for best experience
