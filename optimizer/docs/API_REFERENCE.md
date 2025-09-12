# Optimizer API Reference

## Overview
Complete API reference for the Z-Beam Optimizer system, including all classes, methods, configuration options, and usage examples.

## Core Classes

### ContentOptimizationOrchestrator
**File**: `optimizer/content_optimization.py`
**Purpose**: Main orchestration class for content optimization workflows

#### Constructor
```python
ContentOptimizationOrchestrator(
    winston_api_key: str,
    content_directory: str = "content/components/text",
    timeout: int = 30
)
```

#### Methods

##### `optimize_content()`
```python
def optimize_content(
    self,
    content: str,
    material_name: str,
    author_id: int = 1,
    enhancement_flags: Dict[str, bool] = None,
    max_iterations: int = 3
) -> OptimizationResult
```
**Purpose**: Optimize content with AI detection analysis and iterative improvement

**Parameters**:
- `content` (str): Original content to optimize
- `material_name` (str): Material name for context
- `author_id` (int): Author persona ID (1=Taiwan, 2=Italy, 3=Indonesia, 4=USA)
- `enhancement_flags` (Dict[str, bool]): Enhancement configuration
- `max_iterations` (int): Maximum optimization iterations

**Returns**: `OptimizationResult` object with optimized content and metrics

**Example**:
```python
orchestrator = ContentOptimizationOrchestrator(winston_api_key="your_key")
result = orchestrator.optimize_content(
    content="Original content here...",
    material_name="aluminum",
    author_id=1,
    enhancement_flags={
        'conversational_boost': True,
        'cultural_adaptation': True,
        'detection_avoidance': True
    }
)
print(f"Optimized: {result.content}")
print(f"Quality Score: {result.quality_score}")
```

##### `batch_optimize()`
```python
def batch_optimize(
    self,
    content_list: List[Dict[str, Any]],
    enhancement_flags: Dict[str, bool] = None
) -> List[OptimizationResult]
```
**Purpose**: Optimize multiple content pieces in batch

**Parameters**:
- `content_list` (List[Dict]): List of content dictionaries with 'content', 'material_name', 'author_id'
- `enhancement_flags` (Dict[str, bool]): Global enhancement configuration

**Returns**: List of `OptimizationResult` objects

**Example**:
```python
content_batch = [
    {"content": "Content 1", "material_name": "aluminum", "author_id": 1},
    {"content": "Content 2", "material_name": "steel", "author_id": 2}
]
results = orchestrator.batch_optimize(content_batch)
```

### DynamicPromptGenerator
**File**: `optimizer/text_optimization/dynamic_prompt_generator.py`
**Purpose**: Dynamic prompt optimization with cultural adaptation

#### Constructor
```python
DynamicPromptGenerator(
    api_key: str = None,
    base_url: str = "https://api.deepseek.com/v1",
    model: str = "deepseek-chat",
    timeout: int = 30
)
```

#### Methods

##### `generate_optimized_prompt()`
```python
def generate_optimized_prompt(
    self,
    material_name: str,
    author_id: int,
    enhancement_flags: Dict[str, bool] = None,
    quality_threshold: float = 0.7
) -> str
```
**Purpose**: Generate culturally-adapted, optimized prompts

**Parameters**:
- `material_name` (str): Target material for content generation
- `author_id` (int): Author persona (1-4)
- `enhancement_flags` (Dict[str, bool]): Enhancement configuration
- `quality_threshold` (float): Minimum quality threshold (0.0-1.0)

**Enhancement Flags**:
- `conversational_boost`: Enable conversational language patterns
- `human_elements_emphasis`: Emphasize human characteristics
- `sentence_variability`: Increase sentence structure variation
- `cultural_adaptation`: Apply cultural customization
- `detection_avoidance`: Apply AI detection mitigation
- `structural_optimization`: Improve content organization

**Returns**: Optimized prompt string

**Example**:
```python
generator = DynamicPromptGenerator(api_key="deepseek_key")
prompt = generator.generate_optimized_prompt(
    material_name="titanium",
    author_id=2,  # Italy
    enhancement_flags={
        'conversational_boost': True,
        'cultural_adaptation': True,
        'human_elements_emphasis': True
    },
    quality_threshold=0.8
)
```

##### `analyze_and_improve()`
```python
def analyze_and_improve(
    self,
    current_prompt: str,
    winston_feedback: Dict[str, Any],
    enhancement_flags: Dict[str, bool] = None
) -> str
```
**Purpose**: Improve prompt based on Winston AI feedback

**Parameters**:
- `current_prompt` (str): Current prompt to improve
- `winston_feedback` (Dict): Winston analysis results
- `enhancement_flags` (Dict[str, bool]): Target improvements

**Returns**: Improved prompt string

### ModularLoader
**File**: `optimizer/text_optimization/utils/modular_loader.py`
**Purpose**: Dynamic configuration loading and component assembly

#### Constructor
```python
ModularLoader(
    base_path: str = "components/text/prompts",
    core_config_file: str = "core/ai_detection_core.yaml"
)
```

#### Methods

##### `load_complete_configuration()`
```python
def load_complete_configuration(self) -> Dict[str, Any]
```
**Purpose**: Load and merge all modular components

**Returns**: Complete merged configuration dictionary

**Raises**:
- `FileNotFoundError`: If core configuration or modules missing
- `yaml.YAMLError`: If YAML parsing fails

**Example**:
```python
loader = ModularLoader()
config = loader.load_complete_configuration()
print(f"Loaded sections: {list(config.keys())}")
```

##### `get_component_config()`
```python
def get_component_config(self, component_name: str) -> Dict[str, Any]
```
**Purpose**: Get specific component configuration

**Parameters**:
- `component_name` (str): Name of component to load

**Returns**: Component configuration dictionary

### ContentScorer
**File**: `optimizer/text_optimization/validation/content_scorer.py`
**Purpose**: Multi-dimensional content quality assessment

#### Constructor
```python
ContentScorer(
    winston_api_key: str = None,
    quality_weights: Dict[str, float] = None
)
```

#### Methods

##### `score_content()`
```python
def score_content(
    self,
    content: str,
    material_context: str = None,
    author_context: Dict[str, Any] = None
) -> ContentScore
```
**Purpose**: Comprehensive content quality scoring

**Parameters**:
- `content` (str): Content to score
- `material_context` (str): Material context for relevance scoring
- `author_context` (Dict): Author persona context

**Returns**: `ContentScore` object with detailed metrics

**Scoring Dimensions**:
- **Human Authenticity** (0.0-1.0): How human-like the content appears
- **Technical Accuracy** (0.0-1.0): Technical correctness and relevance
- **Cultural Appropriateness** (0.0-1.0): Cultural adaptation quality
- **Engagement Level** (0.0-1.0): Content engagement and readability
- **Detection Avoidance** (0.0-1.0): AI detection resistance

**Example**:
```python
scorer = ContentScorer(winston_api_key="winston_key")
score = scorer.score_content(
    content="Laser cleaning content...",
    material_context="aluminum",
    author_context={"country": "taiwan", "style": "technical"}
)
print(f"Overall Score: {score.overall_score}")
print(f"Human Authenticity: {score.human_authenticity}")
print(f"Retry Recommended: {score.retry_recommended}")
```

## Configuration Classes

### OptimizationConfig
**Purpose**: Configuration for optimization workflows

#### Attributes
```python
class OptimizationConfig:
    max_iterations: int = 3
    quality_threshold: float = 0.7
    timeout_seconds: int = 30
    enhancement_flags: Dict[str, bool] = None
    winston_threshold: float = 0.3
    content_length_range: Tuple[int, int] = (250, 450)
```

#### Example
```python
config = OptimizationConfig(
    max_iterations=5,
    quality_threshold=0.8,
    enhancement_flags={
        'conversational_boost': True,
        'cultural_adaptation': True
    }
)
```

### ServiceConfiguration
**Purpose**: Service initialization and settings

#### Attributes
```python
class ServiceConfiguration:
    api_providers: Dict[str, Dict[str, Any]]
    cache_settings: Dict[str, Any]
    logging_config: Dict[str, Any]
    performance_settings: Dict[str, Any]
```

### WorkflowConfiguration
**Purpose**: Iterative workflow parameters

#### Attributes
```python
class WorkflowConfiguration:
    strategy: str  # "linear", "exponential", "adaptive"
    max_iterations: int = 10
    exit_conditions: List[str]
    quality_targets: Dict[str, float]
```

## Result Classes

### OptimizationResult
**Purpose**: Complete optimization outcome with metrics

#### Attributes
```python
class OptimizationResult:
    content: str                    # Optimized content
    original_content: str           # Original input content
    quality_score: float            # Overall quality score (0.0-1.0)
    iterations_performed: int       # Number of optimization iterations
    winston_score: float           # AI detection score
    processing_time: float         # Total processing time in seconds
    enhancement_applied: List[str]  # List of applied enhancements
    metrics: Dict[str, Any]        # Detailed optimization metrics
    success: bool                  # Whether optimization succeeded
    error_message: str = None      # Error message if failed
```

#### Methods
```python
def to_dict(self) -> Dict[str, Any]
def was_successful(self) -> bool
def get_improvement_percentage(self) -> float
```

### ContentScore
**Purpose**: Multi-dimensional content quality assessment

#### Attributes
```python
class ContentScore:
    overall_score: float           # Overall quality score (0.0-1.0)
    human_authenticity: float      # Human-like quality (0.0-1.0)
    technical_accuracy: float      # Technical correctness (0.0-1.0)
    cultural_appropriateness: float # Cultural adaptation (0.0-1.0)
    engagement_level: float        # Content engagement (0.0-1.0)
    detection_avoidance: float     # AI detection resistance (0.0-1.0)
    retry_recommended: bool        # Whether retry is recommended
    feedback: List[str]           # Improvement suggestions
    metrics: Dict[str, Any]       # Detailed scoring metrics
```

## Enhancement Flags Reference

### Available Enhancement Flags
```python
enhancement_flags = {
    # Authenticity Enhancements
    'conversational_boost': bool,      # Enable conversational language patterns
    'human_elements_emphasis': bool,   # Emphasize human characteristics
    
    # Cultural Adaptation
    'cultural_adaptation': bool,       # Apply cultural customization
    
    # Detection Avoidance
    'detection_avoidance': bool,       # Apply AI detection mitigation
    'sentence_variability': bool,      # Increase sentence structure variation
    
    # Structural Improvements
    'structural_optimization': bool,   # Improve content organization
    'paragraph_enhancement': bool,     # Enhance paragraph structure
    
    # Quality Enhancements
    'technical_accuracy_boost': bool,  # Enhance technical precision
    'engagement_optimization': bool    # Optimize for reader engagement
}
```

### Flag Combinations by Use Case

#### High-Quality Content Generation
```python
enhancement_flags = {
    'conversational_boost': True,
    'human_elements_emphasis': True,
    'cultural_adaptation': True,
    'technical_accuracy_boost': True,
    'engagement_optimization': True
}
```

#### AI Detection Avoidance Focus
```python
enhancement_flags = {
    'detection_avoidance': True,
    'sentence_variability': True,
    'human_elements_emphasis': True,
    'conversational_boost': True
}
```

#### Cultural Localization
```python
enhancement_flags = {
    'cultural_adaptation': True,
    'conversational_boost': True,
    'human_elements_emphasis': True
}
```

## Author Persona Reference

### Author ID Mapping
```python
AUTHOR_PERSONAS = {
    1: {
        "country": "taiwan",
        "language_style": "technical_precision",
        "cultural_elements": ["efficiency_focus", "detail_oriented"],
        "communication_style": "formal_but_approachable"
    },
    2: {
        "country": "italy", 
        "language_style": "expressive_technical",
        "cultural_elements": ["craftsmanship_pride", "artistic_appreciation"],
        "communication_style": "passionate_and_detailed"
    },
    3: {
        "country": "indonesia",
        "language_style": "collaborative_technical", 
        "cultural_elements": ["community_focus", "practical_solutions"],
        "communication_style": "helpful_and_inclusive"
    },
    4: {
        "country": "usa",
        "language_style": "direct_technical",
        "cultural_elements": ["innovation_focus", "efficiency_emphasis"],
        "communication_style": "confident_and_practical"
    }
}
```

### Persona-Specific Characteristics

#### Taiwan (Author ID: 1)
- **Language**: Precise, technical terminology
- **Style**: Methodical, detail-oriented
- **Cultural Elements**: Technology focus, quality emphasis
- **Typical Phrases**: "精確的方法" (precise method), "技術規格" (technical specifications)

#### Italy (Author ID: 2)  
- **Language**: Expressive, craftsmanship-focused
- **Style**: Artistic appreciation, quality pride
- **Cultural Elements**: Traditional craftsmanship, aesthetic considerations
- **Typical Phrases**: "Come dire...", "Ecco, questo è importante"

#### Indonesia (Author ID: 3)
- **Language**: Collaborative, community-oriented
- **Style**: Helpful, inclusive approach
- **Cultural Elements**: Cooperation, practical solutions
- **Typical Phrases**: Community-focused expressions, practical advice

#### USA (Author ID: 4)
- **Language**: Direct, efficiency-focused
- **Style**: Confident, results-oriented
- **Cultural Elements**: Innovation, practical efficiency
- **Typical Phrases**: "Here's the deal", "Bottom line is..."

## Error Handling

### Exception Types

#### OptimizerError
```python
class OptimizerError(Exception):
    """Base exception for optimizer-related errors."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.details = details or {}
```

#### ConfigurationError
```python
class ConfigurationError(OptimizerError):
    """Raised when configuration is invalid or missing."""
    pass
```

#### GenerationError
```python
class GenerationError(OptimizerError):
    """Raised when content generation fails."""
    pass
```

#### APIError
```python
class APIError(OptimizerError):
    """Raised when API calls fail."""
    pass
```

### Error Handling Examples

#### Basic Error Handling
```python
try:
    result = orchestrator.optimize_content(content, "aluminum")
except ConfigurationError as e:
    print(f"Configuration issue: {e}")
    print(f"Details: {e.details}")
except GenerationError as e:
    print(f"Generation failed: {e}")
except APIError as e:
    print(f"API error: {e}")
except OptimizerError as e:
    print(f"Optimizer error: {e}")
```

#### Comprehensive Error Handling
```python
import logging

def safe_optimize_content(orchestrator, content, material_name):
    try:
        return orchestrator.optimize_content(content, material_name)
    except ConfigurationError as e:
        logging.error(f"Configuration error: {e}")
        # Attempt to fix configuration
        return None
    except APIError as e:
        logging.warning(f"API error, retrying: {e}")
        # Implement retry logic
        return retry_optimization(orchestrator, content, material_name)
    except Exception as e:
        logging.critical(f"Unexpected error: {e}")
        raise
```

## Usage Examples

### Basic Content Optimization
```python
from optimizer.content_optimization import ContentOptimizationOrchestrator

# Initialize orchestrator
orchestrator = ContentOptimizationOrchestrator(
    winston_api_key="your_winston_key",
    timeout=30
)

# Optimize content
content = "Laser cleaning removes contaminants from aluminum surfaces..."
result = orchestrator.optimize_content(
    content=content,
    material_name="aluminum",
    author_id=1,
    enhancement_flags={'conversational_boost': True}
)

print(f"Original: {content}")
print(f"Optimized: {result.content}")
print(f"Quality Score: {result.quality_score}")
```

### Advanced Prompt Generation
```python
from optimizer.text_optimization.dynamic_prompt_generator import DynamicPromptGenerator

# Initialize generator
generator = DynamicPromptGenerator(
    api_key="deepseek_key",
    timeout=30
)

# Generate optimized prompt with full enhancements
prompt = generator.generate_optimized_prompt(
    material_name="titanium",
    author_id=2,  # Italy persona
    enhancement_flags={
        'conversational_boost': True,
        'cultural_adaptation': True,
        'human_elements_emphasis': True,
        'detection_avoidance': True,
        'structural_optimization': True
    },
    quality_threshold=0.8
)

print(f"Generated Prompt: {prompt}")
```

### Batch Processing
```python
# Prepare batch data
materials = ["aluminum", "steel", "titanium", "copper"]
content_batch = []

for material in materials:
    content_batch.append({
        "content": f"Content about {material} laser cleaning...",
        "material_name": material,
        "author_id": 1
    })

# Process batch
results = orchestrator.batch_optimize(
    content_batch,
    enhancement_flags={
        'conversational_boost': True,
        'cultural_adaptation': True
    }
)

# Analyze results
for i, result in enumerate(results):
    print(f"{materials[i]}: Score {result.quality_score:.2f}")
```

### Quality Assessment
```python
from optimizer.text_optimization.validation.content_scorer import ContentScorer

# Initialize scorer
scorer = ContentScorer(winston_api_key="winston_key")

# Score content
score = scorer.score_content(
    content="Your content here...",
    material_context="aluminum",
    author_context={"country": "taiwan", "style": "technical"}
)

print(f"Overall Score: {score.overall_score:.2f}")
print(f"Human Authenticity: {score.human_authenticity:.2f}")
print(f"Technical Accuracy: {score.technical_accuracy:.2f}")
print(f"Cultural Appropriateness: {score.cultural_appropriateness:.2f}")
print(f"Retry Recommended: {score.retry_recommended}")

if score.feedback:
    print("Improvement Suggestions:")
    for suggestion in score.feedback:
        print(f"  - {suggestion}")
```

## Performance Optimization

### Caching Configuration
```python
from functools import lru_cache

# Cache configuration loading
@lru_cache(maxsize=10)
def cached_load_config():
    loader = ModularLoader()
    return loader.load_complete_configuration()

# Use cached configuration
config = cached_load_config()
```

### Memory Management
```python
import gc
import psutil

def monitor_memory_usage():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")

def optimize_memory():
    gc.collect()
    monitor_memory_usage()
```

### Async Processing
```python
import asyncio
from typing import List

async def async_optimize_content(orchestrator, content_item):
    """Async content optimization."""
    return await asyncio.to_thread(
        orchestrator.optimize_content,
        **content_item
    )

async def batch_optimize_async(orchestrator, content_list):
    """Async batch optimization."""
    tasks = [
        async_optimize_content(orchestrator, item)
        for item in content_list
    ]
    return await asyncio.gather(*tasks)

# Usage
content_list = [...]  # Your content list
results = asyncio.run(batch_optimize_async(orchestrator, content_list))
```

This API reference provides comprehensive coverage of all optimizer system components, methods, and usage patterns. Keep this document updated as the API evolves.
