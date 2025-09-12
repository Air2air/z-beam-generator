# Z-Beam Optimizer Quick Start Guide

## 🚀 Getting Started in 5 Minutes

The Z-Beam Optimizer enhances your content with AI detection optimization and quality improvement. This guide shows you how to get started quickly.

## Prerequisites

- Python 3.8+
- Z-Beam Generator installed
- Winston.ai API key (for production use)

## Installation

The optimizer is included with Z-Beam Generator. No additional installation required.

```bash
# Verify optimizer is available
python3 -c "from optimizer.optimization_orchestrator import optimize_content_simple; print('✅ Optimizer ready')"
```

## ⚡ Quick Start Examples

### 1. Basic Content Optimization

```python
import asyncio
from optimizer.optimization_orchestrator import optimize_content_simple

async def main():
    # Your content to optimize
    content = """
    Silicon nitride is a material used in laser cleaning applications.
    It has good thermal properties and can be effectively cleaned using
    laser technology with appropriate parameters.
    """

    # Optimize content
    result = await optimize_content_simple(
        content=content,
        material_name="silicon_nitride",
        target_score=75.0  # Target AI detection score (higher = more human-like)
    )

    if result.success:
        print("✅ Optimization successful!")
        print(f"Score improved: {result.original_score:.1f} → {result.final_score:.1f}")
        print(f"Optimized content:\n{result.optimized_content}")
    else:
        print("❌ Optimization failed")

# Run the example
asyncio.run(main())
```

### 2. Batch Optimization

```python
import asyncio
from optimizer.optimization_orchestrator import batch_optimize_materials

async def main():
    # Multiple materials to optimize
    materials_content = {
        "silicon_nitride": "Content about silicon nitride laser cleaning...",
        "aluminum_oxide": "Content about aluminum oxide laser cleaning...",
        "titanium_dioxide": "Content about titanium dioxide laser cleaning..."
    }

    # Batch optimize all materials
    results = await batch_optimize_materials(
        materials_content=materials_content,
        target_score=75.0
    )

    # Show results
    for material, result in results.items():
        if result.success:
            print(f"✅ {material}: {result.final_score:.1f} (improved +{result.improvement:.1f})")
        else:
            print(f"❌ {material}: Failed")

asyncio.run(main())
```

### 3. Advanced Optimization with Custom Settings

```python
import asyncio
from optimizer.optimization_orchestrator import ContentOptimizationOrchestrator, OptimizationConfig

async def main():
    # Custom optimization configuration
    config = OptimizationConfig(
        target_score=80.0,        # Higher quality target
        max_iterations=7,         # More optimization attempts
        improvement_threshold=5.0, # Require larger improvements
        time_limit_seconds=600    # 10 minute limit
    )

    # Initialize orchestrator
    orchestrator = ContentOptimizationOrchestrator()

    # Optimize with custom settings
    result = await orchestrator.optimize_content(
        content="Your content here...",
        material_name="silicon_nitride",
        config=config
    )

    print(f"Final score: {result.final_score:.1f}")
    print(f"Iterations: {result.iterations_performed}")
    print(f"Total time: {result.total_time:.1f}s")

asyncio.run(main())
```

## 📊 Quality Scoring

Check content quality before optimization:

```python
from optimizer.text_optimization.validation.content_scorer import create_content_scorer

# Create quality scorer
scorer = create_content_scorer(human_threshold=75.0)

# Score your content
score = scorer.score_content(
    content="Your content to evaluate...",
    material_data={"name": "silicon_nitride"},
    author_info={"id": 1}  # Taiwan author
)

print(f"Overall quality: {score.overall_score:.1f}/100")
print(f"Human believability: {score.human_believability:.1f}/100")
print(f"Technical accuracy: {score.technical_accuracy:.1f}/100")
print(f"Author authenticity: {score.author_authenticity:.1f}/100")
print(f"Readability: {score.readability_score:.1f}/100")
print(f"Retry recommended: {score.retry_recommended}")
```

## ⚙️ Configuration

### Environment Setup

```bash
# Set your Winston.ai API key
export WINSTON_API_KEY="your_api_key_here"

# Optional: Customize settings
export AI_DETECTION_TARGET_SCORE="75.0"
export AI_DETECTION_MAX_ITERATIONS="5"
```

### Basic Configuration

```python
from optimizer.optimization_orchestrator import OptimizationConfig

# Simple configuration
config = OptimizationConfig(
    target_score=75.0,    # Target AI detection score (higher = more human-like)
    max_iterations=5,     # Maximum attempts
)

# Advanced configuration
config = OptimizationConfig(
    target_score=80.0,        # Higher quality
    max_iterations=7,         # More attempts
    improvement_threshold=5.0, # Larger improvements required
    time_limit_seconds=600    # Time limit
)
```

## 🎭 Author Personas

The optimizer supports 4 distinct author personas:

```python
# Taiwan (Author ID: 1) - Systematic, methodical
author_info = {"id": 1, "name": "Yi-Chun Lin", "country": "Taiwan"}

# Italy (Author ID: 2) - Technical elegance
author_info = {"id": 2, "name": "Maria Rossi", "country": "Italy"}

# Indonesia (Author ID: 3) - Practical, direct
author_info = {"id": 3, "name": "Sari Dewi", "country": "Indonesia"}

# USA (Author ID: 4) - Conversational, innovative
author_info = {"id": 4, "name": "Dr. Smith", "country": "USA"}
```

Each persona has:
- Unique word limits (250-450 words)
- Cultural writing characteristics
- Language patterns and signature phrases
- Technical expertise focus

## 🔧 Service Management

### Initialize Services

```python
from optimizer.service_initializer import initialize_optimizer_services

# Initialize all optimizer services
init_result = initialize_optimizer_services()

if init_result["success"]:
    print("✅ All services initialized")
    print(f"Services: {init_result['services_initialized']}")
else:
    print("❌ Service initialization failed")
    print(f"Errors: {init_result['errors']}")
```

### Check Service Status

```python
from optimizer.service_initializer import get_optimizer_status

# Get status of all services
status = get_optimizer_status()

print("Service Status:")
for service_name, service_info in status['services'].items():
    health = "✅" if service_info['healthy'] else "❌"
    enabled = "enabled" if service_info.get('enabled', True) else "disabled"
    print(f"  {health} {service_name} ({enabled})")
```

## 📈 Monitoring & Results

### Understanding Optimization Results

```python
result = await optimize_content_simple(content, material_name, target_score)

# Key metrics
print(f"Success: {result.success}")
print(f"Original score: {result.original_score:.1f}")
print(f"Final score: {result.final_score:.1f}")
print(f"Improvement: +{result.improvement:.1f}")
print(f"Iterations: {result.iterations_performed}")
print(f"Processing time: {result.total_time:.1f}s")

# Access optimized content
if result.success:
    optimized_content = result.optimized_content
    print(f"Optimized content length: {len(optimized_content)} characters")
```

### Batch Results Analysis

```python
results = await batch_optimize_materials(materials_content)

# Analyze batch results
successful = sum(1 for r in results.values() if r.success)
total = len(results)
success_rate = (successful / total) * 100

print(f"Batch complete: {successful}/{total} successful ({success_rate:.1f}%)")

# Detailed results
for material, result in results.items():
    status = "✅" if result.success else "❌"
    print(f"{status} {material}: {result.final_score:.1f} ({result.iterations_performed} iterations)")
```

## 🧪 Testing

### Test with Mock Provider

```python
# Use mock provider for testing (no API key required)
from optimizer.services import ServiceConfiguration
from optimizer.services.ai_detection_optimization import AIDetectionOptimizationService

config = ServiceConfiguration(
    name="ai_detection_service",
    settings={
        "allow_mocks_for_testing": True,
        "providers": {
            "mock": {"enabled": True},
            "winston": {"enabled": False}
        }
    }
)

service = AIDetectionOptimizationService(config)
```

### Run Optimizer Tests

```bash
# Run all optimizer tests
pytest optimizer/ -v

# Run specific test file
pytest optimizer/test_optimization_validation.py -v

# Run with coverage
pytest optimizer/ --cov=optimizer --cov-report=html
```

## 🚨 Troubleshooting

### Common Issues

#### 1. "Winston.ai API key not configured"
```python
# Set your API key
import os
os.environ["WINSTON_API_KEY"] = "your_api_key_here"

# Or create .env file
# WINSTON_API_KEY=your_api_key_here
```

#### 2. "Service not initialized"
```python
# Initialize services first
from optimizer.service_initializer import initialize_optimizer_services
init_result = initialize_optimizer_services()
assert init_result["success"], "Service initialization failed"
```

#### 3. "Content too short for analysis"
```python
# Ensure content meets minimum length (300+ characters recommended)
content = "Your content here..."  # Make sure it's substantial
assert len(content) >= 300, "Content too short"
```

#### 4. Optimization taking too long
```python
# Add time limit
config = OptimizationConfig(
    target_score=75.0,
    time_limit_seconds=300  # 5 minute limit
)
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
logger = logging.getLogger("optimizer")
logger.setLevel(logging.DEBUG)

# Run optimization with debug output
result = await optimize_content_simple(content, material_name, target_score)
```

## 📚 Next Steps

### Learn More
- **[README.md](./README.md)**: Comprehensive system overview
- **[API_REFERENCE.md](./API_REFERENCE.md)**: Complete API documentation
- **[CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md)**: Advanced configuration options
- **[IMPROVEMENT_PLAN.md](./IMPROVEMENT_PLAN.md)**: Future enhancements

### Advanced Usage
- **Custom Iteration Functions**: Implement specialized optimization logic
- **Batch Processing**: Optimize multiple materials efficiently
- **Quality Monitoring**: Track optimization performance over time
- **Integration**: Incorporate optimizer into your workflow

### Performance Tips
- **Caching**: Enable caching for repeated content types
- **Batch Processing**: Process multiple items together
- **Quality Thresholds**: Set appropriate targets for your use case
- **Resource Limits**: Configure based on your system capabilities

## 🎯 Quick Reference

### Essential Functions
```python
# Simple optimization
result = await optimize_content_simple(content, material_name, target_score)

# Batch optimization
results = await batch_optimize_materials(materials_content)

# Quality scoring
score = scorer.score_content(content, material_data, author_info)

# Service management
init_result = initialize_optimizer_services()
status = get_optimizer_status()
```

### Key Classes
- `ContentOptimizationOrchestrator`: Main optimization interface
- `OptimizationConfig`: Configuration settings
- `OptimizationResult`: Optimization results
- `ContentScorer`: Quality assessment

### Important Settings
- `target_score`: AI detection target (70-85 recommended)
- `max_iterations`: Optimization attempts (3-7 recommended)
- `time_limit_seconds`: Processing timeout (300-600 recommended)

This quick start guide gets you up and running with the Z-Beam Optimizer in minutes. For more advanced usage, refer to the comprehensive documentation.</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/optimizer/QUICK_START.md
