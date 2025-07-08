# Z-Beam Generator

> **⚠️ BLOAT NOTICE:** Per PROJECT_GUIDE, avoid unnecessary files. The `z_beam_generator.log` in root should be gitignored or removed to prevent repository bloat.

## Overview

Z-Beam Generator is a modular content generation system that creates high-quality, E-A-T compliant articles through a sophisticated generation → optimization pipeline.

## Architecture

```
📋 Config → 🔍 Health Check → 📝 Generation → 🎯 Optimization → 📄 Output
```

### Core Components

```
modules/
├── generation/           # Content creation pipeline
│   ├── content_generator.py    # Main coordinator
│   ├── health_checker.py       # API validation
│   ├── section_generator.py    # Section creation
│   ├── sections_loader.py      # Config loading
│   └── article_composer.py     # Final assembly
├── optimization/         # Content refinement pipeline
│   ├── orchestrator.py         # Main coordinator
│   ├── pipeline_manager.py     # Step loading & ordering
│   ├── prompt_builder.py       # Context-aware prompts
│   └── step_executor.py        # API execution
└── api_client.py         # Provider abstraction
```

## System Flow

### 1. **Generation Pipeline**
- **Health Check** - Validates API connectivity
- **Section Loading** - Reads `prompts/sections.json`
- **Content Generation** - Creates base content per section
- **E-A-T Enhancement** - Applies Google E-A-T requirements

### 2. **Optimization Pipeline**
```
E-A-T Requirements → Narrative Authenticity → Human Naturalness → Authority Enhancement
```

Each step refines content through provider-specific API calls with configurable parameters.

### 3. **Output Assembly**
- Combines optimized sections
- Applies consistent formatting
- Saves to `output/` directory

## Configuration

### Provider Settings
```python
"provider_models": {
    "DEEPSEEK": {
        "model": "deepseek-chat",
        "url_template": "https://api.deepseek.com/v1/chat/completions"
    },
    "XAI": {
        "model": "grok-beta", 
        "url_template": "https://api.x.ai/v1/chat/completions"
    },
    "GEMINI": {
        "model": "gemini-pro",
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    }
}
```

### Provider Characteristics
- **DEEPSEEK**: Best length control, precise output
- **XAI/Grok**: Creative but verbose, may exceed token limits
- **GEMINI**: Balanced performance, good for technical content

### Temperature Controls
```python
"step_temperatures": {
    "human_naturalness": 0.5,           # Higher for creativity
    "authority_technical_enhancement": 0.2,  # Lower for precision
    "narrative_authenticity": 0.4,      # Moderate for flow
    "readability_final_polish": 0.3     # Default precision
}
```

## Quick Start

### 1. **Environment Setup**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install requests
```

### 2. **API Keys**
Set environment variables:
```bash
export DEEPSEEK_API_KEY="your_key_here"
export XAI_API_KEY="your_key_here"
export GEMINI_API_KEY="your_key_here"
```

### 3. **Run Generation**
```bash
python run.py
```

## File Structure

```
z-beam-generator/
├── modules/              # Core system modules
├── prompts/              # Configuration files
│   ├── sections.json     # Section definitions
│   ├── optimizations.json # Optimization steps
│   └── sample_1.txt      # Writing style reference
├── output/               # Generated content
├── run.py                # Main entry point
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Troubleshooting

### Common Issues

#### **Truncated Content**
- **Symptoms**: Sections end mid-sentence
- **Cause**: Token limits too restrictive for provider
- **Solution**: Increase `max_tokens` in config or switch providers

#### **API Timeouts**
- **Symptoms**: Generation fails with timeout errors
- **Cause**: Network issues or provider overload
- **Solution**: Increase `timeout` setting or retry

#### **Empty Responses**
- **Symptoms**: Sections generate but contain no content
- **Cause**: API key issues or provider errors
- **Solution**: Verify API keys and check provider status

#### **Log File Bloat**
- **Issue**: `z_beam_generator.log` appearing in root
- **Solution**: Add to `.gitignore` or configure logging directory
- **Per PROJECT_GUIDE**: Avoid unnecessary files in repository

### Debug Mode
```python
# Enable debug logging in run.py
logging.basicConfig(level=logging.DEBUG)
```

## Writing Sample Integration

Place reference content in `prompts/sample_1.txt` to guide style and tone:

```json
{
  "eat_requirements": {
    "writing_sample_file": "sample_1.txt",
    ...
  }
}
```

## Best Practices

### **Configuration Management**
- Keep sensitive API keys in environment variables
- Use step-specific temperature overrides for fine control
- Test with single sections before full generation

### **Content Quality**
- Review writing samples to ensure appropriate style
- Monitor word counts per section
- Validate technical accuracy in generated content

### **Repository Hygiene** (Per PROJECT_GUIDE)
- Remove/gitignore log files (`z_beam_generator.log`)
- Avoid committing generated content files
- Keep configuration files minimal and focused

## Extending the System

### **Adding New Providers**
1. Add provider config to `provider_models`
2. Implement provider-specific API call in `api_client.py`
3. Add API key mapping

### **Adding Optimization Steps**
1. Create new step in `optimizations.json`
2. Set appropriate `order` value
3. Configure step-specific parameters

### **Adding New Sections**
1. Define section in `sections.json`
2. Set `order` and `materials` array
3. Create section-specific prompt

## License

[Your License Here]

## Support

For issues and feature requests, please refer to the project repository.

---

**⚠️ BLOAT WARNING:** Per PROJECT_GUIDE, regularly clean up log files, temporary files, and unnecessary artifacts to maintain repository cleanliness.