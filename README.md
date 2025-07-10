# Z-Beam Generator

A sophisticated laser cleaning article generator that creates high-quality, technical content with human-like writing patterns.

## Overview

The Z-Beam Generator uses a **four-phase modular pipeline** to create comprehensive laser cleaning articles:

1. **PHASE 1: GENERATION** - Create content sections, metadata, and tags
2. **PHASE 2: OPTIMIZATION** - Apply AI-powered content optimization  
3. **PHASE 3: ORCHESTRATION** - Assemble final structured article
4. **PHASE 4: OUTPUT** - Generate markdown file with YAML frontmatter

## Features

### 🎯 **Content Generation**
- **Material-specific content** for laser cleaning applications
- **Section-based generation** (introduction, comparisons, contaminants, substrates)
- **Technical accuracy** with proper laser parameters and specifications

### 🔧 **Advanced Optimization**
- **Writing Samples Optimizer** - Matches specific author writing styles
- **Iterative Optimizer** - Sequential AI-powered content refinement
- **Full-article optimization** for coherent flow and natural language patterns

### 📊 **Rich Metadata**
- **34+ metadata fields** including material properties, laser parameters
- **Performance metrics** (efficiency, processing time, surface quality)
- **Technical specifications** (wavelength, power density, fluence)
- **Safety and environmental data**

### 🏷️ **Intelligent Tagging**
- **Property-derived tags** from material analysis
- **AI-optimized tag shortening** for better searchability
- **Multi-level tag hierarchy** (properties, applications, safety)

### 👥 **Author Management**
- **Multiple author profiles** with distinct writing styles
- **Author-specific writing samples** for style matching
- **Professional author metadata** (title, country, expertise)

## Architecture

### Core Components

```
📁 Z-Beam Generator/
├── 🔧 generator.py              # Main pipeline orchestrator
├── 📝 content_generator.py      # Section content generation
├── 📊 metadata/                 # Metadata generation
│   └── metadata_generator.py
├── 🏷️ tags/                     # Tag generation and optimization
│   └── tag_generator.py
├── 🎨 optimizers/               # Content optimization
│   ├── base_optimizer.py        # Base class for optimizers
│   ├── writing_samples_optimizer.py
│   └── iterative_optimizer.py
├── 🎭 orchestrator.py           # Final article assembly
├── 🌐 api_client.py             # AI API interface
└── 🚀 run.py                    # Entry point
```

### Pipeline Flow

```
Material Input → Content Generation → Metadata Generation → Tag Generation
                        ↓                      ↓                ↓
                 Section Content        Material Properties    Optimized Tags
                        ↓                      ↓                ↓
                 ═══════════════════════════════════════════════════
                            OPTIMIZATION PHASE
                 ═══════════════════════════════════════════════════
                        ↓
              Writing Samples OR Iterative Optimization
                        ↓
                 Optimized Content
                        ↓
                 Article Orchestration
                        ↓
                 📄 Final Markdown Article
```

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone [repository-url]
cd z-beam-generator

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Set your API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run Generation

```bash
python3 run.py
```

## Configuration

### Basic Settings (`run.py`)

```python
# Material and Author
context = {
    "material": "hafnium",      # Target material
    "author_id": 2,             # Author profile ID
    "article_type": "material"  # Article type
}

# AI Settings
config = {
    "provider": "OPENAI",           # AI provider
    "model": "gpt-4-turbo",         # Model selection
    "temperature": 0.3,             # Creativity level
    "optimization_method": "writing_samples",  # Optimizer choice
}
```

### Advanced Configuration

```python
# Content Limits
"max_section_words": 75,        # Words per section
"target_section_words": 75,     # Target section length
"max_total_words": 800,         # Total article limit

# Optimization Settings
"high_similarity_threshold": 0.95,   # AI detection thresholds
"low_similarity_threshold": 0.7,
"final_similarity_threshold": 0.85,

# Debug Settings
"debug_prompts": True,          # Log AI prompts
"debug_responses": True,        # Log AI responses
"debug_content_flow": True,     # Log content flow
```

## Optimization Methods

### Writing Samples Optimizer
- **Author-specific style matching** using writing samples
- **Full-article optimization** for coherent flow
- **Style consistency** across all sections
- **Professional tone matching**

**Use when:** You want content that matches a specific author's writing style

### Iterative Optimizer  
- **Multi-step refinement** process
- **Sequential improvements** with configurable steps
- **Delta analysis** to track changes
- **Human-like transformation** patterns

**Use when:** You want maximum content transformation and refinement

## Output Structure

### Generated Article Format

```markdown
---
title: "Laser Cleaning hafnium"
authorName: "Mario Jordan"
materialType: "hafnium"
atomicNumber: "72"
density: "13.31 g/cm³"
laserCleaningParameters:
  wavelength: "1064 nm"
  powerDensity: "4.5 kW/cm²"
  fluence: "2.5 J/cm²"
tags: [...]
---

# Laser Cleaning hafnium

## Introduction
[Technical introduction with material-specific content...]

## Comparison with Traditional Methods  
[Detailed comparison analysis...]

## Contaminants Removed
[Specific contaminant types and removal efficiency...]

## Substrate Applications
[Application scenarios and technical parameters...]
```

### Key Output Features

- ✅ **Complete YAML frontmatter** with 30+ metadata fields
- ✅ **Technical accuracy** with proper laser parameters  
- ✅ **Material-specific content** tailored to the target material
- ✅ **Professional formatting** with consistent structure
- ✅ **SEO-optimized tags** for searchability

## File Structure

### Required Directories

```
📁 prompts/
├── 📝 text/
│   └── sections.json           # Section generation prompts
├── 👥 authors/
│   ├── authors.json            # Author profiles
│   ├── author_1_sample.txt     # Writing samples
│   └── author_2_sample.txt
├── 🔧 optimizations/
│   └── iterative.json          # Iterative optimization steps
└── 🏷️ tags/
    └── tag_prompts.json        # Tag generation prompts

📁 output/                      # Generated articles
📁 logs/                        # Application logs
```

### Sample Files

**authors.json:**
```json
[
  {
    "id": 1,
    "name": "Dr. Sarah Chen",
    "title": "Senior Laser Engineer",
    "country": "USA"
  }
]
```

**sections.json:**
```json
{
  "introduction": {
    "title": "Introduction",
    "prompt": "Generate introduction for {material} laser cleaning..."
  }
}
```

## Advanced Features

### Multi-Provider Support
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic Claude** (ready for integration)
- **Google Gemini** (ready for integration)
- **XAI Grok** (ready for integration)

### Quality Assurance
- **Delta analysis** tracking content transformation
- **Similarity thresholds** for AI detection avoidance
- **Word count management** with configurable limits
- **Error handling** with fail-fast approach

### Extensibility
- **Modular optimizer system** - easy to add new optimizers
- **Plugin architecture** for new content types
- **Configurable prompt system** for easy customization
- **Multi-language support** ready for international use

## Troubleshooting

### Common Issues

**ImportError: Cannot import name 'ZBeamGenerator'**
```bash
# Solution: Use function-based import
from generator import generate_article
```

**Missing author writing sample**
```bash
# Ensure file exists:
prompts/authors/author_2_sample.txt
```

**API key not set**
```bash
export OPENAI_API_KEY="your-key-here"
```

### Debug Mode

Enable comprehensive logging:
```python
config = {
    "debug_prompts": True,
    "debug_responses": True,
    "debug_content_flow": True
}
```

## Contributing

### Development Setup

1. **Fork and clone** the repository
2. **Create feature branch**: `git checkout -b feature/new-optimizer`
3. **Install dev dependencies**: `pip install -r requirements-dev.txt`
4. **Run tests**: `python -m pytest tests/`
5. **Submit pull request`

### Adding New Optimizers

1. **Inherit from BaseOptimizer**
2. **Implement optimize_sections method**
3. **Add to optimizer factory in generator.py**
4. **Update configuration options**

```python
from optimizers.base_optimizer import BaseOptimizer

class CustomOptimizer(BaseOptimizer):
    def optimize_sections(self, sections, material, metadata):
        # Your optimization logic here
        return optimized_sections
```

## License

MIT License - see LICENSE file for details.

## Support

- 📧 **Email**: [support-email]
- 📖 **Documentation**: [docs-url]
- 🐛 **Issues**: [github-issues-url]
- 💬 **Discussions**: [github-discussions-url]

---

**🚀 Generate professional laser cleaning articles with advanced AI optimization and human-like writing patterns!**