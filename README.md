# Z-Beam Article Generation System

## Overview
The Z-Beam system generates high-quality, human-like articles about laser cleaning materials with built-in AI detection avoidance and word budget management.

## Quick Start

### 1. Configuration
Edit `run.py` to configure your article generation:

```python
USER_CONFIG = dict(
    material="Steel",                    # Material to write about
    category="Material",                 # Article category
    generator_provider="DEEPSEEK",       # XAI, GEMINI, DEEPSEEK
    detection_provider="DEEPSEEK",       # XAI, GEMINI, DEEPSEEK
    max_article_words=800,              # Total word budget
    ai_detection_threshold=60,          # AI detection target (lower = more human-like)
    human_detection_threshold=60,       # Human detection target
    iterations_per_section=3,           # Max iterations per section
)
```

### 2. Generate Articles
```bash
# Standard article generation
python3 run.py

# Test detector improvements  
python3 run.py --test-detector

# Simulate efficiency (no API calls)
python3 simulate_efficiency.py
```

### 3. Test the System
```bash
# Test efficient system with mocks
python3 test_efficient_system.py

# Test real generation (uses API)
python3 test_real_generation.py
```

## Key Features

### ✅ Word Budget Management
- **Global Control**: Set `max_article_words` for predictable length
- **Smart Allocation**: Automatically distributes words across sections
- **Section Budgets**: Introduction (15%), Comparison (20%), etc.

### ✅ API Efficiency
- **52-63% Fewer API Calls**: Smart iteration and detection skipping
- **Provider Flexibility**: Switch between DEEPSEEK, XAI, GEMINI
- **Quota Management**: Avoid hitting daily limits

### ✅ AI Detection Avoidance
- **Multiple Prompt Variations**: 9 different detection prompts for robustness
- **Iterative Refinement**: Improve content until thresholds are met
- **Performance Tracking**: Monitor and optimize detection scores

### ✅ Modern Architecture
- **Domain-Driven Design**: Clean separation of concerns
- **Dependency Injection**: Modular, testable components
- **Provider Abstraction**: Easy to add new AI providers

## Architecture

```
run.py (config + CLI)
├── ApplicationRunner (orchestration)
├── WordBudgetManager (budget allocation)
├── EfficientContentGenerationService (optimized generation)
├── DetectionService (AI detection + optimization)
└── APIClient (provider abstraction)
```

## Core Services

### Word Budget Manager
- Allocates word budgets per section based on percentages
- Validates total stays within global limit
- Supports different presets (compact, standard, extended)

### Efficient Content Service  
- Skips detection for non-AI sections (charts, tables)
- Uses provider-specific models and endpoints
- Implements smart iteration limits

### Detection Service
- Rotates through 9 prompt variations for robustness
- Tracks performance and optimizes selections
- Provider-agnostic (works with any API)

## Configuration

### Environment Variables
```bash
# API Keys (set the ones you need)
DEEPSEEK_API_KEY=your_deepseek_key
XAI_API_KEY=your_xai_key  
GEMINI_API_KEY=your_gemini_key
```

### Provider Options
- **DEEPSEEK**: Cost-effective, good performance (`deepseek-chat`)
- **XAI**: Fast, good for development (`grok-3-mini-beta`)
- **GEMINI**: High quality but quota limited (`gemini-2.5-flash`)

## Testing

### Simulation Mode
No API calls, validates logic:
```bash
python3 simulate_efficiency.py
```

### Mock Testing
Tests with fake responses:
```bash
python3 test_efficient_system.py
```

### Real Testing
Uses actual APIs:
```bash
python3 test_real_generation.py
```

## Efficiency Improvements

| Metric | Old System | New System | Improvement |
|--------|------------|------------|-------------|
| API Calls | 133 | 63 | -52.6% |
| Articles/Day | 1 | 3-5 | +200-400% |
| Word Control | None | Strict | ✅ |
| Provider Lock-in | Gemini Only | Any Provider | ✅ |

## Troubleshooting

### Quota Issues
- Switch to DEEPSEEK (higher quotas)
- Reduce `iterations_per_section`
- Lower `max_article_words`

### Quality Issues
- Increase `iterations_per_section`
- Lower detection thresholds
- Use GEMINI for higher quality

### Performance Issues
- Use DEEPSEEK for speed
- Enable detection skipping for tables/charts
- Use simulation mode for testing

## Documentation Files

- **API_EFFICIENCY_ANALYSIS.md**: Detailed efficiency analysis
- **IMPLEMENTATION_SUMMARY.md**: Technical implementation details
- **PROMPT_OPTIMIZATION_GUIDE.md**: Guide to detection optimization
- **STREAMLINED_WORKFLOW_GUIDE.md**: Workflow best practices
- **LOGGING_GUIDE.md**: Logging and monitoring setup
