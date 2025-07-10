# Z-Beam Generator

A sophisticated AI-powered content generation system for laser cleaning articles. Generates comprehensive, human-like articles with configurable optimization pipelines.

## 🚀 Quick Start

1. **Edit Configuration** (top of `run.py`):
```python
# Article Context
context = {
    "material": "hafnium",     # Material to write about
    "author_id": 2,           # Author style (1-4)
    "article_type": "material"
}

# Optimization Order (0=skip, 1=first, 2=second, 3=third)
optimization_config = {
    'iterative': 1,                # Structural improvements
    'writing_sample': 2,          # Author voice matching
    'technical_authenticity': 3    # Technical expertise injection
}
```

2. **Run Generation**:
```bash
python3 run.py
```

3. **Check Output**: Article generated in `output/` directory

## 🏗️ System Architecture

### **Phase 1: Content Generation**
- **Sections**: Creates Introduction, Comparison, Contaminants, Substrates using `prompts/text/sections.json`
- **Metadata**: Generates 34+ metadata fields (SEO, social, technical)
- **Tags**: Creates optimized tags for article classification

### **Phase 2: Optimization Pipeline**
Three configurable optimizers run in sequence:

#### **1. Iterative Optimizer** (`optimizers/iterative/`)
- **6-step refinement process** using `iterative.json`
- **Human naturalness** enhancement 
- **Authority & technical** credibility
- **Conversational tone** injection

#### **2. Writing Sample Optimizer** (`optimizers/writing_sample/`)
- **Author voice matching** using writing samples
- **Style consistency** across sections
- **Personal tone** adaptation

#### **3. Technical Authenticity Optimizer** (`optimizers/technical_authenticity/`)
- **Dynamic LLM research** for material-specific facts
- **Real equipment** and manufacturer references
- **Industry standards** (ASTM, ISO, ANSI)
- **Authentic applications** and case studies

### **Phase 3: Assembly**
- **YAML frontmatter** with metadata
- **Markdown formatting** 
- **Final article** output

## 🎛️ Configuration Examples

### **All Three Optimizers (Full Treatment)**
```python
optimization_config = {
    'iterative': 1,                # First: structural improvements
    'writing_sample': 2,          # Second: author voice
    'technical_authenticity': 3    # Third: technical expertise
}
```

### **Technical-First Approach**
```python
optimization_config = {
    'technical_authenticity': 1,   # First: inject technical facts
    'iterative': 2,               # Second: humanize
    'writing_sample': 3          # Third: author style
}
```

### **Two-Step Optimization**
```python
optimization_config = {
    'iterative': 0,               # Skip
    'writing_sample': 1,         # First
    'technical_authenticity': 2   # Second
}
```

### **Single Optimizer Testing**
```python
optimization_config = {
    'iterative': 1,               # Only iterative
    'writing_sample': 0,         # Skip
    'technical_authenticity': 0   # Skip
}
```

### **No Optimization (Baseline)**
```python
optimization_config = {
    'iterative': 0,               # Skip all
    'writing_sample': 0,         # Skip all
    'technical_authenticity': 0   # Skip all
}
```

## 📁 Project Structure

```
z-beam-generator/
├── run.py                          # Main entry point with configuration
├── generator.py                    # Core generation logic
├── api_client.py                   # Multi-provider API client
├── orchestrator.py                 # Article assembly
├── 
├── config/
│   ├── constants.py               # Configuration management
│   └── credentials.json           # API credentials
├── 
├── optimizers/
│   ├── base_optimizer.py          # Base optimizer class
│   ├── simple_order_optimizer.py  # Orchestrates optimization order
│   ├── iterative/
│   │   ├── iterative_optimizer.py
│   │   └── iterative.json         # 6-step optimization prompts
│   ├── writing_sample/
│   │   ├── writing_sample_optimizer.py
│   │   └── samples/               # Author writing samples
│   └── technical_authenticity/
│       ├── technical_authenticity_optimizer.py
│       ├── technical_facts.json   # Dynamic knowledge base
│       ├── equipment.json
│       └── specifications.json
├── 
├── prompts/
│   ├── text/
│   │   └── sections.json          # Section generation prompts
│   └── optimizations/
│       └── iterative.json         # Optimization prompts
├── 
├── authors/
│   └── authors.json               # Author profiles & styles
├── 
├── metadata/
│   └── metadata_generator.py      # Metadata generation
├── 
├── output/                        # Generated articles
└── logs/                          # Execution logs
```

## 🔧 Authors System

Four distinct author profiles with unique writing styles:

- **Author 1**: Technical expert with formal tone
- **Author 2**: Conversational industry veteran  
- **Author 3**: Educational focus with clear explanations
- **Author 4**: Practical field experience emphasis

Each author has writing samples that the system uses to match voice and style.

## 🤖 API Support

Supports multiple AI providers:
- **OpenAI** (GPT-4, GPT-3.5)
- **Google Gemini** (Gemini Pro)
- **XAI** (Grok)
- **DeepSeek** (DeepSeek-V2)

Configure in `config/credentials.json`:
```json
{
  "provider": "openai",
  "openai_api_key": "your-key-here",
  "model": "gpt-4-turbo-preview"
}
```

## 📊 Output Format

Generated articles include:
- **YAML frontmatter** with comprehensive metadata
- **Structured sections** (Introduction, Comparison, Contaminants, Substrates)
- **SEO-optimized** titles and descriptions
- **Social media** ready content
- **Technical accuracy** with real references

## 🔬 Technical Authenticity Features

The Technical Authenticity Optimizer dynamically researches:
- **Material-specific** technical properties
- **Real equipment** models and manufacturers
- **Industry standards** (ASTM, ISO, ANSI numbers)
- **Authentic applications** and case studies
- **Processing parameters** and challenges

Example injected content:
- "Hafnium's thermal conductivity of 23 W/m·K affects laser processing"
- "IPG Photonics YLR-1000 fiber laser system"
- "ASTM B776 - Standard Specification for Hafnium Alloys"

## 🎯 Use Cases

### **Content Marketing**
- **Blog posts** for laser cleaning companies
- **Technical articles** for industry publications
- **Educational content** for training materials

### **SEO Content**
- **Material-specific** landing pages
- **Comparison articles** vs traditional methods
- **Technical guides** for different substrates

### **Research & Development**
- **Baseline content** for technical documentation
- **Market research** article generation
- **Competitive analysis** content

## 🧪 Testing & Experimentation

### **A/B Testing Optimizers**
```bash
# Test individual optimizers
python3 run.py  # iterative only
python3 run.py  # writing_sample only
python3 run.py  # technical_authenticity only
```

### **Order Testing**
```bash
# Different optimization orders
python3 run.py  # 1→2→3
python3 run.py  # 3→1→2
python3 run.py  # 2→3→1
```

### **Material Testing**
```python
# Test different materials
context = {"material": "titanium", "author_id": 1}
context = {"material": "aluminum", "author_id": 2}
context = {"material": "steel", "author_id": 3}
```

## 🔍 Logging & Monitoring

Comprehensive logging shows:
- **Step-by-step** optimization progress
- **Word count** changes per section
- **API call** tracking
- **Error handling** with detailed messages
- **Performance metrics** for each phase

Log files saved to `logs/` with timestamps.

## 🚀 Performance

- **Caching**: Material research cached to avoid repeated API calls
- **Parallel processing**: Multiple sections processed efficiently
- **Error recovery**: Graceful fallbacks for API failures
- **Optimization**: Smart content selection based on section relevance

## 📈 Scalability

- **Multi-material**: Automatically adapts to any material
- **Dynamic knowledge**: LLM-researched technical facts
- **Configurable**: Easy to add new optimizers
- **Modular**: Each component independently testable

## 🛠️ Development

### **Adding New Optimizers**
1. Create optimizer class extending `BaseOptimizer`
2. Add to `simple_order_optimizer.py`
3. Update `optimization_config` in `run.py`

### **Adding New Authors**
1. Add profile to `authors/authors.json`
2. Add writing samples to `optimizers/writing_sample/samples/`
3. Update author references in context

### **Adding New Materials**
No code changes needed - system dynamically researches any material.

## 🎯 Roadmap

- **Multi-language** support
- **Custom prompts** per material type
- **Batch processing** for multiple articles
- **Performance analytics** dashboard
- **Custom author** creation tools

---

**Z-Beam Generator: Sophisticated AI content generation with human-like authenticity and technical precision.**