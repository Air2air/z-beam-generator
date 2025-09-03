# Phrasly.ai Integration Architecture

## Overview

The Phrasly.ai integration provides iterative content improvement based on AI detection scores. This enhancement allows the Z-Beam content generation system to automatically improve the "human-like" quality of generated content by analyzing it with Phrasly.ai's AI detection service and iteratively refining it until target scores are achieved.

## Architecture Components

### 1. PhraslyAIClient
**File:** `components/content/phrasly_integration.py`

Core client for Phrasly.ai API integration:
- **Purpose:** Analyze text for AI detection scores
- **Features:**
  - RESTful API communication with Phrasly.ai
  - Structured response handling with confidence scores
  - Error handling and fallback mechanisms
  - Request/response logging

```python
@dataclass
class AIDetectionResult:
    score: float          # AI detection score (0-100, higher = more AI-like)
    confidence: float     # Confidence level (0-1)
    classification: str   # "human", "ai", or "unclear"
    details: Dict         # Additional analysis details
    processing_time: float
```

### 2. IterativeContentImprover
**File:** `components/content/phrasly_integration.py`

Manages the iterative improvement process:
- **Purpose:** Orchestrate content improvement cycles
- **Features:**
  - Multiple improvement strategies
  - Score tracking and convergence detection
  - Configurable iteration limits
  - Strategy selection based on improvement potential

### 3. EnhancedContentComponentGenerator
**File:** `components/content/enhanced_generator.py`

Enhanced wrapper that integrates Phrasly.ai with existing content generation:
- **Purpose:** Drop-in replacement for standard content generator
- **Features:**
  - Backward compatibility with existing API
  - Optional Phrasly.ai integration
  - Comprehensive metadata tracking
  - Graceful degradation if Phrasly.ai unavailable

### 4. Enhanced Factory
**File:** `components/content/enhanced_factory.py`

Factory functions for creating enhanced generators:
- **Purpose:** Configuration-driven generator creation
- **Features:**
  - YAML configuration support
  - Environment variable integration
  - Validation and error handling

## Integration Flow

### Phase 1: Initial Content Generation
```
1. Generate content using base fail_fast_generator
2. Validate content meets basic quality thresholds
3. Check if Phrasly.ai integration is enabled
```

### Phase 2: AI Detection Analysis
```
1. Send generated content to Phrasly.ai API
2. Receive AI detection score and analysis
3. Evaluate score against target threshold
4. Log analysis results and metadata
```

### Phase 3: Iterative Improvement (if needed)
```
1. Select improvement strategy based on current score
2. Apply strategy modifications to content
3. Re-analyze with Phrasly.ai
4. Compare scores and track improvements
5. Continue until target reached or max iterations exceeded
```

### Phase 4: Finalization
```
1. Return best-performing content
2. Include comprehensive metadata about iterations
3. Log final AI detection score and improvements
```

## Configuration

### Environment Variables
```bash
PHRASLY_API_KEY=your-api-key-here
PHRASLY_BASE_URL=https://api.phrasly.ai
```

### YAML Configuration (`config/gptzero_config.yaml`)
```yaml
PHRASLY_API_KEY: "your-api-key-here"
PHRASLY_BASE_URL: "https://api.phrasly.ai"
PHRASLY_TARGET_SCORE: 30.0      # Target AI detection score
PHRASLY_MAX_ITERATIONS: 3       # Maximum improvement iterations
PHRASLY_IMPROVEMENT_THRESHOLD: 5.0  # Minimum improvement to continue
```

## Improvement Strategies

### 1. Temperature Adjustment
- **Method:** Modify generation temperature for re-generation
- **Goal:** Reduce predictability that triggers AI detection
- **Impact:** Medium improvement potential

### 2. Human Elements Addition
- **Method:** Add contractions, transitional phrases, natural variations
- **Goal:** Introduce human-like language patterns
- **Impact:** High improvement potential for post-processing

### 3. Prompt Instruction Modification
- **Method:** Enhance prompts to emphasize human-like writing
- **Goal:** Guide AI toward more natural language generation
- **Impact:** High improvement potential for future generations

### 4. Writing Style Adjustment
- **Method:** Replace formal phrases with conversational alternatives
- **Goal:** Make content more approachable and human-like
- **Impact:** Medium improvement potential

## Usage Examples

### Basic Integration
```python
from components.content.enhanced_factory import create_enhanced_content_generator

# Create enhanced generator with Phrasly.ai
generator = create_enhanced_content_generator(
    enable_phrasly=True,
    phrasly_target_score=25.0
)

# Generate content with automatic improvement
result = generator.generate(
    material_name="Alumina",
    material_data=material_data,
    api_client=grok_client,
    author_info={"id": 2, "name": "Dr. Maria Rossi"}
)
```

### Configuration File Usage
```python
from components.content.enhanced_factory import create_enhanced_content_generator_from_config

# Load from configuration file
generator = create_enhanced_content_generator_from_config("config/gptzero_config.yaml")
```

### Manual Phrasly.ai Integration
```python
from components.content.phrasly_integration import PhraslyAIClient, IterativeContentImprover

# Create Phrasly.ai client
phrasly_client = PhraslyAIClient()

# Create improver with custom settings
improver = IterativeContentImprover(
    phrasly_client=phrasly_client,
    target_score=20.0,
    max_iterations=5
)

# Improve existing content
final_content, history = improver.improve_content(
    initial_content=generated_content,
    material_name="Steel",
    author_info=author_info,
    generation_params=params
)
```

## Benefits

### 1. Quality Improvement
- **Automatic Enhancement:** Content automatically improved to meet human-like standards
- **Measurable Results:** Quantified improvement tracking with before/after scores
- **Consistent Quality:** Ensures all generated content meets AI detection thresholds

### 2. Operational Efficiency
- **Reduced Manual Review:** Less need for human editing of AI-generated content
- **Batch Processing:** Scales to handle large volumes of content generation
- **Cost Optimization:** Balances API costs with quality requirements

### 3. Analytics and Insights
- **Performance Tracking:** Detailed metrics on improvement effectiveness
- **Strategy Optimization:** Data-driven refinement of improvement approaches
- **Quality Assurance:** Automated validation of content authenticity

## Error Handling and Resilience

### Graceful Degradation
- **Phrasly.ai Unavailable:** Falls back to standard generation without improvement
- **API Rate Limits:** Implements backoff and retry mechanisms
- **Network Issues:** Continues with original content if analysis fails

### Comprehensive Logging
- **Iteration Tracking:** Detailed logs of each improvement cycle
- **Score Progression:** Before/after score comparisons
- **Strategy Effectiveness:** Performance metrics for each improvement method

## Integration with Existing System

### Backward Compatibility
- **Drop-in Replacement:** Enhanced generator maintains same interface
- **Optional Integration:** Phrasly.ai features can be disabled
- **Configuration Flexibility:** Multiple configuration options available

### Component Architecture
- **Modular Design:** Separate concerns for generation, analysis, and improvement
- **Factory Pattern:** Consistent object creation and configuration
- **Dependency Injection:** Clean separation of API clients and services

## Future Enhancements

### Advanced Strategies
- **Machine Learning Models:** Train custom models for content improvement
- **Author-Specific Tuning:** Personalized improvement strategies per author
- **Multi-Language Support:** Extend to additional languages beyond English

### Analytics and Reporting
- **Dashboard Integration:** Real-time monitoring of improvement metrics
- **Trend Analysis:** Long-term tracking of content quality trends
- **Performance Benchmarking:** Comparative analysis across different strategies

### API Optimization
- **Batch Processing:** Analyze multiple content pieces simultaneously
- **Caching:** Cache analysis results to reduce API calls
- **Rate Limit Management:** Intelligent request scheduling and throttling
