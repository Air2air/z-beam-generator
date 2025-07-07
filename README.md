# Z-Beam Generator

> **📖 DOCUMENTATION**: See [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md) for ALL project information, development rules, and technical details.

**Z-Beam Generator** creates optimized MDX content for laser cleaning websites using a radically simplified, single-pass architecture.

## Quick Start

1. **Configure**: Edit `run.py` to set your material, provider, and API keys
2. **Run**: `python run.py` 
3. **Output**: MDX files generated in `../z-beam-test-push/app/content/`

## For Developers

**🔥 CRITICAL**: Read [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md) before making ANY changes. This project enforces extreme simplicity and anti-bloat principles.

## Architecture

- **Single-pass generation**: No iteration or optimization during production
- **Template-driven**: Pre-optimized JSON templates with minimal logic
- **Fail-fast**: Clear error messages, no graceful degradation
- **Anti-hardcoding**: All configuration via GlobalConfigManager

See [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md) for complete technical details.
