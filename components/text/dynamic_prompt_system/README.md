# Dynamic Prompt Generation System

A standalone system for dynamically evolving AI detection prompts based on Winston AI analysis, designed to work similarly to iterative text generation systems.

## Overview

The Dynamic Prompt Generation System analyzes Winston AI detection results and gradually evolves the `ai_detection.yaml` prompts to improve future content generation. This creates a self-improving AI detection optimization system that evolves based on real performance data.

## Architecture

```
dynamic_prompt_system/
├── __init__.py                 # Main DynamicPromptSystem class
├── winston_analyzer.py         # Analyzes Winston results for improvement needs
├── prompt_evolution_manager.py # Manages evolution history and statistics
└── dynamic_prompt_generator.py # Core prompt generation and application logic
```

## Key Features

### 🎯 Intelligent Analysis
- Analyzes Winston AI detection scores and classifications
- Determines which prompt sections need improvement
- Prioritizes improvements based on score ranges and content analysis

### 🤖 DeepSeek Integration
- Uses DeepSeek API for intelligent prompt improvement suggestions
- Generates targeted, actionable improvements for specific prompt sections
- Maintains consistency with existing prompt patterns

### 📈 Gradual Evolution
- Applies only 1-2 improvements per iteration to avoid overwhelming changes
- Works like the text generation system with incremental improvements
- Includes random elements for natural evolution (40% application chance)

### 🔧 Template Variable System
- Maintains dynamic config substitution with `${variable_name}` syntax
- Automatically substitutes values from `AI_DETECTION_CONFIG`
- Preserves template variables when saving updates

### 📊 Evolution Tracking
- Comprehensive history of all prompt evolutions
- Statistics and analytics for improvement tracking
- Score trend analysis and success rate monitoring

## Usage

### Basic Usage

```python
from components.text.dynamic_prompt_system import DynamicPromptSystem

# Initialize the system
prompt_system = DynamicPromptSystem()

# Analyze Winston results and evolve prompts
result = prompt_system.analyze_and_evolve(
    winston_result={
        'overall_score': 45.0,
        'classification': 'ai',
        'sentence_analysis': {'low_score_percentage': 15.0}
    },
    content="Your generated content here...",
    iteration_context={
        'iteration_history': [...],
        'current_score': 45.0,
        'target_score': 70.0
    }
)

print(f"Evolution result: {result}")
```

### Advanced Usage

```python
# Get evolution statistics
stats = prompt_system.get_current_stats()
print(f"Current version: {stats['current_version']}")
print(f"Total evolutions: {stats['total_evolutions']}")

# Get evolution history
history = prompt_system.get_evolution_history()
for evolution in history[-5:]:  # Last 5 evolutions
    print(f"Score: {evolution['winston_score']}, Applied: {evolution['improvements_applied']}")

# Force evolution (bypass random chance)
success = prompt_system.force_evolution(winston_result, content, iteration_context)
```

## Integration with Text Generation

The system is designed to integrate seamlessly with the text generation pipeline:

1. **Analysis Phase**: Examines Winston scores after each iteration
2. **Generation Phase**: Creates targeted improvements using DeepSeek
3. **Application Phase**: Applies improvements gradually (40% chance)
4. **Tracking Phase**: Records evolution history and statistics

## Configuration

The system uses the following configuration from `AI_DETECTION_CONFIG`:

- `target_score`: Target Winston score for content
- `winston_human_range`: Score range considered human-like
- `winston_unclear_range`: Score range considered unclear
- `winston_ai_range`: Score range considered AI-generated

## Evolution Strategy

### Improvement Priorities

1. **Critical (Score < 30)**: Fundamental improvements
   - AI detection avoidance
   - Human writing characteristics
   - Natural imperfections

2. **High (Score < 50)**: Authenticity enhancements
   - Human authenticity enhancements
   - Cognitive variability
   - Personal touch

3. **Medium (Score < 70)**: Refinement
   - Conversational flow
   - Cultural humanization
   - Detection response

4. **Low (Score < Target)**: Minor tweaks
   - Content transformation rules
   - Iteration refinement mechanisms

### Gradual Application

- Maximum 2-3 sections targeted per evolution
- Only 1 improvement applied per section per iteration
- 40% chance of applying improvements (gradual evolution)
- Random elements prevent predictable patterns

## Monitoring and Analytics

### Evolution Statistics

```python
stats = prompt_system.get_evolution_stats()
# {
#     'total_evolutions': 25,
#     'success_rate': 68.0,
#     'average_score': 52.3,
#     'score_trend': 'improving',
#     'most_targeted_sections': [
#         ('cognitive_variability', 8),
#         ('human_authenticity_enhancements', 6),
#         ('conversational_flow', 5)
#     ]
# }
```

### Score Improvement Tracking

```python
improvements = prompt_system.get_score_improvements()
for improvement in improvements:
    print(f"Score improved by {improvement['score_improvement']:.1f} points")
```

## File Structure

- `ai_detection.yaml`: The evolving prompts file
- `evolution_history.json`: Complete evolution history and statistics
- Template variables: `${variable_name}` format for dynamic configuration

## Best Practices

1. **Monitor Evolution**: Regularly check evolution statistics and trends
2. **Balance Application**: The 40% application rate prevents over-evolution
3. **Review Improvements**: Examine applied improvements for effectiveness
4. **Backup Prompts**: Keep backups of working prompt configurations
5. **Test Changes**: Validate improvements with test content generation

## Troubleshooting

### Common Issues

1. **No Improvements Generated**
   - Check Winston API connectivity
   - Verify DeepSeek API configuration
   - Ensure content meets minimum length requirements

2. **Improvements Not Applied**
   - Check random chance (40% application rate)
   - Verify prompt file permissions
   - Ensure template variables are properly formatted

3. **Poor Evolution Results**
   - Review Winston analysis quality
   - Check content diversity and length
   - Validate DeepSeek prompt engineering

### Debug Mode

Enable detailed logging to troubleshoot issues:

```python
import logging
logging.getLogger('components.text.dynamic_prompt_system').setLevel(logging.DEBUG)
```

## Future Enhancements

- Machine learning-based improvement prediction
- A/B testing for prompt variations
- Automated rollback for poor-performing improvements
- Multi-objective optimization (score + other metrics)
- Integration with other AI detection services
