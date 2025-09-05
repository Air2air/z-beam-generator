# AI Detection Prompts - Modular Architecture

This directory contains the modular AI detection prompt system for the Z-Beam content generator. The architecture has been reorganized for better maintainability, scalability, and clarity.

## 📁 Directory Structure

```
components/text/prompts/
├── README.md                    # This documentation
├── core/                        # Core configuration files
│   ├── ai_detection_core.yaml   # Main configuration with modular references
│   ├── base_content_prompt.yaml # Base content generation prompts
│   └── evolution_history.json   # Version history and evolution tracking
├── modules/                     # Modular AI detection components
│   ├── human_characteristics/   # Human-like writing patterns
│   ├── detection_avoidance/     # AI detection trigger avoidance
│   ├── structural_improvements/ # Paragraph/sentence structure
│   ├── authenticity_enhancements/# Personal touch and authenticity
│   └── cultural_adaptation/     # Cultural writing style adaptations
├── personas/                    # Author-specific persona configurations
├── formatting/                  # Formatting and style configurations
├── utils/                       # Utility scripts and tools
│   ├── modular_loader.py        # Main configuration loader
│   ├── version_manager.py       # Version management system
│   ├── auto_version_bumper.py   # Automated version bumping
│   └── complexity_analyzer.py   # Configuration complexity analysis
├── docs/                        # Documentation and governance
│   ├── GOVERNANCE.md           # Governance and maintenance rules
│   └── MIGRATION_PLAN.md       # Migration and evolution plans
└── legacy/                      # Legacy files (for reference)
    └── ai_detection.yaml       # Original monolithic configuration
```

## 🎯 Key Benefits

- **🔧 Maintainability**: Each module focuses on a specific aspect
- **📈 Scalability**: Easy to add new modules without affecting others
- **🧪 Testability**: Individual components can be tested in isolation
- **🔄 Flexibility**: Components can be updated independently
- **⚡ Performance**: Caching system prevents redundant file reads
- **🛡️ Reliability**: Fallback mechanisms ensure system stability

## 🚀 Usage

### Loading Configuration

```python
from components.text.prompts.utils.modular_loader import ModularConfigLoader

# Load complete modular configuration
loader = ModularConfigLoader()
config = loader.load_config(use_modular=True)

# Or use convenience function
from components.text.prompts.utils.modular_loader import load_ai_detection_config
config = load_ai_detection_config()
```

### Core Components

#### 1. Core Configuration (`core/`)
- **`ai_detection_core.yaml`**: Main configuration file with references to modular components
- **`base_content_prompt.yaml`**: Base content generation prompts and requirements
- **`evolution_history.json`**: Tracks version changes and evolution

#### 2. Modular Components (`modules/`)
Each module contains focused YAML files for specific aspects:

- **Human Characteristics**: Conversational patterns, cognitive variability, natural imperfections
- **Detection Avoidance**: Patterns to avoid common AI detection triggers
- **Structural Improvements**: Paragraph and sentence structure enhancements
- **Authenticity Enhancements**: Personal touches and authentic writing elements
- **Cultural Adaptation**: Nationality-specific writing style adaptations

#### 3. Personas (`personas/`)
Author-specific configurations:
- `taiwan_persona.yaml`
- `italy_persona.yaml`
- `indonesia_persona.yaml`
- `usa_persona.yaml`

#### 4. Formatting (`formatting/`)
Formatting configurations:
- `taiwan_formatting.yaml`
- `italy_formatting.yaml`
- `indonesia_formatting.yaml`
- `usa_formatting.yaml`

## 🛠️ Development Guidelines

### Adding New Modules

1. Create a new directory under `modules/`
2. Add YAML configuration files
3. Update `core/ai_detection_core.yaml` to reference the new module
4. Test the integration

### Modifying Existing Components

1. Always backup before changes
2. Use the version manager for version control
3. Test changes thoroughly
4. Update documentation

### Version Management

```python
from components.text.prompts.utils.version_manager import AIDetectionVersionManager

version_manager = AIDetectionVersionManager()
current_version = version_manager.get_current_version()
```

## 🔧 Utilities

### Modular Loader
- **File**: `utils/modular_loader.py`
- **Purpose**: Loads and merges modular configurations
- **Features**: Deep merging, caching, error handling

### Version Manager
- **File**: `utils/version_manager.py`
- **Purpose**: Manages versioning and changelog
- **Features**: Semantic versioning, automatic changelog generation

### Auto Version Bumper
- **File**: `utils/auto_version_bumper.py`
- **Purpose**: Automatically bumps versions based on changes
- **Features**: Intelligent version detection, changelog updates

### Complexity Analyzer
- **File**: `utils/complexity_analyzer.py`
- **Purpose**: Analyzes configuration complexity
- **Features**: Complexity scoring, maintenance recommendations

## 📚 Documentation

- **[GOVERNANCE.md](docs/GOVERNANCE.md)**: Rules and guidelines for maintenance
- **[MIGRATION_PLAN.md](docs/MIGRATION_PLAN.md)**: Plans for future evolution

## 🔄 Migration from Legacy

The original monolithic `ai_detection.yaml` has been moved to `legacy/` for reference. The system now uses the modular architecture automatically. No code changes are required for existing integrations.

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
python3 -c "
from components.text.prompts.utils.modular_loader import ModularConfigLoader
loader = ModularConfigLoader()
config = loader.load_config(use_modular=True)
print(f'✅ Loaded {len(config)} configuration sections')
"
```

## 📞 Support

For questions about the modular architecture or configuration files, refer to:
1. This README
2. [GOVERNANCE.md](docs/GOVERNANCE.md) for maintenance rules
3. Individual module READMEs (when available)

---

**Version**: 1.3.0
**Last Updated**: September 4, 2025
**Architecture**: Modular Configuration System
