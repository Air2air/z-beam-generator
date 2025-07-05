# Prompt Optimization System

The Z-Beam Generator now includes an advanced prompt optimization system that automatically tracks performance, learns from results, and generates improved prompts based on what works best.

## 🎯 Features

### 1. **Performance Tracking**
- Automatically tracks success rates and scores for all prompt variations
- Stores historical data persistently in `generator/cache/prompt_performance.json`
- Analyzes patterns across iterations, sections, and content types

### 2. **Adaptive Prompt Selection**
- **Iteration 1**: Uses best-performing prompt based on historical data
- **Later iterations**: Avoids recently failed prompts, ensures diversity
- **Smart rotation**: Balances between proven performers and exploration

### 3. **Optimized Prompt Generation**
- Analyzes successful prompt patterns to extract effective elements
- Generates new prompts that combine the best aspects of high-performing variations
- Creates both AI and human detection prompts based on performance data

### 4. **Performance Analysis**
- Identifies top-performing and underperforming prompts
- Provides actionable recommendations for improvement
- Tracks trends over time to optimize selection strategies

## 🛠️ Usage

### Command Line Interface

```bash
# Show comprehensive performance report
python prompt_optimizer_cli.py report

# Analyze prompt patterns (ai, human, or all)
python prompt_optimizer_cli.py analyze ai

# Generate optimized prompt (preview only)
python prompt_optimizer_cli.py generate ai --preview

# Generate and save optimized prompt
python prompt_optimizer_cli.py save human

# Test prompt selection with sample content
python prompt_optimizer_cli.py test both 3

# Clear performance data (use with caution)
python prompt_optimizer_cli.py clear
```

### Programmatic API

```python
from generator.core.application import Application
from generator.core.interfaces.services import IDetectionService

# Initialize
app = Application()
app.initialize()
detection_service = app.container.get(IDetectionService)

# Get performance report
report = detection_service.get_performance_report()
print(report)

# Analyze patterns
analysis = detection_service.get_optimization_analysis("ai")

# Generate optimized prompt
content, filename = detection_service.generate_optimized_prompt("ai")

# Save optimized prompt and add to rotation
saved_path = detection_service.save_optimized_prompt("ai")
```

## 📊 How It Works

### Performance Metrics
- **Success Rate**: Percentage of times prompt achieved target threshold (≤50%)
- **Average Score**: Mean detection score across all uses
- **Usage Count**: Number of times prompt has been used
- **Score History**: Recent scores for trend analysis

### Selection Algorithm
1. **Performance-Based**: Prioritizes prompts with best success rates and lowest scores
2. **Diversity Ensured**: Avoids repeating failed patterns in same session
3. **Exploration Balance**: Rotates through variations to gather comprehensive data

### Optimization Process
1. **Pattern Analysis**: Extracts common elements from successful prompts
2. **Content Synthesis**: Combines effective patterns into new prompts
3. **Adaptive Refinement**: Continuously improves based on new performance data

## 🔄 Integration with Detection Service

The optimization system is seamlessly integrated with the existing detection service:

- **Automatic Tracking**: Every detection call automatically updates performance data
- **Zero Configuration**: Works out-of-the-box with existing prompt variations
- **Backward Compatible**: Legacy prompt selection still available as fallback

### Enhanced Logging
```
01:56:05 - INFO - Selected best performing prompt: ai_detection_prompt_minimal
01:56:05 - INFO - Using AI detection prompt variation: ai_detection_prompt_minimal (iteration 1)
```

## 📈 Benefits

### Immediate
- **Better Detection Accuracy**: Uses proven high-performing prompts first
- **Reduced API Costs**: Fewer iterations needed when using optimal prompts
- **Improved Content Quality**: More effective detection leads to better improvements

### Long-term
- **Self-Improving System**: Gets better over time as it learns from usage
- **Adaptive Optimization**: Automatically adjusts to changing content patterns
- **Data-Driven Decisions**: Performance data guides prompt development

## 🔧 Configuration

### Storage Location
Performance data is stored in: `generator/cache/prompt_performance.json`

### Available Prompt Variations
- **AI Detection**: `ai_detection_prompt_minimal`, `ai_detection_v1-v4`
- **Human Detection**: `human_detection_prompt_minimal`, `human_detection_v1-v4`

### Success Thresholds
- **AI Detection**: Success when score ≤ 50%
- **Human Detection**: Success when score ≤ 50%

## 🚀 Future Enhancements

1. **Dynamic Prompt Adjustment**: Real-time prompt modification based on performance
2. **Content-Type Specialization**: Different optimal prompts for different content types
3. **A/B Testing Framework**: Systematic testing of prompt variations
4. **Machine Learning Integration**: Advanced pattern recognition for prompt optimization

## 📋 Example Performance Report

```
🎯 Prompt Performance Report
==================================================

Total prompt uses: 8
AI detection prompts tracked: 4
Human detection prompts tracked: 3

🏆 Top AI Detection Prompts:
  1. ai_detection_v2 - Success: 75.0%, Avg Score: 35.2, Uses: 4
  2. ai_detection_prompt_minimal - Success: 60.0%, Avg Score: 42.1, Uses: 5

🏆 Top HUMAN Detection Prompts:
  1. human_detection_v1 - Success: 80.0%, Avg Score: 25.3, Uses: 3

💡 Recommendations:
  • Use 'ai_detection_v2' as primary ai detection prompt (success rate: 75.0%)
  • Use 'human_detection_v1' as primary human detection prompt (success rate: 80.0%)
```

This system ensures that the Z-Beam Generator continuously improves its detection accuracy and content quality through data-driven prompt optimization.
