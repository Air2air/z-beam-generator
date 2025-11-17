# Z-Beam Generator - Quick Start Guide

**Get up and running in 5 minutes** ⚡

---

## 📋 Prerequisites

- Python 3.12+
- API keys for DeepSeek, Grok, and Winston.ai
- Basic command line knowledge

---

## 🚀 Installation

### 1. Clone & Setup Environment

```bash
git clone https://github.com/Air2air/z-beam-generator.git
cd z-beam-generator

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Configure API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
# Required keys:
# - DEEPSEEK_API_KEY
# - GROK_API_KEY  
# - WINSTON_API_KEY
```

### 3. Validate Setup

```bash
# Test API connections
python3 run.py --test-api

# Check environment
python3 run.py --check-env
```

---

## 🎯 First Generation

### Generate a Caption

```bash
# Basic caption generation
python3 run.py --caption "Aluminum"

# With specific author voice
python3 run.py --caption "Steel" --author canadian
```

### Generate Other Components

```bash
# Generate subtitle
python3 run.py --subtitle "Brass"

# Generate FAQ
python3 run.py --faq "Titanium"

# Generate description
python3 run.py --description "Copper"
```

### Deploy All Components

```bash
# Generate and export everything for a material
python3 run.py --material "Stainless Steel" --deploy
```

---

## 📊 Check Quality

### View Generation Results

```bash
# Check Winston.ai human scores
python3 run.py --data-completeness-report

# View recent generations
sqlite3 data/winston_feedback.db "SELECT material, component_type, human_score, timestamp FROM detection_results ORDER BY timestamp DESC LIMIT 10"
```

### Integrity Checks

```bash
# Run pre-generation integrity check
python3 run.py --integrity-check

# Post-generation checks run automatically after each generation
```

---

## 🆘 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **API connection fails** | Check keys in `.env` file |
| **Winston SSL errors** | Fixed - using `https://api.gowinston.ai` |
| **Generation fails** | Run `--integrity-check` for diagnostics |
| **Missing material** | Check `data/materials/Materials.yaml` |

### Get Help

```bash
# View all commands
python3 run.py --help

# Diagnostic tools
python3 scripts/tools/api_terminal_diagnostics.py winston
```

---

## 📖 Next Steps

1. **Read Documentation**: `docs/INDEX.md` - Complete navigation hub
2. **Understand System**: `docs/QUICK_REFERENCE.md` - Fast problem resolution
3. **Configure Voice**: `docs/06-ai-systems/voice-system.md` - Author profiles
4. **Batch Operations**: `docs/04-operations/batch-operations.md` - Generate multiple materials

---

## 🤖 For AI Assistants

If you're an AI assistant (Copilot, Grok, Claude):
1. Read `AI_ASSISTANT_GUIDE.md` first
2. Check `docs/01-getting-started/ai-assistants.md` for specific guidance
3. Use `docs/QUICK_REFERENCE.md` for common issues

---

## 📞 Support

- **Documentation**: `/docs/INDEX.md`
- **Issues**: GitHub Issues
- **Quick Ref**: `/docs/QUICK_REFERENCE.md`

---

**Last Updated**: November 16, 2025  
**Version**: 2.0 (Post-cleanup)
