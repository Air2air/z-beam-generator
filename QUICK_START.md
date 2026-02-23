# Z-Beam Generator - Quick Start Guide

**Get up and running in 5 minutes** ⚡

---

## 📋 Prerequisites

- Python 3.12+
- API keys for DeepSeek, Grok, and Winston.ai
- Basic command line knowledge

## ⚠️ Execution Requirement (No venv)

- Run all project tasks directly with `python3` from the repository root.
- Do **not** create or activate a virtual environment for routine generation, postprocess, export, integrity, or test commands.
- Example: `python3 run.py --integrity-check --quick`

---

## 🚀 Installation

### 1. Clone & Install

```bash
git clone https://github.com/Air2air/z-beam-generator.git
cd z-beam-generator
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (required):
#   DEEPSEEK_API_KEY=your_key_here
#   GROK_API_KEY=your_key_here  
#   WINSTON_API_KEY=your_key_here
```

### 3. Validate Setup

```bash
# Test API connections
python3 run.py --test-api

# Run integrity check
python3 run.py --integrity-check
```

---

## 🎯 First Generation

### Single Component

```bash
# Generate a micro
python3 run.py --micro "Aluminum"

# Generate a material description
python3 run.py --material-description "Steel"

# Generate an FAQ
python3 run.py --faq "Copper"
```

### Full Material

```bash
# Generate and export all components for a material
python3 run.py --material "Stainless Steel" --deploy
```

---

## 📊 Batch Operations

```bash
# Test batch generation (10 materials)
python3 run.py --batch-test

# Full deployment (all materials)
python3 run.py --deploy
```

---

## 🔍 Quality Checks

```bash
# View completeness report
python3 run.py --data-completeness-report

# Check recent Winston scores
sqlite3 data/winston_feedback.db "SELECT material, component_type, human_score, timestamp FROM detection_results ORDER BY timestamp DESC LIMIT 10"
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| **API connection fails** | Check `.env` has valid API keys |
| **Generation fails** | Run `--integrity-check` for diagnostics |
| **Missing material** | Check `data/materials/Materials.yaml` |

**Full Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📖 Next Steps

- **📖 Documentation Map**: [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) - Complete navigation
- **🤖 AI Assistant Guide**: [.github/copilot-instructions.md](.github/copilot-instructions.md) - Development guidelines
- **❓ Quick Reference**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Fast problem resolution
- **🏗️ Architecture**: [docs/02-architecture/](docs/02-architecture/) - System design

---

**Last Updated**: November 17, 2025  
**Version**: 3.0.0
