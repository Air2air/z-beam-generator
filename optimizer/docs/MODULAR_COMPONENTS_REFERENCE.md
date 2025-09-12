# Modular Components Reference

## Overview
The Z-Beam optimizer uses a modular component system for dynamic prompt construction and enhancement. This system allows for flexible, runtime-configurable prompt optimization with specialized modules for different aspects of content enhancement.

## Architecture

### Component System Structure
```
components/text/prompts/
├── core/
│   └── ai_detection_core.yaml          # Main configuration with modular mappings
└── modules/                            # Modular component library
    ├── authenticity_enhancements.yaml  # Natural language patterns
    ├── cultural_adaptation.yaml        # Regional customization  
    ├── detection_avoidance.yaml        # AI detection mitigation
    ├── human_characteristics.yaml      # Human writing traits
    └── structural_improvements.yaml    # Content organization
```

### Integration Points
```
optimizer/text_optimization/
├── utils/
│   └── modular_loader.py               # Component loading and assembly
├── dynamic_prompt_generator.py         # Primary integration point
└── dynamic_prompt_system/              # Advanced prompt evolution
```

## Component Modules

### 1. Authenticity Enhancements
**File**: `components/text/prompts/modules/authenticity_enhancements.yaml`
**Purpose**: Inject natural language patterns and human-like characteristics

#### Key Features:
- **Conversational Elements**: Informal language patterns, contractions
- **Personal Touch**: Anecdotal references, subjective opinions
- **Natural Flow**: Sentence rhythm variations, natural pauses
- **Colloquial Language**: Industry-specific informal terms

#### Usage:
```python
enhancement_flags = {
    'conversational_boost': True,  # Triggers authenticity enhancements
    'human_elements_emphasis': True
}
```

#### Configuration Structure:
```yaml
authenticity_enhancements:
  conversational_patterns:
    - "You know what I've noticed..."
    - "Here's the thing about..."
    - "I've got to say..."
  personal_elements:
    - "In my experience..."
    - "I remember when..."
    - "What really gets me is..."
```

### 2. Cultural Adaptation
**File**: `components/text/prompts/modules/cultural_adaptation.yaml`
**Purpose**: Provide regional and cultural customization

#### Key Features:
- **Language Patterns**: Country-specific expressions and idioms
- **Cultural References**: Local customs, traditions, practices
- **Technical Terminology**: Regional variations in industry terms
- **Communication Styles**: Formal vs informal cultural preferences

#### Usage:
```python
enhancement_flags = {
    'cultural_adaptation': True  # Applies cultural customization
}
# Works with persona system (Taiwan, Italy, Indonesia, USA)
```

#### Configuration Structure:
```yaml
cultural_adaptation:
  taiwan:
    expressions:
      - "確實是這樣" (Indeed this is so)
      - "就是說啊" (That's right)
    technical_terms:
      - "雷射清潔" (laser cleaning)
  italy:
    expressions:
      - "Ecco, questo è importante"
      - "Come dire..."
```

### 3. Detection Avoidance
**File**: `components/text/prompts/modules/detection_avoidance.yaml`
**Purpose**: Implement AI detection mitigation strategies

#### Key Features:
- **Variability Patterns**: Sentence structure variations
- **Human Inconsistencies**: Natural errors and corrections
- **Flow Disruptions**: Natural topic transitions
- **Style Mixing**: Multiple writing approach combinations

#### Usage:
```python
enhancement_flags = {
    'detection_avoidance': True  # Applies when AI scores are high
}
```

#### Configuration Structure:
```yaml
detection_avoidance:
  variability_techniques:
    sentence_starters:
      - "Well, to be honest..."
      - "Actually, thinking about it..."
    transition_phrases:
      - "But here's the thing..."
      - "On the other hand..."
  inconsistency_patterns:
    - "minor grammatical variations"
    - "natural topic drift"
```

### 4. Human Characteristics
**File**: `components/text/prompts/modules/human_characteristics.yaml`
**Purpose**: Embed human writing traits and behaviors

#### Key Features:
- **Emotional Expressions**: Personal feelings and reactions
- **Subjective Statements**: Opinions and preferences
- **Experience References**: Personal anecdotes and observations
- **Uncertainty Markers**: Natural hesitation and qualification

#### Usage:
```python
enhancement_flags = {
    'human_elements_emphasis': True  # Emphasizes human traits
}
```

#### Configuration Structure:
```yaml
human_characteristics:
  emotional_markers:
    - "I'm really excited about..."
    - "What bothers me is..."
    - "I find it fascinating that..."
  uncertainty_expressions:
    - "I think..."
    - "It seems to me..."
    - "From what I can tell..."
```

### 5. Structural Improvements
**File**: `components/text/prompts/modules/structural_improvements.yaml`
**Purpose**: Optimize content organization and flow

#### Key Features:
- **Paragraph Structure**: Logical organization patterns
- **Transition Optimization**: Smooth content flow
- **Information Hierarchy**: Clear content prioritization
- **Readability Enhancement**: Improved comprehension flow

#### Usage:
```python
enhancement_flags = {
    'structural_optimization': True  # Applies structural improvements
}
```

#### Configuration Structure:
```yaml
structural_improvements:
  paragraph_patterns:
    introduction:
      - "Let me start by explaining..."
      - "First, it's important to understand..."
    transitions:
      - "Moving on to..."
      - "This brings us to..."
    conclusions:
      - "To sum it up..."
      - "The key takeaway here is..."
```

## Modular Loader System

### ModularLoader Class
**File**: `optimizer/text_optimization/utils/modular_loader.py`

#### Core Methods:

##### `load_complete_configuration()`
```python
def load_complete_configuration(self) -> Dict[str, Any]:
    """
    Load and merge all modular components into complete configuration.
    
    Returns:
        Dict containing merged configuration from all modules
        
    Raises:
        FileNotFoundError: If core configuration or modules missing
        yaml.YAMLError: If YAML parsing fails
    """
```

##### `_load_modular_components()`
```python
def _load_modular_components(self, modules_config: Dict[str, str]) -> Dict[str, Any]:
    """
    Load individual component modules and merge configurations.
    
    Args:
        modules_config: Mapping of component names to file paths
        
    Returns:
        Merged configuration dictionary
    """
```

#### Usage Example:
```python
from optimizer.text_optimization.utils.modular_loader import ModularLoader

# Initialize loader
loader = ModularLoader()

# Load complete configuration
try:
    config = loader.load_complete_configuration()
    print(f"Loaded {len(config)} configuration sections")
    
    # Access specific modules
    authenticity = config.get('authenticity_enhancements', {})
    cultural = config.get('cultural_adaptation', {})
    
except FileNotFoundError as e:
    print(f"Configuration file missing: {e}")
except Exception as e:
    print(f"Loading failed: {e}")
```

## Integration with Dynamic Prompt Generator

### Primary Integration Point
**File**: `optimizer/text_optimization/dynamic_prompt_generator.py`

#### Method: `_load_current_prompts()`
```python
def _load_current_prompts(self):
    """Load prompts with modular loader priority."""
    try:
        # Primary: Use modular loader for complete configuration
        return self.modular_loader.load_complete_configuration()
    except Exception as e:
        logger.warning(f"Modular loader failed: {e}")
        # Fallback: Direct file loading
        return self._load_direct_prompts()
```

#### Enhancement Flag Processing
```python
def generate_optimized_prompt(self, material_name: str, author_id: int, 
                            enhancement_flags: Dict[str, bool] = None):
    """
    Generate optimized prompt using modular components.
    
    Enhancement flags trigger specific modules:
    - conversational_boost → authenticity_enhancements
    - cultural_adaptation → cultural_adaptation
    - detection_avoidance → detection_avoidance  
    - human_elements_emphasis → human_characteristics
    - structural_optimization → structural_improvements
    """
```

## Configuration Management

### Core Configuration File
**File**: `components/text/prompts/core/ai_detection_core.yaml`

#### Modular Components Mapping:
```yaml
modular_components:
  authenticity_enhancements: "modules/authenticity_enhancements.yaml"
  cultural_adaptation: "modules/cultural_adaptation.yaml"
  detection_avoidance: "modules/detection_avoidance.yaml"
  human_characteristics: "modules/human_characteristics.yaml"
  structural_improvements: "modules/structural_improvements.yaml"
```

### Path Resolution
- **Base Path**: `components/text/prompts/`
- **Relative Paths**: All module paths are relative to base path
- **Automatic Discovery**: ModularLoader resolves full paths automatically

## Troubleshooting

### Common Issues

#### 1. Missing Modular Components Section
**Error**: `KeyError: 'modular_components'`
**Solution**: Add modular_components section to `ai_detection_core.yaml`

#### 2. Module File Not Found
**Error**: `FileNotFoundError: modules/[component].yaml`
**Solution**: Verify all module files exist in `components/text/prompts/modules/`

#### 3. YAML Parsing Errors
**Error**: `yaml.YAMLError`
**Solution**: Validate YAML syntax in all module files

#### 4. Configuration Merge Conflicts
**Error**: Inconsistent merged configuration
**Solution**: Check for conflicting keys across modules

### Diagnostic Commands

#### Validate Module Loading
```bash
python3 -c "
from optimizer.text_optimization.utils.modular_loader import ModularLoader
loader = ModularLoader()
try:
    config = loader.load_complete_configuration()
    print('✅ Modular components loaded successfully')
    print(f'   Sections: {list(config.keys())}')
    for section, content in config.items():
        print(f'   {section}: {len(content)} items')
except Exception as e:
    print(f'❌ Loading failed: {e}')
"
```

#### Test Component Integration
```bash
python3 -c "
from optimizer.text_optimization.dynamic_prompt_generator import DynamicPromptGenerator
try:
    generator = DynamicPromptGenerator()
    print('✅ DynamicPromptGenerator initialized successfully')
    print('✅ Modular component integration working')
except Exception as e:
    print(f'❌ Integration failed: {e}')
"
```

#### Validate System Health
```bash
python3 scripts/tools/prompt_chain_diagnostics.py
```

## Best Practices

### 1. Module Development
- **Single Responsibility**: Each module should focus on one enhancement aspect
- **Clear Naming**: Use descriptive keys for configuration sections
- **Consistent Structure**: Follow established YAML patterns
- **Documentation**: Include comments explaining module purpose

### 2. Configuration Management
- **Version Control**: Track all module changes
- **Testing**: Validate modules before deployment
- **Backup**: Maintain known-good configurations
- **Monitoring**: Log module loading success/failures

### 3. Integration Patterns
- **Graceful Fallbacks**: Handle module loading failures
- **Selective Enhancement**: Use flags to control module application
- **Performance**: Cache loaded configurations when possible
- **Error Handling**: Comprehensive exception management

## Future Enhancements

### Planned Features
1. **Dynamic Module Discovery**: Auto-detect new modules
2. **Configuration Validation**: Schema-based module validation
3. **Performance Optimization**: Lazy loading and caching
4. **Module Dependencies**: Inter-module dependency management
5. **A/B Testing**: Module effectiveness comparison

### Extension Points
- **Custom Modules**: Framework for user-defined components
- **Plugin System**: External module integration
- **API Interface**: REST API for module management
- **Real-time Updates**: Hot-reload configuration changes
